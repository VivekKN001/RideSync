"""M2: dispatch strategies on real Manhattan demand (TLC replay), straight-line vs OSRM road times.

Run it once per travel model to separate "real demand" from "real road network":

    python experiments/m2_real_demand.py --travel straight
    python experiments/m2_real_demand.py --travel osrm        # needs `docker compose up -d osrm`

Travel models use the fits in data/processed/calibration.json (`python -m ridesync.routing.calibrate`).
Optimal arms also solve every batch with cheapest-edge greedy as a shadow (not acted on), so the report
shows the per-batch optimality gap directly.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

from ridesync.experiments import Arm, markdown_report, paired_summary, run_grid
from ridesync.matching import CancelBelief, CostParams
from ridesync.routing import travel_from_calibration
from ridesync.sim import SimConfig

RESULTS = Path(__file__).parent / "results"
DEFAULT_SLICE = "data/processed/trips_2024-03-13_1700_3h_manhattan_f0.1.parquet"
METRICS = [
    "cancel_rate", "wait_all_mean_s", "wait_mean_s", "pickup_mean_s", "completed_per_hour",
    "driver_idle_frac", "batch_riders_mean", "shadow_gap_s_per_batch", "shadow_worse_batches_frac",
]
AWARE = CostParams(trip_value_s=900.0, cancel=CancelBelief())


def arm(label, strategy, interval, cost=None):
    o = {"dispatch.strategy": strategy, "dispatch.interval_s": float(interval)}
    if cost is not None:
        o["dispatch.cost"] = cost
    if strategy == "lsa":
        o["dispatch.shadow_strategy"] = "global_greedy"
    return Arm(label, o)


ARMS = [
    arm("immediate_greedy", "fifo_greedy", 0),
    arm("batched_greedy@10s", "global_greedy", 10),
    arm("optimal@10s", "lsa", 10),
    arm("batched_greedy@10s+aware", "global_greedy", 10, AWARE),
    arm("optimal@10s+aware", "lsa", 10, AWARE),
    arm("batched_greedy@30s+aware", "global_greedy", 30, AWARE),
    arm("optimal@30s+aware", "lsa", 30, AWARE),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--travel", choices=["straight", "osrm"], default="straight")
    ap.add_argument("--osrm-url", default="http://localhost:5000")
    ap.add_argument("--slice", default=DEFAULT_SLICE)
    ap.add_argument("--fleets", type=int, nargs="+", default=[300, 350, 400, 450, 500])
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()

    try:
        travel = travel_from_calibration(args.travel, args.osrm_url)
    except RuntimeError as e:
        sys.exit(str(e))
    base = SimConfig(travel=travel).with_(**{
        "demand.trips_path": args.slice,
        "demand.duration_s": 3 * 3600.0,
        "demand.warmup_s": 1800.0,
        "dispatch.max_candidates": 20,
    })
    t0 = time.time()
    df = run_grid(base, ARMS, {"drivers.num_drivers": args.fleets}, range(args.seeds), workers=args.workers)
    print(f"{len(df)} runs in {time.time() - t0:.0f}s")

    observed = pd.read_parquet(args.slice)["observed_wait_s"].dropna()
    tag = f"m2_{args.travel}"
    RESULTS.mkdir(exist_ok=True)
    df.to_csv(RESULTS / f"{tag}_runs.csv", index=False)
    summary = paired_summary(df, "immediate_greedy", METRICS, ["drivers.num_drivers"])
    summary.to_csv(RESULTS / f"{tag}_summary.csv", index=False)

    notes = [
        f"Demand: `{args.slice}`. Travel: {args.travel} ({base.travel}).",
        f"Real-world benchmark (Uber, request → driver on scene): mean {observed.mean():.0f}s, "
        f"p50 {observed.median():.0f}s, p90 {observed.quantile(0.9):.0f}s.",
    ]
    text = markdown_report(summary, f"M2 — real Manhattan demand, {args.travel} travel times",
                           "immediate_greedy", "drivers.num_drivers", notes)
    gap = summary[summary["arm"].str.startswith("optimal")][
        ["drivers.num_drivers", "arm", "shadow_gap_s_per_batch", "shadow_worse_batches_frac", "batch_riders_mean"]]
    text += "\n## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)\n\n"
    text += "| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |\n|---|---|---|---|---|\n"
    for _, r in gap.iterrows():
        text += (f"| {r['drivers.num_drivers']} | {r['arm']} | {r['shadow_gap_s_per_batch']:.1f} "
                 f"| {r['shadow_worse_batches_frac'] * 100:.1f}% | {r['batch_riders_mean']:.1f} |\n")
    (RESULTS / f"{tag}_report.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
