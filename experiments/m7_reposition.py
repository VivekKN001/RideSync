"""M7: moving idle drivers toward demand. Stay put vs drift to usual hot spots vs a coordinated plan.

    python -m ridesync.ml.train demand                 # drift and the forecast arm need data/models/demand.joblib
    python -m ridesync.data.tlc --date 2026-07-22      # a test day of the demand model (July 2026)
    python experiments/m7_reposition.py [--fleets 300 400 500] [--seeds 6] [--workers 4]

Demand is Wednesday 2026-07-22, 17:00-20:00: a test day, so neither the forecast nor drift's "usual" map
(training days 1-21) has seen it. Dispatch is the best M2 arm (optimal every 30 s, cancellation-aware)
on the calibrated straight-line model with per-trip noise, and riders give up on late drivers
(``riders.enroute_cancel``, median tolerance 3 min), so shorter pickups can show up as fewer cancellations.

Arms (same riders and draws per seed; deltas paired against ``none``, and against ``drift``):
- ``none``: idle drivers wait where their last trip ended (every earlier milestone).
- ``drift``: drivers head for the nearest usually-busy zone on their own. The realistic baseline.
- ``planned_reactive`` / ``planned_forecast``: the platform fills zones short of drivers, with demand
  from the last 15 minutes or from the M6 forecast.
A move-cap check reruns ``planned_forecast`` with 5-minute moves (default 10) at the middle fleet.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

from ridesync.data.slices import run_start_and_frac
from ridesync.experiments import Arm, paired_summary, run_grid
from ridesync.matching import CancelBelief, CostParams
from ridesync.routing import travel_from_calibration
from ridesync.sim import SimConfig

RESULTS = Path(__file__).parent / "results"
DEFAULT_SLICE = "data/processed/trips_2026-07-22_1700_3h_manhattan_f0.1.parquet"
AWARE = CostParams(trip_value_s=900.0, cancel=CancelBelief())
# Real drives vary around the quote: per-trip lognormal noise, the ETA model's robust test residual (M6).
# Quotes come from the noise-free matrix, so drivers are sometimes late and riders can give up on them.
NOISE = 0.27
FLEET = "drivers.num_drivers"
METRICS = ["cancel_rate", "cancel_late_rate", "wait_all_mean_s", "pickup_mean_s", "completed_per_hour",
           "driver_idle_frac", "driver_reposition_frac", "empty_frac", "moves_per_driver_hour",
           "reposition_km_per_hour", "moves_dispatched_frac", "move_planned_mean_s"]
ARMS = [
    Arm("none"),
    Arm("drift", {"reposition.policy": "drift"}),
    Arm("planned_reactive", {"reposition.policy": "planned", "reposition.demand": "reactive"}),
    Arm("planned_forecast", {"reposition.policy": "planned", "reposition.demand": "forecast"}),
]
CAP_ARM = Arm("planned_forecast_5min", {"reposition.policy": "planned", "reposition.demand": "forecast",
                                        "reposition.max_move_s": 300.0})


def _d(r, m, scale=1.0, digits=0):
    d = r.get(f"d_{m}")
    if d is None or d != d:
        return ""
    return f"{d * scale:+.{digits}f} ± {r[f'ci_{m}'] * scale:.{digits}f}"


def _table(s: pd.DataFrame, fleet: int, baseline: str) -> list:
    g = s[s[FLEET] == fleet]
    lines = ["| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s "
             "| trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in g.iterrows():
        r = r.to_dict()
        if r["arm"] == baseline:
            r = {k: v for k, v in r.items() if not k.startswith(("d_", "ci_"))}
        cut = r["moves_dispatched_frac"]
        cut = "" if cut != cut else f"{cut * 100:.0f}"
        lines.append(
            f"| {r['arm']} | {r['cancel_rate'] * 100:.1f} | {_d(r, 'cancel_rate', 100, 1)} | {r['cancel_late_rate'] * 100:.1f} "
            f"| {r['wait_all_mean_s']:.0f} | {_d(r, 'wait_all_mean_s')} | {r['pickup_mean_s']:.0f} | {_d(r, 'pickup_mean_s')} "
            f"| {r['completed_per_hour']:.0f} | {_d(r, 'completed_per_hour', 1, 1)} "
            f"| {r['empty_frac'] * 100:.1f} | {_d(r, 'empty_frac', 100, 1)} "
            f"| {r['moves_per_driver_hour']:.2f} | {r['reposition_km_per_hour']:.0f} "
            f"| {cut} |")
    return lines


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", default=DEFAULT_SLICE)
    ap.add_argument("--fleets", type=int, nargs="+", default=[300, 400, 500])
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--tag", default=None, help="output file prefix under experiments/results (default: m7_reposition)")
    args = ap.parse_args()

    base = SimConfig(travel=travel_from_calibration("straight")).with_(**{
        "demand.trips_path": args.slice, "demand.duration_s": 3 * 3600.0, "demand.warmup_s": 1800.0,
        "dispatch.strategy": "lsa", "dispatch.interval_s": 30.0, "dispatch.cost": AWARE, "dispatch.max_candidates": 20,
        "riders.enroute_cancel": True, "travel.noise_sigma": NOISE,
    })
    fare = Path("data/models/fare.json")
    if fare.exists():
        from ridesync.ml.fare import fare_from_file

        base = base.with_(fare=fare_from_file(str(fare)))  # for the road factor of reposition km

    t0 = time.time()
    df = run_grid(base, ARMS, {FLEET: args.fleets}, range(args.seeds), workers=args.workers)
    mid = sorted(args.fleets)[len(args.fleets) // 2]
    cap = run_grid(base, [ARMS[0], ARMS[3], CAP_ARM], {FLEET: [mid]}, range(args.seeds), workers=args.workers)
    print(f"{len(df) + len(cap)} runs in {time.time() - t0:.0f}s")
    for d in (df, cap):
        d["empty_frac"] = d["driver_enroute_frac"] + d["driver_reposition_frac"]
    RESULTS.mkdir(exist_ok=True)
    tag = args.tag or "m7_reposition"
    df.to_csv(RESULTS / f"{tag}_runs.csv", index=False)
    cap.to_csv(RESULTS / f"{tag}_cap_runs.csv", index=False)

    vs_none = paired_summary(df, "none", METRICS, [FLEET])
    vs_drift = paired_summary(df[df["arm"] != "none"], "drift", METRICS, [FLEET])
    vs_none.to_csv(RESULTS / f"{tag}_summary.csv", index=False)
    cap_s = paired_summary(cap, "planned_forecast", METRICS, [FLEET])

    p = base.reposition
    start, _ = run_start_and_frac(base.demand)
    lines = [f"# M7: repositioning idle drivers (Manhattan TLC replay, {start:%Y-%m-%d %H:%M}, 3 h)", "",
             f"Optimal @30 s, cancellation-aware, straight-line travel with per-trip noise (sigma {NOISE}); "
             f"riders give up on late drivers "
             f"(median tolerance {base.riders.lateness_tolerance_median_s:.0f} s). Every {p.interval_s:.0f} s the policy "
             f"may move drivers idle >= {p.min_idle_s:.0f} s, at most {p.max_share:.0%} of the idle fleet, on drives "
             f"<= {p.max_move_s:.0f} s. {args.seeds} seeds, mean ± 95% CI of paired differences.",
             "`empty driving` = share of driver time driving without a rider (to pickups + repositioning).", ""]
    for n in args.fleets:
        lines += [f"## {n} drivers: against `none`", ""] + _table(vs_none, n, "none") + [""]
        lines += [f"### {n} drivers: against `drift`", ""] + _table(vs_drift, n, "drift") + [""]
    lines += [f"## Move cap: 5 vs 10 minutes, {mid} drivers (against `planned_forecast`, 10 min)", ""]
    lines += _table(cap_s, mid, "planned_forecast") + [""]
    text = "\n".join(lines) + "\n"
    (RESULTS / f"{tag}_report.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
