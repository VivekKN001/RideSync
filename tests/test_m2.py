import re
from urllib.parse import unquote

import numpy as np
import pandas as pd
import pytest

from ridesync.dispatch import eta_matrix
from ridesync.geo import Route, StraightLineModel, haversine_m
from ridesync.routing.osrm import OSRMModel
from ridesync.sim import SimConfig, simulate, summarize
from ridesync.sim.engine import RiderState, Simulation

UNROUTABLE_LAT = 40.9  # the fake server can't route to or from points at this latitude


class FakeResponse:
    status_code = 200

    def __init__(self, body):
        self.body = body

    def json(self):
        return self.body


class FakeOSRM:
    """Enough of the OSRM HTTP API for the client: straight-line times at 5 m/s."""

    def __init__(self):
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params))
        service = re.search(r"/(table|route)/v1/", url).group(1)
        coords = unquote(url.rsplit("/", 1)[1]).split(";")
        pts = np.array([[float(c.split(",")[1]), float(c.split(",")[0])] for c in coords])  # lat, lon
        bad = np.isclose(pts[:, 0], UNROUTABLE_LAT)
        if service == "table":
            src = [int(i) for i in params["sources"].split(";")]
            dst = [int(i) for i in params["destinations"].split(";")]
            t = haversine_m(pts[src], pts[dst]) / 5.0
            rows = [[None if bad[s] or bad[d] else float(t[i, j]) for j, d in enumerate(dst)] for i, s in enumerate(src)]
            return FakeResponse({"code": "Ok", "durations": rows})
        if bad.any():
            return FakeResponse({"code": "NoRoute", "message": "no route"})
        a, b = pts
        mid = (a + b) / 2 + np.array([0.001, 0.0])  # a dog-leg so the path has 3 vertices
        path = np.vstack([a, mid, b])
        seg = haversine_m(path[:-1], path[1:]).diagonal() / 5.0
        return FakeResponse({
            "code": "Ok",
            "routes": [{
                "duration": float(seg.sum()),
                "geometry": {"coordinates": [[lon, lat] for lat, lon in path]},
                "legs": [{"annotation": {"duration": seg.tolist()}}],
            }],
        })


def pts(n, seed=0):
    rng = np.random.default_rng(seed)
    return np.column_stack([40.75 + rng.uniform(-0.03, 0.03, n), -73.98 + rng.uniform(-0.02, 0.02, n)])


def test_osrm_table_chunks_and_scales():
    fake = FakeOSRM()
    m = OSRMModel(time_multiplier=2.0, max_table=7, session=fake)
    o, d = pts(17, 1), pts(12, 2)
    got = m.matrix(o, d)
    assert got.shape == (17, 12)
    assert np.allclose(got, haversine_m(o, d) / 5.0 * 2.0, atol=0.1)  # URL coords are rounded to 1e-6 deg
    assert len(fake.calls) == 3 * 2  # ceil(17/7) x ceil(12/7)


def test_osrm_table_unroutable_is_inf():
    m = OSRMModel(session=FakeOSRM())
    o = pts(3)
    o[1, 0] = UNROUTABLE_LAT
    got = m.matrix(o, pts(4, 5))
    assert np.all(np.isinf(got[1])) and np.all(np.isfinite(got[[0, 2]]))


def test_osrm_route_geometry_timing_and_cache():
    fake = FakeOSRM()
    m = OSRMModel(time_multiplier=1.5, session=fake)
    a, b = pts(2, 3)
    r = m.route(a, b)
    assert len(r.path) == 3
    assert r.cum_s[0] == 0 and r.cum_s[-1] == pytest.approx(r.duration_s)
    assert np.all(np.diff(r.cum_s) >= 0)
    assert np.allclose(r.position(0), a) and np.allclose(r.position(r.duration_s), b)
    assert m.route(a, b) is r and len(fake.calls) == 1


