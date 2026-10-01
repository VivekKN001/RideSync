"""Run the live simulator against Kafka. Start the matcher first (``python -m ridesync.live.matcher``).

    python -m ridesync.live.sim --speed 10                         # real Manhattan demand, 3 h, at 10x
    python -m ridesync.live.sim --speed 30 --travel osrm --compare-offline
    python -m ridesync.live.sim --speed 20 --surge reactive                  # M6: the simulator prices zones
    python -m ridesync.live.sim --speed 20 --surge forecast --price-service  # M6: ridesync.live.pricing does
    python -m ridesync.live.sim --speed 20 --reposition none --no-late-cancel  # without the M10 behaviour

Defaults are the best M2 arm: optimal matching every 30 s with the cancellation-aware cost,
500 drivers, on the TLC slice. Since M10 the run also has the matcher's repositioning plan (M7's best,
``planned`` with the demand forecast) and riders who give up on a late driver; with ``--surge``, reserve
drivers log on and idle drivers chase higher prices (M6b's medium response). At the end it prints the metrics, the live diagnostics
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

from ..env import MODELS_DIR
from ..data.slices import DEFAULT_SLICE
from ..matching import CancelBelief, CostParams
from ..routing import travel_from_calibration
from ..sim import SimConfig, simulate, summarize
from .world import LiveConfig, LiveSimulation

AWARE = CostParams(trip_value_s=900.0, cancel=CancelBelief())
# M6b's medium driver response (experiments/m6b_supply.py)
SUPPLY = {"supply.reserve_share": 0.2, "supply.log_on_elasticity": 1.0, "supply.chase_strength": 0.5}
REPORT = [
    "requests", "completed", "cancel_rate", "cancel_late_rate", "wait_all_mean_s", "wait_mean_s", "pickup_mean_s",
    "time_to_match_mean_s", "completed_per_hour", "driver_idle_frac", "batches", "batch_riders_mean",
    "solve_ms_mean", "decline_rate",
    "app_opens", "priced_out_rate", "served_rate", "mean_multiplier_paid", "revenue_per_hour", "eta_abs_error_mean_s",
    "moves_per_driver_hour", "reposition_km_per_hour", "drivers_online_mean", "reserve_logons",
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
    ap.add_argument("--surge", choices=["off", "reactive", "forecast"], default="off", help="M6 surge pricing")
    ap.add_argument("--elasticity", type=float, default=None, help="rider price elasticity (default: PricingConfig)")
    ap.add_argument("--eta-model", default=None, help="M6 ETA correction on the travel model (data/models/eta_<travel>.joblib)")
    ap.add_argument("--reposition", choices=["none", "drift", "planned"], default="planned",
                    help="M7/M10 idle-driver repositioning: planned by the matcher, or drivers drifting on their own")
    ap.add_argument("--reposition-demand", choices=["reactive", "forecast"], default="forecast",
                    help="planned: expected demand from recent app opens or the demand model (falls back to reactive "
                         "without the model or a real start time)")
    ap.add_argument("--late-cancel", action=argparse.BooleanOptionalAction, default=True,
                    help="riders give up on a driver who is late against the quoted pickup")
    ap.add_argument("--supply", action=argparse.BooleanOptionalAction, default=True,
                    help="with --surge: reserve drivers log on and idle drivers chase higher prices (M6b)")


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
    if args.surge != "off":
        o["pricing.enabled"] = True
        o["pricing.demand"] = args.surge
        if args.elasticity is not None:
            o["pricing.elasticity"] = args.elasticity
        if args.supply:
            o.update(SUPPLY)
    if args.late_cancel:
        o["riders.enroute_cancel"] = True
    o.update(_reposition(args))
    cfg = SimConfig().with_(**o)
    if args.eta_model:
        from dataclasses import replace

        cfg = cfg.with_(travel=replace(cfg.travel, eta_model=args.eta_model))  # world and matcher both
    fare = Path(f"{MODELS_DIR}/fare.json")
    if fare.exists():
        from ..ml.fare import fare_from_file

        cfg = cfg.with_(fare=fare_from_file(str(fare)))
    return cfg


def _reposition(args) -> dict:
    """Repositioning overrides, stepping down to what the local files allow (with a note)."""
    from ..sim.config import RepositionConfig

    rc = RepositionConfig()
    if args.reposition == "none":
        return {}
    missing = [p for p in (rc.zones_path, rc.points_path) if not Path(p).exists()]
    if missing:
        print(f"note: no repositioning, it needs {' and '.join(missing)}", flush=True)
        return {}
    o = {"reposition.policy": args.reposition, "reposition.demand": args.reposition_demand}
    needs_model = args.reposition == "drift" or args.reposition_demand == "forecast"
    if needs_model and (args.slice == "synthetic" or not Path(rc.forecast_path).exists()):
        if args.reposition == "drift":
            print(f"note: no repositioning, drift needs {rc.forecast_path} and a TLC slice", flush=True)
            return {}
        print("note: repositioning on recent app opens; the forecast needs the demand model and a TLC slice", flush=True)
        o["reposition.demand"] = "reactive"
    return o


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
        **{f"moves_{k}": v for k, v in sorted(sim.move_outcomes.items())},
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
    ap.add_argument("--price-service", action="store_true",
                    help="with --surge: take prices from ridesync.live.pricing (needs Flink) instead of pricing locally")
    ap.add_argument("--json", type=Path, help="write metrics and diagnostics here")
    args = ap.parse_args(argv)
    if args.speed <= 0:
        ap.error("--speed must be > 0 (lockstep mode is ridesync.live.lockstep)")

    cfg = config_from_args(args)
    live = LiveConfig(speed=args.speed, tick_s=args.tick, ping_s=args.ping,
                      price_source="service" if args.price_service else "local")
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
        print(f"{k:<24}" + "".join(f"{out[c].get(k, float('nan')):>14.4g}" for c in cols))
    print("\ndiagnostics")
    for k, v in diag.items():
        print(f"  {k:<22} {v:.4g}" if isinstance(v, float) else f"  {k:<22} {v}")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
