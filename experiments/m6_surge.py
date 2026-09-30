"""M6: surge pricing on real Manhattan demand. No surge vs reactive vs forecast-driven prices.

    python -m ridesync.ml.train demand      # the forecast arm needs data/models/demand.joblib
    python -m ridesync.ml.train fare        # optional: fitted fares (else FareConfig placeholders)
    python experiments/m6_surge.py [--fleets 300 400 500] [--elasticities 0.3 0.5 0.8] [--seeds 6]

Dispatch is the best M2 arm (optimal every 30 s, cancellation-aware cost) on the calibrated
straight-line model. The fleet is fixed, so surge can only ration demand: it cannot bring drivers.
Every arm under a seed sees the same riders and the same accept/leave/retry draws, so deltas are
paired against the no-surge arm at the same fleet and elasticity.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from ridesync.env import MODELS_DIR
from ridesync.data.slices import DEFAULT_SLICE
from ridesync.experiments import Arm, paired_summary, run_grid
from ridesync.matching import CancelBelief, CostParams
from ridesync.routing import travel_from_calibration
from ridesync.sim import SimConfig

RESULTS = Path(__file__).parent / "results"
AWARE = CostParams(trip_value_s=900.0, cancel=CancelBelief())
METRICS = [
    "app_opens", "served_rate", "priced_out_rate", "retried_rate", "cancel_rate", "wait_all_mean_s",
    "completed_per_hour", "revenue_per_hour", "surge_revenue_per_hour", "mean_multiplier_paid", "surged_trip_frac",
    "driver_idle_frac",
]
ARMS = [
    Arm("no_surge"),
    Arm("surge_reactive", {"pricing.enabled": True, "pricing.demand": "reactive"}),
    Arm("surge_forecast", {"pricing.enabled": True, "pricing.demand": "forecast"}),
]
FLEET, ELAST = "drivers.num_drivers", "pricing.elasticity"


def _d(r, m, scale=1.0, digits=0):
    d = r.get(f"d_{m}")
    if d is None or d != d:
        return ""
    return f"{d * scale:+.{digits}f} ± {r[f'ci_{m}'] * scale:.{digits}f}"


def report(s, notes) -> str:
    lines = ["# M6: surge pricing (Manhattan TLC replay)", "", *notes, "",
             "Deltas are paired against `no_surge` at the same fleet, elasticity and seed (mean ± 95% CI, Student t over seeds).",
             "`served` = completed trips / app opens. `cancel` is per request. Revenue is fare × multiplier.", ""]
    for n in sorted(s[FLEET].unique()):
        for e in sorted(s[ELAST].unique()):
            g = s[(s[FLEET] == n) & (s[ELAST] == e)]
            lines += [f"## {n} drivers, elasticity {e:g}", "",
                      "| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s "
                      "| trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |",
                      "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
            for _, r in g.iterrows():
                r = r.to_dict()
                lines.append(
                    f"| {r['arm']} | {r['served_rate'] * 100:.1f} | {_d(r, 'served_rate', 100, 1)} "
                    f"| {r['priced_out_rate'] * 100:.1f} | {r['cancel_rate'] * 100:.1f} | {_d(r, 'cancel_rate', 100, 1)} "
                    f"| {r['wait_all_mean_s']:.0f} | {_d(r, 'wait_all_mean_s')} "
                    f"| {r['completed_per_hour']:.0f} | {_d(r, 'completed_per_hour')} "
                    f"| {r['revenue_per_hour']:,.0f} | {_d(r, 'revenue_per_hour')} "
                    f"| {r['mean_multiplier_paid']:.2f} | {r['surged_trip_frac'] * 100:.0f} |")
            lines.append("")
    return "\n".join(lines) + "\n"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", default=DEFAULT_SLICE)
    ap.add_argument("--fleets", type=int, nargs="+", default=[300, 400, 500])
    ap.add_argument("--elasticities", type=float, nargs="+", default=[0.3, 0.5, 0.8])
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--tag", default=None, help="output file prefix under experiments/results (default: m6_surge)")
    ap.add_argument("--no-forecast", action="store_true", help="skip the forecast arm (no demand model yet)")
    ap.add_argument("--resume", action="store_true",
                    help="keep the runs already in the runs CSV, run only the missing ones, save each as it finishes")
    args = ap.parse_args()

    base = SimConfig(travel=travel_from_calibration("straight")).with_(**{
        "demand.trips_path": args.slice, "demand.duration_s": 3 * 3600.0, "demand.warmup_s": 1800.0,
        "dispatch.strategy": "lsa", "dispatch.interval_s": 30.0, "dispatch.cost": AWARE, "dispatch.max_candidates": 20,
    })
    notes = []
    fare = Path(f"{MODELS_DIR}/fare.json")
    if fare.exists():
        from ridesync.ml.fare import fare_from_file

        base = base.with_(fare=fare_from_file(str(fare)))
        notes.append(f"Fares fitted to TLC: {base.fare}.")
    else:
        notes.append(f"Fares are the placeholder `FareConfig` defaults ({base.fare}); run `python -m ridesync.ml.train fare`.")
    arms = [a for a in ARMS if not (args.no_forecast and a.label == "surge_forecast")]
    if any(a.label == "surge_forecast" for a in arms) and not Path(base.pricing.forecast_path).exists():
        sys.exit(f"no demand model at {base.pricing.forecast_path}: run `python -m ridesync.ml.train demand` or pass --no-forecast")
    p = base.pricing
    notes.append(f"Policy: every {p.interval_s:.0f} s, pressure = (demand over {p.horizon_s:.0f} s + waiting) / free supply, "
                 f"pooled over zones within {p.pool_radius_m:.0f} m; "
                 f"multiplier = 1 + {p.slope:g} × (pressure − {p.threshold:g}), steps of {p.step:g}, cap {p.cap:g}. "
                 f"Riders who decline leave with probability {p.leave_prob:g}, else retry once after a median "
                 f"{p.retry_median_s:.0f} s.")

    t0 = time.time()
    RESULTS.mkdir(exist_ok=True)
    ckpt = RESULTS / f"{args.tag or 'm6_surge'}_runs.csv" if args.resume else None
    df = run_grid(base, arms, {FLEET: args.fleets, ELAST: args.elasticities}, range(args.seeds), workers=args.workers,
                  checkpoint=ckpt)
    print(f"{len(df)} runs in {time.time() - t0:.0f}s")
    RESULTS.mkdir(exist_ok=True)
    tag = args.tag or "m6_surge"
    df.to_csv(RESULTS / f"{tag}_runs.csv", index=False)
    s = paired_summary(df, "no_surge", METRICS, [FLEET, ELAST])
    s.to_csv(RESULTS / f"{tag}_summary.csv", index=False)
    text = report(s, notes)
    (RESULTS / f"{tag}_report.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
