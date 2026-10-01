"""M10: repositioning, drivers logging on and off, and riders cancelling on late drivers, in live mode.

As for M3, the central check is that a lockstep run (in-memory bus, zero latency) gives *identical* results
to the offline simulator, now with each of these on: the matcher's repositioning plan, made from its own
rebuilt view of the world, is the offline plan, and the simulator's own driver and rider behaviour runs as
offline. Then: message reordering, a matcher restart in the middle of a run, and stale moves.
"""
from pathlib import Path

import numpy as np
import pytest

from ridesync.dispatch import DriverState
from ridesync.live.bus import InMemoryBus
from ridesync.live.lockstep import run_lockstep
from ridesync.live.matcher import Matcher
from ridesync.live.schema import run_config
from ridesync.live.world import LiveConfig, LiveSimulation
from ridesync.sim import SimConfig, simulate, summarize
from ridesync.sim.config import TravelConfig
from test_live import ShuffledBus, outcome

ZONES = "data/processed/taxi_zones.json"
POINTS = "data/models/zone_points.parquet"
DEMAND_MODEL = "data/models/demand.joblib"
needs_zones = pytest.mark.skipif(not (Path(ZONES).exists() and Path(POINTS).exists()),
                                 reason="needs the taxi zones and zone points (python -m ridesync.stream.zones, ml.train)")
needs_model = pytest.mark.skipif(not Path(DEMAND_MODEL).exists(), reason="needs the demand model (ml.train demand)")

# The synthetic city sits on midtown Manhattan, inside the taxi zones.
BASE = SimConfig().with_(**{
    "demand.duration_s": 2700.0, "demand.warmup_s": 300.0, "demand.requests_per_hour": 1200.0,
    "drivers.num_drivers": 110, "dispatch.strategy": "lsa", "dispatch.interval_s": 30.0,
    "dispatch.max_candidates": 15,
})
# The matcher believes drives take half as long as they do: quotes are optimistic, so riders give up.
LATE = {"riders.enroute_cancel": True, "riders.lateness_tolerance_median_s": 60.0}
OPTIMISTIC = {"belief": TravelConfig(speed_mps=BASE.travel.speed_mps * 2.0)}
PLANNED = {"reposition.policy": "planned", "reposition.interval_s": 120.0, "reposition.min_idle_s": 60.0}
FORECAST = {**PLANNED, "reposition.demand": "forecast", "demand.start": "2026-07-15T17:00:00"}
DRIFT = {"reposition.policy": "drift", "reposition.interval_s": 120.0, "reposition.min_idle_s": 60.0,
         "demand.start": "2026-07-15T17:00:00"}
SUPPLY = {"pricing.enabled": True, "drivers.num_drivers": 80, "supply.reserve_share": 0.3,
          "supply.log_on_elasticity": 1.5, "supply.chase_strength": 1.0, "supply.log_on_delay_s": 120.0,
          "supply.log_off_idle_s": 180.0}


def _same_as_offline(cfg, **kw):
    sim, matcher = run_lockstep(cfg, **kw)
    np.testing.assert_equal(outcome(sim), outcome(simulate(cfg)))
    assert not any(k.startswith("rejected") for k in sim.outcomes)
    assert not any(k.startswith("rejected") for k in sim.move_outcomes)
    assert matcher.skipped == 0 and matcher.expired == 0
    return sim, matcher


# ------------------------------------------------------------------ lockstep == offline
@pytest.mark.parametrize("partitions", [1, 3])
def test_late_cancels_live_equal_offline(partitions):
    sim, _ = _same_as_offline(BASE.with_(**LATE, **OPTIMISTIC), partitions=partitions)
    assert summarize(sim)["cancel_late_rate"] > 0  # the case is exercised: riders did give up on drivers


@needs_zones
@pytest.mark.parametrize("partitions", [1, 3])
def test_planned_repositioning_live_equals_offline(partitions):
    sim, matcher = _same_as_offline(BASE.with_(**PLANNED), partitions=partitions)
    assert matcher.moves_sent == sim.move_outcomes["started"] == len(sim.moves) > 0
    assert any(m["dispatched"] for m in sim.moves)  # some drivers were dispatched on the way


@needs_zones
@needs_model
def test_forecast_repositioning_live_equals_offline():
    sim, _ = _same_as_offline(BASE.with_(**FORECAST))
    assert sim.moves


@needs_zones
@needs_model
def test_drift_live_equals_offline():
    sim, matcher = _same_as_offline(BASE.with_(**DRIFT))
    assert sim.moves and matcher.moves_sent == 0  # drivers drift on their own: the matcher sends nothing


@needs_zones
def test_supply_response_live_equals_offline():
    sim, _ = _same_as_offline(BASE.with_(**SUPPLY))
    assert sim.logons > 0  # (flat synthetic demand keeps prices up, so nobody logs off again: see below)
    assert any(m["kind"] == "chase" for m in sim.moves)


