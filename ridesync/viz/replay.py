"""Build a self-contained replay page: two dispatch strategies on the same real demand, side by side.

    python -m ridesync.viz.replay                      # -> experiments/results/replay.html
    python -m ridesync.viz.replay --drivers 350 --seed 1

Both runs use the same riders, the same driver start positions and the same
accept/decline draws (common random numbers), so every difference on screen
comes from the dispatch policy. Driver movement is recorded through the
engine's ``_publish_driver`` hook, the same one the live simulator publishes
from. Travel uses the calibrated straight-line model, so vehicles move in
straight lines at the fitted Manhattan speed rather than along streets.

The map is drawn in "Manhattan grid north": rotated 29 degrees so the avenues
run up the page, the way NYC street maps are usually oriented.
"""
from __future__ import annotations

import argparse
import json
import math
import zipfile
from pathlib import Path
from typing import Dict, List

import numpy as np

from ..matching import CancelBelief, CostParams
from ..routing import travel_from_calibration
from ..sim import SimConfig, Simulation, summarize
from ..sim.engine import Driver, DriverState, RiderState

TEMPLATE = Path(__file__).with_name("replay_template.html")
DEFAULT_SLICE = "data/processed/trips_2024-03-13_1700_3h_manhattan_f0.1.parquet"
ZONES_ZIP = "data/raw/taxi_zones.zip"
GRID_DEG = 29.0                      # Manhattan's street grid is about 29 degrees east of true north
LAT0, LON0 = 40.7580, -73.9855       # Times Square: origin of the local metric frame
# The replay's arms don't reposition or cancel en route; if a config does, those show as free / quote cancels.
STATE_CODE = {DriverState.IDLE: 0, DriverState.EN_ROUTE: 1, DriverState.ON_TRIP: 2, DriverState.REPOSITIONING: 0}
REASON_CODE = {None: 0, "no_match": 1, "eta_quote": 2, "late_driver": 2}
SERIES_STEP_S = 30.0

ARMS = {
    "greedy": ("Immediate nearest driver", "Each request takes the closest free driver the moment it arrives.",
               {"dispatch.strategy": "fifo_greedy", "dispatch.interval_s": 0.0}),
    "optimal": ("Optimal batch every 30 s", "Collects requests for 30 s, then solves the whole batch at once "
                "and skips matches the rider would likely cancel.",
                {"dispatch.strategy": "lsa", "dispatch.interval_s": 30.0,
                 "dispatch.cost": CostParams(trip_value_s=900.0, cancel=CancelBelief())}),
}


def to_xy(lat, lon) -> np.ndarray:
    """(lat, lon) degrees -> metres in a local frame rotated to Manhattan grid north."""
    lat, lon = np.asarray(lat, float), np.asarray(lon, float)
    x = (lon - LON0) * 111_320.0 * math.cos(math.radians(LAT0))
    y = (lat - LAT0) * 110_574.0
    a = math.radians(GRID_DEG)
    return np.stack([x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)], axis=-1)


class RecordingSimulation(Simulation):
    """Offline simulation that keeps every driver leg: when it started, where it goes, in which state."""

    def __init__(self, cfg: SimConfig):
        super().__init__(cfg)
        self.legs: List[tuple] = []

    def _publish_driver(self, d: Driver) -> None:
        r = d.leg.route
        self.legs.append((d.id, self.now, STATE_CODE[d.state], *r.start, *r.end, d.leg.t0, d.leg.t1))

    def run(self):
        for d in self.drivers:
            self._publish_driver(d)
        return super().run()


LANDMARKS = [  # label, lat, lon
    ("Financial District", 40.7075, -74.0090),
    ("Midtown", 40.7549, -73.9840),
    ("Central Park", 40.7826, -73.9656),
    ("Harlem", 40.8116, -73.9465),
    ("Washington Heights", 40.8417, -73.9394),
]


def zones_xy(zip_path: str, tolerance_m: float = 25.0) -> List[dict]:
    import geopandas as gpd

    with zipfile.ZipFile(zip_path) as z:
        shp = next(n for n in z.namelist() if n.endswith(".shp"))
    gdf = gpd.read_file(f"zip://{zip_path}!{shp}")
    gdf = gdf[gdf["borough"] == "Manhattan"].to_crs(4326)
    out = []
    for geom, name in zip(gdf.geometry, gdf["zone"]):
        polys = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
        rings = []
        for p in polys:
            xy = to_xy(np.array(p.exterior.coords)[:, 1], np.array(p.exterior.coords)[:, 0])
            # Simplify in metres after projecting (keeps the file small; 25 m is invisible at this scale).
            from shapely.geometry import LineString

            simple = np.array(LineString(xy).simplify(tolerance_m).coords)
            if len(simple) >= 4:
                rings.append(np.round(simple).astype(int).ravel().tolist())
        if rings:
            out.append({"park": name == "Central Park", "rings": rings})
    return out


