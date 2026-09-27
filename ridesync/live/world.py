"""The live simulator: the offline engine's world, paced by the wall clock and talking over a bus.

It is the source of truth. It publishes rider and driver events, applies the
offers the matcher sends, and answers each one on ``offer-responses``. The
matcher only proposes: an offer for a rider who has already cancelled, or for a
driver who is no longer free, is rejected with a reason.

Dispatch events of the offline engine become *ticks* here: at every ``tick_s``
of simulated time the simulator writes a ``tick`` to every partition of the
world topics, after all events up to that time. The matcher dispatches on those
watermarks (event time), so results don't depend on the speed factor, only on
how long offers take to come back.

With ``speed <= 0`` the simulator doesn't pace itself. A ``lockstep`` callback
runs the matcher to completion at every tick instead (``ridesync.live.lockstep``),
which reproduces the offline simulation exactly.
"""
from __future__ import annotations

import heapq
import random
import time
from collections import Counter
from dataclasses import dataclass
from typing import Callable, List, Optional

from ..geo import TravelTimeModel
from ..sim.config import SimConfig
from ..sim.engine import DISPATCH, REQUEST, Driver, DriverState, Rider, RiderState, Simulation
from .bus import Bus
from .schema import (
    CONTROL_TYPES, DISPATCH_BATCHES, DISPATCH_OFFERS, DRIVER_EVENTS, OFFER_RESPONSES, RIDER_EVENTS, VERSION,
    WORLD_TOPICS, run_config,
)

PING = DISPATCH + 1  # after dispatch at equal timestamps


@dataclass(frozen=True)
class LiveConfig:
    speed: float = 10.0            # simulated seconds per wall-clock second; <= 0 = unpaced (lockstep)
    tick_s: float = 1.0            # watermark interval, simulated seconds
    ping_s: float = 5.0            # driver location pings (for maps and stream features); 0 = off
    offer_timeout_s: float = 15.0  # offers applied later than this after their batch are rejected
    drain_s: float = 2.0           # wall seconds to keep reading batch stats after the run ends
    # A bad network: this share of rider/driver events is published up to jitter_ms late (wall clock),
    # so they reach consumers out of order. Control messages are never delayed.
    jitter_frac: float = 0.0
    jitter_ms: float = 0.0