def test_osrm_no_route_falls_back():
    m = OSRMModel(session=FakeOSRM(), fallback_speed_mps=4.0)
    a, b = pts(2)
    b[0] = UNROUTABLE_LAT
    r = m.route(a, b)
    assert m.fallbacks == 1
    assert r.duration_s == pytest.approx(haversine_m(a, b)[0, 0] / 4.0)


def test_route_position_interpolates_by_time():
    path = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]])
    r = Route(30.0, path, np.array([0.0, 10.0, 30.0]))
    assert np.allclose(r.position(5), [0.5, 0.0])
    assert np.allclose(r.position(20), [1.0, 0.5])
    assert np.allclose(r.position(99), [1.0, 1.0])
    assert np.allclose(Route.stationary(np.array([3.0, 4.0])).position(10), [3.0, 4.0])


def test_simulation_runs_on_osrm_client():
    cfg = SimConfig().with_(**{"demand.duration_s": 1200.0, "demand.warmup_s": 0.0,
                               "demand.requests_per_hour": 300.0, "drivers.num_drivers": 40,
                               "dispatch.max_candidates": 10})
    sim = Simulation(cfg, travel=OSRMModel(session=FakeOSRM())).run()
    assert all(r.state in (RiderState.DONE, RiderState.CANCELLED) for r in sim.riders)
    assert summarize(sim)["completed"] > 0


class FlakyOSRM(FakeOSRM):
    """Drops the connection a few times, like a server closing a reused keep-alive connection."""

    def __init__(self, failures):
        super().__init__()
        self.failures = failures

    def get(self, url, params=None, timeout=None):
        import requests

        if self.failures:
            self.failures -= 1
            raise requests.ConnectionError("Remote end closed connection without response")
        return super().get(url, params=params, timeout=timeout)


def test_osrm_retries_dropped_connections():
    import requests

    m = OSRMModel(session=FlakyOSRM(failures=2))
    assert np.isfinite(m.matrix(pts(2, 1), pts(3, 2))).all()
    assert m.retries == 2
    with pytest.raises(requests.ConnectionError):
        OSRMModel(session=FlakyOSRM(failures=10), max_retries=3).matrix(pts(2, 1), pts(3, 2))


def test_pruning_keeps_nearest_and_matches_full_when_k_large():
    base = SimConfig().with_(**{"demand.duration_s": 1800.0, "demand.warmup_s": 300.0,
                                "demand.requests_per_hour": 600.0, "drivers.num_drivers": 100})
    full = summarize(simulate(base))
    wide = summarize(simulate(base.with_(**{"dispatch.max_candidates": 100})))
    assert full["completed"] == wide["completed"] and full["wait_mean_s"] == wide["wait_mean_s"]

    positions, origins = pts(10, 7), pts(4, 8)
    eta = eta_matrix(StraightLineModel(), positions, origins, np.zeros(10), max_candidates=3)
    assert np.all(np.isfinite(eta).sum(axis=1) == 3)
    exact = StraightLineModel().matrix(positions, origins).T
    assert np.allclose(eta.min(axis=1), exact.min(axis=1))


# ------------------------------------------------------------------ TLC slice
@pytest.fixture
def zones():
    gpd = pytest.importorskip("geopandas")
    from shapely.geometry import box

    return gpd.GeoDataFrame({
        "LocationID": [1, 2, 3, 103],
        "zone": ["a", "b", "c", "island"],
        "borough": ["Manhattan", "Manhattan", "Queens", "Manhattan"],
        "geometry": [box(-74.00, 40.70, -73.99, 40.71), box(-73.99, 40.71, -73.98, 40.72),
                     box(-73.90, 40.70, -73.89, 40.71), box(-74.02, 40.69, -74.01, 40.70)],
    }, crs="EPSG:4326")


