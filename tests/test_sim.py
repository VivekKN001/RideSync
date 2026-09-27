import math

import pytest

from ridesync.sim import SimConfig, simulate, summarize
from ridesync.sim.engine import RiderState

SMALL = SimConfig().with_(
    **{"demand.duration_s": 3600.0, "demand.warmup_s": 600.0, "demand.requests_per_hour": 600.0,
       "drivers.num_drivers": 120}
)


@pytest.mark.parametrize("strategy,interval", [("fifo_greedy", 0.0), ("global_greedy", 5.0), ("hungarian", 5.0)])
def test_every_rider_resolves(strategy, interval):
    sim = simulate(SMALL.with_(**{"dispatch.strategy": strategy, "dispatch.interval_s": interval}))
    assert all(r.state in (RiderState.DONE, RiderState.CANCELLED) for r in sim.riders)
    for r in sim.riders:
        if r.state is RiderState.DONE:
            assert r.spec.request_t <= r.matched_t <= r.pickup_t <= r.dropoff_t
    m = summarize(sim)
    assert m["completion_rate"] + m["cancel_rate"] == pytest.approx(1.0)
    fracs = m["driver_idle_frac"] + m["driver_enroute_frac"] + m["driver_ontrip_frac"]
    assert fracs == pytest.approx(1.0)


def test_deterministic():
    a = summarize(simulate(SMALL))
    b = summarize(simulate(SMALL))
    for k in a:
        if not k.startswith("solve_ms"):
            assert a[k] == b[k] or (math.isnan(a[k]) and math.isnan(b[k])), k


def test_same_seed_same_riders_across_strategies():
    a = simulate(SMALL.with_(**{"dispatch.strategy": "fifo_greedy"}))
    b = simulate(SMALL.with_(**{"dispatch.strategy": "hungarian"}))
    assert [r.spec.request_t for r in a.riders] == [r.spec.request_t for r in b.riders]


def test_hungarian_and_lsa_agree():
    a = summarize(simulate(SMALL.with_(**{"dispatch.strategy": "hungarian"})))
    b = summarize(simulate(SMALL.with_(**{"dispatch.strategy": "lsa"})))
    assert a["completed"] == b["completed"]
    assert a["wait_mean_s"] == pytest.approx(b["wait_mean_s"], rel=1e-6)
