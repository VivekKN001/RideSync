"""Riders who give up on a late driver, and (M7) idle drivers moving toward demand."""
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from ridesync.geo import StraightLineModel
from ridesync.reposition import Mover, drift_moves, plan_moves
from ridesync.sim import SimConfig, simulate, summarize
from ridesync.sim.config import RepositionConfig, TravelConfig
from ridesync.sim.engine import DriverState, RiderState, Simulation

SMALL = SimConfig().with_(**{
    "demand.duration_s": 3600.0, "demand.warmup_s": 600.0, "demand.requests_per_hour": 900.0,
    "drivers.num_drivers": 90, "dispatch.strategy": "lsa", "dispatch.interval_s": 10.0,
})
# The matcher believes drives take half as long as they do: every quote is optimistic.
OPTIMISTIC = SMALL.with_(belief=TravelConfig(speed_mps=SMALL.travel.speed_mps * 2.0))
LATE = {"riders.enroute_cancel": True}


def _outcomes(sim):
    return [(r.state, r.pickup_t, r.dropoff_t, r.cancel_reason) for r in sim.riders]


# ------------------------------------------------------------------ late drivers (step 1)
def test_enroute_cancel_is_a_no_op_when_nobody_is_ever_late():
    base = simulate(SMALL)
    patient = simulate(SMALL.with_(**LATE, **{"riders.lateness_tolerance_median_s": 1e9}))
    assert _outcomes(base) == _outcomes(patient)
    assert summarize(patient)["cancel_late_rate"] == 0.0


def test_riders_give_up_on_late_drivers():
    off, on = simulate(OPTIMISTIC), simulate(OPTIMISTIC.with_(**LATE))
    s_off, s_on = summarize(off), summarize(on)
    assert s_off["cancel_late_rate"] == 0.0 and s_on["cancel_late_rate"] > 0.01
    late = [r for r in on.riders if r.cancel_reason == "late_driver"]
    for r in late:
        assert r.state is RiderState.CANCELLED and r.pickup_t is None and r.matched_t is not None
        assert r.cancel_t > r.matched_t + r.quoted_eta_s  # only after the quote plus a tolerance
    assert all(r.state in (RiderState.DONE, RiderState.CANCELLED, RiderState.PRICED_OUT) for r in on.riders)
    assert all(d.state is DriverState.IDLE and d.rider_id is None and d.next_rider_id is None for d in on.drivers)


def test_driver_of_a_cancelled_rider_stops_on_the_way():
    class Recorder(Simulation):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.log = []

        def _publish_driver(self, d):
            self.log.append((self.now, d.id, d.state, d.pos.copy()))

    sim = Recorder(OPTIMISTIC.with_(**LATE)).run()
    checked = 0
    for r in (r for r in sim.riders if r.cancel_reason == "late_driver"):
        stops = [p for t, did, s, p in sim.log if did == r.driver_id and t == r.cancel_t and s is DriverState.IDLE]
        if not stops:
            continue  # the rider was queued behind the driver's trip, which simply goes on
        # Stopped short of the pickup: not teleported there, and not left at the end of its route.
        assert np.linalg.norm(stops[-1] - r.spec.origin) > 1e-6
        checked += 1
    assert checked > 0


def test_live_mode_refuses_enroute_cancel_and_repositioning():
    from ridesync.live.bus import InMemoryBus
    from ridesync.live.world import LiveSimulation

    with pytest.raises(ValueError, match="offline only"):
        LiveSimulation(SMALL.with_(**LATE), InMemoryBus())
    with pytest.raises(ValueError, match="offline only"):
        LiveSimulation(SMALL.with_(**{"reposition.policy": "planned"}), InMemoryBus())


# ------------------------------------------------------------------ repositioning policies (M7)
RC = RepositionConfig(policy="planned", min_idle_s=60.0, max_move_s=900.0, max_share=1.0)
A, B, C = 1, 2, 3
TARGETS = {A: np.array([40.75, -73.99]), B: np.array([40.76, -73.98]), C: np.array([40.85, -73.93])}
TRAVEL = StraightLineModel()  # 7 m/s x 1.35: A-B ~ 280 s, A-C ~ 2,000 s


def _movers(zone, n, idle_s=300.0, first_id=0):
    return [Mover(first_id + i, TARGETS[zone] + 1e-4 * i, zone, idle_s) for i in range(n)]