@needs_zones
def test_a_driver_who_logs_off_is_offline_to_the_matcher_and_cannot_be_offered():
    bus = InMemoryBus()
    sim = LiveSimulation(BASE.with_(**SUPPLY), bus, LiveConfig(speed=0.0, tick_s=30.0, ping_s=0.0))
    matcher = Matcher(bus, travel=sim.belief)
    sim._broadcast("run_start", started_ms=sim.started_ms, config=run_config(sim.cfg.dispatch, sim.cfg.travel, 15.0))
    d = sim.drivers[0]
    sim._set_state(d, DriverState.OFFLINE)
    sim._publish_driver(d)
    matcher.step()
    assert matcher.drivers[d.id].state is DriverState.OFFLINE
    r = sim.riders[0]
    sim._on_request(r.spec.id)
    sim.apply_offer({"offer_id": "x", "batch_t": sim.now, "rider": r.spec.id, "driver": d.id, "eta_s": 60.0})
    assert sim.outcomes == {"rejected:driver_offline": 1}


@needs_zones
def test_everything_at_once_live_equals_offline():
    _same_as_offline(BASE.with_(**SUPPLY, **PLANNED, **LATE, **OPTIMISTIC), partitions=3)


@needs_zones
@pytest.mark.parametrize("seed", [0, 1])
def test_reordering_still_equals_offline(seed):
    # Offer answers can overtake the driver statuses they produced. The matcher then waits for those statuses
    # before planning, so it never plans with a driver it believes idle but who has just been matched.
    cfg = BASE.with_(**PLANNED, **LATE, **OPTIMISTIC)
    sim, _ = run_lockstep(cfg, bus=ShuffledBus(3, seed))
    np.testing.assert_equal(outcome(sim), outcome(simulate(cfg)))
    assert not any(k.startswith("rejected") for k in sim.move_outcomes)


# ------------------------------------------------------------------ restarts and stale moves
@needs_zones
def test_matcher_restart_rebuilds_repositioning_drivers():
    cfg = BASE.with_(**PLANNED)
    bus = InMemoryBus(3)
    sim = LiveSimulation(cfg, bus, LiveConfig(speed=0.0, tick_s=30.0, ping_s=0.0))
    box = {"matcher": Matcher(bus, travel=sim.belief), "ticks": 0, "checked": False}

    def settle():
        box["ticks"] += 1
        while box["matcher"].step() + sim.poll(0.0):
            pass
        if box["ticks"] >= 5 and not box["checked"] and any(
                d.state is DriverState.REPOSITIONING for d in sim.drivers):
            fresh = Matcher(bus, travel=sim.belief)  # the old one "crashed"; this one replays the topics
            fresh.step()
            assert not fresh.catching_up
            for d in sim.drivers:
                f = fresh.drivers[d.id]
                assert (f.state, f.free_at, f.has_next, f.state_since) == (d.state, d.free_at, d.has_next,
                                                                           d.state_since)
                assert f.move_zone == d.move_zone
                if d.state is DriverState.REPOSITIONING:  # the only state dispatch places along its leg
                    assert f.position_at(sim.now).tolist() == d.position_at(sim.now).tolist()
            assert fresh.estimator.recent.keys() == box["matcher"].estimator.recent.keys()
            box["matcher"], box["checked"] = fresh, True

    sim.lockstep = settle
    sim.run()
    assert box["checked"]
    assert sim.move_outcomes["started"] > 0


@needs_zones
def test_simulator_rejects_moves_for_busy_drivers_and_stale_moves():
    sim = LiveSimulation(BASE.with_(**PLANNED), InMemoryBus(), LiveConfig(speed=0.0, tick_s=30.0, ping_s=0.0))
    zone = next(iter(sim.repo_targets))
    busy, idle = sim.drivers[0], sim.drivers[1]
    busy.state = DriverState.EN_ROUTE
    sim.now = 100.0
    sim.apply_move({"move_id": "a", "plan_t": 100.0, "driver": busy.id, "zone": zone})
    sim.apply_move({"move_id": "b", "plan_t": 0.0, "driver": idle.id, "zone": zone})
    sim.apply_move({"move_id": "b", "plan_t": 0.0, "driver": idle.id, "zone": zone})  # redelivered: no-op
    assert sim.move_outcomes == {"rejected:driver_busy": 1, "rejected:expired": 1}
    assert idle.state is DriverState.IDLE


def test_repositioning_interval_must_be_a_multiple_of_the_batch_interval():
    with pytest.raises(ValueError, match="multiple"):
        LiveSimulation(BASE.with_(**{**PLANNED, "reposition.interval_s": 100.0}), InMemoryBus())


def test_matcher_waits_for_a_run_without_crashing():
    m = Matcher(InMemoryBus())  # empty topics: nothing has started yet (the service at startup)
    m.step()
    m.step()
    assert m.run is None and not m.catching_up
