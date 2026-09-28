"""Train the M6 models on TLC March 2024 and write their evaluation reports.

    python -m ridesync.ml.train demand                  # ~1-2 min: data/models/demand.joblib
    python -m ridesync.ml.train fare                    # ~1 min:   data/models/fare.json
    python -m ridesync.ml.train eta --base straight     # ~2-4 min: data/models/eta_straight.joblib
    python -m ridesync.ml.train eta --base osrm         # needs OSRM up (one ~530 x 530 table, cached)
    python -m ridesync.ml.train all                     # demand, fare, eta straight

Reports go to experiments/results/m6_*_report.md. Needs data/raw/fhvhv_tripdata_<month>.parquet
(``python -m ridesync.data.fetch --tlc 2024-03``) and data/raw/taxi_zones.zip.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Optional, Sequence

RESULTS = Path("experiments/results")


def _table(rows: List[dict], cols: List[str], fmt: dict) -> List[str]:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(fmt.get(c, "{}").format(r[c]) for c in cols) + " |")
    return out


def train_demand(month: str, max_iter: int) -> None:
    from .demand import MODEL_PATH, train

    t0 = time.time()
    fc, rows, summary = train(month, max_iter)
    fc.save(MODEL_PATH)
    lines = [f"# M6: demand forecast (TLC {month}, Manhattan)", "",
             f"Requests per taxi zone per 15 minutes, full scale. Train: days 1-21, test: days 22-31. "
             f"{summary['zones']} zones, {summary['requests']:,} requests; a zone-bucket averages "
             f"{summary['mean_per_zone_bucket']:.1f} requests ({summary['test_mean_per_zone_bucket']:.1f} on test days).",
             "WAPE = sum |error| / sum actual. Lower is better.", ""]
    for h in sorted({r["horizon_min"] for r in rows}):
        lines += [f"## {h} minutes ahead", ""]
        lines += _table([r for r in rows if r["horizon_min"] == h], ["method", "wape", "mae"],
                        {"wape": "{:.1%}", "mae": "{:.2f}"})
        lines.append("")
    _write("m6_demand_report.md", lines)
    print(f"demand: saved {MODEL_PATH} in {time.time() - t0:.0f}s")


def train_fare(month: str) -> None:
    from .fare import FARE_PATH, train

    fit = train(month)
    lines = [f"# M6: fare fit (TLC {month}, Manhattan, weekday 10:00-15:59)", "",
             "Median regression of `base_passenger_fare` on trip miles and minutes.", "", "```",
             json.dumps(fit, indent=2), "```"]
    _write("m6_fare_report.md", lines)
    print(f"fare: {fit} -> {FARE_PATH}")


def train_eta(base: str, month: str, per_day: int, osrm_url: str, max_iter: int) -> None:
    import joblib

    from .eta import MODEL_PATH, train

    t0 = time.time()
    bundle, rows, extra = train(base, month, per_day, osrm_url, max_iter)
    path = MODEL_PATH.format(base=base)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path)
    lines = [f"# M6: ETA correction on the `{base}` base model (TLC {month}, Manhattan trips)", "",
             f"Train: days 1-21 ({extra['train_trips']:,} trips), test: days 22-31 ({extra['test_trips']:,} trips). "
             "Errors are on observed pickup-to-dropoff times (`trip_time`).",
             f"Trip ends are placed on random points in their zones. Placing the same trip twice already changes "
             f"the base time by a median {extra['placement_median_ape']:.1%}: part of every error below is that, not the model.",
             f"Residual log-error sigma of the corrected model: {extra['residual_sigma']:.3f} "
             f"(robust, from the IQR: {extra['residual_iqr_sigma']:.3f}).", ""]
    lines += _table(rows, ["method", "mae_s", "mape", "median_ape", "p90_ape", "bias_s"],
                    {"mae_s": "{:.0f}", "mape": "{:.1%}", "median_ape": "{:.1%}", "p90_ape": "{:.1%}", "bias_s": "{:+.0f}"})
    _write(f"m6_eta_{base}_report.md", lines)
    print(f"eta ({base}): saved {path} in {time.time() - t0:.0f}s")


def _write(name: str, lines: Sequence[str]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main(argv: Optional[Sequence[str]] = None) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["demand", "fare", "eta", "all"])
    ap.add_argument("--month", default="2024-03")
    ap.add_argument("--base", choices=["straight", "osrm"], default="straight", help="eta: base travel model")
    ap.add_argument("--osrm-url", default="http://localhost:5000")
    ap.add_argument("--per-day", type=int, default=20000, help="eta: trips sampled per day")
    ap.add_argument("--max-iter", type=int, default=300, help="boosting rounds")
    args = ap.parse_args(argv)
    if args.what in ("demand", "all"):
        train_demand(args.month, args.max_iter)
    if args.what in ("fare", "all"):
        train_fare(args.month)
    if args.what in ("eta", "all"):
        train_eta(args.base, args.month, args.per_day, args.osrm_url, args.max_iter)


if __name__ == "__main__":
    main()
