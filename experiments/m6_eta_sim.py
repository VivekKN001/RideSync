"""M6: does a better ETA model help dispatch? The matcher's belief vs the world's truth.

    python -m ridesync.ml.train eta --base straight
    python experiments/m6_eta_sim.py [--base straight|osrm] [--drivers 400] [--seeds 6]
    python experiments/m6_eta_sim.py --late-tolerance 120 180 300   # riders also give up on late drivers

The world drives with the learned correction on top of the calibrated base, plus per-trip lognormal
noise (sigma from the model's own test residuals unless --noise is given). That is our best
estimate of real Manhattan driving, and it is also the model under test: the experiment measures how
much a matcher loses by not knowing where and when the roads are slow, assuming the correction is
right. It is not an independent test of the correction; the accuracy tables in
m6_eta_<base>_report.md are.

Arms (same world, same seeds):
- ``global_multiplier``: the matcher uses the calibrated base (one speed or multiplier for the city).
- ``hour_table`` / ``zone_hour_table`` / ``dist_hour_table``: the base times a lookup of the median
  correction by hour of day, by pickup zone and hour, or by distance band and hour (trained with the ETA
  model). The simple beliefs a platform would build first. ``dist_hour_table`` knows that short drives
  are slower per km, which matters for pickups; it is the fair baseline for the learned model.
- ``learned_eta``: the matcher uses the corrected model (noise-free).
Deltas are reported against ``global_multiplier`` and against ``dist_hour_table``.

Read the cancellation column with care. Riders cancel when the *quoted* ETA is too long, but never
while the driver is on the way (``RiderBehavior``). An optimistic quote is therefore never punished:
the rider accepts, then simply waits longer. A matcher with honest ETAs can show *more* cancellations
for that reason alone. Quote accuracy (|ETA error|, late > 2 min) is the fair comparison.

``--late-tolerance`` turns on ``riders.enroute_cancel``: a rider whose driver hasn't arrived by the quote
plus a lognormal tolerance (the given medians) cancels, so an optimistic quote now costs something. It
writes ``m6_eta_sim_<base>_late_report.md``.
"""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import replace
from pathlib import Path

import pandas as pd

from ridesync.data.slices import DEFAULT_SLICE
from ridesync.experiments import Arm, paired_summary, run_grid
from ridesync.matching import CancelBelief, CostParams
from ridesync.ml.eta import MODEL_PATH, load_bundle
from ridesync.routing import travel_from_calibration
from ridesync.sim import SimConfig