class LiveSimulation(Simulation):
    def __init__(self, cfg: SimConfig, bus: Bus, live: LiveConfig = LiveConfig(),
                 travel: Optional[TravelTimeModel] = None, run_id: Optional[str] = None):
        if cfg.dispatch.interval_s <= 0:
            raise ValueError("live mode dispatches in batches: set dispatch.interval_s > 0")
        super().__init__(cfg, travel)
        self.live = live
        self.bus = bus
        self.producer = bus.producer()
        # Assigned before run_start is sent, so every offer for this run is seen.
        self.inbox = bus.consumer([DISPATCH_OFFERS, DISPATCH_BATCHES], from_beginning=False)
        self.started_ms = int(time.time() * 1000)
        self.run_id = run_id or f"{self.started_ms}-seed{cfg.seed}"
        self.lockstep: Optional[Callable[[], None]] = None

        self.offer_delay_s: List[float] = []  # simulated time from batch to the offer being applied
        self.offer_transit_ms: List[float] = []  # wall time from the matcher sending an offer to it arriving here
        self.tick_to_batch_ms: List[float] = []  # wall time from sending a tick to the matcher solving that batch
        self.outcomes: Counter = Counter()    # accepted / declined / quote_cancelled / rejected:<reason>
        self.max_lag_s = 0.0                  # worst simulated-time lag behind the wall clock
        self._seen_offers: set = set()
        self._tick_no = 0
        self._wall0 = time.monotonic()
        self._wall0_ms = float(self.started_ms)
        # Event time: the wall-clock moment an event is due, so consumers (Flink) see times that move forward
        # across runs. msps = wall milliseconds per simulated second.
        self._msps = 1000.0 / live.speed if live.speed > 0 else 1000.0
        self._delayed: list = []
        self._jitter_rng = random.Random(cfg.seed * 7919 + 17)
        self.delayed_events = 0
        self._status_seq = [0] * len(self.drivers)  # orders a driver's statuses that share a timestamp

    # -------------------------------------------------------------- publish
    def _send(self, topic: str, key, msg: dict, partition: Optional[int] = None) -> None:
        msg.update(v=VERSION, run=self.run_id, t=self.now, ts=round(self._wall0_ms + self.now * self._msps),
                   msps=self._msps)
        if (self.live.jitter_frac > 0 and self.live.speed > 0 and topic in WORLD_TOPICS
                and msg["type"] not in CONTROL_TYPES and self._jitter_rng.random() < self.live.jitter_frac):
            due = time.monotonic() + self._jitter_rng.uniform(0, self.live.jitter_ms) / 1000
            heapq.heappush(self._delayed, (due, self.delayed_events, topic, str(key), msg, partition))
            self.delayed_events += 1
            return
        self.producer.produce(topic, str(key), msg, partition)

    def _pump(self, everything: bool = False) -> None:
        """Publish delayed events that are due (or all of them)."""
        now = time.monotonic()
        while self._delayed and (everything or self._delayed[0][0] <= now):
            _, _, topic, key, msg, partition = heapq.heappop(self._delayed)
            self.producer.produce(topic, key, msg, partition)

    def _broadcast(self, typ: str, **fields) -> None:
        for topic in WORLD_TOPICS:
            for p in range(self.bus.partitions(topic)):
                self._send(topic, "", {"type": typ, **fields}, partition=p)

    def _publish_rider(self, r: Rider, kind: str) -> None:
        msg = {"type": kind, "rider": r.spec.id}
        if kind == "requested":
            msg.update(origin=r.spec.origin.tolist(), dest=r.spec.dest.tolist(), request_t=r.spec.request_t)
        elif kind == "cancelled":
            msg["reason"] = r.cancel_reason
        else:
            msg["driver"] = r.driver_id
            if kind == "matched":
                msg["quoted_eta_s"] = r.quoted_eta_s
        self._send(RIDER_EVENTS, r.spec.id, msg)

    def _publish_driver(self, d: Driver) -> None:
        self._status_seq[d.id] += 1
        self._send(DRIVER_EVENTS, d.id, {
            "type": "status", "driver": d.id, "seq": self._status_seq[d.id], "state": d.state.value,
            "pos": d.pos.tolist(), "free_at": d.free_at, "has_next": d.has_next, "rider": d.rider_id,
        })

    # ------------------------------------------------------------------ run
    def run(self) -> "LiveSimulation":
        self._wall0 = time.monotonic()
        self._wall0_ms = time.time() * 1000
        self._broadcast("run_start", started_ms=self.started_ms,
                        config=run_config(self.cfg.dispatch, self.cfg.travel, self.live.offer_timeout_s))
        for d in self.drivers:
            self._publish_driver(d)
        for r in self.riders:
            self._schedule(r.spec.request_t, REQUEST, r.spec.id)
        self._schedule_tick()
        if self.live.ping_s > 0:
            self._schedule(self.live.ping_s, PING)
        self.producer.flush()

        handlers = self._handlers()
        handlers[PING] = self._on_ping
        while self._events:
            if self.live.speed > 0:
                self._pace(self._events[0][0])
            t, kind, _, args = heapq.heappop(self._events)
            self.now = t
            handlers[kind](*args)

        self._pump(everything=True)
        self._broadcast("run_end")
        self.producer.flush()
        if self.live.speed > 0:
            deadline = time.monotonic() + self.live.drain_s
            while time.monotonic() < deadline:
                self.poll(0.05)
        self._finish()
        return self

    def _schedule_tick(self) -> None:
        self._tick_no += 1
        self._schedule(self._tick_no * self.live.tick_s, DISPATCH)

    def _on_dispatch(self) -> None:
        # Offline this runs the matcher; live it publishes the watermark and lets the matcher act.
        self._broadcast("tick", wall=time.time())  # no flush: the producer's short linger sends it within milliseconds
        if self.lockstep is not None:
            self.lockstep()
        if self.now < self.cfg.demand.duration_s or self.waiting:
            self._schedule_tick()

    def _on_ping(self) -> None:
        for d in self.drivers:
            self._send(DRIVER_EVENTS, d.id, {"type": "ping", "driver": d.id, "pos": d.leg.position(self.now).tolist()})
        if self._events:  # stop pinging once nothing else is left to happen
            self._schedule(self.now + self.live.ping_s, PING)

    # --------------------------------------------------------------- pacing
    def _clock(self) -> float:
        return (time.monotonic() - self._wall0) * self.live.speed

    def _pace(self, t_next: float) -> None:
        """Wait until the wall clock reaches t_next, applying offers as they arrive."""
        self.poll(0.0)
        while self._events and self._events[0][0] >= t_next:
            self._pump()
            ahead = t_next - self._clock()
            if ahead <= 0:
                self.max_lag_s = max(self.max_lag_s, -ahead)
                return
            self.poll(min(ahead / self.live.speed, 0.05))

    # --------------------------------------------------------------- offers
    def poll(self, timeout_s: float) -> int:
        """Apply waiting offers and record batch stats. Returns the number of messages handled."""
        msgs = self.inbox.poll(timeout_s)
        for m in msgs:
            v = m.value
            if v.get("run") != self.run_id:
                continue
            if v["type"] == "offer":
                if self.live.speed > 0:
                    # An offer lands at the current wall-clock time, never past the next pending event.
                    nxt = self._events[0][0] if self._events else float("inf")
                    self.now = max(self.now, min(self._clock(), nxt))
                self.apply_offer(v)
            elif v["type"] == "batch":
                self.stats.record_batch(v["riders"], v["drivers"], v["solve_ms"], v["cost"], v["shadow_cost"])
                if v.get("tick_lag_ms") is not None:
                    self.tick_to_batch_ms.append(v["tick_lag_ms"])
        return len(msgs)

    def apply_offer(self, offer: dict) -> None:
        oid = offer["offer_id"]
        if oid in self._seen_offers:  # at-least-once delivery: a redelivered offer is a no-op
            return
        self._seen_offers.add(oid)
        r, d = self.riders[offer["rider"]], self.drivers[offer["driver"]]
        self.offer_delay_s.append(self.now - offer["batch_t"])
        if "wall" in offer:
            self.offer_transit_ms.append((time.time() - offer["wall"]) * 1000)

        reason = None
        if r.state is not RiderState.WAITING:
            reason = "rider_gone"
        elif d.state is DriverState.EN_ROUTE or d.has_next:
            reason = "driver_busy"
        elif self.now - offer["batch_t"] > self.live.offer_timeout_s:
            reason = "expired"

        msg = {"type": "offer_response", "offer_id": oid, "rider": r.spec.id, "driver": d.id}
        if reason is None:
            msg["outcome"] = outcome = self._offer(r, d, offer["eta_s"])
            self.outcomes[outcome] += 1
        else:
            msg.update(outcome="rejected", reason=reason)
            self.outcomes[f"rejected:{reason}"] += 1
        self._send(OFFER_RESPONSES, r.spec.id, msg)
