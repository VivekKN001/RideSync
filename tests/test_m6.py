"""M6: demand forecast, surge pricing, ETA correction, and the simulator/live plumbing they need.

Model training on the real TLC month is not run here (``python -m ridesync.ml.train``); the model
code is tested on small synthetic data instead.
"""
import math
from collections import Counter
from dataclasses import replace
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from ridesync.data.slices import run_start_and_frac, slice_meta
from ridesync.geo import StraightLineModel
from ridesync.live.bus import InMemoryBus
from ridesync.live.lockstep import run_lockstep
from ridesync.live.schema import RIDER_EVENTS, DRIVER_EVENTS, ZONE_PRICES, decode
from ridesync.ml.demand import (
    PER_DAY, DemandForecaster, count_matrix, features, fit_and_evaluate, hist_mean, FEATURES,
)
from ridesync.ml.eta import CorrectedModel, NoisyModel, TrafficFeed, check_base
from ridesync.ml.fare import fares
from ridesync.pricing import DemandEstimator, conversion, multiplier, pressure, zone_prices
from ridesync.sim import SimConfig, simulate, summarize
from ridesync.sim.config import DemandConfig, FareConfig, PricingConfig, TravelConfig
from ridesync.sim.engine import RiderState
from ridesync.stream.features import run_reference
from ridesync.stream.zones import ZoneIndex

ZONES_JSON = Path("data/processed/taxi_zones.json")
needs_zones = pytest.mark.skipif(not ZONES_JSON.exists(), reason="run `python -m ridesync.stream.zones` first")

SMALL = SimConfig().with_(**{
    "demand.duration_s": 3600.0, "demand.warmup_s": 600.0, "demand.requests_per_hour": 900.0,
    "drivers.num_drivers": 90, "dispatch.strategy": "lsa", "dispatch.interval_s": 10.0,
})
SURGE = SMALL.with_(**{"pricing.enabled": True})


def _same(a: dict, b: dict) -> None:
    for k in a:
        if not k.startswith("solve_ms"):
            assert a[k] == b[k] or (math.isnan(a[k]) and math.isnan(b[k])), k


# ------------------------------------------------------------------ slices
def test_slice_meta_from_file_name():
    start, frac = slice_meta("data/processed/trips_2024-03-13_1700_3h_manhattan_f0.1.parquet")
    assert start == datetime(2024, 3, 13, 17, 0) and frac == 0.1
    assert slice_meta("elsewhere.parquet") is None
    d = DemandConfig(trips_path="x/trips_2024-03-13_1700_3h_manhattan_f0.1.parquet", start="2024-03-14 08:00")
    assert run_start_and_frac(d) == (datetime(2024, 3, 14, 8, 0), 0.1)
    assert run_start_and_frac(DemandConfig()) == (None, 1.0)


# ------------------------------------------------------------------ demand forecast
def test_count_matrix():
    C = count_matrix(np.array([0, 0, 1, 5, 2]), np.array([0, 0, 1, 1, -1]), n_zones=2, n_buckets=3)
    assert C.tolist() == [[2, 0, 0], [0, 1, 0]]  # bucket 5 is outside, zone -1 unknown


@pytest.mark.parametrize("k", [1, 2, 4])
def test_features_never_read_the_future(k):
    rng = np.random.default_rng(0)
    C = rng.poisson(5, size=(3, 20 * PER_DAY)).astype(float)
    for b in [PER_DAY * 8 + 3, PER_DAY * 15, PER_DAY * 19 + 95]:
        full = features(C, np.array([b]), k, origin_dow=4)
        blind = C.copy()
        blind[:, b - k + 1:] = np.nan  # everything after the last known bucket
        assert np.array_equal(full, features(blind, np.array([b]), k, origin_dow=4), equal_nan=True)
    X = features(C, np.array([PER_DAY * 8]), 1, origin_dow=4)
    assert X[1, FEATURES.index("lag1")] == C[1, PER_DAY * 8 - 1]
    assert X[1, FEATURES.index("lweek")] == C[1, PER_DAY]
    assert X[1, FEATURES.index("dow")] == (4 + 8) % 7


