"""Live mode: the simulator and matcher as separate services over a bus.

The central test: over an in-memory bus with zero latency (lockstep), live mode
gives *identical* results to the offline simulator, so everything the live path
adds (events, JSON, the matcher's rebuilt view, per-partition watermarks)
loses nothing. The Kafka test at the end runs only when a broker is up.
"""
import random
import socket
import threading
import uuid
from collections import deque
from dataclasses import asdict

import numpy as np
import pytest

from ridesync.live.bus import InMemoryBus, InMemoryConsumer
from ridesync.live.lockstep import run_lockstep
from ridesync.live.matcher import Matcher
from ridesync.live.schema import (
    DISPATCH_OFFERS, DRIVER_EVENTS, OFFER_RESPONSES, RIDER_EVENTS, dispatch_from_dict, run_config,
)
from ridesync.live.world import LiveConfig, LiveSimulation
from ridesync.matching import CancelBelief, CostParams
from ridesync.sim import SimConfig, simulate, summarize
from ridesync.sim.config import DispatchConfig
from ridesync.sim.engine import RiderState

SMALL = SimConfig().with_(**{
    "demand.duration_s": 1800.0, "demand.warmup_s": 300.0, "demand.requests_per_hour": 900.0,
    "drivers.num_drivers": 80,
})
AWARE = CostParams(trip_value_s=900.0, cancel=CancelBelief())
CONFIGS = {
    "greedy@10": {"dispatch.strategy": "global_greedy", "dispatch.interval_s": 10.0},
    "hungarian@5": {"dispatch.strategy": "hungarian", "dispatch.interval_s": 5.0},
    "lsa@30+aware+pruned+shadow": {
        "dispatch.strategy": "lsa", "dispatch.interval_s": 30.0, "dispatch.cost": AWARE,
        "dispatch.max_candidates": 10, "dispatch.shadow_strategy": "global_greedy",
    },
    "lsa@10+no-chaining+seed3": {
        "dispatch.strategy": "lsa", "dispatch.interval_s": 10.0, "dispatch.chain_horizon_s": 0.0, "seed": 3,
    },
}


def outcome(sim):
    riders = [(r.state, r.matched_t, r.pickup_t, r.dropoff_t, r.quoted_eta_s, r.driver_id, r.cancel_reason,
               r.cancel_t) for r in sim.riders]
    drivers = [dict(d.time_in) for d in sim.drivers]
    metrics = {k: v for k, v in summarize(sim).items() if not k.startswith("solve_ms")}
    return riders, drivers, metrics


# ------------------------------------------------------------ lockstep
@pytest.mark.parametrize("partitions", [1, 3])
@pytest.mark.parametrize("name", CONFIGS)
def test_lockstep_equals_offline(name, partitions):
    cfg = SMALL.with_(**CONFIGS[name])
    sim, matcher = run_lockstep(cfg, partitions)
    np.testing.assert_equal(outcome(sim), outcome(simulate(cfg)))
    assert not any(k.startswith("rejected") for k in sim.outcomes)
    assert matcher.skipped == 0 and matcher.expired == 0


class ShuffledBus(InMemoryBus):
    """Delivers a random interleaving of partitions (order kept only within each), a random part per poll."""

    def __init__(self, partitions: int, seed: int):
        super().__init__(partitions)
        self.rng = random.Random(seed)

    def consumer(self, topics, from_beginning, skip_types=()):
        return ShuffledConsumer(self, topics, from_beginning, skip_types)


class ShuffledConsumer(InMemoryConsumer):
    def __init__(self, *args):
        super().__init__(*args)
        self.queues = {}

    def poll(self, timeout_s=0.0):
        for m in super().poll():
            self.queues.setdefault((m.topic, m.partition), deque()).append(m)
        out = []
        total = sum(len(q) for q in self.queues.values())
        for _ in range(self.bus.rng.randint(1, total) if total else 0):
            q = self.bus.rng.choice([q for q in self.queues.values() if q])
            out.append(q.popleft())
        return out

    def caught_up(self):
        return super().caught_up() and not any(self.queues.values())


@pytest.mark.parametrize("seed", [0, 1])
def test_lockstep_survives_reordering(seed):
    # Kafka only orders messages within a partition. With deliveries interleaved across partitions and
    # topics, and split over several polls, the watermark still guarantees the matcher sees every event
    # before a batch, so the results stay identical.
    cfg = SMALL.with_(**CONFIGS["lsa@30+aware+pruned+shadow"])
    sim, _ = run_lockstep(cfg, bus=ShuffledBus(3, seed))
    np.testing.assert_equal(outcome(sim), outcome(simulate(cfg)))


