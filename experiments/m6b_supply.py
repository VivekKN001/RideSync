"""M6b: surge pricing when drivers respond. Does surge still only ration demand once drivers log on and chase it?

    python experiments/m6b_supply.py [--slice ...] [--fleets 300 400 500] [--seeds 6] [--tag m6b_supply]

Same setup as M6 surge (optimal every 30 s, cancellation-aware, calibrated straight-line travel, fitted fares,
rider elasticity 0.5), plus ``SimConfig.supply``: a reserve of offline drivers (20% of the fleet) who log on
when their area surges, and idle drivers who chase higher prices. No public data gives how strongly drivers
respond, so the arms vary it:

- ``no_surge``: fixed prices, fixed fleet. ``reposition``: fixed prices, M7's coordinated repositioning (moves
  drivers to forecast demand for free, where surge moves them by charging riders).
- ``surge_fixed``: M6's reactive surge with a fixed fleet (the old result).
- ``surge_logon`` / ``surge_chase``: one response at a time. ``surge_both``: both, medium.
  ``surge_strong``: both, strong. ``surge_forecast_both``: forecast-driven prices, both, medium.

Paired against ``no_surge`` (and ``surge_fixed``) at the same fleet and seed.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from ridesync.data.slices import DEFAULT_SLICE
from ridesync.env import MODELS_DIR
from ridesync.experiments import Arm, paired_summary, run_grid
from ridesync.matching import CancelBelief, CostParams
from ridesync.routing import travel_from_calibration
from ridesync.sim import SimConfig

RESULTS = Path(__file__).parent / "results"
AWARE = CostParams(trip_value_s=900.0, cancel=CancelBelief())
FLEET = "drivers.num_drivers"
METRICS = [
    "served_rate", "priced_out_rate", "cancel_rate", "wait_all_mean_s", "completed_per_hour", "revenue_per_hour",
    "mean_multiplier_paid", "surged_trip_frac", "drivers_online_mean", "earnings_per_online_hour", "reserve_logons",
    "chase_moves_per_hour", "reposition_km_per_hour",
]
SURGE = {"pricing.enabled": True, "pricing.demand": "reactive"}
RESERVE = {"supply.reserve_share": 0.2}
MEDIUM = {**RESERVE, "supply.log_on_elasticity": 1.0, "supply.chase_strength": 0.5}
STRONG = {**RESERVE, "supply.log_on_elasticity": 2.0, "supply.chase_strength": 1.0}
ARMS = [
    Arm("no_surge"),
    Arm("reposition", {"reposition.policy": "planned", "reposition.demand": "forecast"}),
    Arm("surge_fixed", SURGE),
    Arm("surge_logon", {**SURGE, **RESERVE, "supply.log_on_elasticity": 1.0}),
    Arm("surge_chase", {**SURGE, "supply.chase_strength": 0.5}),
    Arm("surge_both", {**SURGE, **MEDIUM}),
    Arm("surge_strong", {**SURGE, **STRONG}),
    Arm("surge_forecast_both", {**SURGE, "pricing.demand": "forecast", **MEDIUM}),
]


def _d(r, m, scale=1.0, digits=0):
    d = r.get(f"d_{m}")
    if d is None or d != d:
        return ""
    return f"{d * scale:+.{digits}f} ± {r[f'ci_{m}'] * scale:.{digits}f}"


def report(vs_none, vs_fixed, notes, seeds) -> str:
    lines = ["# M6b: surge pricing when drivers respond", "", *notes, "",
             f"{seeds} seeds. Deltas are paired against `no_surge` at the same fleet and seed (mean ± 95% CI, Student t "
             "over seeds); the last column against `surge_fixed`. `served` = completed trips / app opens. `online` = "
             "drivers working, on average. `earnings/h` = fares × multiplier per online driver-hour.", ""]
    for n in sorted(vs_none[FLEET].unique()):
        g = vs_none[vs_none[FLEET] == n]
        f = vs_fixed[vs_fixed[FLEET] == n].set_index("arm")
        lines += [f"## {n} drivers", "",
                  "| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult "
                  "| online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for _, r in g.iterrows():
            r = r.to_dict()
            vf = _d(f.loc[r["arm"]].to_dict(), "completed_per_hour") if r["arm"] in f.index else ""
            lines.append(
                f"| {r['arm']} | {r['served_rate'] * 100:.1f} | {_d(r, 'served_rate', 100, 1)} | "
                f"{r['priced_out_rate'] * 100:.1f} | {r['cancel_rate'] * 100:.1f} | {r['wait_all_mean_s']:.0f} | "
                f"{r['completed_per_hour']:.0f} | {_d(r, 'completed_per_hour')} | {r['mean_multiplier_paid']:.2f} | "
                f"{r['drivers_online_mean']:.0f} | {r['earnings_per_online_hour']:.1f} | {r['reserve_logons']:.0f} | "
                f"{r['chase_moves_per_hour']:.0f} | {vf} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", default=DEFAULT_SLICE)
    ap.add_argument("--fleets", type=int, nargs="+", default=[300, 400, 500])
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--elasticity", type=float, default=0.5, help="rider price elasticity")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--tag", default="m6b_supply", help="output file prefix under experiments/results")
    ap.add_argument("--resume", action="store_true",
                    help="keep the runs already in the runs CSV, run only the missing ones, save each as it finishes")
    args = ap.parse_args()

    base = SimConfig(travel=travel_from_calibration("straight")).with_(**{
        "demand.trips_path": args.slice, "demand.duration_s": 3 * 3600.0, "demand.warmup_s": 1800.0,
        "dispatch.strategy": "lsa", "dispatch.interval_s": 30.0, "dispatch.cost": AWARE, "dispatch.max_candidates": 20,
        "pricing.elasticity": args.elasticity,
    })
    fare = Path(f"{MODELS_DIR}/fare.json")
    if fare.exists():
        from ridesync.ml.fare import fare_from_file

        base = base.with_(fare=fare_from_file(str(fare)))
    if not Path(base.pricing.forecast_path).exists():
        sys.exit(f"no demand model at {base.pricing.forecast_path}: run `python -m ridesync.ml.train demand`")
    s = base.supply
    notes = [f"Demand: `{args.slice}`. Rider elasticity {args.elasticity:g}. Fares: {base.fare}.",
             f"Supply response: reserve {RESERVE['supply.reserve_share']:.0%} of the fleet, logging on with probability "
             f"1 − m^−ε at each price update (medium ε = {MEDIUM['supply.log_on_elasticity']:g}, strong "
             f"{STRONG['supply.log_on_elasticity']:g}) after a median {s.log_on_delay_s:.0f} s, off after "
             f"{s.log_off_idle_s:.0f} s idle unsurged; chasing with probability strength × price gap (medium "
             f"{MEDIUM['supply.chase_strength']:g}, strong {STRONG['supply.chase_strength']:g}) to the best price within "
             f"{s.chase_max_s:.0f} s."]

    t0 = time.time()
    RESULTS.mkdir(exist_ok=True)
    ckpt = RESULTS / f"{args.tag}_runs.csv" if args.resume else None
    df = run_grid(base, ARMS, {FLEET: args.fleets}, range(args.seeds), workers=args.workers, checkpoint=ckpt)
    print(f"{len(df)} runs in {time.time() - t0:.0f}s")
    df.to_csv(RESULTS / f"{args.tag}_runs.csv", index=False)
    vs_none = paired_summary(df, "no_surge", METRICS, [FLEET])
    vs_fixed = paired_summary(df[df["arm"] != "no_surge"], "surge_fixed", METRICS, [FLEET])
    vs_none.to_csv(RESULTS / f"{args.tag}_summary.csv", index=False)
    text = report(vs_none, vs_fixed, notes, args.seeds)
    (RESULTS / f"{args.tag}_report.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
