"""M1c: how much better is the optimal batch solution than greedy on the *same* batch?

The live system dispatches with the optimal solver. Each batch is also solved
by a shadow greedy strategy that is never acted on, which isolates solver
quality from its knock-on effects on the fleet.

    python experiments/m1c_batch_gap.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from ridesync.experiments import Arm, run_grid
from ridesync.matching import CancelBelief, CostParams
from ridesync.sim import SimConfig

RESULTS = Path(__file__).parent / "results"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    arms = []
    for shadow in ("global_greedy", "fifo_greedy"):
        for label, cost in (("plain", CostParams()), ("aware(V=900)", CostParams(trip_value_s=900, cancel=CancelBelief()))):
            arms.append(Arm(f"optimal@10s {label} vs {shadow}", {
                "dispatch.strategy": "lsa", "dispatch.interval_s": 10.0,
                "dispatch.shadow_strategy": shadow, "dispatch.cost": cost,
            }))
    df = run_grid(SimConfig(), arms, {"drivers.num_drivers": [250, 300, 350, 400]}, range(4))
    cols = ["shadow_gap_s_per_batch", "shadow_gap_frac", "shadow_worse_batches_frac", "batch_riders_mean"]
    table = df.groupby(["drivers.num_drivers", "arm"], sort=False)[cols].mean().reset_index()
    RESULTS.mkdir(exist_ok=True)
    lines = ["# M1c — per-batch optimality gap (greedy objective − optimal objective)", "",
             "| drivers | arm | gap s / batch | gap % of objective | batches where greedy is worse | riders / batch |",
             "|---|---|---|---|---|---|"]
    for _, r in table.iterrows():
        lines.append(f"| {r['drivers.num_drivers']} | {r['arm']} | {r['shadow_gap_s_per_batch']:.1f} "
                     f"| {r['shadow_gap_frac']*100:.2f} | {r['shadow_worse_batches_frac']*100:.1f}% | {r['batch_riders_mean']:.1f} |")
    text = "\n".join(lines) + "\n"
    (RESULTS / "m1c_report.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