def test_matcher_restart_rebuilds_state():
    cfg = SMALL.with_(**CONFIGS["lsa@10+no-chaining+seed3"])
    bus = InMemoryBus(3)
    sim = LiveSimulation(cfg, bus, LiveConfig(speed=0.0, tick_s=10.0, ping_s=0.0))
    box = {"matcher": Matcher(bus, travel=sim.travel), "ticks": 0, "checked": False}

    def settle():
        box["ticks"] += 1
        if box["ticks"] == 60:  # the matcher "crashes"; a fresh one replays the topics from the beginning
            fresh = Matcher(bus, travel=sim.travel)
            fresh.step()
            assert not fresh.catching_up
            assert set(fresh.waiting) == set(sim.waiting)
            for d in sim.drivers:
                f = fresh.drivers[d.id]
                assert (f.state, f.free_at, f.has_next) == (d.state, d.free_at, d.has_next)
                assert f.pos.tolist() == d.pos.tolist()
            box["matcher"], box["checked"] = fresh, True
        while box["matcher"].step() + sim.poll(0.0):
            pass

    sim.lockstep = settle
    sim.run()
    assert box["checked"]
    assert all(r.state in (RiderState.DONE, RiderState.CANCELLED) for r in sim.riders)
    assert not any(k.startswith("rejected") for k in sim.outcomes)
    # The fresh matcher treats the boundary at the restart tick as already handled, so riders wait one
    # extra batch there; otherwise the run carries on as before.
    live, offline = summarize(sim), summarize(simulate(cfg))
    assert abs(live["completed"] - offline["completed"]) <= 0.02 * offline["completed"]


# ---------------------------------------------------------- matcher unit
def _control(bus, typ, run, t, **extra):
    for topic in (RIDER_EVENTS, DRIVER_EVENTS):
        for p in range(bus.n_partitions):
            bus.produce(topic, "", {"v": 1, "type": typ, "run": run, "t": t, **extra}, partition=p)


def _run_start(bus, run, started_ms, cfg=SMALL):
    _control(bus, "run_start", run, 0.0, started_ms=started_ms,
             config=run_config(cfg.dispatch, cfg.travel, offer_timeout_s=15.0))


def test_matcher_restores_offers_in_flight():
    bus = InMemoryBus(1)
    _run_start(bus, "r1", 1)
    bus.produce(RIDER_EVENTS, "3", {"v": 1, "type": "requested", "run": "r1", "t": 1.0, "rider": 3,
                                    "origin": [40.75, -73.98], "dest": [40.76, -73.97], "request_t": 1.0})
    bus.produce(DISPATCH_OFFERS, "7", {"v": 1, "type": "offer", "run": "r1", "t": 5.0, "offer_id": "1-3-7",
                                       "batch_t": 5.0, "rider": 3, "driver": 7, "eta_s": 100.0, "wall": 0.0})
    m = Matcher(bus)
    m.step()
    assert "1-3-7" in m.pending  # sent before the restart, still unanswered: rider 3 and driver 7 stay reserved
    bus.produce(OFFER_RESPONSES, "3", {"v": 1, "type": "offer_response", "run": "r1", "t": 6.0,
                                       "offer_id": "1-3-7", "rider": 3, "driver": 7, "outcome": "declined"})
    m.step()
    assert not m.pending
    assert m.declined == {3: {7}}


def test_matcher_follows_newest_run_and_ignores_older():
    bus = InMemoryBus(2)
    _run_start(bus, "old", 1)
    _run_start(bus, "new", 2)
    _control(bus, "tick", "old", 50.0)
    m = Matcher(bus)
    m.step()
    assert m.run == "new"
    assert m.watermark() == 0.0  # the old run's ticks don't move the new run's watermark


def test_watermark_waits_for_every_partition():
    bus = InMemoryBus(2)
    _run_start(bus, "r", 1)
    m = Matcher(bus)
    m.step()
    for topic, p in [(RIDER_EVENTS, 0), (RIDER_EVENTS, 1), (DRIVER_EVENTS, 0)]:
        bus.produce(topic, "", {"v": 1, "type": "tick", "run": "r", "t": 10.0}, partition=p)
    m.step()
    assert m.watermark() == 0.0
    bus.produce(DRIVER_EVENTS, "", {"v": 1, "type": "tick", "run": "r", "t": 10.0}, partition=1)
    m.step()
    assert m.watermark() == 10.0


