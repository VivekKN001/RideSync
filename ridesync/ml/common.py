"""Shared data plumbing for the M6 models: the service area, month reads, the train/test split."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Sequence

MODELS = Path("data/models")
RAW = Path("data/raw")
LOOKUP_CSV = RAW / "taxi_zone_lookup.csv"
TRAIN_DAYS = 21  # March 1-21 train, 22-31 test


def service_zones(boroughs: Sequence[str] = ("Manhattan",), lookup: Path = LOOKUP_CSV) -> List[int]:
    """Taxi zone ids in the boroughs, minus the islands without car access (same area as the demand slices)."""
    from ..data.tlc import EXCLUDED_ZONES

    want = {b.lower() for b in boroughs}
    with open(lookup, newline="", encoding="utf-8") as f:
        ids = [int(r["LocationID"]) for r in csv.DictReader(f) if r["Borough"].lower() in want]
    return sorted(set(ids) - EXCLUDED_ZONES)


def month_start(month: str):
    import pandas as pd

    return pd.Timestamp(f"{month}-01")


def read_service_trips(month: str, columns: Sequence[str], zones: Sequence[int]):
    """Trips of the month inside the service area, filtered like ``ridesync.data.tlc.build_slice``:
    pickup and dropoff in the area, in different zones, not a shared ride. Filters are pushed down,
    so only matching rows of the requested columns are loaded."""
    import pyarrow.compute as pc
    import pyarrow.dataset as ds

    from ..data.tlc import trips_path

    area = list(map(int, zones))
    flt = (
        pc.field("PULocationID").isin(area) & pc.field("DOLocationID").isin(area)
        & (pc.field("PULocationID") != pc.field("DOLocationID"))
        & (pc.field("shared_request_flag") != "Y")
    )
    return ds.dataset(trips_path(month)).to_table(columns=list(columns), filter=flt).to_pandas()


def is_train_day(ts, month: str):
    """Boolean mask: the timestamp falls on one of the first TRAIN_DAYS days of the month."""
    return (ts - month_start(month)).dt.days < TRAIN_DAYS
