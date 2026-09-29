"""Reduce each TLC month to the small tables the models train on (M8).

    python -m ridesync.data.monthly 2024-01:2026-07          # skips months already done

A raw month is ~0.5 GB and ~20 M trips; the models need far less of it. Per month, under
data/monthly/<YYYY-MM>/:

- ``counts.npy``: requests per service zone per 15 minutes, full scale (the demand model's data),
  shape (zones, days x 96), float32. Rows follow ``meta.json["zones"]``.
- ``eta.parquet``: up to ``per_day`` sampled trips per day with their live-traffic features, computed
  from every trip of the month (``TrafficFeed``), so a sample never loses the city-wide picture.
- ``fare.parquet``: up to ``fare_per_day`` sampled trips per day with fares and fees, including
  ``cbd_congestion_fee`` (NYC congestion pricing, from January 2025; NaN before).
- ``traffic.npz``: the month's ``TrafficFeed`` tables, for simulations that run inside the month.
- ``fees.json``: fee sums over every valid trip, so a multi-month mean is exact.
- ``meta.json``: written last; a month without it is redone.

Trips are filtered like the demand slices (``ridesync.ml.common.read_service_trips``). Each month is
read once, and only the columns needed, so a month takes about a minute and 1-2 GB of memory.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Optional, Sequence

import numpy as np

MONTHLY = Path("data/monthly")
VERSION = 1
BUCKET_S = 900
PER_DAY_BUCKETS = 96
FEES = ["tolls", "bcf", "sales_tax", "congestion_surcharge", "cbd_congestion_fee"]
TRAFFIC_COLS = ["city_mph_30", "city_trips_30", "pu_mph_60", "do_mph_60"]
COLUMNS = ["hvfhs_license_num", "request_datetime", "dropoff_datetime", "PULocationID", "DOLocationID",
           "trip_miles", "trip_time", "base_passenger_fare", *FEES]


def month_dir(month: str, root: Path = MONTHLY) -> Path:
    return root / month


def is_done(month: str, root: Path = MONTHLY) -> bool:
    meta = month_dir(month, root) / "meta.json"
    if not meta.exists():
        return False
    try:
        return json.loads(meta.read_text()).get("version") == VERSION
    except ValueError:
        return False


def read_month(path: Path, zones: Sequence[int], month: str):
    """The month's service-area trips (pandas), requested inside the month. Missing fee columns are NaN."""
    import pandas as pd
    import pyarrow.compute as pc
    import pyarrow.dataset as ds

    dset = ds.dataset(path)
    have = set(dset.schema.names)
    area = list(map(int, zones))
    start = pd.Timestamp(f"{month}-01")
    end = start + pd.offsets.MonthBegin(1)
    flt = (
        pc.field("PULocationID").isin(area) & pc.field("DOLocationID").isin(area)
        & (pc.field("PULocationID") != pc.field("DOLocationID"))
        & (pc.field("shared_request_flag") != "Y")
        & (pc.field("request_datetime") >= start) & (pc.field("request_datetime") < end)
    )
    df = dset.to_table(columns=[c for c in COLUMNS if c in have], filter=flt).to_pandas()
    for c in COLUMNS:
        if c not in df:
            df[c] = np.nan
    return df, start, end