def test_hist_mean_is_same_weekday_and_time():
    C = np.zeros((1, 21 * PER_DAY))
    C[0, 5] = 3.0
    C[0, 7 * PER_DAY + 5] = 6.0
    target = np.array([14 * PER_DAY + 5])
    assert hist_mean(C, target, np.arange(14 * PER_DAY), 0)[0] == 4.5


def _synthetic_counts(days=28, zones=3, seed=0):
    rng = np.random.default_rng(seed)
    b = np.arange(days * PER_DAY)
    shape = 4 + 3 * np.sin(2 * np.pi * (b % PER_DAY) / PER_DAY)  # daily cycle
    scale = np.array([1.0, 2.0, 0.5])[:zones, None]
    return rng.poisson(shape[None, :] * scale).astype(float)


def test_forecaster_trains_evaluates_and_round_trips(tmp_path):
    pytest.importorskip("sklearn")
    C = _synthetic_counts()
    origin = datetime(2024, 3, 1)
    fc, rows = fit_and_evaluate(C, [10, 20, 30], origin, train_days=21, max_iter=30)
    by = {(r["horizon_min"], r["method"]): r["wape"] for r in rows}
    assert by[(15, "model (GBT, Poisson)")] < by[(15, "last value")]  # it learned the daily cycle
    path = tmp_path / "demand.joblib"
    fc.save(str(path))
    fc2 = DemandForecaster.load(str(path))
    now = datetime(2024, 3, 25, 17, 5)
    a = fc.expected(now, 900.0, {})
    assert a.shape == (3,) and (a >= 0).all()
    assert np.allclose(a, fc2.expected(now, 900.0, {}))
    # What the caller observed replaces history: tripling the recent buckets raises the forecast.
    b0 = int(fc.bucket_of(now))
    observed = {b: C[:, b] * 3 for b in range(b0 - 4, b0)}
    assert fc.expected(now, 900.0, observed).sum() > a.sum()
    with pytest.raises(ValueError):
        fc.expected(now, 1800.0, {})


# ------------------------------------------------------------------ pricing policy
def test_multiplier_steps_and_cap():
    cfg = PricingConfig(threshold=1.0, slope=0.5)
    assert multiplier(0.0, cfg) == 1.0 and multiplier(1.0, cfg) == 1.0
    assert multiplier(1.49, cfg) == 1.0 and multiplier(1.5, cfg) == 1.25
    assert multiplier(3.0, cfg) == 2.0 and multiplier(99.0, cfg) == cfg.cap
    ps = np.linspace(0, 10, 101)
    ms = [multiplier(p, cfg) for p in ps]
    assert all(a <= b for a, b in zip(ms, ms[1:]))
    assert pressure(3, 1, 0) == 4.0 and pressure(3, 1, 2) == 2.0


def test_pooled_pressure_uses_neighbours_supply():
    cfg = PricingConfig(threshold=1.0, slope=0.5)
    demand, waiting, supply = {1: 4.0, 2: 0.0}, {}, {1: 0.0, 2: 4.0}
    assert zone_prices([1, 2], demand, waiting, supply, cfg) == {1: cfg.cap, 2: 1.0}
    pooled = zone_prices([1, 2], demand, waiting, supply, cfg, {1: [1, 2], 2: [2, 1]})
    assert pooled == {1: 1.0, 2: 1.0}  # a free driver next door covers zone 1's riders


def test_zone_neighbours_by_centroid():
    sq = lambda lat, lon: [[[lat, lon], [lat + 0.001, lon], [lat + 0.001, lon + 0.001], [lat, lon + 0.001]]]
    zi = ZoneIndex([{"id": 1, "name": "a", "borough": "x", "polygons": sq(40.70, -74.0)},
                    {"id": 2, "name": "b", "borough": "x", "polygons": sq(40.71, -74.0)},   # ~1.1 km north
                    {"id": 3, "name": "c", "borough": "x", "polygons": sq(40.75, -74.0)}])  # ~5.6 km north
    nb = zi.neighbours(2000.0)
    assert sorted(nb[1]) == [1, 2] and sorted(nb[2]) == [1, 2] and nb[3] == [3]
    assert zi.neighbours(0.0)[1] == [1]


