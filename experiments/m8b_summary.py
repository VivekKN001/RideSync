"""M8b: the headline numbers of M2, M6 (ETA, surge) and M7 on three July 2026 days (and M2 at full scale and on
road times), side by side.

Reads the summaries the tagged runs wrote (``--tag m8b_<experiment>_<day>``), plus the M2-M7 originals on
March 2024 for reference, and writes experiments/results/m8b_summary_report.md.

    python experiments/m8b_summary.py
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

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


def _per_seed(runs: pd.DataFrame, arm: str, baseline: str, n: int, col: str, scale: float = 1.0,
              fmt: str = "{:+.1f}") -> str:
    """Each seed's paired delta, "a / b": with 2 seeds a 95% interval says nothing, so show both."""
    g = runs[runs["drivers.num_drivers"] == n].pivot_table(index="seed", columns="arm", values=col)
    return " / ".join(fmt.format(v * scale) for v in (g[arm] - g[baseline]))


def m2_rows(s: pd.DataFrame, label: str, runs: Optional[pd.DataFrame] = None) -> list:
    """``runs`` (the runs CSV) switches to per-seed deltas when it has fewer than 3 seeds."""
    few = runs is not None and runs["seed"].nunique() < 3
    out = []
    for n in sorted(s["drivers.num_drivers"].unique()):
        base = s[(s["arm"] == "immediate_greedy") & (s["drivers.num_drivers"] == n)].iloc[0]
        r = s[(s["arm"] == BEST) & (s["drivers.num_drivers"] == n)].iloc[0]
        rel = f"({r['d_completed_per_hour'] / base['completed_per_hour']:+.1%})"
        if few:
            d = lambda col, scale=1.0, fmt="{:+.1f}": _per_seed(runs, BEST, "immediate_greedy", n, col, scale, fmt)  # noqa: E731
            out.append(f"| {label} | {n} | {base['cancel_rate']:.1%} | {d('cancel_rate', 100)} pp (per seed) | "
                       f"{d('completed_per_hour', 1, '{:+.0f}')} {rel} | {d('wait_all_mean_s', 1, '{:+.0f}')} |")
        else:
            out.append(f"| {label} | {n} | {base['cancel_rate']:.1%} | {_pm(r, 'cancel_rate', 100)} pp | "
                       f"{_pm(r, 'completed_per_hour', 1, '{:+.0f}')} {rel} | {_pm(r, 'wait_all_mean_s', 1, '{:+.0f}')} |")
    return out


def main() -> None:
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    lines = ["# M8b: the experiments on more days and at full scale", "",
             "Same code and settings as M2, M6 (surge) and M7, with the M8 models (trained 2025-01..2026-06) and "
             "straight-line travel calibrated on 15 July 2026 unless marked road times (OSRM × 2.26). Every day is in the models' test month. 10% of Manhattan "
             "trips unless marked full scale (fleets 10x). Paired deltas, mean ± 95% CI (Student t over seeds).", "",
             f"## Batching with the cancellation-aware cost (`{BEST}`) against instant nearest-driver (M2)", "",
             "| day | drivers | cancel % (instant) | Δ cancel | Δ trips/h | Δ wait_all s |", "|---|---|---|---|---|---|"]
    for key, label in [("m2_straight", "Wed 13 Mar 2024, 17-20 (M2)"), *[(f"m8b_m2_{d}", v) for d, v in DAYS.items()],
                       ("m8b_m2_full", "Wed 15 Jul 2026, 17-20, full scale"),
                       ("m2_osrm", "Wed 13 Mar 2024, 17-20, road times (M2)"),
                       *[(f"m8b_m2_osrm_{d}", f"{v}, road times") for d, v in DAYS.items()],
                       ("m8b_m2_osrm_full", "Wed 15 Jul 2026, 17-20, full scale, road times")]:
        s = _read(key)
        if s is not None:
            runs = RESULTS / f"{key}_runs.csv"
            lines += m2_rows(s, label, pd.read_csv(runs) if runs.exists() else None)

    lines += ["", "## Optimal against greedy on the same 30 s batches and cost, full scale", "",
              "Paired `optimal@30s+aware` − `batched_greedy@30s+aware`. With 2 seeds each seed's delta is shown, "
              "not an interval.", "",
              "| travel | drivers | seeds | Δ trips/h | Δ cancel | Δ wait_all s | batches where greedy is worse |",
              "|---|---|---|---|---|---|---|"]
    for key, label in [("m8b_m2_full", "straight-line"), ("m8b_m2_osrm_full", "road times (OSRM)")]:
        p = RESULTS / f"{key}_runs.csv"
        if not p.exists():
            continue
        df = pd.read_csv(p)
        s = paired_summary(df, "batched_greedy@30s+aware", ["completed_per_hour", "cancel_rate", "wait_all_mean_s",
                                                            "shadow_worse_batches_frac"], ["drivers.num_drivers"])
        for _, r in s[s["arm"] == BEST].sort_values("drivers.num_drivers").iterrows():
            n_drivers = r["drivers.num_drivers"]
            n = df[(df["arm"] == BEST) & (df["drivers.num_drivers"] == n_drivers)]["seed"].nunique()
            if n < 3:
                d = lambda col, scale=1.0, fmt="{:+.1f}": _per_seed(df, BEST, "batched_greedy@30s+aware", n_drivers,  # noqa: E731
                                                                    col, scale, fmt)
                cells = (f"{d('completed_per_hour', 1, '{:+.0f}')} (per seed) | {d('cancel_rate', 100)} pp | "
                         f"{d('wait_all_mean_s', 1, '{:+.0f}')}")
            else:
                cells = (f"{_pm(r, 'completed_per_hour', 1, '{:+.0f}')} | {_pm(r, 'cancel_rate', 100)} pp | "
                         f"{_pm(r, 'wait_all_mean_s', 1, '{:+.0f}')}")
            lines.append(f"| {label} | {n_drivers} | {n} | {cells} | {r['shadow_worse_batches_frac']:.0%} |")

    lines += ["", "## Learned ETA against a distance × hour table, riders cancelling on late drivers (M6)", "",
              "400 drivers. Lateness tolerance = median time past the quote a rider waits before cancelling.", "",
              "| day | tolerance | cancel % (table) | Δ cancel | Δ trips/h | abs ETA error s (table → learned) |",
              "|---|---|---|---|---|---|"]
    tol = "riders.lateness_tolerance_median_s"
    for key, label in [("m6_eta_sim_straight_late", "Wed 13 Mar 2024 (M6)"), ("m8b_eta_sim_straight_late", DAYS["wed_pm"]),
                       ("m8b_eta_sim_osrm_late", f"{DAYS['wed_pm']}, road times")]:
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
