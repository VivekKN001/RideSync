"""M3: what does going live cost? The same dispatch config offline, in lockstep, and over Kafka.

    docker compose up -d kafka
    python experiments/m3_live_vs_offline.py                    # speeds 10x 30x 60x, 2 seeds
    python experiments/m3_live_vs_offline.py --speeds 30 --seeds 1 --hours 1
    python experiments/m3_live_vs_offline.py --resume          # after an interruption
    python experiments/m3_live_vs_offline.py --m10 --speeds 10 30   # M10: with the matcher's repositioning plan

For every seed:
- offline: the discrete-event simulator (``simulate``)
- lockstep: live code over an in-memory bus with zero latency. Must be identical to offline
  (the script checks it), so any live-vs-offline difference comes from latency alone.
- live @ speed: the simulator and a matcher *process* talking over Kafka, paced at N simulated
  seconds per wall second. A wall-clock delay d costs d * N simulated seconds, so higher speeds
  magnify latency. Real deployment is 1x.

Each live run gets fresh topics (prefix ``m3exp.``, recreated), so the matcher never replays old runs.

``--m10`` adds what M10 brought live: the matcher's repositioning plan (forecast demand), riders who give up on a
late driver, and M7's noisy travel times (so drivers are late sometimes). Reports go to ``m10_live_*``.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

from ridesync.live.lockstep import run_lockstep
from ridesync.live.sim import AWARE, DEFAULT_SLICE, run_live
from ridesync.live.topics import ensure_topics
from ridesync.live.world import LiveConfig
from ridesync.routing import travel_from_calibration
from ridesync.sim import SimConfig, simulate, summarize

RESULTS = Path(__file__).parent / "results"
PREFIX = "m3exp."
METRICS = ["cancel_rate", "wait_all_mean_s", "wait_mean_s", "pickup_mean_s", "time_to_match_mean_s",
           "completed_per_hour", "driver_idle_frac", "batches", "batch_riders_mean"]
M10_METRICS = ["cancel_late_rate", "moves_per_driver_hour"]
NOISE = 0.27  # M7's world noise on travel times (experiments/m7_reposition.py)
DIAG = ["offer_delay_mean_s", "offer_delay_p99_s", "offer_transit_ms_p50", "offer_transit_ms_p99",
        "tick_to_batch_ms_p50", "tick_to_batch_ms_p99", "rejected_frac", "max_lag_s", "wall_s"]


def start_matcher(bootstrap: str) -> subprocess.Popen:
    proc = subprocess.Popen(
        [sys.executable, "-u", "-m", "ridesync.live.matcher", "--bootstrap", bootstrap, "--prefix", PREFIX,
         "--exit-after-run", "--log-every", "60"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
    )
    for line in proc.stdout:  # wait until it has caught up (empty topics: immediately)
        if "ready" in line:
            return proc
    raise RuntimeError("matcher exited before becoming ready")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--speeds", type=float, nargs="+", default=[10.0, 30.0, 60.0])
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--hours", type=float, default=3.0)
    ap.add_argument("--drivers", type=int, default=500)
    ap.add_argument("--interval", type=float, default=30.0)
    ap.add_argument("--travel", choices=["straight", "osrm"], default="straight")
    ap.add_argument("--slice", default=DEFAULT_SLICE)
    ap.add_argument("--bootstrap", default="localhost:9092")
    ap.add_argument("--resume", action="store_true", help="skip runs already saved in the runs CSV")
    ap.add_argument("--m10", action="store_true", help="planned repositioning, late cancels and noisy travel (M10)")
    args = ap.parse_args()

    base = SimConfig(travel=travel_from_calibration(args.travel)).with_(**{
        "demand.trips_path": args.slice,
        "demand.duration_s": args.hours * 3600.0,
        "demand.warmup_s": 1800.0,
        "drivers.num_drivers": args.drivers,
        "dispatch.strategy": "lsa",
        "dispatch.interval_s": args.interval,
        "dispatch.cost": AWARE,
        "dispatch.max_candidates": 20,
    })
    if args.m10:
        base = base.with_(**{"reposition.policy": "planned", "reposition.demand": "forecast",
                             "riders.enroute_cancel": True, "travel.noise_sigma": NOISE})

    RESULTS.mkdir(exist_ok=True)
    tag = f"m10_live_{args.travel}" if args.m10 else f"m3_{args.travel}"
    runs_csv = RESULTS / f"{tag}_runs.csv"
    # Every finished run is saved at once; --resume skips runs already in the CSV (a live seed takes ~40 min).
    rows = pd.read_csv(runs_csv).to_dict("records") if args.resume and runs_csv.exists() else []
    done = {(r["mode"], float(r["speed"]), int(r["seed"])) for r in rows}
    if done:
        print(f"resuming: {len(done)} run(s) already in {runs_csv.name}", flush=True)

    def save(row):
        rows.append(row)
        pd.DataFrame(rows).to_csv(runs_csv, index=False)

    for seed in range(args.seeds):
        cfg = base.with_(seed=seed)
        if ("offline", 0.0, seed) not in done or ("lockstep", 0.0, seed) not in done:
            offline = summarize(simulate(cfg))
            lock_sim, _ = run_lockstep(cfg)
            lock = summarize(lock_sim)
            same = all(lock[k] == offline[k] or (lock[k] != lock[k] and offline[k] != offline[k])
                       for k in offline if not k.startswith("solve_ms"))
            rows[:] = [r for r in rows if not (r["mode"] in ("offline", "lockstep") and r["seed"] == seed)]
            save({"mode": "offline", "speed": 0.0, "seed": seed, **offline})
            save({"mode": "lockstep", "speed": 0.0, "seed": seed, "identical_to_offline": same, **lock})
            print(f"seed {seed}: offline and lockstep {'IDENTICAL' if same else 'DIFFERENT'}", flush=True)
        offline = next(r for r in rows if r["mode"] == "offline" and r["seed"] == seed)

        for speed in args.speeds:
            if ("live", speed, seed) in done:
                print(f"seed {seed} @ {speed:g}x: already done, skipping", flush=True)
                continue
            ensure_topics(args.bootstrap, prefix=PREFIX, recreate=True)
            matcher = start_matcher(args.bootstrap)
            t0 = time.time()
            sim, metrics, diag = run_live(cfg, LiveConfig(speed=speed), args.bootstrap, PREFIX)
            try:
                matcher.wait(timeout=60)
            except subprocess.TimeoutExpired:
                matcher.kill()
            save({"mode": "live", "speed": speed, "seed": seed, **metrics, **diag})
            print(f"seed {seed} @ {speed:g}x: {time.time() - t0:.0f}s wall, "
                  f"cancel {metrics['cancel_rate']:.3f} (offline {offline['cancel_rate']:.3f}), "
                  f"offer delay {diag['offer_delay_mean_s']:.2f}s sim, "
                  f"transit p50 {diag['offer_transit_ms_p50']:.1f} ms", flush=True)

    df = pd.DataFrame(rows)
    df = df[df["seed"] < args.seeds]
    off = df[df["mode"] == "offline"].set_index("seed")
    lines = [
        "# M10: live over Kafka vs offline, with repositioning and late cancels" if args.m10 else
        "# M3: live over Kafka vs offline, same config and seeds", "",
        f"Demand `{args.slice}`, {args.hours:g} h, {args.drivers} drivers, optimal (lsa) every {args.interval:g} s, "
        f"cancellation-aware cost, {args.travel} travel"
        + (f" with noise sigma {NOISE}; the matcher's repositioning plan (forecast demand) every 5 min, riders who "
           "give up on a late driver" if args.m10 else "")
        + f". {args.seeds} seed(s); deltas are paired with offline for the same seed.",
        "",
        f"Lockstep (live code, zero latency) identical to offline for every seed: "
        f"**{bool(df[df['mode'] == 'lockstep']['identical_to_offline'].all())}**",
        "",
        "| mode | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | time to match s | Δ trips/h | batches |",
        "|---|---|---|---|---|---|---|---|",
    ]
    if args.m10:
        lines[-2] = lines[-2] + " late cancel % | moves / driver-h |"
        lines[-1] = lines[-1] + "---|---|"
    for (mode, speed), g in df[df["mode"] != "lockstep"].groupby(["mode", "speed"], sort=False):
        g = g.set_index("seed")
        d = g[METRICS] - off.loc[g.index, METRICS]
        label = "offline" if mode == "offline" else f"live {speed:g}x"
        lines.append(
            f"| {label} | {g['cancel_rate'].mean() * 100:.2f} | {d['cancel_rate'].mean() * 100:+.2f} "
            f"| {g['wait_all_mean_s'].mean():.1f} | {d['wait_all_mean_s'].mean():+.1f} "
            f"| {g['time_to_match_mean_s'].mean():.1f} | {d['completed_per_hour'].mean():+.1f} "
            f"| {g['batches'].mean():.0f} |"
            + (f" {g['cancel_late_rate'].mean() * 100:.2f} | {g['moves_per_driver_hour'].mean():.2f} |"
               if args.m10 else "")
        )
    lines += ["", "## Where the latency goes (live runs, mean over seeds)", "",
              "| speed | offer delay, sim s (mean / p99) | tick → batch solved, ms (p50 / p99) "
              "| offer → simulator, ms (p50 / p99) | rejected offers % | max lag, sim s | wall s |",
              "|---|---|---|---|---|---|---|"]
    for speed, g in df[df["mode"] == "live"].groupby("speed"):
        m = g[DIAG].mean()
        lines.append(
            f"| {speed:g}x | {m['offer_delay_mean_s']:.2f} / {m['offer_delay_p99_s']:.2f} "
            f"| {m['tick_to_batch_ms_p50']:.1f} / {m['tick_to_batch_ms_p99']:.1f} "
            f"| {m['offer_transit_ms_p50']:.1f} / {m['offer_transit_ms_p99']:.1f} "
            f"| {m['rejected_frac'] * 100:.2f} | {m['max_lag_s']:.1f} | {m['wall_s']:.0f} |"
        )
    if args.m10:
        live = df[df["mode"] == "live"]
        # the simulator's move outcomes (diagnostics), not the moves_* metrics of summarize
        cols = sorted(c for c in live.columns if c == "moves_started" or c.startswith("moves_rejected"))
        if cols:
            lines += ["", "Repositioning moves the simulator received from the matcher (live runs, total): "
                      + ", ".join(f"{c[len('moves_'):]} {int(live[c].fillna(0).sum())}" for c in cols) + "."]
    text = "\n".join(lines) + "\n"
    (RESULTS / f"{tag}_report.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