def test_conversion():
    assert conversion(1.0, 0.5) == 1.0
    assert conversion(2.0, 0.5) == pytest.approx(2 ** -0.5)
    assert conversion(2.0, 0.8) < conversion(1.5, 0.8) < 1.0


def test_reactive_estimate_is_a_sliding_window():
    est = DemandEstimator(PricingConfig(horizon_s=600.0), None, 1.0)
    est.add_open(7, 0.0)
    est.add_open(7, 100.0)
    assert est.estimate([7, 8], 600.0) == {7: 1.0, 8: 0.0}  # the open at 0 is exactly one horizon old
    est.add_open(7, 650.0)
    assert est.estimate([7], 700.0) == {7: 1.0}
    assert est.estimate([7], 1300.0) == {7: 0.0}


def test_forecast_estimate_needs_an_aligned_start():
    fc = DemandForecaster({}, [1], "2024-03-01T00:00:00", np.zeros((1, 10)))
    with pytest.raises(ValueError):
        DemandEstimator(PricingConfig(demand="forecast"), datetime(2024, 3, 1, 0, 7), 0.1, fc)
    with pytest.raises(RuntimeError):
        DemandEstimator(PricingConfig(demand="forecast"), datetime(2024, 3, 1), 0.1, None)


def test_fares_have_a_floor():
    cfg = FareConfig(base=2.0, per_mile=2.0, per_min=1.0, min_fare=10.0, road_factor=1.0)
    f = fares(cfg, np.array([100.0, 1609.344 * 5]), np.array([60.0, 1200.0]))
    assert f[0] == 10.0 and f[1] == pytest.approx(2 + 10 + 20)


# ------------------------------------------------------------------ surge in the simulator
@needs_zones
def test_surge_that_never_surges_changes_nothing():
    base = summarize(simulate(SMALL))
    flat = summarize(simulate(SMALL.with_(**{"pricing.enabled": True, "pricing.cap": 1.0})))
    _same(base, flat)


@needs_zones
def test_surge_prices_out_retries_and_resolves_everyone():
    sim = simulate(SURGE)
    states = Counter(r.state for r in sim.riders)
    assert set(states) <= {RiderState.DONE, RiderState.CANCELLED, RiderState.PRICED_OUT}
    assert states[RiderState.PRICED_OUT] > 0 and sim.price_log
    retried = [r for r in sim.riders if r.attempt == 1]
    assert retried and all(r.spec.request_t > r.open_t for r in retried)
    assert all(r.price >= 1.0 for r in sim.riders)
    for r in sim.riders:
        if r.state is RiderState.DONE:
            assert r.spec.request_t <= r.matched_t <= r.pickup_t <= r.dropoff_t
    m = summarize(sim)
    assert m["app_opens"] >= m["requests"]
    assert m["served_rate"] == pytest.approx(m["completed"] / m["app_opens"])
    assert m["mean_multiplier_paid"] > 1.0 and m["surge_revenue_per_hour"] > 0


@needs_zones
def test_surge_arms_face_the_same_riders():
    off, on = simulate(SMALL), simulate(SURGE)
    assert [r.open_t for r in off.riders] == [r.open_t for r in on.riders]
    no_retry = simulate(SURGE.with_(**{"pricing.retry": False}))
    assert all(r.attempt == 0 for r in no_retry.riders)


@needs_zones
def test_surge_lockstep_equals_offline_and_publishes_quotes_and_prices():
    offline = simulate(SURGE)
    live, _ = run_lockstep(SURGE)
    _same(summarize(offline), summarize(live))
    msgs = [decode(p) for topic, _, _, _, _, p in live.bus.log]
    quotes = [m for m in msgs if m["type"] == "quoted"]
    assert len([q for q in quotes if q["attempt"] == 0]) == len(live.riders)
    assert sum(not q["accepted"] for q in quotes) > 0
    prices = [m for m in msgs if m["type"] == "prices"]
    assert len(prices) == len(live.price_log) and all("ts" in p for p in prices)


