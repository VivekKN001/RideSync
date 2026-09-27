"""Experiment harness: run arms x parameter grid x seeds in parallel, then compare arms.

Every arm under a given seed sees identical riders and identical driver
accept/decline draws (common random numbers). So arms are compared by
**paired** per-seed differences against a baseline, which gives much tighter
confidence intervals than comparing independent means.
"""
from __future__ import annotations

import itertools
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence

import numpy as np
import pandas as pd

from .sim import SimConfig, simulate, summarize


@dataclass(frozen=True)
class Arm:
    label: str
    overrides: Dict[str, object] = field(default_factory=dict)


def _run(job) -> dict:
    base, arm, point, seed = job
    cfg = base.with_(**arm.overrides, **point, seed=seed)
    row = {"arm": arm.label, "seed": seed, **point}
    row.update(summarize(simulate(cfg)))
    return row


def run_grid(
    base: SimConfig,
    arms: Sequence[Arm],
    grid: Dict[str, Iterable],
    seeds: Iterable[int],
    workers: int | None = None,
) -> pd.DataFrame:
    keys = list(grid)
    points = [dict(zip(keys, values)) for values in itertools.product(*grid.values())]
    jobs = [(base, arm, point, seed) for arm in arms for point in points for seed in seeds]
    with ProcessPoolExecutor(max_workers=workers or os.cpu_count()) as pool:
        rows = list(pool.map(_run, jobs, chunksize=1))
    return pd.DataFrame(rows)


def paired_summary(
    df: pd.DataFrame, baseline: str, metrics: List[str], by: List[str]
) -> pd.DataFrame:
    """Per arm and grid point: mean of each metric and mean paired delta vs baseline with a 95% CI."""
    base = df[df["arm"] == baseline].set_index(by + ["seed"])[metrics]
    out = []
    for keys, g in df.groupby(["arm"] + by, sort=False):
        g = g.set_index(by + ["seed"])[metrics]
        diff = g - base.loc[g.index]
        n = len(g)
        row = dict(zip(["arm"] + by, keys))
        for m in metrics:
            row[m] = g[m].mean()
            if keys[0] != baseline:
                half = 1.96 * diff[m].std(ddof=1) / np.sqrt(n) if n > 1 else float("nan")
                row[f"d_{m}"] = diff[m].mean()
                row[f"ci_{m}"] = half
        out.append(row)
    return pd.DataFrame(out)


def _delta(row, m, scale=1.0, digits=0) -> str:
    d = row.get(f"d_{m}")
    if d is None or d != d:
        return ""
    return f"{d * scale:+.{digits}f} ± {row[f'ci_{m}'] * scale:.{digits}f}"


def markdown_report(summary: pd.DataFrame, title: str, baseline: str, fleet_col: str, notes: List[str] = ()) -> str:
    lines = [f"# {title}", "",
             f"Deltas are paired against `{baseline}` for the same seed (mean ± 95% CI).",
             "`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.",
             *notes]
    for n in summary[fleet_col].unique():
        s = summary[summary[fleet_col] == n]
        lines += ["", f"## {n} drivers", "",
                  "| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for _, r in s.iterrows():
            r = r.to_dict()
            lines.append(
                f"| {r['arm']} | {r['cancel_rate']*100:.1f} | {_delta(r, 'cancel_rate', 100, 1)} "
                f"| {r['wait_all_mean_s']:.0f} | {_delta(r, 'wait_all_mean_s')} | {r['wait_mean_s']:.0f} "
                f"| {r['pickup_mean_s']:.0f} | {r['completed_per_hour']:.0f} | {_delta(r, 'completed_per_hour')} "
                f"| {r['driver_idle_frac']*100:.1f} | {r['batch_riders_mean']:.1f} |"
            )
    return "\n".join(lines) + "\n"