def _series(sim: RecordingSimulation, t_end: float) -> Dict[str, list]:
    ts = np.arange(0.0, t_end + SERIES_STEP_S, SERIES_STEP_S)
    legs = np.array(sim.legs)
    counts = np.zeros((3, len(ts)), dtype=int)
    for did in range(len(sim.drivers)):
        mine = legs[legs[:, 0] == did]
        idx = np.searchsorted(mine[:, 1], ts, side="right") - 1
        states = mine[np.clip(idx, 0, None), 2].astype(int)
        for s in range(3):
            counts[s] += states == s
    req = np.array([r.spec.request_t for r in sim.riders])
    matched = np.array([r.matched_t if r.matched_t is not None else np.inf for r in sim.riders])
    cancel = np.array([r.cancel_t if r.cancel_t is not None else np.inf for r in sim.riders])
    done = np.array([r.dropoff_t if r.dropoff_t is not None else np.inf for r in sim.riders])
    waiting = [int(((req <= t) & (matched > t) & (cancel > t)).sum()) for t in ts]
    return {
        "t": ts.tolist(), "waiting": waiting, "idle": counts[0].tolist(), "enroute": counts[1].tolist(),
        "ontrip": counts[2].tolist(),
        "completed": [int((done <= t).sum()) for t in ts], "cancelled": [int((cancel <= t).sum()) for t in ts],
    }


def _num(x, nd=1):
    return -1 if x is None else round(float(x), nd)


def export(cfg: SimConfig) -> dict:
    runs, sims = [], []
    for key, (label, desc, overrides) in ARMS.items():
        sim = RecordingSimulation(cfg.with_(**overrides))
        sim.run()
        sims.append(sim)
        m = summarize(sim)
        legs = sorted(sim.legs, key=lambda l: (l[0], l[1]))  # by driver, then time (stable)
        a = np.array(legs)
        p0, p1 = to_xy(a[:, 3], a[:, 4]), to_xy(a[:, 5], a[:, 6])
        offsets = np.searchsorted(a[:, 0], np.arange(len(sim.drivers) + 1)).tolist()
        runs.append({
            "key": key, "label": label, "desc": desc,
            "metrics": {k: m[k] for k in ("requests", "completed", "cancel_rate", "cancel_no_match_rate",
                                          "cancel_eta_rate", "wait_all_mean_s", "wait_mean_s", "pickup_mean_s",
                                          "completed_per_hour", "driver_idle_frac", "batch_riders_mean")},
            "riders": {
                "matched": [_num(r.matched_t) for r in sim.riders],
                "pickup": [_num(r.pickup_t) for r in sim.riders],
                "dropoff": [_num(r.dropoff_t) for r in sim.riders],
                "cancel": [_num(r.cancel_t) for r in sim.riders],
                "reason": [REASON_CODE[r.cancel_reason] for r in sim.riders],
            },
            "legs": {
                "offsets": offsets,
                "t0": np.round(a[:, 7], 1).tolist(), "t1": np.round(a[:, 8], 1).tolist(),
                "s": a[:, 2].astype(int).tolist(),
                "x0": np.round(p0[:, 0]).astype(int).tolist(), "y0": np.round(p0[:, 1]).astype(int).tolist(),
                "x1": np.round(p1[:, 0]).astype(int).tolist(), "y1": np.round(p1[:, 1]).astype(int).tolist(),
            },
        })
    t_end = max(s.now for s in sims)
    for run, sim in zip(runs, sims):
        run["series"] = _series(sim, t_end)

    riders = sims[0].riders
    o = to_xy([r.spec.origin[0] for r in riders], [r.spec.origin[1] for r in riders])
    return {
        "meta": {
            "date": "Wednesday 13 March 2024", "start_clock_s": 17 * 3600, "t_end": t_end,
            "window": [cfg.demand.warmup_s, cfg.demand.duration_s], "drivers": cfg.drivers.num_drivers,
            "seed": cfg.seed, "speed_kmh": round(cfg.travel.speed_mps * 3.6, 1), "detour": cfg.travel.detour,
            "grid_deg": GRID_DEG,
        },
        "zones": zones_xy(ZONES_ZIP),
        "landmarks": [{"label": n, "x": int(round(p[0])), "y": int(round(p[1]))}
                      for n, p in zip([l[0] for l in LANDMARKS],
                                      to_xy([l[1] for l in LANDMARKS], [l[2] for l in LANDMARKS]))],
        "riders": {
            "req": [round(r.spec.request_t, 1) for r in riders],
            "ox": np.round(o[:, 0]).astype(int).tolist(), "oy": np.round(o[:, 1]).astype(int).tolist(),
        },
        "runs": runs,
    }


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Build the side-by-side dispatch replay page")
    ap.add_argument("--slice", default=DEFAULT_SLICE)
    ap.add_argument("--drivers", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path, default=Path("experiments/results/replay.html"))
    args = ap.parse_args(argv)

    cfg = SimConfig(travel=travel_from_calibration("straight")).with_(**{
        "seed": args.seed, "demand.trips_path": args.slice, "demand.duration_s": 3 * 3600.0,
        "demand.warmup_s": 1800.0, "drivers.num_drivers": args.drivers, "dispatch.max_candidates": 20,
    })
    data = json.dumps(export(cfg), separators=(",", ":"))
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__REPLAY_DATA__*/null", data)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    print(f"wrote {args.out} ({len(html) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