@needs_zones
def test_stream_features_count_app_opens_and_declines():
    from ridesync.stream.zones import ZoneIndex

    live, _ = run_lockstep(SURGE)
    msgs = [decode(p) for topic, _, _, _, _, p in live.bus.log if topic in (RIDER_EVENTS, DRIVER_EVENTS)]
    rows, late, _ = run_reference(msgs, ZoneIndex.load(str(ZONES_JSON)))
    assert late == []
    quotes = [m for m in msgs if m["type"] == "quoted"]
    assert sum(r["quotes"] for r in rows) == sum(q["attempt"] == 0 for q in quotes) == len(live.riders)
    assert sum(r["declines"] for r in rows) == sum(not q["accepted"] for q in quotes)
    requested = sum(r.state is not RiderState.PRICED_OUT for r in live.riders)
    assert sum(r["requests"] for r in rows) == requested


@needs_zones
def test_pricing_service_prices_a_busy_zone():
    from ridesync.live.pricing import PricingService
    from ridesync.live.world import LiveConfig, LiveSimulation

    bus = InMemoryBus(1)
    svc = PricingService(bus)
    # A run that asks for service pricing: its run_start tells the service the config.
    sim = LiveSimulation(SURGE.with_(**{"demand.duration_s": 60.0}), bus, LiveConfig(speed=0.0, ping_s=0.0,
                                                                                       price_source="service"))
    sim.run()
    svc.step()
    assert svc.run == sim.run_id
    prod = bus.producer()
    row = {"v": 1, "type": "zone_minute", "run": sim.run_id, "zone": 161, "idle_end": 0, "requests": 5, "matches": 0,
           "cancels_no_match": 0, "cancels_eta": 0, "quotes": 12, "declines": 0, "late": 0}
    for minute in range(6):
        prod.produce("zone-features", "k", {**row, "minute": minute, "t": minute * 60.0, "ts": 1000 * minute})
    svc.step()
    out = [decode(p) for topic, _, _, _, _, p in bus.log if topic == ZONE_PRICES]
    assert len(out) == 1 and out[0]["t"] == 300.0 and out[0]["source"] == "service:reactive"
    assert out[0]["prices"]["161"] == PricingConfig().cap  # 72 opens + 30 waiting, no free drivers


# ------------------------------------------------------------------ ETA correction
class _Const:
    def __init__(self, v):
        self.v = v

    def predict(self, X):
        return np.full(len(X), self.v)


class _NoZones:
    def zone_of(self, lat, lon):
        return 0


def test_eta_range_brackets_the_point_eta():
    base = StraightLineModel()
    a, b = np.array([[40.75, -73.99]]), np.array([[40.76, -73.98], [40.70, -74.00]])
    bundle = {"model": _Const(0.0), "zones": [1],
              "interval_models": {0.1: _Const(math.log(0.8)), 0.9: _Const(math.log(1.3))}}
    m = CorrectedModel(base, bundle, _NoZones(), None)
    lo, hi = m.eta_range(a, b)
    assert np.allclose(lo, 0.8 * base.matrix(a, b)) and np.allclose(hi, 1.3 * base.matrix(a, b))
    assert np.all(lo <= m.matrix(a, b)) and np.all(m.matrix(a, b) <= hi)
    with pytest.raises(ValueError, match="no range models"):
        CorrectedModel(base, {"model": _Const(0.0), "zones": [1]}, _NoZones(), None).eta_range(a, b)


def test_corrected_model_scales_matrix_and_route():
    base = StraightLineModel()
    a, b = np.array([[40.75, -73.99]]), np.array([[40.76, -73.98], [40.70, -74.00]])
    same = CorrectedModel(base, {"model": _Const(0.0), "zones": [1]}, _NoZones(), datetime(2024, 3, 13, 17))
    assert np.allclose(same.matrix(a, b), base.matrix(a, b))
    slow = CorrectedModel(base, {"model": _Const(math.log(1.5)), "zones": [1]}, _NoZones(), None)
    assert np.allclose(slow.matrix(a, b), 1.5 * base.matrix(a, b))
    r = slow.route(a[0], b[0])
    assert r.duration_s == pytest.approx(1.5 * base.route(a[0], b[0]).duration_s)
    assert r.cum_s[-1] == pytest.approx(r.duration_s)
    wild = CorrectedModel(base, {"model": _Const(5.0), "zones": [1]}, _NoZones(), None)
    assert np.allclose(wild.matrix(a, b), 4.0 * base.matrix(a, b))  # clipped
    inf = np.array([[np.inf]])
    assert np.isinf(slow.factor(inf, a, b[:1]) * inf).all()


