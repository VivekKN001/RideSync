"""Run the live simulator against Kafka. Start the matcher first (``python -m ridesync.live.matcher``).

    python -m ridesync.live.sim --speed 10                         # real Manhattan demand, 3 h, at 10x
    python -m ridesync.live.sim --speed 30 --travel osrm --compare-offline

Defaults are the best M2 arm: optimal matching every 30 s with the cancellation-aware cost,
500 drivers, on the TLC slice. At the end it prints the metrics, the live diagnostics
(offer round-trip in simulated seconds, rejected offers, lag behind the wall clock) and,
with ``--compare-offline``, the offline simulator's metrics for the same config and seed.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict

import numpy as np

from ..matching import CancelBelief, CostParams
from ..routing import travel_from_calibration
from ..sim import SimConfig, simulate, summarize
from .world import LiveConfig, LiveSimulation

DEFAULT_SLICE = "data/processed/trips_2024-03-13_1700_3h_manhattan_f0.1.parquet"
AWARE = CostParams(trip_value_s=900.0, cancel=CancelBelief())
REPORT = [
    "requests", "completed", "cancel_rate", "wait_all_mean_s", "wait_mean_s", "pickup_mean_s",
    "time_to_match_mean_s", "completed_per_hour", "driver_idle_frac", "batches", "batch_riders_mean",
    "solve_ms_mean", "decline_rate",
]


def add_args(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--slice", default=DEFAULT_SLICE, help="TLC demand slice; 'synthetic' for the synthetic city")
    ap.add_argument("--drivers", type=int, default=500)
    ap.add_argument("--strategy", default="lsa")
    ap.add_argument("--interval", type=float, default=30.0, help="batch interval, simulated seconds")
    ap.add_argument("--cost", choices=["aware", "plain"], default="aware")
    ap.add_argument("--travel", choices=["straight", "osrm"], default="straight")
    ap.add_argument("--osrm-url", default="http://localhost:5000")
    ap.add_argument("--hours", type=float, default=3.0)
    ap.add_argument("--warmup-min", type=float, default=30.0)
    ap.add_argument("--seed", type=int, default=0)


def config_from_args(args) -> SimConfig:
    o = {
        "seed": args.seed,
        "travel": travel_from_calibration(args.travel, args.osrm_url),
        "demand.duration_s": args.hours * 3600.0,
        "demand.warmup_s": args.warmup_min * 60.0,
        "drivers.num_drivers": args.drivers,
        "dispatch.strategy": args.strategy,
        "dispatch.interval_s": args.interval,
        "dispatch.max_candidates": 20,
    }
    if args.cost == "aware":
        o["dispatch.cost"] = AWARE
    if args.slice != "synthetic":
        o["demand.trips_path"] = args.slice
    return SimConfig().with_(**o)


def diagnostics(sim: LiveSimulation, wall_s: float) -> Dict[str, float]:
    delay = np.array(sim.offer_delay_s)
    tick_ms, transit_ms = np.array(sim.tick_to_batch_ms), np.array(sim.offer_transit_ms)
    pct = lambda x, q: float(np.percentile(x, q)) if x.size else float("nan")  # noqa: E731
    offers = sum(sim.outcomes.values())
    rejected = sum(v for k, v in sim.outcomes.items() if k.startswith("rejected"))
    return {
        "wall_s": wall_s,
        "offers_received": offers,
        "offer_delay_mean_s": float(delay.mean()) if delay.size else float("nan"),
        "offer_delay_p99_s": float(np.percentile(delay, 99)) if delay.size else float("nan"),
        "offer_delay_max_s": float(delay.max()) if delay.size else float("nan"),
        "tick_to_batch_ms_p50": pct(tick_ms, 50),
        "tick_to_batch_ms_p99": pct(tick_ms, 99),
        "offer_transit_ms_p50": pct(transit_ms, 50),
        "offer_transit_ms_p99": pct(transit_ms, 99),
        "rejected_frac": rejected / offers if offers else 0.0,
        **{f"n_{k}": v for k, v in sorted(sim.outcomes.items())},
        "max_lag_s": sim.max_lag_s,
    }


def run_live(cfg: SimConfig, live: LiveConfig, bootstrap: str, prefix: str = "") -> tuple:
    from .kafka_bus import KafkaBus
    from .topics import ensure_topics

    ensure_topics(bootstrap, prefix=prefix)
    sim = LiveSimulation(cfg, KafkaBus(bootstrap, prefix), live)
    t0 = time.monotonic()
    sim.run()
    return sim, summarize(sim), diagnostics(sim, time.monotonic() - t0)


def main(argv=None) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_args(ap)
    ap.add_argument("--speed", type=float, default=10.0, help="simulated seconds per wall second")
    ap.add_argument("--tick", type=float, default=1.0, help="watermark interval, simulated seconds")
    ap.add_argument("--ping", type=float, default=5.0, help="driver location ping interval; 0 = off")
    ap.add_argument("--bootstrap", default="localhost:9092")
    ap.add_argument("--prefix", default="", help="topic name prefix; must match the matcher's")
    ap.add_argument("--compare-offline", action="store_true")
    ap.add_argument("--json", type=Path, help="write metrics and diagnostics here")
    args = ap.parse_args(argv)
    if args.speed <= 0:
        ap.error("--speed must be > 0 (lockstep mode is ridesync.live.lockstep)")

    cfg = config_from_args(args)
    live = LiveConfig(speed=args.speed, tick_s=args.tick, ping_s=args.ping)
    hours = cfg.demand.duration_s / 3600
    print(f"live run: {hours:g} h of demand at {args.speed:g}x -> about {hours * 60 / args.speed:.0f} min wall "
          f"(plus the tail until the last trip ends)", flush=True)
    sim, metrics, diag = run_live(cfg, live, args.bootstrap, args.prefix)
    out = {"run": sim.run_id, "live": metrics, "diagnostics": diag}
    if args.compare_offline:
        out["offline"] = summarize(simulate(cfg))

    print(f"\nrun {sim.run_id}")
    cols = ["live"] + (["offline"] if args.compare_offline else [])
    print(f"{'metric':<24}" + "".join(f"{c:>14}" for c in cols))
    for k in REPORT:
        print(f"{k:<24}" + "".join(f"{out[c][k]:>14.4g}" for c in cols))
    print("\ndiagnostics")
    for k, v in diag.items():
        print(f"  {k:<22} {v:.4g}" if isinstance(v, float) else f"  {k:<22} {v}")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
