"""The matcher service: builds its own view of the world from events and dispatches on event time.

    python -m ridesync.live.matcher [--bootstrap localhost:9092] [--exit-after-run]

State (rebuilt from the topics, never shared with the simulator):

- drivers: the latest ``status`` per driver (``ridesync.dispatch.DriverView``)
- waiting riders: ``requested`` minus ``matched`` / ``cancelled``
- declined (rider, driver) pairs, from offer responses
- pending offers: sent but not yet answered. Their rider and driver are left out
  of later batches until the answer arrives or the offer times out.

A batch for boundary ``k * interval_s`` fires once the watermark (the minimum
latest tick over all world-topic partitions) reaches it, so every event up to
that time has been read. If the matcher falls behind by several boundaries it
fires once, at the latest one, and counts the others as skipped.

On start the matcher reads every topic from the beginning ("catch-up") without
dispatching, which restores the current run's state including offers still in
flight. It follows whichever run started most recently and takes that run's
dispatch and travel config from its ``run_start`` message.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import dataclass
from typing import Dict, Optional, Set

import numpy as np

from ..dispatch import DispatchStats, DriverState, build_batch, solve_batch
from ..geo import TravelTimeModel
from ..matching import get_strategy
from ..routing import make_travel_model
from .bus import Bus, Message
from .schema import (
    CONTROL_TYPES, DISPATCH_BATCHES, DISPATCH_OFFERS, DRIVER_EVENTS, OFFER_RESPONSES, RIDER_EVENTS, VERSION,
    WORLD_TOPICS, dispatch_from_dict, travel_from_dict,
)


@dataclass
class DriverRecord:
    id: int
    state: DriverState
    pos: np.ndarray
    free_at: float
    has_next: bool


@dataclass
class WaitingRider:
    id: int
    origin: np.ndarray
    request_t: float


@dataclass
class Pending:
    rider: int
    driver: int
    batch_t: float


class Matcher:
    def __init__(self, bus: Bus, travel: Optional[TravelTimeModel] = None):
        """``travel`` overrides the run's travel model (tests share one instance with the simulator)."""
        self.bus = bus
        self.producer = bus.producer()
        self.consumer = bus.consumer(
            [RIDER_EVENTS, DRIVER_EVENTS, OFFER_RESPONSES, DISPATCH_OFFERS], from_beginning=True, skip_types=["ping"]
        )
        self.partitions = [(t, p) for t in WORLD_TOPICS for p in range(bus.partitions(t))]
        self._travel_override = travel
        self._travel_cache: Dict[str, TravelTimeModel] = {}
        self.catching_up = True
        self.run: Optional[str] = None
        self.started_ms = -1
        self.messages = 0

    # ---------------------------------------------------------------- runs
    def _start_run(self, msg: dict) -> None:
        cfg = msg["config"]
        self.run, self.started_ms = msg["run"], msg["started_ms"]
        self.dispatch = dispatch_from_dict(cfg["dispatch"])
        self.offer_timeout_s = cfg["offer_timeout_s"]
        self.strategy = get_strategy(self.dispatch.strategy)
        self.shadow = get_strategy(self.dispatch.shadow_strategy) if self.dispatch.shadow_strategy else None
        if self._travel_override is not None:
            self.travel = self._travel_override
        else:
            key = json.dumps(cfg["travel"], sort_keys=True)
            if key not in self._travel_cache:
                self._travel_cache[key] = make_travel_model(travel_from_dict(cfg["travel"]))
            self.travel = self._travel_cache[key]

        self.drivers: Dict[int, DriverRecord] = {}
        self.waiting: Dict[int, WaitingRider] = {}
        self.declined: Dict[int, Set[int]] = {}
        self.pending: Dict[str, Pending] = {}
        self.resolved: Set[str] = set()
        self.marks: Dict[tuple, float] = {}
        self.mark_wall: Dict[tuple, float] = {}  # wall clock at which each partition's latest tick was sent
        self.replay_marks: Dict[tuple, float] = {}  # watermarks from history only (for resuming after catch-up)
        self.ended: Set[tuple] = set()
        self.next_k = 1
        self.seq = 0
        self.skipped = 0
        self.expired = 0
        self.stats = DispatchStats()

    def watermark(self) -> float:
        if self.run is None or len(self.marks) < len(self.partitions):
            return -math.inf
        return min(self.marks.values())

    def run_finished(self) -> bool:
        return self.run is not None and len(self.ended) == len(self.partitions)

    # -------------------------------------------------------------- events
    def handle(self, m: Message) -> None:
        v = m.value
        typ = v["type"]
        if typ == "run_start" and v["started_ms"] > self.started_ms:
            self._start_run(v)
        if v.get("run") != self.run:
            return  # an older run, or nothing started yet
        if typ == "run_end":
            # Not a watermark: the simulator stops ticking once nobody waits, then finishes the last
            # trips, so the jump to the end time holds no batch boundaries worth dispatching.
            self.ended.add((m.topic, m.partition))
        elif typ in CONTROL_TYPES:
            self.marks[(m.topic, m.partition)] = v["t"]
            self.mark_wall[(m.topic, m.partition)] = v.get("wall")
            if m.replay:
                self.replay_marks[(m.topic, m.partition)] = v["t"]
        elif m.topic == RIDER_EVENTS:
            rid = v["rider"]
            if typ == "requested":
                self.waiting[rid] = WaitingRider(rid, np.array(v["origin"]), v["request_t"])
            elif typ in ("matched", "cancelled"):
                self.waiting.pop(rid, None)
                self.declined.pop(rid, None)
        elif m.topic == DRIVER_EVENTS:
            if typ == "status":
                did = v["driver"]
                self.drivers[did] = DriverRecord(did, DriverState(v["state"]), np.array(v["pos"]), v["free_at"],
                                                 v["has_next"])
        elif m.topic == OFFER_RESPONSES:
            oid = v["offer_id"]
            self.resolved.add(oid)
            self.pending.pop(oid, None)
            if v["outcome"] == "declined" and v["rider"] in self.waiting:
                self.declined.setdefault(v["rider"], set()).add(v["driver"])
        elif m.topic == DISPATCH_OFFERS:
            # Our own offers. Only needed while catching up, to restore offers still in flight.
            if self.catching_up and v["offer_id"] not in self.resolved:
                self.pending[v["offer_id"]] = Pending(v["rider"], v["driver"], v["batch_t"])

    def step(self, timeout_s: float = 0.0) -> int:
        """Read what's available, then dispatch if a batch boundary has passed. Returns messages read."""
        msgs = self.consumer.poll(timeout_s)
        for m in msgs:
            self.handle(m)
        self.messages += len(msgs)
        if self.catching_up and self.consumer.caught_up():
            self.catching_up = False
            if self.run is not None and len(self.replay_marks) == len(self.partitions):
                # Joined a run in progress: boundaries up to the history's watermark were already dispatched
                # (by the previous matcher instance), so resume at the next one.
                self.next_k = math.floor(min(self.replay_marks.values()) / self.dispatch.interval_s) + 1
        if not self.catching_up:
            self._maybe_dispatch()
        return len(msgs)

    # ------------------------------------------------------------ dispatch
    def _maybe_dispatch(self) -> None:
        wm = self.watermark()
        if not math.isfinite(wm) or wm < self.next_k * self.dispatch.interval_s:
            return
        k = math.floor(wm / self.dispatch.interval_s)
        self.skipped += k - self.next_k
        self.next_k = k + 1
        self._expire(wm)
        # Latency diagnostic: the tick that completed this watermark was sent by the simulator at this wall time.
        sent = self.mark_wall.get(min(self.marks, key=self.marks.get))
        self._dispatch(k * self.dispatch.interval_s, sent)

    def _expire(self, wm: float) -> None:
        # The simulator rejects offers applied more than offer_timeout_s after their batch, and
        # its watermark only passes that deadline after it has handled or rejected the offer.
        for oid in [oid for oid, p in self.pending.items() if wm > p.batch_t + self.offer_timeout_s]:
            del self.pending[oid]
            self.expired += 1

    def _dispatch(self, now: float, tick_sent: Optional[float] = None) -> None:
        busy_r = {p.rider for p in self.pending.values()}
        busy_d = {p.driver for p in self.pending.values()}
        riders = sorted((w for w in self.waiting.values() if w.id not in busy_r), key=lambda w: (w.request_t, w.id))
        drivers = [self.drivers[i] for i in sorted(self.drivers) if i not in busy_d]
        batch = build_batch(
            now,
            [w.id for w in riders],
            np.array([w.origin for w in riders]),
            [w.request_t for w in riders],
            drivers,
            self.declined,
            self.travel,
            self.dispatch,
        )
        if batch is None:
            return
        result = solve_batch(batch, self.strategy, self.shadow)
        self.stats.record_batch(len(batch.rider_ids), len(batch.driver_ids), result.solve_ms,
                                result.cost, result.shadow_cost)
        self.seq += 1
        head = {"v": VERSION, "run": self.run, "t": now}
        self.producer.produce(DISPATCH_BATCHES, self.run, {
            **head, "type": "batch", "batch_t": now, "seq": self.seq, "riders": len(batch.rider_ids),
            "drivers": len(batch.driver_ids), "offers": len(result.pairs), "solve_ms": result.solve_ms,
            "cost": result.cost, "shadow_cost": result.shadow_cost, "skipped": self.skipped,
            "tick_lag_ms": None if tick_sent is None else (time.time() - tick_sent) * 1000,
        })
        head["wall"] = time.time()
        for rid, did, eta_s in result.pairs:
            oid = f"{self.seq}-{rid}-{did}"
            self.pending[oid] = Pending(rid, did, now)
            self.producer.produce(DISPATCH_OFFERS, str(did), {
                **head, "type": "offer", "offer_id": oid, "batch_t": now, "rider": rid, "driver": did, "eta_s": eta_s,
            })


