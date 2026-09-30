"""Calibrate travel-time models against observed TLC trip times (pickup -> dropoff).

- straight: fit ``speed_mps`` (detour fixed) so the median predicted trip time matches the median observed.
- osrm:     fit ``time_multiplier`` = median(observed / OSRM duration) over a sample of trips.

Medians (not means) because the sampled in-zone coordinates add noise and a
few trips have extreme durations (waiting, detours).

    python -m ridesync.routing.calibrate --slice data/processed/<slice>.parquet [--osrm http://localhost:5000]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from ..env import CALIBRATION
from ..geo import haversine_pairs_m

OUT = Path(CALIBRATION)


def calibrate_straight(trips: pd.DataFrame, detour: float = 1.35) -> dict:
    d = haversine_pairs_m(trips[["pu_lat", "pu_lon"]].to_numpy(), trips[["do_lat", "do_lon"]].to_numpy())
    obs = trips["observed_trip_s"].to_numpy()
    ok = (obs > 60) & (d > 200)
    speed = float(np.median(d[ok] * detour / obs[ok]))
    return {"speed_mps": speed, "detour": detour, "n": int(ok.sum())}


def calibrate_osrm(trips: pd.DataFrame, osrm, n: int = 2000, seed: int = 0) -> dict:
    sample = trips[trips["observed_trip_s"] > 60].sample(n=min(n, len(trips)), random_state=seed)
    pu = sample[["pu_lat", "pu_lon"]].to_numpy()
    do = sample[["do_lat", "do_lon"]].to_numpy()
    raw = np.array([osrm.route(a, b).duration_s for a, b in zip(pu, do)]) / osrm.time_multiplier
    obs = sample["observed_trip_s"].to_numpy()
    ok = np.isfinite(raw) & (raw > 30)
    ratio = obs[ok] / raw[ok]
    return {
        "time_multiplier": float(np.median(ratio)),
        "ratio_p10": float(np.percentile(ratio, 10)),
        "ratio_p90": float(np.percentile(ratio, 90)),
        "n": int(ok.sum()),
        "fallbacks": osrm.fallbacks,
    }


def main(argv: Optional[Sequence[str]] = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slice", required=True)
    ap.add_argument("--osrm", help="OSRM base URL; omit to calibrate only the straight-line model")
    ap.add_argument("--n", type=int, default=2000)
    args = ap.parse_args(argv)

    trips = pd.read_parquet(args.slice)
    result = json.loads(OUT.read_text()) if OUT.exists() else {}
    result["slice"] = args.slice
    result["straight"] = calibrate_straight(trips)
    print("straight:", result["straight"])
    if args.osrm:
        from .osrm import OSRMModel

        result["osrm"] = calibrate_osrm(trips, OSRMModel(args.osrm), args.n)
        print("osrm:", result["osrm"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
