"""Experiment harness: run arms x parameter grid x seeds in parallel, then compare arms.

Every arm under a given seed sees identical riders and identical driver
accept/decline draws (common random numbers). So arms are compared by
**paired** per-seed differences against a baseline, which gives much tighter
confidence intervals than comparing independent means.
"""
from __future__ import annotations

import itertools
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Union

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


def _norm(v):
    """Grid values as they come back from a CSV: numbers compare as floats."""
    return float(v) if isinstance(v, (int, float, np.number)) and not isinstance(v, bool) else v


def run_grid(
    base: SimConfig,
    arms: Sequence[Arm],
    grid: Dict[str, Iterable],
    seeds: Iterable[int],
    workers: Optional[int] = None,
    checkpoint: Union[str, Path, None] = None,
) -> pd.DataFrame:
    """Every arm x grid point x seed, in parallel. Rows come back in that order.

    ``checkpoint`` is a CSV of finished runs: runs already in it are skipped, and each new run is appended
    the moment it finishes. A long grid (hours of OSRM at full scale) can then be stopped and resumed,
    and a crash loses only the runs in flight. With RIDESYNC_NO_SIM set, a missing run is an error instead:
    rerunning a script with ``--resume`` then only rebuilds its summary and report from the saved runs.
    """
    keys = list(grid)
    points = [dict(zip(keys, values)) for values in itertools.product(*grid.values())]
    jobs = [(base, arm, point, seed) for arm in arms for point in points for seed in seeds]
    key = lambda label, point, seed: (label, *(_norm(point[k]) for k in keys), _norm(seed))  # noqa: E731

    done: Dict[tuple, dict] = {}
    path = Path(checkpoint) if checkpoint is not None else None
    if path is not None and path.exists() and path.stat().st_size > 0:
        for r in pd.read_csv(path).to_dict("records"):
            done[key(r["arm"], r, r["seed"])] = r
    todo = [j for j in jobs if key(j[1].label, j[2], j[3]) not in done]
    if todo and os.environ.get("RIDESYNC_NO_SIM"):  # regenerating reports from saved runs: never simulate
        _, arm, point, seed = todo[0]
        raise RuntimeError(f"RIDESYNC_NO_SIM: {len(todo)} of {len(jobs)} runs are not in {path}, "
                           f"e.g. {arm.label} {point} seed {seed}")
    if todo:
        with ProcessPoolExecutor(max_workers=workers or os.cpu_count()) as pool:
            futures = [pool.submit(_run, j) for j in todo]
            for f in as_completed(futures):
                row = f.result()
                done[key(row["arm"], row, row["seed"])] = row
                if path is not None:
                    new = not path.exists() or path.stat().st_size == 0
                    pd.DataFrame([row]).to_csv(path, mode="a", header=new, index=False)
    return pd.DataFrame([done[key(arm.label, point, seed)] for _, arm, point, seed in jobs])


def paired_summary(
    df: pd.DataFrame, baseline: str, metrics: List[str], by: List[str]
) -> pd.DataFrame:
    """Per arm and grid point: mean of each metric and mean paired delta vs baseline with a 95% CI.

    The interval is Student's t on the per-seed differences (n - 1 degrees of freedom). With 3-8 seeds the
    normal 1.96 would make it 1.2-2.2x too narrow; with 2 seeds the interval is honest but very wide.
    """
    from scipy.stats import t as student_t

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
                half = student_t.ppf(0.975, n - 1) * diff[m].std(ddof=1) / np.sqrt(n) if n > 1 else float("nan")
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
             f"Deltas are paired against `{baseline}` for the same seed (mean ± 95% CI, Student t over seeds).",
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
