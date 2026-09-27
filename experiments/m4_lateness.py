"""M4: how long should the stream job wait for late events?

    python experiments/m4_lateness.py

A 3 h Manhattan run (lockstep, so event time = real time at 1x) gives the world's
event stream. Each event is then delayed on its way to the stream job like on a
phone network: 20% of events get a lognormal delay (median 300 ms, long tail),
ticks are never delayed. The same arrival order goes through the zone-feature
logic (the code the Flink job runs; the M4 check found Flink's rows identical)
with different watermark allowances.

Trade-off per allowance B:
- completeness: events arriving after their minute closed are *late*, reported but not counted;
- freshness: a minute's row is emitted once the watermark passes its end, so rows arrive B ms later.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from ridesync.live.lockstep import run_lockstep
from ridesync.live.schema import DRIVER_EVENTS, RIDER_EVENTS, decode
from ridesync.live.sim import AWARE, DEFAULT_SLICE
from ridesync.routing import travel_from_calibration
from ridesync.sim import SimConfig
from ridesync.stream.features import (
    add_event, close_until, enrich, entity_key, new_zone_state, next_timer, zone_key,
)
from ridesync.stream.zones import ZoneIndex

RESULTS = Path(__file__).parent / "results"
BOUNDS_MS = [0, 250, 500, 1000, 2000, 5000]
DELAYED_FRAC, MEDIAN_MS, SIGMA = 0.2, 300.0, 1.0


def run(msgs, arrival, zones, bound_ms, demand_minutes):
    entities, states = {}, {}
    zone_events = late = lost_requests = 0
    emit_delay = []
    max_ts = None
    for i in np.argsort(arrival, kind="stable"):
        msg, now = msgs[i], arrival[i]
        max_ts = msg["ts"] if max_ts is None else max(max_ts, msg["ts"])
        key = entity_key(msg)
        if key is not None:
            st, events = enrich(entities.get(key), msg, zones)
            if st is None:
                entities.pop(key, None)
            else:
                entities[key] = st
            for ev in events:
                zone_events += 1
                zst = states.setdefault(zone_key(ev), new_zone_state())
                if add_event(zst, ev):
                    late += 1
                    lost_requests += ev["kind"] == "request"
        wm = max_ts - bound_ms
        for zk, zst in states.items():
            nxt = next_timer(zst)
            if nxt is not None and nxt <= wm:
                run_id, zone = zk.rsplit("|", 1)
                for row in close_until(zst, run_id, int(zone), wm):
                    if row["minute"] < demand_minutes:  # after demand ends the simulator stops ticking
                        emit_delay.append(now - row["ts"])  # wall time from the minute's end to its row
    requests = sum(m["type"] == "requested" for m in msgs)
    return {"bound_ms": bound_ms, "late_pct": 100 * late / zone_events, "requests_lost_pct": 100 * lost_requests / requests,
            "row_delay_p50_ms": float(np.percentile(emit_delay, 50)), "row_delay_p95_ms": float(np.percentile(emit_delay, 95))}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cfg = SimConfig(travel=travel_from_calibration("straight")).with_(**{
        "demand.trips_path": DEFAULT_SLICE, "demand.duration_s": 3 * 3600.0, "demand.warmup_s": 1800.0,
        "drivers.num_drivers": 500, "dispatch.strategy": "lsa", "dispatch.interval_s": 30.0,
        "dispatch.cost": AWARE, "dispatch.max_candidates": 20,
    })
    sim, _ = run_lockstep(cfg, tick_s=1.0)  # ticks every simulated second, like a live run
    msgs = [decode(p) for topic, _, _, _, _, p in sim.bus.log if topic in (RIDER_EVENTS, DRIVER_EVENTS)]
    rng = np.random.default_rng(0)
    ts = np.array([m["ts"] for m in msgs], dtype=float)
    delayed = np.array([m["type"] not in ("tick", "run_start", "run_end") for m in msgs]) & (rng.random(len(msgs)) < DELAYED_FRAC)
    delay = np.where(delayed, MEDIAN_MS * np.exp(rng.normal(0, SIGMA, len(msgs))), 0.0)
    arrival = ts + delay
    d = delay[delayed]
    print(f"{len(msgs)} events, {delayed.sum()} delayed: p50 {np.percentile(d, 50):.0f} ms, "
          f"p95 {np.percentile(d, 95):.0f} ms, p99 {np.percentile(d, 99):.0f} ms, max {d.max():.0f} ms")

    zones = ZoneIndex.load()
    rows = [run(msgs, arrival, zones, b, int(cfg.demand.duration_s // 60)) for b in BOUNDS_MS]
    lines = [
        "# M4: watermark allowance vs late events",
        "",
        f"3 h Manhattan run, 500 drivers, optimal every 30 s. {DELAYED_FRAC:.0%} of rider and driver events delayed "
        f"(lognormal, median {MEDIAN_MS:.0f} ms, sigma {SIGMA}): observed p50 {np.percentile(d, 50):.0f} ms, "
        f"p95 {np.percentile(d, 95):.0f} ms, p99 {np.percentile(d, 99):.0f} ms, max {d.max() / 1000:.1f} s. "
        "Ticks are never delayed.",
        "",
        "Row readiness is measured over the demand window (17:00-20:00), while the simulator ticks every second.",
        "",
        "| allowance | late events | requests missing from counts | row ready after minute ends (p50 / p95) |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['bound_ms'] / 1000:g} s | {r['late_pct']:.2f}% | {r['requests_lost_pct']:.2f}% "
                     f"| {r['row_delay_p50_ms'] / 1000:.2f} s / {r['row_delay_p95_ms'] / 1000:.2f} s |")
    text = "\n".join(lines) + "\n"
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "m4_lateness_report.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
