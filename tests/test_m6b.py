"""M6b: drivers who respond to surge prices. Off by default and then invisible; when on, drivers are
conserved, offline drivers never get riders, and chasing stays within its limits."""
from pathlib import Path

import pytest

from ridesync.dispatch import DriverState
from ridesync.sim import SimConfig, simulate, summarize
from ridesync.sim.config import SupplyConfig

ZONES = "data/processed/taxi_zones.json"
POINTS = "data/models/zone_points.parquet"
pytestmark = pytest.mark.skipif(not (Path(ZONES).exists() and Path(POINTS).exists()),
                                reason="needs the taxi zones and zone points (python -m ridesync.stream.zones, ml.train)")

# The synthetic city sits on midtown Manhattan, inside the taxi zones. Few drivers, so prices surge.
BASE = SimConfig().with_(**{
    "demand.duration_s": 5400.0, "demand.warmup_s": 900.0, "demand.requests_per_hour": 1500.0,
    "drivers.num_drivers": 120, "dispatch.strategy": "lsa", "dispatch.interval_s": 30.0, "pricing.enabled": True,
})
BOTH = {"supply.reserve_share": 0.3, "supply.log_on_elasticity": 1.5, "supply.chase_strength": 1.0,
        "supply.log_on_delay_s": 120.0, "supply.log_off_idle_s": 600.0}


def test_off_by_default_and_then_invisible():
    ref = summarize(simulate(BASE))
    # A reserve that can never log on, and zero chasing, is the same as no supply response at all.
    same = summarize(simulate(BASE.with_(**{"supply.reserve_share": 0.3, "supply.log_on_elasticity": 0.0})))
    outcome = lambda m: {k: (None if v != v else v) for k, v in m.items() if not k.startswith("solve_ms")}  # noqa: E731
    assert outcome(same) == outcome(ref)  # everything but wall-clock solve times, NaN == NaN
    assert not SupplyConfig().enabled
    assert ref["drivers_online_mean"] == pytest.approx(120)
    assert ref["reserve_logons"] == 0 and ref["chase_moves_per_hour"] == 0


def test_needs_surge_pricing():
    with pytest.raises(ValueError, match="pricing.enabled"):
        simulate(BASE.with_(**{"pricing.enabled": False}, **BOTH))


def test_drivers_are_conserved_and_offline_drivers_never_work():
    sim = simulate(BASE.with_(**BOTH))
    m = summarize(sim)
    reserve = sim.drivers[sim.n_fleet:]
    assert len(reserve) == 36 and sim.logons > 0
    online_at_end = sum(d.state is not DriverState.OFFLINE for d in reserve)
    assert sim.logons - sim.logoffs == online_at_end
    assert all(d.state is not DriverState.OFFLINE for d in sim.drivers[:sim.n_fleet])  # the fleet never logs off
    assert all(d.rider_id is None and d.next_rider_id is None for d in sim.drivers if d.state is DriverState.OFFLINE)
    # Every driver's time adds up to the window, online or not.
    lo, hi = sim.window
    for d in sim.drivers:
        assert sum(d.time_in.values()) == pytest.approx(hi - lo)
    # A reserve driver who never logged on never carried anyone.
    carried = {r.driver_id for r in sim.riders if r.pickup_t is not None}
    never_on = [d for d in reserve if d.time_in[DriverState.OFFLINE] == pytest.approx(hi - lo)]
    assert never_on and not carried & {d.id for d in never_on}
    assert 120 < m["drivers_online_mean"] < 156


def test_chasing_moves_are_bounded():
    sim = simulate(BASE.with_(**BOTH))
    chases = [mv for mv in sim.moves if mv["kind"] == "chase"]
    assert chases
    assert all(mv["planned_s"] <= BASE.supply.chase_max_s + 1e-6 for mv in chases)  # belief == world here
    assert all(mv["kind"] in ("chase", "plan") for mv in sim.moves)


def test_response_brings_drivers_and_lowers_prices():
    fixed, resp = summarize(simulate(BASE)), summarize(simulate(BASE.with_(**BOTH)))
    assert resp["drivers_online_mean"] > fixed["drivers_online_mean"]
    assert resp["mean_multiplier_paid"] < fixed["mean_multiplier_paid"]
    assert resp["completed"] > fixed["completed"]