def fake_trips():
    t0 = pd.Timestamp("2024-03-13 17:00")
    rows = [
        # op, request, on_scene offset, PU, DO, shared
        ("HV0003", 10, 120, 1, 2, "N"),
        ("HV0005", 20, None, 2, 1, "N"),
        ("HV0003", 30, 90, 1, 3, "N"),    # leaves the service area
        ("HV0003", 40, 60, 1, 1, "N"),    # same zone
        ("HV0003", 50, 60, 1, 2, "Y"),    # shared
        ("HV0003", 60, 60, 103, 1, "N"),  # excluded island
        ("HV0003", 5, 200, 2, 1, "N"),
    ]
    return pd.DataFrame({
        "hvfhs_license_num": [r[0] for r in rows],
        "request_datetime": [t0 + pd.Timedelta(seconds=r[1]) for r in rows],
        "on_scene_datetime": [t0 + pd.Timedelta(seconds=r[1] + r[2]) if r[2] else pd.NaT for r in rows],
        "pickup_datetime": [t0 + pd.Timedelta(seconds=r[1] + 300) for r in rows],
        "dropoff_datetime": [t0 + pd.Timedelta(seconds=r[1] + 900) for r in rows],
        "PULocationID": [r[3] for r in rows],
        "DOLocationID": [r[4] for r in rows],
        "trip_miles": 1.5,
        "trip_time": 600,
        "shared_request_flag": [r[5] for r in rows],
    }), t0


def test_build_slice_filters_and_samples_inside_zones(zones):
    import shapely

    from ridesync.data.tlc import build_slice

    trips, t0 = fake_trips()
    sl = build_slice(trips, zones, t0, ["Manhattan"], seed=1)
    assert list(sl["request_s"]) == [5.0, 10.0, 20.0]
    assert list(sl["operator"]) == ["uber", "uber", "lyft"]
    assert sl["observed_wait_s"].iloc[0] == 200 and np.isnan(sl["observed_wait_s"].iloc[2])
    geoms = zones.set_index("LocationID").geometry
    for _, r in sl.iterrows():
        assert shapely.contains_xy(geoms[r["pu_zone"]], r["pu_lon"], r["pu_lat"])
        assert shapely.contains_xy(geoms[r["do_zone"]], r["do_lon"], r["do_lat"])


def test_replay_demand_drives_simulation(zones, tmp_path):
    from ridesync.data.tlc import build_slice

    trips, t0 = fake_trips()
    path = tmp_path / "slice.parquet"
    build_slice(trips, zones, t0, ["Manhattan"], seed=1).to_parquet(path)
    cfg = SimConfig().with_(**{"demand.trips_path": str(path), "demand.duration_s": 3600.0,
                               "demand.warmup_s": 0.0, "drivers.num_drivers": 5})
    sim = simulate(cfg)
    assert [r.spec.request_t for r in sim.riders] == [5.0, 10.0, 20.0]
    assert all(r.state in (RiderState.DONE, RiderState.CANCELLED) for r in sim.riders)
    again = simulate(cfg)
    assert [r.state for r in again.riders] == [r.state for r in sim.riders]


class GarbledOSRM(FakeOSRM):
    """Answers with an empty body or a 502 a few times, as Docker's port proxy does under heavy load."""

    def __init__(self, failures):
        super().__init__()
        self.failures = failures

    def get(self, url, params=None, timeout=None):
        import requests

        if self.failures:
            self.failures -= 1
            bad = requests.Response()
            bad.status_code = 200 if self.failures % 2 else 502
            bad._content = b""
            return bad
        return super().get(url, params=params, timeout=timeout)


def test_osrm_retries_empty_and_bad_gateway_replies():
    m = OSRMModel(session=GarbledOSRM(failures=2))
    assert np.isfinite(m.matrix(pts(2, 1), pts(3, 2))).all()
    assert m.retries == 2
    with pytest.raises(ValueError):
        OSRMModel(session=GarbledOSRM(failures=9), max_retries=3).matrix(pts(2, 1), pts(3, 2))