def count_matrix(df, zones: Sequence[int], start, days: int) -> np.ndarray:
    row = {int(z): i for i, z in enumerate(zones)}
    b = ((df["request_datetime"] - start).dt.total_seconds().to_numpy() // BUCKET_S).astype(np.int64)
    z = df["PULocationID"].map(row).to_numpy()
    n = days * PER_DAY_BUCKETS
    flat = np.bincount(z.astype(np.int64) * n + b, minlength=len(zones) * n)
    return flat.reshape(len(zones), n).astype(np.float32)


def sample_per_day(df, per_day: int, seed: int):
    if per_day <= 0:
        return df.iloc[:0]
    shuffled = df.sample(frac=1.0, random_state=seed)
    return shuffled.groupby(shuffled["request_datetime"].dt.day).head(per_day).sort_values("request_datetime")


def reduce_month(month: str, per_day: int = 3000, fare_per_day: int = 2000, seed: int = 0,
                 root: Path = MONTHLY, raw_path: Optional[Path] = None, zones: Optional[Sequence[int]] = None) -> dict:
    """Write the month's tables (see the module docstring) and return its meta."""
    import pandas as pd

    from ..ml.common import service_zones
    from ..ml.eta import TrafficFeed
    from .tlc import trips_path

    zones = list(map(int, zones if zones is not None else service_zones()))
    path = Path(raw_path) if raw_path else trips_path(month)
    if not path.exists():
        raise FileNotFoundError(f"{path}: run `python -m ridesync.data.fetch --tlc {month}`")
    t0 = time.time()
    df, start, end = read_month(path, zones, month)
    days = (end - start).days
    out = month_dir(month, root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "meta.json").unlink(missing_ok=True)

    np.save(out / "counts.npy", count_matrix(df, zones, start, days))

    # ETA sample, with traffic features from every trip of the month.
    ok = (df["trip_time"] > 60) & (df["trip_time"] < 3 * 3600) & (df["trip_miles"] > 0.1)
    trips = df.loc[ok, ["request_datetime", "dropoff_datetime", "PULocationID", "DOLocationID", "trip_miles", "trip_time"]]
    feed = TrafficFeed.from_trips(trips, zones, start.to_pydatetime())
    np.savez_compressed(out / "traffic.npz", t0=np.array(start.isoformat()), city_mph=feed.city_mph,
                        city_n=feed.city_n, pu_mph=feed.pu_mph, do_mph=feed.do_mph)
    eta = sample_per_day(trips, per_day, seed).drop(columns=["dropoff_datetime"]).reset_index(drop=True)
    zi = {z: i for i, z in enumerate(zones)}
    tr = feed.lookup((eta["request_datetime"] - start).dt.total_seconds().to_numpy(),
                     eta["PULocationID"].map(zi).to_numpy(float), eta["DOLocationID"].map(zi).to_numpy(float))
    for k, c in enumerate(TRAFFIC_COLS):
        eta[c] = tr[:, k].astype(np.float32)
    eta.to_parquet(out / "eta.parquet", index=False)

    # Fares: a daily sample of valid trips, and exact fee sums over all of them.
    valid = (df["base_passenger_fare"] > 0) & (df["trip_miles"] > 0.1) & (df["trip_time"] > 60)
    fcols = ["hvfhs_license_num", "request_datetime", "PULocationID", "DOLocationID", "trip_miles", "trip_time",
             "base_passenger_fare", *FEES]
    sample_per_day(df.loc[valid, fcols], fare_per_day, seed + 1).reset_index(drop=True).to_parquet(out / "fare.parquet", index=False)
    v = df.loc[valid]
    fees = {"trips": int(len(v)), "fare_sum": float(v["base_passenger_fare"].sum()),
            **{f"{f}_sum": float(v[f].fillna(0.0).sum()) for f in FEES},
            f"{FEES[-1]}_charged": int((v[FEES[-1]].fillna(0.0) > 0).sum())}
    (out / "fees.json").write_text(json.dumps(fees, indent=1))

    meta = {"version": VERSION, "month": month, "start": start.isoformat(), "days": days, "zones": zones,
            "requests": int(len(df)), "eta_trips": int(len(eta)), "per_day": per_day, "fare_per_day": fare_per_day,
            "seed": seed, "source": str(path), "seconds": round(time.time() - t0, 1)}
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    del df, trips, v
    return meta


def main(argv: Optional[Sequence[str]] = None) -> None:
    from .fetch import expand_months

    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("months", nargs="+", metavar="YYYY-MM[:YYYY-MM]")
    ap.add_argument("--per-day", type=int, default=3000, help="ETA trips sampled per day")
    ap.add_argument("--fare-per-day", type=int, default=2000, help="fare trips sampled per day")
    ap.add_argument("--force", action="store_true", help="redo months that are already done")
    args = ap.parse_args(argv)
    done: List[str] = []
    for month in expand_months(args.months):
        if is_done(month) and not args.force:
            print(f"{month}: done already")
            continue
        m = reduce_month(month, args.per_day, args.fare_per_day)
        done.append(month)
        print(f"{month}: {m['requests']:,} requests, {m['eta_trips']:,} ETA trips, {m['seconds']:.0f}s", flush=True)
    print(f"reduced {len(done)} month(s)")


if __name__ == "__main__":
    main()