def main(argv=None) -> None:
    from .kafka_bus import KafkaBus
    from .topics import ensure_topics

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--bootstrap", default="localhost:9092")
    ap.add_argument("--prefix", default="", help="topic name prefix (experiments use their own topics)")
    ap.add_argument("--exit-after-run", action="store_true", help="exit once the current run has ended")
    ap.add_argument("--log-every", type=float, default=10.0, help="status line interval, wall seconds")
    args = ap.parse_args(argv)

    ensure_topics(args.bootstrap, prefix=args.prefix)
    matcher = Matcher(KafkaBus(args.bootstrap, args.prefix))
    print("matcher: catching up...", flush=True)
    last_log = time.monotonic()
    stale: Optional[str] = None  # a run that had already ended when catch-up finished
    try:
        while True:
            was_catching_up = matcher.catching_up
            matcher.step(0.05)
            if was_catching_up and not matcher.catching_up:
                stale = matcher.run if matcher.run_finished() else None
                print(f"matcher: caught up after {matcher.messages} messages; ready", flush=True)
            now = time.monotonic()
            if now - last_log >= args.log_every:
                last_log = now
                if matcher.run is None:
                    print("matcher: waiting for a run", flush=True)
                else:
                    s = matcher.stats
                    print(f"matcher: run {matcher.run} wm={matcher.watermark():.0f}s batches={s.batches} "
                          f"waiting={len(matcher.waiting)} pending={len(matcher.pending)} "
                          f"skipped={matcher.skipped} expired={matcher.expired} "
                          f"solve_ms_mean={np.mean(s.solve_ms) if s.solve_ms else 0:.1f}", flush=True)
            if args.exit_after_run and not matcher.catching_up and matcher.run_finished() and matcher.run != stale:
                print(f"matcher: run {matcher.run} ended after {matcher.stats.batches} batches", flush=True)
                break
    except KeyboardInterrupt:
        pass
    finally:
        matcher.producer.flush()
        matcher.consumer.close()
    sys.exit(0)


if __name__ == "__main__":
    main()