def test_dispatch_config_round_trip():
    cfg = DispatchConfig(strategy="lsa", interval_s=30.0, cost=AWARE, max_candidates=20,
                         shadow_strategy="global_greedy")
    assert dispatch_from_dict(asdict(cfg)) == cfg
    plain = DispatchConfig()
    assert dispatch_from_dict(asdict(plain)) == plain


def test_live_rejects_event_driven_dispatch():
    with pytest.raises(ValueError, match="interval_s"):
        LiveSimulation(SMALL.with_(**{"dispatch.interval_s": 0.0}), InMemoryBus())


def test_simulator_rejects_stale_and_duplicate_offers():
    cfg = SMALL.with_(**{"dispatch.interval_s": 10.0, "drivers.accept_prob": 1.0})
    sim = LiveSimulation(cfg, InMemoryBus(1), LiveConfig(speed=0.0, ping_s=0.0))
    for rid in (0, 1):
        sim._on_request(rid)
    offer = {"offer_id": "a", "batch_t": 0.0, "rider": 0, "driver": 0, "eta_s": 60.0}
    sim.apply_offer(offer)
    sim.apply_offer(offer)  # redelivered: a no-op
    assert dict(sim.outcomes) == {"accepted": 1}
    sim.apply_offer({**offer, "offer_id": "b", "driver": 1})               # rider 0 is already matched
    sim.apply_offer({**offer, "offer_id": "c", "rider": 1})                # driver 0 is now en route
    sim.now = 20.0
    sim.apply_offer({**offer, "offer_id": "d", "rider": 1, "driver": 2})   # 20 s after its batch: too late
    assert sim.outcomes["rejected:rider_gone"] == 1
    assert sim.outcomes["rejected:driver_busy"] == 1
    assert sim.outcomes["rejected:expired"] == 1
    assert sim.riders[1].state is RiderState.WAITING


# ---------------------------------------------------------------- Kafka
BOOTSTRAP = "localhost:9092"


def _broker_up() -> bool:
    try:
        with socket.create_connection(("localhost", 9092), timeout=0.5):
            return True
    except OSError:
        return False


@pytest.mark.skipif(not _broker_up(), reason="no Kafka broker on localhost:9092 (docker compose up -d kafka)")
def test_kafka_end_to_end():
    pytest.importorskip("confluent_kafka")
    from confluent_kafka.admin import AdminClient

    from ridesync.live.kafka_bus import KafkaBus
    from ridesync.live.topics import ensure_topics

    prefix = f"ridesync-test-{uuid.uuid4().hex[:8]}."
    ensure_topics(BOOTSTRAP, partitions=3, prefix=prefix)
    try:
        matcher = Matcher(KafkaBus(BOOTSTRAP, prefix))
        stop = threading.Event()

        def serve():
            while not stop.is_set():
                matcher.step(0.02)

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        cfg = SMALL.with_(**{"demand.duration_s": 900.0, "demand.warmup_s": 120.0, "drivers.num_drivers": 60,
                             "dispatch.strategy": "lsa", "dispatch.interval_s": 10.0})
        sim = LiveSimulation(cfg, KafkaBus(BOOTSTRAP, prefix), LiveConfig(speed=50.0, ping_s=5.0))
        sim.run()
        stop.set()
        thread.join(5)

        assert matcher.run == sim.run_id and matcher.stats.batches > 0
        assert all(r.state in (RiderState.DONE, RiderState.CANCELLED) for r in sim.riders)
        offers = sum(sim.outcomes.values())
        rejected = sum(v for k, v in sim.outcomes.items() if k.startswith("rejected"))
        # At 50x, 1 ms of wall-clock delay is 50 ms of simulated time; a heavily loaded machine can push
        # offers past their 15 s deadline. The outcomes are in the message if this ever trips.
        assert offers > 0 and rejected <= 0.05 * offers, dict(sim.outcomes)
        # Never two riders on board one driver at once.
        trips = {}
        for r in sim.riders:
            if r.state is RiderState.DONE:
                trips.setdefault(r.driver_id, []).append((r.pickup_t, r.dropoff_t))
        for spans in trips.values():
            spans.sort()
            assert all(a[1] <= b[0] for a, b in zip(spans, spans[1:]))
        live, offline = summarize(sim), summarize(simulate(cfg))
        assert abs(live["completed"] - offline["completed"]) <= 0.1 * offline["completed"]
    finally:
        admin = AdminClient({"bootstrap.servers": BOOTSTRAP})
        topics = [t for t in admin.list_topics(timeout=10).topics if t.startswith(prefix)]
        if topics:
            for f in admin.delete_topics(topics).values():
                f.result()
