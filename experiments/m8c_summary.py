"""M8c: the models and the main experiments on four test months, side by side.

Each test month's models train on the 12 months before it (October 2025, January 2026, April 2026;
``RIDESYNC_MODELS=data/models_<month>``); July 2026 is M8's (trained on 2025-01..2026-06). Every test day
is a mid-month Wednesday, 17:00-20:00, 10% of Manhattan trips, with travel calibrated on that day.

    python experiments/m8c_summary.py      # -> experiments/results/m8c_summary_report.md
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from ridesync.experiments import paired_summary

RESULTS = Path(__file__).parent / "results"
# month -> (label, model report prefix, experiment tags: m2, m2 on OSRM, m7, ETA-sim)
MONTHS = {
    "2025-10": ("Oct 2025 (Wed 15th)", "m8c_2025-10", "m8c_m2_2025-10", "m8c_m2_osrm_2025-10", "m8c_m7_2025-10",
                "m8c_eta_sim_2025-10_straight_late"),
    "2026-01": ("Jan 2026 (Wed 14th)", "m8c_2026-01", "m8c_m2_2026-01", "m8c_m2_osrm_2026-01", "m8c_m7_2026-01",
                "m8c_eta_sim_2026-01_straight_late"),
    "2026-04": ("Apr 2026 (Wed 15th)", "m8c_2026-04", "m8c_m2_2026-04", "m8c_m2_osrm_2026-04", "m8c_m7_2026-04",
                "m8c_eta_sim_2026-04_straight_late"),
    "2026-07": ("Jul 2026 (Wed 15th)", "m8", "m8b_m2_wed_pm", "m8b_m2_osrm_wed_pm", "m8b_m7_wed_pm",
                "m8b_eta_sim_straight_late"),
}
BEST = "optimal@30s+aware"


def table(path: Path, heading: Optional[str] = None) -> Optional[pd.DataFrame]:
    """The first markdown table in a report (after ``heading`` if given), as strings."""
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    if heading is not None:
        lines = lines[next(i for i, l in enumerate(lines) if l.startswith(heading)):]
    rows = [l for l in lines if l.startswith("|")]
    start = next(i for i, l in enumerate(lines) if l.startswith("|"))
    rows = []
    for l in lines[start:]:
        if not l.startswith("|"):
            break
        rows.append([c.strip() for c in l.strip().strip("|").split("|")])
    return pd.DataFrame(rows[2:], columns=rows[0])


def pct(s: str) -> float:
    return float(s.rstrip("%"))


def _pm(r, col: str, scale: float = 1.0, fmt: str = "{:+.1f}") -> str:
    return f"{fmt.format(r['d_' + col] * scale)} ± {r['ci_' + col] * scale:.1f}"


def models() -> List[str]:
    out = ["## The models on each test month", "",
           "| test month | demand WAPE, 15 min: model / best baseline | 60 min | ETA MAPE: learned / distance x hour table "
           "/ base alone | ETA range coverage (target 80%) |", "|---|---|---|---|---|"]
    for m, (label, prefix, *_) in MONTHS.items():
        cells = []
        for h in ("## 15 minutes ahead", "## 60 minutes ahead"):
            t = table(RESULTS / f"{prefix}_demand_report.md", h)
            if t is None:
                cells.append("")
                continue
            model = pct(t.iloc[0]["wape"])
            base = min(pct(v) for v in t.iloc[1:]["wape"])
            cells.append(f"{model:.1f}% / {base:.1f}%")
        eta_path = RESULTS / f"{prefix}_eta_straight_report.md"
        t = table(eta_path)
        if t is not None:
            get = lambda key: pct(t[t["method"].str.startswith(key)].iloc[-1]["mape"])  # noqa: E731
            cells.append(f"{get('base x learned'):.1f}% / {get('base x distance'):.1f}% / {get('base model alone'):.1f}%")
            cov = re.search(r"([0-9.]+)% of trips land inside", eta_path.read_text(encoding="utf-8"))
            cells.append(f"{cov.group(1)}%" if cov else "")
        else:
            cells += ["", ""]
        out.append(f"| {label} | " + " | ".join(cells) + " |")
    return out


def batching() -> List[str]:
    out = ["", f"## Batching with the cancellation-aware cost (`{BEST}`) against instant nearest-driver", "",
           "| test month | travel | drivers | cancel % (instant) | Δ cancel | Δ trips/h |", "|---|---|---|---|---|---|"]
    for m, (label, _, m2, m2o, *_) in MONTHS.items():
        for tag, travel in ((m2, "straight-line"), (m2o, "road times")):
            p = RESULTS / f"{tag}_summary.csv"
            if not p.exists():
                continue
            s = pd.read_csv(p)
            for n in (300, 400, 500):
                b = s[(s["arm"] == "immediate_greedy") & (s["drivers.num_drivers"] == n)]
                r = s[(s["arm"] == BEST) & (s["drivers.num_drivers"] == n)]
                if b.empty or r.empty:
                    continue
                b, r = b.iloc[0], r.iloc[0]
                out.append(f"| {label} | {travel} | {n} | {b['cancel_rate']:.1%} | {_pm(r, 'cancel_rate', 100)} pp | "
                           f"{_pm(r, 'completed_per_hour', 1, '{:+.0f}')} ({r['d_completed_per_hour'] / b['completed_per_hour']:+.1%}) |")
    return out


def reposition() -> List[str]:
    out = ["", "## Coordinated repositioning (`planned_forecast`, the month's own demand model) against staying put", "",
           "| test month | drivers | cancel % (none) | Δ cancel | Δ trips/h | Δ empty driving |", "|---|---|---|---|---|---|"]
    for m, (label, _, _, _, m7, _) in MONTHS.items():
        p = RESULTS / f"{m7}_summary.csv"
        if not p.exists():
            continue
        s = pd.read_csv(p)
        for n in (400, 500):
            b = s[(s["arm"] == "none") & (s["drivers.num_drivers"] == n)].iloc[0]
            r = s[(s["arm"] == "planned_forecast") & (s["drivers.num_drivers"] == n)].iloc[0]
            out.append(f"| {label} | {n} | {b['cancel_rate']:.1%} | {_pm(r, 'cancel_rate', 100)} pp | "
                       f"{_pm(r, 'completed_per_hour', 1, '{:+.0f}')} | {_pm(r, 'empty_frac', 100)} pp |")
    return out


def eta() -> List[str]:
    out = ["", "## Learned ETA (the month's own model) against the distance x hour table, riders cancelling on late "
           "drivers, 400 drivers", "",
           "| test month | tolerance | Δ cancel | Δ trips/h |", "|---|---|---|---|"]
    tol = "riders.lateness_tolerance_median_s"
    for m, (label, *_, es) in MONTHS.items():
        p = RESULTS / f"{es}_runs.csv"
        if not p.exists():
            continue
        s = paired_summary(pd.read_csv(p), "dist_hour_table", ["cancel_rate", "completed_per_hour"], [tol])
        for t in sorted(s[tol].unique()):
            b = s[(s["arm"] == "dist_hour_table") & (s[tol] == t)].iloc[0]
            r = s[(s["arm"] == "learned_eta") & (s[tol] == t)].iloc[0]
            out.append(f"| {label} | {t:.0f} s | {_pm(r, 'cancel_rate', 100)} pp | "
                       f"{_pm(r, 'completed_per_hour', 1, '{:+.0f}')} ({r['d_completed_per_hour'] / b['completed_per_hour']:+.1%}) |")
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    lines = ["# M8c: four test months", "", __doc__.split("\n\n")[1].replace("\n", " "), "",
             "Paired deltas, mean ± 95% CI (Student t over seeds).", "",
             *models(), *batching(), *reposition(), *eta()]
    text = "\n".join(lines) + "\n"
    (RESULTS / "m8c_summary_report.md").write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
