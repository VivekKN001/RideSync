"""M8: does more data, or more recent data, predict July 2026 better?

Every arm trains the same models with the same features and settings; only the training period
differs. All are tested on July 2026.

    mar2024        2024-03             the month the M6 models were trained on
    jun2026        2026-06             the last month before the test
    18mo           2025-01..2026-06    since NYC congestion pricing began (the M8 default)
    18mo_1mo_rows  18mo, subsampled to jun2026's number of rows: span without the volume
    30mo           2024-01..2026-06    everything, including the year before congestion pricing

Demand: requests per zone per 15 minutes, 15 and 60 minutes ahead (WAPE). The count history for the
lag features is always real, so every arm forecasts July from the same recent counts.
ETA: the learned correction with live traffic on the straight-line base (MAE, median APE).

    python experiments/m8_compare.py            # needs data/monthly for 2024-01..2026-07
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

from ridesync.ml.common import Period, load_counts, load_table, service_zones
from ridesync.ml.demand import buckets_of, evaluate, fit
from ridesync.ml.eta import FACTOR_CLIP, _errors, _fit, base_matrix, place_trips, zone_points
from ridesync.routing import make_travel_model, travel_from_calibration

RESULTS = Path(__file__).parent / "results"
TEST = "2026-07"
ARMS = {"mar2024": "2024-03", "jun2026": "2026-06", "18mo": "2025-01:2026-06",
        "18mo_1mo_rows": "2025-01:2026-06", "30mo": "2024-01:2026-06"}
SMALL, SMALL_LIKE = "18mo_1mo_rows", "jun2026"


def demand(max_iter: int, seed: int) -> list:
    zones = service_zones()
    te = Period.parse(TEST)
    C, origin = load_counts(Period.parse(f"2024-01:{TEST}").months(), zones)
    origin = origin.to_pydatetime()
    test_b = buckets_of(te, origin)
    rng = np.random.default_rng(seed)
    rows = []
    for arm, spec in ARMS.items():
        t0 = time.time()
        train_b = buckets_of(Period.parse(spec), origin)
        if arm == SMALL:
            n = len(buckets_of(Period.parse(ARMS[SMALL_LIKE]), origin))
            train_b = np.sort(rng.choice(train_b, n, replace=False))
        models = fit(C, origin, train_b, horizons=(1, 4), max_iter=max_iter)
        for r in evaluate(models, C, origin, train_b, test_b, baselines=(arm == "18mo"), label="model"):
            rows.append({"arm": arm if r["method"] == "model" else f"baseline: {r['method']}",
                         "train_rows": len(train_b) * C.shape[0], **r})
        print(f"demand {arm}: {time.time() - t0:.0f}s", flush=True)
    return rows


def eta(max_iter: int, seed: int) -> list:
    zones = service_zones()
    tcfg = travel_from_calibration("straight")
    pts = zone_points(zones)
    sig = f"{tcfg.speed_mps:.4f}_{tcfg.detour:.2f}"
    P = base_matrix(pts[["lat", "lon"]].to_numpy(), make_travel_model(tcfg), cache=f"data/models/pool_straight_{sig}.npy")
    trips = load_table(Period.parse(f"2024-01:{TEST}").months(), "eta")
    s = place_trips(trips, pts, P, zones, np.zeros(len(trips), bool), seed)
    t = trips["request_datetime"]
    ok = np.isfinite(s.base_s) & (s.base_s > 30) & ~np.isnan(s.pu_idx) & ~np.isnan(s.do_idx)
    te = ok & Period.parse(TEST).mask(t).to_numpy()
    y = np.log(s.observed_s / s.base_s)
    obs, base = s.observed_s[te], s.base_s[te]
    rows = [{"arm": "baseline: base model alone", "train_rows": 0, **_errors(obs, base)}]
    rng = np.random.default_rng(seed)
    n_small = int((ok & Period.parse(ARMS[SMALL_LIKE]).mask(t).to_numpy()).sum())
    for arm, spec in ARMS.items():
        t0 = time.time()
        tr = ok & Period.parse(spec).mask(t).to_numpy()
        if arm == SMALL:
            keep = np.zeros_like(tr)
            keep[rng.choice(np.flatnonzero(tr), n_small, replace=False)] = True
            tr = keep
        model = _fit(s.X(tr), y[tr], max_iter)
        pred = base * np.clip(np.exp(model.predict(s.X(te))), *FACTOR_CLIP)
        rows.append({"arm": arm, "train_rows": int(tr.sum()), **_errors(obs, pred)})
        print(f"eta {arm}: {time.time() - t0:.0f}s", flush=True)
    return rows


def main(argv=None) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--max-iter", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)
    d, e = demand(args.max_iter, args.seed), eta(args.max_iter, args.seed)

    lines = ["# M8: which training data predicts July 2026 best?", "",
             "Same models, features and settings in every arm; only the training period differs. "
             "All tested on July 2026 (Manhattan, TLC high-volume FHV). "
             "`18mo_1mo_rows` is the 18 months cut down to June 2026's number of rows: the span without the volume.", ""]
    for h in (15, 60):
        lines += [f"## Demand, {h} minutes ahead (requests per zone per 15 min)", "",
                  "| arm | training rows | WAPE | MAE |", "|---|---|---|---|"]
        for r in [r for r in d if r["horizon_min"] == h]:
            rows = f"{r['train_rows']:,}" if not r["arm"].startswith("baseline") else ""
            lines.append(f"| {r['arm']} | {rows} | {r['wape']:.2%} | {r['mae']:.2f} |")
        lines.append("")
    lines += ["## ETA correction (straight-line base, live traffic), trip time pickup to dropoff", "",
              "| arm | training trips | MAE s | median APE | p90 APE | bias s |", "|---|---|---|---|---|---|"]
    for r in e:
        n = f"{r['train_rows']:,}" if r["train_rows"] else ""
        lines.append(f"| {r['arm']} | {n} | {r['mae_s']:.0f} | {r['median_ape']:.1%} | {r['p90_ape']:.1%} | {r['bias_s']:+.0f} |")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "m8_compare_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
