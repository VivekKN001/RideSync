"""NYC TLC high-volume for-hire (Uber/Lyft) trip data -> simulator demand slices.

TLC publishes trips at taxi-zone level, not coordinates, so each trip's pickup
and dropoff are sampled uniformly inside their zone polygons (seeded). OSRM
snaps them to the nearest road when routing.

Columns worth knowing:
- ``request_datetime``: when the rider requested; this drives the replay.
- ``on_scene_datetime``: driver arrival. Uber (HV0003) fills it for every trip,
  Lyft (HV0005) almost never, so ``observed_wait_s`` is NaN for most Lyft rows.
  It is the real-world wait benchmark for calibrating the simulator.
- ``trip_time``: seconds from pickup to dropoff. Used to calibrate OSRM times (and to train the M6 ETA model).

    python -m ridesync.data.tlc --date 2026-07-15 --start 17:00 --hours 3 --boroughs Manhattan --sample-frac 0.1
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Optional, Sequence

import numpy as np
import pandas as pd

from ..env import setting

RAW = Path("data/raw")
# Monthly trip files are ~0.5 GB each; RIDESYNC_TLC_DIR puts them on a bigger disk (default: data/raw). Like the
# other settings it comes from the environment or from .env, so a machine keeps its own path out of the code.
TLC_DIR = Path(setting("RIDESYNC_TLC_DIR") or RAW)
PROCESSED = Path("data/processed")
ZONES_ZIP = RAW / "taxi_zones.zip"
ZONES_LAYER = "taxi_zones/taxi_zones.shp"

# Liberty, Ellis and Governor's islands: in the Manhattan borough, but not reachable by car.
EXCLUDED_ZONES = frozenset({103, 104, 105})

TRIP_COLUMNS = [
    "hvfhs_license_num", "request_datetime", "on_scene_datetime", "pickup_datetime", "dropoff_datetime",
    "PULocationID", "DOLocationID", "trip_miles", "trip_time", "shared_request_flag",
]
OPERATORS = {"HV0002": "juno", "HV0003": "uber", "HV0004": "via", "HV0005": "lyft"}


def trips_path(month: str) -> Path:
    return TLC_DIR / f"fhvhv_tripdata_{month}.parquet"


def load_zones(zip_path: Path = ZONES_ZIP):
    """Taxi zones as a GeoDataFrame in WGS84 with columns LocationID, zone, borough, geometry."""
    import geopandas as gpd

    zones = gpd.read_file(f"zip://{zip_path}!{ZONES_LAYER}").to_crs(epsg=4326)
    return zones[["LocationID", "zone", "borough", "geometry"]]


def service_zone_ids(zones, boroughs: Iterable[str]) -> set:
    boroughs = {b.lower() for b in boroughs}
    ids = zones.loc[zones["borough"].str.lower().isin(boroughs), "LocationID"].astype(int)
    return set(ids) - EXCLUDED_ZONES


def read_window(path: Path, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Trips requested in [start, end), read with a pushed-down filter so the full month isn't loaded."""
    import pyarrow.compute as pc
    import pyarrow.dataset as ds

    flt = (pc.field("request_datetime") >= start) & (pc.field("request_datetime") < end)
    return ds.dataset(path).to_table(columns=TRIP_COLUMNS, filter=flt).to_pandas()


