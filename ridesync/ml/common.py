"""Shared data plumbing for the models: the service area, periods, the reduced monthly tables.

Since M8 the models train on ``data/monthly`` (``ridesync.data.monthly``), over periods given as
``YYYY-MM[-DD]:YYYY-MM[-DD]`` (both ends included). The defaults train on 2025-01..2026-06 and test on
2026-07; the M6 setup is ``--train 2024-03-01:2024-03-21 --test 2024-03-22:2024-03-31``.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

from ..env import MODELS_DIR

MODELS = Path(MODELS_DIR)
RAW = Path("data/raw")
MONTHLY = Path("data/monthly")
LOOKUP_CSV = RAW / "taxi_zone_lookup.csv"
TRAIN_DAYS = 21  # the M6 split: March 1-21 train, 22-31 test
DEFAULT_TRAIN = "2025-01:2026-06"
DEFAULT_TEST = "2026-07"


@dataclass(frozen=True)
class Period:
    """Days ``[start, end)`` as naive local timestamps (TLC times are New York local time)."""

    start: "object"
    end: "object"

    @classmethod
    def parse(cls, spec: str) -> "Period":
        """"2026-07", "2025-01:2026-06" or "2024-03-01:2024-03-21"; both ends are included."""
        import pandas as pd

        a, _, b = spec.partition(":")
        b = b or a

        def first(x):
            return pd.Timestamp(x if len(x) > 7 else f"{x}-01")

        def after(x):
            return pd.Timestamp(x) + pd.Timedelta(days=1) if len(x) > 7 else pd.Timestamp(f"{x}-01") + pd.offsets.MonthBegin(1)

        p = cls(first(a), after(b))
        if p.end <= p.start:
            raise ValueError(f"empty period {spec!r}")
        return p

    def months(self) -> List[str]:
        import pandas as pd

        m, out = pd.Timestamp(self.start).to_period("M"), []
        while m.start_time < self.end:
            out.append(str(m))
            m += 1
        return out

    def mask(self, ts):
        """Boolean mask of a pandas datetime Series (or array) inside the period."""
        return (ts >= self.start) & (ts < self.end)

    def __str__(self) -> str:
        import pandas as pd

        return f"{self.start:%Y-%m-%d} to {(self.end - pd.Timedelta(days=1)):%Y-%m-%d}"


def split(train: str, test: str) -> Tuple[Period, Period]:
    """Parse a train and a test period; the test period must start after training ends (no leakage)."""
    tr, te = Period.parse(train), Period.parse(test)
    if te.start < tr.end:
        raise ValueError(f"test period {te} overlaps or precedes training {tr}")
    return tr, te


def monthly_meta(month: str, root: Path = MONTHLY) -> dict:
    p = root / month / "meta.json"
    if not p.exists():
        raise FileNotFoundError(f"{p} missing: run `python -m ridesync.data.monthly {month}`")
    return json.loads(p.read_text())


def load_counts(months: Sequence[str], zones: Sequence[int], root: Path = MONTHLY):
    """Demand counts of consecutive months side by side: ((Z, B) float array, origin Timestamp of bucket 0)."""
    import numpy as np
    import pandas as pd

    parts = []
    for m in months:
        meta = monthly_meta(m, root)
        if list(meta["zones"]) != list(map(int, zones)):
            raise ValueError(f"{m} was reduced with other zones; redo it with --force")
        parts.append(np.load(root / m / "counts.npy"))
    return np.concatenate(parts, axis=1).astype(float), pd.Timestamp(f"{months[0]}-01")


def load_table(months: Sequence[str], name: str, root: Path = MONTHLY):
    """One of the monthly parquet tables (``eta`` or ``fare``) over several months."""
    import pandas as pd

    for m in months:
        monthly_meta(m, root)
    return pd.concat([pd.read_parquet(root / m / f"{name}.parquet") for m in months], ignore_index=True)


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
