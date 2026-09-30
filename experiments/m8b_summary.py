"""M8b: the headline numbers of M2, M6 (ETA, surge) and M7 on three July 2026 days (and M2 at full scale and on
road times), side by side.

Reads the summaries the tagged runs wrote (``--tag m8b_<experiment>_<day>``), plus the M2-M7 originals on
March 2024 for reference, and writes experiments/results/m8b_summary_report.md.

    python experiments/m8b_summary.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ridesync.experiments import paired_summary

RESULTS = Path(__file__).parent / "results"
DAYS = {"wed_pm": "Wed 15 Jul 2026, 17-20", "wed_am": "Wed 15 Jul 2026, 07-10", "sat_night": "Sat 18 Jul 2026, 20-23"}
BEST = "optimal@30s+aware"


def _read(name: str):
    p = RESULTS / f"{name}_summary.csv"
    return pd.read_csv(p) if p.exists() else None


def _pm(row, col: str, scale: float = 1.0, fmt: str = "{:+.1f}") -> str:
    return f"{fmt.format(row['d_' + col] * scale)} ± {row['ci_' + col] * scale:.1f}"


def m2_rows(s: pd.DataFrame, label: str) -> list:
    out = []
    for n in sorted(s["drivers.num_drivers"].unique()):
        base = s[(s["arm"] == "immediate_greedy") & (s["drivers.num_drivers"] == n)].iloc[0]
        r = s[(s["arm"] == BEST) & (s["drivers.num_drivers"] == n)].iloc[0]
        out.append(f"| {label} | {n} | {base['cancel_rate']:.1%} | {_pm(r, 'cancel_rate', 100)} pp | "
                   f"{_pm(r, 'completed_per_hour', 1, '{:+.0f}')} ({r['d_completed_per_hour'] / base['completed_per_hour']:+.1%}) | "
                   f"{_pm(r, 'wait_all_mean_s', 1, '{:+.0f}')} |")
    return out


def main() -> None:
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    lines = ["# M8b: the experiments on more days and at full scale", "",
             "Same code and settings as M2, M6 (surge) and M7, with the M8 models (trained 2025-01..2026-06) and "
             "straight-line travel calibrated on 15 July 2026 unless marked road times (OSRM × 2.26). Every day is in the models' test month. 10% of Manhattan "
             "trips unless marked full scale (fleets 10x). Paired deltas, mean ± 95% CI.", "",
             f"## Batching with the cancellation-aware cost (`{BEST}`) against instant nearest-driver (M2)", "",
             "| day | drivers | cancel % (instant) | Δ cancel | Δ trips/h | Δ wait_all s |", "|---|---|---|---|---|---|"]
    for key, label in [("m2_straight", "Wed 13 Mar 2024, 17-20 (M2)"), *[(f"m8b_m2_{d}", v) for d, v in DAYS.items()],
                       ("m8b_m2_full", "Wed 15 Jul 2026, 17-20, full scale"),
                       ("m2_osrm", "Wed 13 Mar 2024, 17-20, road times (M2)"),
                       ("m8b_m2_osrm_wed_pm", "Wed 15 Jul 2026, 17-20, road times")]:
        s = _read(key)
        if s is not None:
            lines += m2_rows(s, label)

    lines += ["", "## Learned ETA against a distance × hour table, riders cancelling on late drivers (M6)", "",
              "400 drivers. Lateness tolerance = median time past the quote a rider waits before cancelling.", "",
              "| day | tolerance | cancel % (table) | Δ cancel | Δ trips/h | abs ETA error s (table → learned) |",
              "|---|---|---|---|---|---|"]
    tol = "riders.lateness_tolerance_median_s"
    for key, label in [("m6_eta_sim_straight_late", "Wed 13 Mar 2024 (M6)"), ("m8b_eta_sim_straight_late", DAYS["wed_pm"])]:
        p = RESULTS / f"{key}_runs.csv"
        if not p.exists():
            continue
        df = pd.read_csv(p)
        s = paired_summary(df, "dist_hour_table", ["cancel_rate", "completed_per_hour", "eta_abs_error_mean_s"], [tol])
        for t in sorted(s[tol].unique()):
            base = s[(s["arm"] == "dist_hour_table") & (s[tol] == t)].iloc[0]
            r = s[(s["arm"] == "learned_eta") & (s[tol] == t)].iloc[0]
            lines.append(f"| {label} | {t:.0f} s | {base['cancel_rate']:.1%} | {_pm(r, 'cancel_rate', 100)} pp | "
                         f"{_pm(r, 'completed_per_hour', 1, '{:+.0f}')} ({r['d_completed_per_hour'] / base['completed_per_hour']:+.1%}) | "
                         f"{base['eta_abs_error_mean_s']:.0f} → {r['eta_abs_error_mean_s']:.0f} |")

    lines += ["", "## Surge pricing against none, elasticity 0.5 (M6)", "",
              "| day | drivers | arm | Δ trips/h | Δ cancel | Δ wait_all s | Δ revenue/h |", "|---|---|---|---|---|---|---|"]
    for key, label in [("m6_surge", "Wed 13 Mar 2024 (M6)"), *[(f"m8b_surge_{d}", v) for d, v in DAYS.items()]]:
        s = _read(key)
        if s is None:
            continue
        s = s[(s["pricing.elasticity"] == 0.5) & (s["arm"] != "no_surge")]
        for _, r in s.sort_values(["drivers.num_drivers", "arm"]).iterrows():
            lines.append(f"| {label} | {r['drivers.num_drivers']} | {r['arm']} | {_pm(r, 'completed_per_hour', 1, '{:+.0f}')} | "
                         f"{_pm(r, 'cancel_rate', 100)} pp | {_pm(r, 'wait_all_mean_s', 1, '{:+.0f}')} | "
                         f"{_pm(r, 'revenue_per_hour', 1, '{:+.0f}')} |")

    lines += ["", "## Repositioning idle drivers against staying put (M7)", "",
              "| day | drivers | arm | cancel % (none) | Δ cancel | Δ trips/h | Δ pickup s | Δ empty driving |",
              "|---|---|---|---|---|---|---|---|"]
    for key, label in [("m7_reposition", "Wed 27 Mar 2024 (M7)"), *[(f"m8b_m7_{d}", v) for d, v in DAYS.items()]]:
        s = _read(key)
        if s is None:
            continue
        for n in sorted(s["drivers.num_drivers"].unique()):
            base = s[(s["arm"] == "none") & (s["drivers.num_drivers"] == n)].iloc[0]
            for arm in ("drift", "planned_forecast"):
                r = s[(s["arm"] == arm) & (s["drivers.num_drivers"] == n)].iloc[0]
                lines.append(f"| {label} | {n} | {arm} | {base['cancel_rate']:.1%} | {_pm(r, 'cancel_rate', 100)} pp | "
                             f"{_pm(r, 'completed_per_hour', 1, '{:+.0f}')} | {_pm(r, 'pickup_mean_s', 1, '{:+.0f}')} | "
                             f"{_pm(r, 'empty_frac', 100)} pp |")
    text = "\n".join(lines) + "\n"
    (RESULTS / "m8b_summary_report.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
