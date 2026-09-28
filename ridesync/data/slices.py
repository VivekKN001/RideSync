"""What a TLC demand slice covers, read from its file name (``ridesync.data.tlc.slice_name``).

    trips_2024-03-13_1700_3h_manhattan_f0.1.parquet -> (2024-03-13 17:00, 0.1)

Dependency-free, so the simulator can use it without pandas.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

_NAME = re.compile(r"trips_(\d{4}-\d{2}-\d{2})_(\d{2})(\d{2})_[\d.]+h_.+_f([\d.]+)\.parquet$")


def slice_meta(path: str) -> Optional[Tuple[datetime, float]]:
    """(start, sample fraction) of a slice, or None if the name doesn't follow the convention."""
    m = _NAME.search(Path(path).name)
    if m is None:
        return None
    date, hh, mm, frac = m.groups()
    return datetime.fromisoformat(f"{date} {hh}:{mm}"), float(frac)


def run_start_and_frac(demand) -> Tuple[Optional[datetime], float]:
    """Start of simulated t = 0 and the sample fraction for a ``DemandConfig``: explicit fields first,
    then the slice name. Synthetic demand has no start and a fraction of 1."""
    meta = slice_meta(demand.trips_path) if demand.trips_path else None
    start = datetime.fromisoformat(demand.start) if demand.start else (meta[0] if meta else None)
    frac = demand.sample_frac if demand.sample_frac is not None else (meta[1] if meta else 1.0)
    return start, frac
