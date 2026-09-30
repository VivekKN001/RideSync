"""M1b: does a cancellation-aware cost let optimal matching beat greedy?

Every greedy arm and every optimal arm gets the same edge costs, so any gap
between them comes from the solver, not the objective.

  +aware(V)   edge cost e + V * P(cancel | e); an edge is only used if it beats waiting
              (see ridesync/matching/problem.py)
  belief      the matcher's cancellation model; "true" equals the simulator's
              population distribution (lognormal median 600 s, sigma 0.4). The
              pessimistic and optimistic arms test sensitivity to a wrong model.

    python experiments/m1b_cancel_aware.py [--seeds 8]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from ridesync.experiments import Arm, markdown_report, paired_summary, run_grid
from ridesync.matching import CancelBelief, CostParams
from ridesync.sim import SimConfig

RESULTS = Path(__file__).parent / "results"
METRICS = [
    "cancel_rate", "cancel_eta_rate", "cancel_no_match_rate", "wait_all_mean_s", "wait_mean_s",
    "pickup_mean_s", "completed_per_hour", "driver_idle_frac", "batch_riders_mean",
]
TRUE_BELIEF = CancelBelief(600.0, 0.4)


def aware(value_s: float, belief: CancelBelief = TRUE_BELIEF) -> CostParams:
    return CostParams(trip_value_s=value_s, cancel=belief)


def arm(label, strategy, interval, cost=None):
    overrides = {"dispatch.strategy": strategy, "dispatch.interval_s": float(interval)}
    if cost is not None:
        overrides["dispatch.cost"] = cost
    return Arm(label, overrides)


def build_arms(windows, values):
    arms = [arm("immediate_greedy", "fifo_greedy", 0)]
    arms += [arm(f"immediate_greedy+aware(V={v})", "fifo_greedy", 0, aware(v)) for v in values]
    for w in windows:
        arms.append(arm(f"batched_greedy@{w}s", "global_greedy", w))
        arms += [arm(f"batched_greedy@{w}s+aware(V={v})", "global_greedy", w, aware(v)) for v in values]
        arms.append(arm(f"optimal@{w}s", "lsa", w))
        arms += [arm(f"optimal@{w}s+aware(V={v})", "lsa", w, aware(v)) for v in values]
    v = values[-1]
    arms.append(arm(f"optimal@10s+aware(V={v}) belief=pessimistic(400s)", "lsa", 10, aware(v, CancelBelief(400.0, 0.4))))
    arms.append(arm(f"optimal@10s+aware(V={v}) belief=optimistic(900s)", "lsa", 10, aware(v, CancelBelief(900.0, 0.4))))
    return arms


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--resume", action="store_true",
                    help="keep the runs already in the runs CSV, run only the missing ones, save each as it finishes")
    args = ap.parse_args()

    windows, values, fleets = [5, 10, 30], [900.0, 1500.0], [250, 300, 350, 400]
    t0 = time.time()
    RESULTS.mkdir(exist_ok=True)
    df = run_grid(SimConfig(), build_arms(windows, values), {"drivers.num_drivers": fleets}, range(args.seeds),
                  checkpoint=RESULTS / "m1b_runs.csv" if args.resume else None)
    print(f"{len(df)} runs in {time.time() - t0:.0f}s")

    RESULTS.mkdir(exist_ok=True)
    df.to_csv(RESULTS / "m1b_runs.csv", index=False)
    summary = paired_summary(df, "immediate_greedy", METRICS, ["drivers.num_drivers"])
    summary.to_csv(RESULTS / "m1b_summary.csv", index=False)
    text = markdown_report(summary, "M1b — cancellation-aware cost", "immediate_greedy", "drivers.num_drivers")
    (RESULTS / "m1b_report.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
