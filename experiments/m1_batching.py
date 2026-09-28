"""M1: when does batched optimal matching beat greedy?

Arms:
  immediate_greedy     nearest free driver for each rider, dispatched on every event
  batched_greedy@W     cheapest-edge-first greedy over a W-second batch
  optimal@W/λ=L        optimal batch assignment (JV solver; tests show it equals our Hungarian)
                       with wait weight L in the unmatched-rider cost

Swept over fleet size (supply/demand density) with paired seeds.

    python experiments/m1_batching.py [--seeds 8] [--quick]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from ridesync.experiments import Arm, markdown_report, paired_summary, run_grid
from ridesync.matching import CostParams
from ridesync.sim import SimConfig

RESULTS = Path(__file__).parent / "results"
METRICS = [
    "cancel_rate", "wait_all_mean_s", "wait_mean_s", "wait_p90_s", "pickup_mean_s",
    "completed_per_hour", "driver_idle_frac", "driver_enroute_frac", "batch_riders_mean",
]


def arms(windows, lambdas):
    out = [Arm("immediate_greedy", {"dispatch.strategy": "fifo_greedy", "dispatch.interval_s": 0.0})]
    for w in windows:
        out.append(Arm(f"batched_greedy@{w}s", {"dispatch.strategy": "global_greedy", "dispatch.interval_s": float(w)}))
    for w in windows:
        for lam in lambdas:
            out.append(Arm(f"optimal@{w}s/λ={lam}", {
                "dispatch.strategy": "lsa",
                "dispatch.interval_s": float(w),
                "dispatch.cost": CostParams(wait_weight=lam),
            }))
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # the report uses Δ and λ; Windows consoles default to cp1252
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--quick", action="store_true", help="small grid for a smoke run")
    args = ap.parse_args()

    if args.quick:
        windows, lambdas, fleets, seeds = [5, 20], [0.0, 1.0], [250, 350], range(3)
    else:
        windows, lambdas, fleets, seeds = [2, 5, 10, 20, 30], [0.0, 1.0], [250, 300, 350, 400, 450], range(args.seeds)

    t0 = time.time()
    df = run_grid(SimConfig(), arms(windows, lambdas), {"drivers.num_drivers": fleets}, seeds)
    print(f"{len(df)} runs in {time.time() - t0:.0f}s")

    RESULTS.mkdir(exist_ok=True)
    df.to_csv(RESULTS / "m1_runs.csv", index=False)
    summary = paired_summary(df, "immediate_greedy", METRICS, ["drivers.num_drivers"])
    summary.to_csv(RESULTS / "m1_summary.csv", index=False)
    text = markdown_report(summary, "M1 — batched optimal vs greedy dispatch", "immediate_greedy", "drivers.num_drivers")
    (RESULTS / "m1_report.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