def test_noise_depends_on_the_drive_not_the_call_order():
    base = StraightLineModel()
    p, q, s = np.array([40.75, -73.99]), np.array([40.76, -73.98]), np.array([40.72, -74.0])
    n1, n2 = NoisyModel(base, 0.3, seed=1), NoisyModel(base, 0.3, seed=1)
    first = n1.route(p, q).duration_s
    n2.route(p, s)
    assert n2.route(p, q).duration_s == first != base.route(p, q).duration_s
    assert NoisyModel(base, 0.3, seed=2).route(p, q).duration_s != first
    assert np.array_equal(n1.matrix(p[None], q[None]), base.matrix(p[None], q[None]))


def test_traffic_feed_sees_only_finished_trips():
    import pandas as pd

    t0 = datetime(2024, 3, 1)
    # Zone 1 -> 2: ten trips finish in the first 5 minutes at 12 mph, ten in the next 5 at 6 mph.
    rows = [(t0 + pd.Timedelta(seconds=60 + i), 1, 2, 1.0, 300.0) for i in range(10)] +            [(t0 + pd.Timedelta(seconds=360 + i), 1, 2, 1.0, 600.0) for i in range(10)]
    df = pd.DataFrame(rows, columns=["dropoff_datetime", "PULocationID", "DOLocationID", "trip_miles", "trip_time"])
    f = TrafficFeed.from_trips(df, [1, 2], t0)
    out = f.lookup(np.array([100.0, 400.0, 700.0, -5.0]), np.array([0.0, 0, 0, 0]), np.array([1.0, 1, np.nan, 1]))
    assert np.isnan(out[0, 0]) and out[0, 1] == 0          # nothing has finished yet
    assert out[1].tolist() == [12.0, 10.0, 12.0, 12.0]      # only the first bucket, not the one in progress
    assert out[2, 0] == 8.0 and out[2, 1] == 20 and np.isnan(out[2, 3])  # 20 mi / 2.5 h; unknown dropoff zone
    assert np.isnan(out[3]).all()                           # before the table
    assert TrafficFeed.from_dict(f.to_dict()).lookup(np.array([400.0]), np.array([0.0]), np.array([1.0]))[0, 0] == 12.0


def test_eta_bundle_must_match_its_base():
    t = TravelConfig(model="straight", speed_mps=3.75, detour=1.35)
    bundle = {"base": {"model": "straight", "speed_mps": 3.75, "detour": 1.35, "time_multiplier": 1.0}}
    check_base(bundle, t)
    with pytest.raises(ValueError):
        check_base(bundle, replace(t, speed_mps=7.0))
    with pytest.raises(ValueError):
        check_base(bundle, TravelConfig(model="osrm", time_multiplier=2.09))


def test_belief_equal_to_world_changes_nothing_and_a_wrong_belief_misquotes():
    base = summarize(simulate(SMALL))
    _same(base, summarize(simulate(SMALL.with_(belief=SMALL.travel))))
    assert base["eta_abs_error_mean_s"] < 1e-6
    fast = summarize(simulate(SMALL.with_(belief=replace(SMALL.travel, speed_mps=SMALL.travel.speed_mps * 1.5))))
    assert fast["eta_error_mean_s"] > 30.0  # the matcher thinks drives are shorter than they are


def test_world_noise_makes_quotes_inexact_but_unbiased_in_the_median():
    sim = simulate(SMALL.with_(**{"travel.noise_sigma": 0.3}))
    err = [(r.pickup_t - r.matched_t) - r.quoted_eta_s for r in sim.riders if r.state is RiderState.DONE]
    assert np.mean(np.abs(err)) > 10.0 and abs(np.median(err)) < 30.0