def sample_points_in_zones(zones, zone_ids: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """One uniform random (lat, lon) inside the polygon of each entry of ``zone_ids``."""
    import shapely

    out = np.full((len(zone_ids), 2), np.nan)
    geoms = zones.set_index("LocationID").geometry
    for zid in np.unique(zone_ids):
        idx = np.nonzero(zone_ids == zid)[0]
        poly = geoms.loc[int(zid)]
        minx, miny, maxx, maxy = poly.bounds
        got = []
        need = len(idx)
        while need > 0:
            k = max(need * 4, 64)
            xs, ys = rng.uniform(minx, maxx, k), rng.uniform(miny, maxy, k)
            inside = shapely.contains_xy(poly, xs, ys)
            pts = np.column_stack([ys[inside], xs[inside]])[:need]  # (lat, lon)
            got.append(pts)
            need -= len(pts)
        out[idx] = np.vstack(got)
    return out


def build_slice(
    trips: pd.DataFrame,
    zones,
    start: pd.Timestamp,
    boroughs: Sequence[str],
    sample_frac: float = 1.0,
    seed: int = 0,
) -> pd.DataFrame:
    """Filter to the service area, subsample, and attach sampled coordinates.

    Returns one row per request with ``request_s`` relative to ``start``, plus the observed
    wait and trip times as benchmarks.
    """
    rng = np.random.default_rng(seed)
    area = service_zone_ids(zones, boroughs)
    df = trips[
        (trips["shared_request_flag"] != "Y")
        & trips["PULocationID"].isin(area)
        & trips["DOLocationID"].isin(area)
        & (trips["PULocationID"] != trips["DOLocationID"])  # same-zone hops sample to near-zero trips
    ]
    if sample_frac < 1.0:
        df = df.sample(frac=sample_frac, random_state=seed)
    df = df.sort_values("request_datetime").reset_index(drop=True)

    pu = sample_points_in_zones(zones, df["PULocationID"].to_numpy(), rng)
    do = sample_points_in_zones(zones, df["DOLocationID"].to_numpy(), rng)
    return pd.DataFrame({
        "request_s": (df["request_datetime"] - start).dt.total_seconds(),
        "pu_zone": df["PULocationID"].astype(int),
        "do_zone": df["DOLocationID"].astype(int),
        "pu_lat": pu[:, 0], "pu_lon": pu[:, 1],
        "do_lat": do[:, 0], "do_lon": do[:, 1],
        "operator": df["hvfhs_license_num"].map(OPERATORS).fillna("other"),
        "observed_wait_s": (df["on_scene_datetime"] - df["request_datetime"]).dt.total_seconds(),
        "observed_trip_s": df["trip_time"].astype(float),
        "trip_miles": df["trip_miles"].astype(float),
    })


def slice_name(date: str, start: str, hours: float, boroughs: Sequence[str], sample_frac: float) -> str:
    b = "-".join(sorted(x.lower().replace(" ", "") for x in boroughs))
    return f"trips_{date}_{start.replace(':', '')}_{hours:g}h_{b}_f{sample_frac:g}.parquet"


def describe(sl: pd.DataFrame, hours: float, sample_frac: float) -> str:
    w = sl["observed_wait_s"].dropna()
    rate = len(sl) / hours
    lines = [
        f"requests: {len(sl)}  ({rate:.0f}/h in the slice, ~{rate / sample_frac:.0f}/h real)",
        f"operators: {sl['operator'].value_counts().to_dict()}",
        f"observed wait (Uber, request->on scene): n={len(w)} mean={w.mean():.0f}s "
        f"p50={w.median():.0f}s p90={w.quantile(0.9):.0f}s",
        f"observed trip: p50={sl['observed_trip_s'].median():.0f}s  "
        f"median speed={np.nanmedian(sl['trip_miles'] * 1609.34 / sl['observed_trip_s']) * 3.6:.1f} km/h",
    ]
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default="2026-07-15", help="the day to replay (its month's trip file must be downloaded)")
    ap.add_argument("--start", default="17:00")
    ap.add_argument("--hours", type=float, default=3.0)
    ap.add_argument("--boroughs", nargs="+", default=["Manhattan"])
    ap.add_argument("--sample-frac", type=float, default=0.1,
                    help="Manhattan peak is ~15k requests/h; subsample and scale the fleet to match")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    start = pd.Timestamp(f"{args.date} {args.start}")
    trips = read_window(trips_path(args.date[:7]), start, start + pd.Timedelta(hours=args.hours))
    sl = build_slice(trips, load_zones(), start, args.boroughs, args.sample_frac, args.seed)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    out = PROCESSED / slice_name(args.date, args.start, args.hours, args.boroughs, args.sample_frac)
    sl.to_parquet(out, index=False)
    print(f"wrote {out}")
    print(describe(sl, args.hours, args.sample_frac))


if __name__ == "__main__":
    main()
