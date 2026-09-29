"""Train the models on the reduced TLC months and write their evaluation reports.

    python -m ridesync.ml.train demand                  # data/models/demand.joblib
    python -m ridesync.ml.train fare                    # data/models/fare.json
    python -m ridesync.ml.train eta --base straight     # data/models/eta_straight.joblib
    python -m ridesync.ml.train eta --base osrm         # needs OSRM up (one ~530 x 530 table, cached)
    python -m ridesync.ml.train all                     # demand, fare, eta straight

By default models train on 2025-01..2026-06 and are tested on 2026-07 (``--train``, ``--test``; periods
are ``YYYY-MM[-DD]:YYYY-MM[-DD]``, both ends included). The M6 setup was
``--train 2024-03-01:2024-03-21 --test 2024-03-22:2024-03-31``. Needs the months reduced first:
``python -m ridesync.data.fetch --tlc 2025-01:2026-07`` then ``python -m ridesync.data.monthly 2025-01:2026-07``.
Reports go to experiments/results/<prefix>_*_report.md (``--report``, default m8).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Optional, Sequence

from .common import DEFAULT_TEST, DEFAULT_TRAIN

RESULTS = Path("experiments/results")


def _table(rows: List[dict], cols: List[str], fmt: dict) -> List[str]:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(fmt.get(c, "{}").format(r[c]) for c in cols) + " |")
    return out


def _title(report: str) -> str:
    return report.upper()


def train_demand(train: str, test: str, max_iter: int, report: str) -> None:
    from .demand import MODEL_PATH
    from .demand import train as fit

    t0 = time.time()
    fc, rows, summary = fit(train, test, max_iter)
    fc.save(MODEL_PATH)
    lines = [f"# {_title(report)}: demand forecast (TLC, Manhattan)", "",
             f"Requests per taxi zone per 15 minutes, full scale. Train: {summary['train']}, test: {summary['test']} "
             f"(history for the lag features from {summary['history_from']}). "
             f"{summary['zones']} zones, {summary['requests']:,} requests; a zone-bucket averages "
             f"{summary['mean_per_zone_bucket']:.1f} requests ({summary['test_mean_per_zone_bucket']:.1f} in the test period).",
             "WAPE = sum |error| / sum actual. Lower is better.", ""]
    for h in sorted({r["horizon_min"] for r in rows}):
        lines += [f"## {h} minutes ahead", ""]
        lines += _table([r for r in rows if r["horizon_min"] == h], ["method", "wape", "mae"],
                        {"wape": "{:.1%}", "mae": "{:.2f}"})
        lines.append("")
    _write(f"{report}_demand_report.md", lines)
    print(f"demand: saved {MODEL_PATH} in {time.time() - t0:.0f}s")


def train_fare(train: str, test: str, report: str) -> None:
    from .fare import FARE_PATH
    from .fare import train as fit_fare

    fit = fit_fare(train, test)
    f = fit["fees"]
    lines = [f"# {_title(report)}: fare fit (TLC, Manhattan)", "",
             "Median regression of `base_passenger_fare` on trip miles and minutes, fitted on weekday 10:00-15:59 "
             f"(when Uber's and Lyft's own surge is rarest) of {fit['fit_period']} and tested on {fit['test']}. "
             "APE = |error| / fare.", "",
             f"Simulator fare: **${fit['base']:.2f} + ${fit['per_mile']:.2f}/mile + ${fit['per_min']:.2f}/minute**, "
             f"minimum ${fit['min_fare']:.2f}; straight-line to road miles x{fit['road_factor']:.2f}.", ""]
    for name, c in fit["companies"].items():
        lines.append(f"- {name}: ${c['base']:.2f} + ${c['per_mile']:.2f}/mile + ${c['per_min']:.2f}/minute, "
                     f"minimum ${c['min_fare']:.2f}")
    lines += ["", "## Test days", ""]
    lines += _table(fit["evaluation"], ["model", "test", "mae", "median_ape", "p90_ape", "bias", "n"],
                    {"mae": "${:.2f}", "median_ape": "{:.1%}", "p90_ape": "{:.1%}", "bias": "{:+.2f}", "n": "{:,}"})
    lines += ["", f"## On top of the fare ({fit['test']}, all hours, mean per trip)", "",
              f"Tolls ${f['tolls']:.2f}, Black Car Fund ${f['bcf']:.2f}, sales tax ${f['sales_tax']:.2f}, "
              f"congestion surcharge ${f['congestion_surcharge']:.2f}, congestion pricing (CBD) fee "
              f"${f['cbd_congestion_fee']:.2f} (charged on {f['cbd_charged_share']:.0%} of trips): "
              f"{f['fees_share_of_fare']:.1%} on top of the fare. "
              f"Median rider total ${f['rider_total_median']:.2f}. Taxes and fees are not platform revenue, so the "
              "simulator's revenue is fare x multiplier."]
    _write(f"{report}_fare_report.md", lines)
    print("\n".join(lines))
    print(f"fare -> {FARE_PATH}")


def train_eta(base: str, train: str, test: str, per_day: Optional[int], osrm_url: str, max_iter: int, report: str) -> None:
    import joblib

    from .eta import MODEL_PATH
    from .eta import train as fit_eta

    t0 = time.time()
    bundle, rows, extra = fit_eta(base, train, test, per_day, osrm_url, max_iter)
    path = MODEL_PATH.format(base=base)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    for name, b in bundle.pop("baselines").items():  # eta_<base>_hour.joblib, eta_<base>_zone_hour.joblib
        joblib.dump(b, MODEL_PATH.format(base=f"{base}_{name}"))
    joblib.dump(bundle, path)
    lines = [f"# {_title(report)}: ETA correction on the `{base}` base model (TLC, Manhattan trips)", "",
             f"Train: {extra['train']} ({extra['train_trips']:,} trips), test: {extra['test']} ({extra['test_trips']:,} trips). "
             "Errors are on observed pickup-to-dropoff times (`trip_time`).",
             f"Trip ends are placed on random points in their zones. Placing the same trip twice already changes "
             f"the base time by a median {extra['placement_median_ape']:.1%}: part of every error below is that, not the model.",
             f"Residual log-error sigma of the corrected model: {extra['residual_sigma']:.3f} "
             f"(robust, from the IQR: {extra['residual_iqr_sigma']:.3f}).", ""]
    lines += _table(rows, ["method", "mae_s", "mape", "median_ape", "p90_ape", "bias_s"],
                    {"mae_s": "{:.0f}", "mape": "{:.1%}", "median_ape": "{:.1%}", "p90_ape": "{:.1%}", "bias_s": "{:+.0f}"})
    lo, hi = extra["interval"]
    lines += ["", "## ETA range", "",
              f"Quantile-loss trees for the {lo:.0%} and {hi:.0%} points of the same correction give a range to quote "
              f"(\"8-11 min\"). On the test days {extra['interval_coverage']:.1%} of trips land inside it (target "
              f"{hi - lo:.0%}; {extra['interval_below']:.1%} faster, {extra['interval_above']:.1%} slower). Median width "
              f"{extra['interval_median_width_s'] / 60:.1f} min, {extra['interval_median_width_frac']:.0%} of the point ETA."]
    _write(f"{report}_eta_{base}_report.md", lines)
    print("\n".join(lines[-3:]))
    print(f"eta ({base}): saved {path} in {time.time() - t0:.0f}s")


def _write(name: str, lines: Sequence[str]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main(argv: Optional[Sequence[str]] = None) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["demand", "fare", "eta", "all"])
    ap.add_argument("--train", default=DEFAULT_TRAIN, help="training period, e.g. 2025-01:2026-06")
    ap.add_argument("--test", default=DEFAULT_TEST, help="test period, after training, e.g. 2026-07")
    ap.add_argument("--report", default="m8", help="report file prefix under experiments/results")
    ap.add_argument("--base", choices=["straight", "osrm"], default="straight", help="eta: base travel model")
    ap.add_argument("--osrm-url", default="http://localhost:5000")
    ap.add_argument("--per-day", type=int, default=None, help="eta: at most this many trips per day (default: all sampled)")
    ap.add_argument("--max-iter", type=int, default=300, help="boosting rounds")
    args = ap.parse_args(argv)
    if args.what in ("demand", "all"):
        train_demand(args.train, args.test, args.max_iter, args.report)
    if args.what in ("fare", "all"):
        train_fare(args.train, args.test, args.report)
    if args.what in ("eta", "all"):
        train_eta(args.base, args.train, args.test, args.per_day, args.osrm_url, args.max_iter, args.report)


if __name__ == "__main__":
    main()
