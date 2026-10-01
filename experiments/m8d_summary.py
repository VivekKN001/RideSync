"""M8d: do the headline results hold on every day of the test months, not just the one day each was run on?

Every Wednesday evening (17-20) of October 2025, January, April and July 2026 (19 days), plus a Wednesday morning
(07-10) and a Saturday night (20-23) in each month. Each day uses its month's models and travel calibration,
10% of Manhattan trips, straight-line travel, 6 seeds (``experiments/run_m8d_days.sh``). Days run before M8d keep
their M8b/M8c/M6b tags.

Each effect is measured per day as a paired delta against its baseline (mean over seeds); trips/h as a percentage
of the baseline, so busy and quiet days compare. Across days: the mean ± 95% CI (Student t over days, the days
being the independent units), the range, and on how many days the effect had the same sign.

    python experiments/m8d_summary.py      # -> experiments/results/m8d_summary_report.md
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

RESULTS = Path(__file__).parent / "results"
FLEET = "drivers.num_drivers"
TOL = "riders.lateness_tolerance_median_s"
MONTHS = {"2025-10": "Oct 2025", "2026-01": "Jan 2026", "2026-04": "Apr 2026", "2026-07": "Jul 2026"}
WINDOWS = {"1700": "Wed 17-20", "0700": "Wed 07-10", "2000": "Sat 20-23"}

# day key (date_start) -> experiment tags (m2, m7, ETA, m6b) for days that ran before M8d
OLD = {
    "2025-10-15_1700": ("m8c_m2_2025-10", "m8c_m7_2025-10", "m8c_eta_sim_2025-10_straight_late", "m6b_supply_2025-10"),
    "2026-01-14_1700": ("m8c_m2_2026-01", "m8c_m7_2026-01", "m8c_eta_sim_2026-01_straight_late", "m6b_supply_2026-01"),
    "2026-04-15_1700": ("m8c_m2_2026-04", "m8c_m7_2026-04", "m8c_eta_sim_2026-04_straight_late", "m6b_supply_2026-04"),
    "2026-07-15_1700": ("m8b_m2_wed_pm", "m8b_m7_wed_pm", "m8b_eta_sim_straight_late", "m6b_supply_wed_pm"),
    "2026-07-15_0700": ("m8b_m2_wed_am", "m8b_m7_wed_am", None, "m6b_supply_wed_am"),
    "2026-07-18_2000": ("m8b_m2_sat_night", "m8b_m7_sat_night", None, "m6b_supply_sat_night"),
}
EXPERIMENTS = ("m2", "m7", "eta", "m6b")

# effect: (label, experiment, arm, baseline, grid filter, metric, relative?)
EFFECTS = [
    ("batch300", "batching vs instant, 300 drivers: trips/h", "m2", "optimal@30s+aware", "immediate_greedy",
     {FLEET: 300}, "completed_per_hour", True),
    ("batch400", "batching vs instant, 400 drivers: trips/h", "m2", "optimal@30s+aware", "immediate_greedy",
     {FLEET: 400}, "completed_per_hour", True),
    ("batch500", "batching vs instant, 500 drivers: trips/h", "m2", "optimal@30s+aware", "immediate_greedy",
     {FLEET: 500}, "completed_per_hour", True),
    ("batch400c", "batching vs instant, 400 drivers: cancel (pp)", "m2", "optimal@30s+aware", "immediate_greedy",
     {FLEET: 400}, "cancel_rate", False),
    ("repo400", "repositioning (forecast) vs none, 400: trips/h", "m7", "planned_forecast", "none",
     {FLEET: 400}, "completed_per_hour", True),
    ("repo500", "repositioning (forecast) vs none, 500: trips/h", "m7", "planned_forecast", "none",
     {FLEET: 500}, "completed_per_hour", True),
    ("eta180", "learned ETA vs distance x hour table, 400, tolerance 180 s: trips/h", "eta", "learned_eta",
     "dist_hour_table", {TOL: 180.0}, "completed_per_hour", True),
    ("surge_fixed", "surge, fixed fleet vs no surge, 300: trips/h", "m6b", "surge_fixed", "no_surge",
     {FLEET: 300}, "completed_per_hour", True),
    ("surge_both", "surge, drivers log on + chase vs no surge, 300: trips/h", "m6b", "surge_both", "no_surge",
     {FLEET: 300}, "completed_per_hour", True),
    ("surge_both_earn", "surge, drivers log on + chase vs no surge, 300: earnings/online h", "m6b", "surge_both",
     "no_surge", {FLEET: 300}, "earnings_per_online_hour", True),
    ("repo_vs_surge500", "repositioning vs surge (both), 500: trips/h", "m6b", "reposition", "surge_both",
     {FLEET: 500}, "completed_per_hour", True),
]


def days() -> List[Tuple[str, str, str]]:
    """(month, date, start) of every day with results, from the run files on disk."""
    keys = set(OLD)
    for p in RESULTS.glob("m8d_m2_*_runs.csv"):
        keys.add(p.name[len("m8d_m2_"):-len("_runs.csv")])
    out = [(k[:7], k[:10], k[11:]) for k in keys]
    return sorted(out, key=lambda d: (d[0], d[2] != "1700", d[1], d[2]))


def tag(key: str, exp: str) -> Optional[str]:
    if key in OLD:
        old = OLD[key][EXPERIMENTS.index(exp)]
        if old is not None:
            return old
    return {"m2": f"m8d_m2_{key}", "m7": f"m8d_m7_{key}", "eta": f"m8d_eta_sim_{key}_straight_late",
            "m6b": f"m8d_m6b_{key}"}[exp]


def effect(runs: pd.DataFrame, arm: str, base: str, where: Dict[str, float], metric: str, rel: bool) -> float:
    """Mean paired delta over seeds: % of the baseline (rel) or percentage points (rates)."""
    for k, v in where.items():
        runs = runs[runs[k] == v]
    a = runs[runs["arm"] == arm].set_index("seed")[metric]
    b = runs[runs["arm"] == base].set_index("seed")[metric]
    if a.empty or b.empty:
        return float("nan")
    d = (a - b.loc[a.index]).mean()
    return 100 * d / b.loc[a.index].mean() if rel else 100 * d


def per_day() -> pd.DataFrame:
    rows = []
    cache: Dict[str, Optional[pd.DataFrame]] = {}
    for month, date, start in days():
        key = f"{date}_{start}"
        row = {"month": month, "date": date, "window": start}
        for name, _, exp, arm, base, where, metric, rel in EFFECTS:
            t = tag(key, exp)
            if t not in cache:
                p = RESULTS / f"{t}_runs.csv"
                cache[t] = pd.read_csv(p) if p.exists() else None
            row[name] = effect(cache[t], arm, base, where, metric, rel) if cache[t] is not None else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def pooled(v: pd.Series) -> str:
    v = v.dropna()
    n = len(v)
    if n == 0:
        return ""
    if n == 1:
        return f"{v.iloc[0]:+.1f} (1 day)"
    half = student_t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n)
    same = max((v > 0).sum(), (v < 0).sum())
    return f"{v.mean():+.1f} ± {half:.1f} [{v.min():+.1f}..{v.max():+.1f}] {same}/{n}"


def wednesdays(df: pd.DataFrame) -> List[str]:
    pm = df[df["window"] == "1700"]
    counts = {m: (pm["month"] == m).sum() for m in MONTHS}
    out = ["## Every Wednesday evening", "",
           "Per cell: mean over days ± 95% CI [lowest..highest day] and the number of days with the majority sign. "
           "Trips/h and earnings in % of the baseline, cancellations in percentage points.", "",
           "| effect | " + " | ".join(f"{label} ({counts[m]} days)" for m, label in MONTHS.items())
           + f" | all {len(pm)} days |", "|---|" + "---|" * (len(MONTHS) + 1)]
    for name, label, *_ in EFFECTS:
        cells = [pooled(pm[pm["month"] == m][name]) for m in MONTHS]
        out.append(f"| {label} | " + " | ".join(cells) + f" | {pooled(pm[name])} |")
    return out


def windows(df: pd.DataFrame) -> List[str]:
    other = df[df["window"] != "1700"]
    out = ["", "## Morning peak and Saturday night, every month", "",
           "One day per month and window; the mid-month Wednesday evening of each month is in the per-day table.", "",
           "| effect | " + " | ".join(WINDOWS[w] for w in ("0700", "2000")) + " |", "|---|---|---|"]
    for name, label, *_ in EFFECTS:
        cells = [pooled(other[other["window"] == w][name]) for w in ("0700", "2000")]
        out.append(f"| {label} | " + " | ".join(cells) + " |")
    return out


def table(df: pd.DataFrame) -> List[str]:
    out = ["", "## Every day", "", "Point estimates (mean over 6 seeds) per day; the column keys are the effects above, "
           "in order.", "", "| day | window | " + " | ".join(name for name, *_ in EFFECTS) + " |",
           "|---|---|" + "---|" * len(EFFECTS)]
    for _, r in df.iterrows():
        day = datetime.fromisoformat(r["date"]).strftime("%a %d %b %Y")
        out.append(f"| {day} | {WINDOWS[r['window']][4:]} | "
                   + " | ".join("" if np.isnan(r[name]) else f"{r[name]:+.1f}" for name, *_ in EFFECTS) + " |")
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    df = per_day()
    df.to_csv(RESULTS / "m8d_per_day.csv", index=False)
    intro = __doc__.split("\n\n")[:3]
    lines = ["# M8d: every day of the test months", "", *(p.replace("\n", " ") for p in intro[:2]), "",
             *wednesdays(df), *windows(df), *table(df)]
    text = "\n".join(lines) + "\n"
    (RESULTS / "m8d_summary_report.md").write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