RESULTS = Path(__file__).parent / "results"
TOL = "riders.lateness_tolerance_median_s"
AWARE = CostParams(trip_value_s=900.0, cancel=CancelBelief())
METRICS = ["eta_abs_error_mean_s", "eta_error_mean_s", "eta_late_2min_frac", "cancel_rate", "cancel_eta_rate",
           "cancel_late_rate", "wait_all_mean_s", "pickup_mean_s", "completed_per_hour", "driver_idle_frac"]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", choices=["straight", "osrm"], default="straight")
    ap.add_argument("--osrm-url", default="http://localhost:5000")
    ap.add_argument("--slice", default=DEFAULT_SLICE)
    ap.add_argument("--drivers", type=int, nargs="+", default=[400])
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--noise", type=float, default=None, help="world noise sigma (default: model residual, robust)")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--tag", default=None, help="output file prefix under experiments/results (default: m6_eta_sim)")
    ap.add_argument("--late-tolerance", type=float, nargs="*", default=[],
                    help="median lateness tolerances (s); turns on riders.enroute_cancel")
    args = ap.parse_args()

    model_path = MODEL_PATH.format(base=args.base)
    if not Path(model_path).exists():
        sys.exit(f"no ETA model at {model_path}: run `python -m ridesync.ml.train eta --base {args.base}`")
    bundle = load_bundle(model_path)
    sigma = args.noise if args.noise is not None else bundle["residual_iqr_sigma"]

    base_travel = travel_from_calibration(args.base, args.osrm_url)
    world = replace(base_travel, eta_model=model_path, noise_sigma=sigma)
    base = SimConfig(travel=world).with_(**{
        "demand.trips_path": args.slice, "demand.duration_s": 3 * 3600.0, "demand.warmup_s": 1800.0,
        "dispatch.strategy": "lsa", "dispatch.interval_s": 30.0, "dispatch.cost": AWARE, "dispatch.max_candidates": 20,
    })
    grid = {"drivers.num_drivers": args.drivers}
    suffix = ""
    if args.late_tolerance:
        base = base.with_(**{"riders.enroute_cancel": True})
        grid[TOL] = args.late_tolerance
        suffix = "_late"
    tables = {name: MODEL_PATH.format(base=f"{args.base}_{name}") for name in ("hour", "zone_hour", "dist_hour")}
    missing = [p for p in tables.values() if not Path(p).exists()]
    if missing:
        sys.exit(f"no lookup baselines at {missing}: retrain with `python -m ridesync.ml.train eta --base {args.base}`")
    arms = [
        Arm("global_multiplier", {"belief": base_travel}),
        Arm("hour_table", {"belief": replace(base_travel, eta_model=tables["hour"])}),
        Arm("zone_hour_table", {"belief": replace(base_travel, eta_model=tables["zone_hour"])}),
        Arm("dist_hour_table", {"belief": replace(base_travel, eta_model=tables["dist_hour"])}),
        Arm("learned_eta", {"belief": replace(base_travel, eta_model=model_path)}),
    ]
    t0 = time.time()
    df = run_grid(base, arms, grid, range(args.seeds), workers=args.workers)
    print(f"{len(df)} runs in {time.time() - t0:.0f}s")
    RESULTS.mkdir(exist_ok=True)
    tag = args.tag or "m6_eta_sim"
    df.to_csv(RESULTS / f"{tag}_{args.base}{suffix}_runs.csv", index=False)
    summaries = {b: paired_summary(df, b, METRICS, list(grid)) for b in ("global_multiplier", "dist_hour_table")}

    def d(r, m, scale=1.0, digits=0):
        v = r.get(f"d_{m}")
        return "" if v is None or v != v else f"{v * scale:+.{digits}f} ± {r[f'ci_{m}'] * scale:.{digits}f}"

    lines = [f"# {tag.split('_')[0].upper()}: matcher ETA belief vs world truth (`{args.base}` base, `{Path(args.slice).name}`)", "",
             f"World: calibrated `{args.base}` × learned correction × lognormal noise (sigma {sigma:.3f}). "
             "Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI) against the arm named in each "
             "table's heading.",
             "`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than "
             "2 min later than quoted.",
             ("Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, "
              "sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over "
              "completed pickups only." if suffix else
              "Caveat: simulated riders cancel on a long *quote* but never while the driver is en route, so an "
              "optimistic belief is not punished for being late. More cancellations under honest ETAs can be that "
              "artifact alone; compare quote accuracy first."), ""]
    s0 = summaries["global_multiplier"]
    for pt in s0[list(grid)].drop_duplicates().to_dict("records"):
        title = f"{pt['drivers.num_drivers']} drivers" + (f", lateness tolerance median {pt[TOL]:.0f} s" if suffix else "")
        for baseline, s in summaries.items():
            g = s[(s[list(grid)] == pd.Series(pt)).all(axis=1)]
            lines += [f"## {title}: against `{baseline}`", "",
                      "| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % "
                      "| wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |",
                      "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
            for _, r in g.iterrows():
                r = r.to_dict()
                lines.append(
                    f"| {r['arm']} | {r['eta_abs_error_mean_s']:.0f} | {d(r, 'eta_abs_error_mean_s')} | {r['eta_error_mean_s']:+.0f} "
                    f"| {r['eta_late_2min_frac'] * 100:.1f} | {r['cancel_rate'] * 100:.1f} | {d(r, 'cancel_rate', 100, 1)} "
                    f"| {r['cancel_late_rate'] * 100:.1f} | {r['wait_all_mean_s']:.0f} | {d(r, 'wait_all_mean_s')} "
                    f"| {r['pickup_mean_s']:.0f} | {r['completed_per_hour']:.0f} | {d(r, 'completed_per_hour')} |")
            lines.append("")
    text = "\n".join(lines) + "\n"
    (RESULTS / f"{tag}_{args.base}{suffix}_report.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