def test_plan_moves_fills_the_short_zone_from_the_surplus():
    # 6 free drivers, all in A; demand split evenly between A and B: 3 should go to B.
    moves = plan_moves(_movers(A, 6), {A: 6}, {A: 10.0, B: 10.0}, TARGETS, TRAVEL, RC, n_idle=6)
    assert len(moves) == 3 and all(z == B for _, z in moves)


def test_plan_moves_respects_budget_idle_time_and_distance():
    demand = {A: 10.0, B: 10.0}
    assert len(plan_moves(_movers(A, 6), {A: 6}, demand, TARGETS, TRAVEL, replace(RC, max_share=0.34), 6)) == 2
    assert plan_moves(_movers(A, 6, idle_s=30.0), {A: 6}, demand, TARGETS, TRAVEL, RC, 6) == []
    far = {A: 10.0, C: 10.0}  # C is ~33 min away: beyond the cap
    assert plan_moves(_movers(A, 6), {A: 6}, far, TARGETS, TRAVEL, RC, 6) == []


def test_plan_moves_does_nothing_when_supply_matches_demand():
    movers = _movers(A, 3) + _movers(B, 3, first_id=10)
    assert plan_moves(movers, {A: 3, B: 3}, {A: 5.0, B: 5.0}, TARGETS, TRAVEL, RC, 6) == []


def test_drift_goes_to_the_nearest_usually_busy_zone():
    rc = replace(RC, policy="drift", hot_quantile=0.5)
    usual = {A: 1.0, B: 50.0, C: 60.0}  # B and C are "usually busy"; B is the near one
    moves = drift_moves(_movers(A, 2), usual, TARGETS, TRAVEL, rc, n_idle=2)
    assert sorted(moves) == [(0, B), (1, B)]
    assert drift_moves(_movers(B, 2), usual, TARGETS, TRAVEL, rc, n_idle=2) == []  # already there


# ------------------------------------------------------------------ repositioning in the simulator (M7)
needs_zones = pytest.mark.skipif(
    not (Path("data/processed/taxi_zones.json").exists() and Path("data/models/zone_points.parquet").exists()),
    reason="needs data/processed/taxi_zones.json and data/models/zone_points.parquet")
PLANNED = SMALL.with_(**{"reposition.policy": "planned", "reposition.interval_s": 120.0,
                         "reposition.min_idle_s": 60.0, "drivers.num_drivers": 140})


@needs_zones
def test_repositioning_with_no_budget_changes_nothing():
    base = simulate(PLANNED.with_(**{"reposition.policy": "none"}))
    idle = simulate(PLANNED.with_(**{"reposition.max_share": 0.0}))
    assert _outcomes(base) == _outcomes(idle) and idle.moves == []


@needs_zones
def test_repositioning_moves_drivers_and_keeps_the_books():
    sim = simulate(PLANNED.with_(**{"demand.warmup_s": 0.0}))  # most moves rebalance the uniform start
    s = summarize(sim)
    assert len(sim.moves) > 0 and s["moves_per_driver_hour"] > 0 and s["reposition_km_per_hour"] > 0
    assert s["driver_reposition_frac"] > 0
    shares = s["driver_idle_frac"] + s["driver_enroute_frac"] + s["driver_ontrip_frac"] + s["driver_reposition_frac"]
    assert shares == pytest.approx(1.0)
    assert all(m["end_t"] is not None and m["end_t"] <= m["t0"] + m["planned_s"] + 1e-6 for m in sim.moves)
    assert all(d.state is DriverState.IDLE and d.move is None for d in sim.drivers)
    assert all(r.state in (RiderState.DONE, RiderState.CANCELLED) for r in sim.riders)


@needs_zones
def test_a_driver_dispatched_on_the_way_starts_from_where_it_is():
    class Recorder(Simulation):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.pickups = []

        def _start_pickup(self, d, r):
            self.pickups.append((self.now, d.id, d.leg.position(self.now).copy()))
            super()._start_pickup(d, r)

    sim = Recorder(PLANNED).run()
    cut = [m for m in sim.moves if m["dispatched"]]
    assert cut, "expected some moves to end in a dispatch"
    for m in cut:
        assert m["end_t"] < m["t0"] + m["planned_s"]
        (t, did, pos), = [p for p in sim.pickups if p[1] == m["driver"] and p[0] == m["end_t"]]
        assert np.allclose(pos, m["route"].position(m["end_t"] - m["t0"]))  # mid-route, not at its target
