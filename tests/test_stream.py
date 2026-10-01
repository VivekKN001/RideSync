"""M4 stream features: zone lookup, the two stages, lateness, and a full run reconciled against the simulator."""
import random
from collections import Counter
from pathlib import Path

import pytest

from ridesync.live.lockstep import run_lockstep
from ridesync.live.schema import DRIVER_EVENTS, RIDER_EVENTS, decode
from ridesync.sim import SimConfig
from ridesync.sim.engine import RiderState
from ridesync.stream.features import (
    add_event, close_until, enrich, entity_key, new_zone_state, run_reference, window_end_ts,
)
from ridesync.stream.zones import OUTSIDE, ZoneIndex

# Two 1 km squares side by side, as zones 1 and 2.
SQUARES = ZoneIndex([
    {"id": 1, "name": "West", "borough": "Test", "polygons": [[[0.0, 0.0], [0.0, 0.01], [0.01, 0.01], [0.01, 0.0], [0.0, 0.0]]]},
    {"id": 2, "name": "East", "borough": "Test", "polygons": [[[0.0, 0.01], [0.0, 0.02], [0.01, 0.02], [0.01, 0.01], [0.0, 0.01]]]},
])
WEST, EAST = [0.005, 0.005], [0.005, 0.015]


def msg(typ, t, **kw):
    return {"type": typ, "run": "r", "t": float(t), "ts": 1_000_000 + int(t * 1000), "msps": 1000.0, **kw}


def test_zone_index_squares_and_outside():
    assert SQUARES.zone_of(*WEST) == 1
    assert SQUARES.zone_of(*EAST) == 2
    assert SQUARES.zone_of(0.02, 0.02) == OUTSIDE


REAL_ZONES = Path("data/processed/taxi_zones.json")


@pytest.mark.skipif(not REAL_ZONES.exists(), reason="run `python -m ridesync.stream.zones` first")
def test_real_zones_known_places():
    z = ZoneIndex.load(str(REAL_ZONES))
    assert z.names[z.zone_of(40.7580, -73.9855)] == "Times Sq/Theatre District"
    assert z.names[z.zone_of(40.7069, -74.0110)] in ("Financial District North", "Financial District South")
    assert z.zone_of(40.70, -74.05) == OUTSIDE  # New York Harbor


def test_driver_supply_moves_between_zones_and_ignores_stale_status():
    st, ev = enrich(None, msg("status", 0, driver=7, state="idle", pos=WEST), SQUARES)
    assert [(e["zone"], e["delta"]) for e in ev] == [(1, 1)]
    st, ev = enrich(st, msg("status", 10, driver=7, state="en_route", pos=EAST), SQUARES)
    assert [(e["zone"], e["delta"]) for e in ev] == [(1, -1)]
    st, ev = enrich(st, msg("status", 5, driver=7, state="idle", pos=WEST), SQUARES)  # arrives late: superseded
    assert ev == [] and st["t"] == 10
    st, ev = enrich(st, msg("status", 20, driver=7, state="idle", pos=EAST), SQUARES)
    assert [(e["zone"], e["delta"]) for e in ev] == [(2, 1)]


def test_same_instant_statuses_are_ordered_by_seq_not_arrival():
    # Trip ends (idle, seq 5) and the next pickup starts (en_route, seq 6) at the same t; the network
    # delivers them the other way round. The driver must end up busy, not as a phantom free driver.
    st, _ = enrich(None, msg("status", 0, driver=1, seq=4, state="on_trip", pos=WEST), SQUARES)
    st, ev = enrich(st, msg("status", 60, driver=1, seq=6, state="en_route", pos=EAST), SQUARES)
    st, late = enrich(st, msg("status", 60, driver=1, seq=5, state="idle", pos=WEST), SQUARES)
    assert ev == [] and late == [] and st["idle"] is False


def test_rider_events_count_in_the_request_zone_even_when_they_overtake_the_request():
    st, ev = enrich(None, msg("matched", 40, rider=3, driver=1, quoted_eta_s=120.0), SQUARES)
    assert ev == [] and "pending" in st
    st, ev = enrich(st, msg("requested", 10, rider=3, origin=WEST, dest=EAST, request_t=10.0), SQUARES)
    assert [(e["kind"], e["zone"]) for e in ev] == [("request", 1), ("match", 1)]
    assert ev[1]["wait_s"] == 30.0
    st, ev = enrich(st, msg("dropped_off", 900, rider=3, driver=1), SQUARES)
    assert st is None and ev[0]["kind"] == "dropoff"


def test_window_rows_late_events_and_quiet_minutes():
    st = new_zone_state()
    for t in (5, 30):
        assert not add_event(st, {"run": "r", "zone": 1, "t": t, "ts": 1_000_000 + t * 1000, "msps": 1000.0,
                                  "kind": "request"})
    add_event(st, {"run": "r", "zone": 1, "t": 50, "ts": 1_050_000, "msps": 1000.0, "kind": "idle", "delta": 1})
    end = window_end_ts({"t": 50, "ts": 1_050_000, "msps": 1000.0})
    assert end == 1_060_000
    rows = close_until(st, "r", 1, end)
    assert len(rows) == 1 and rows[0]["requests"] == 2 and rows[0]["idle_end"] == 1
    # An event for minute 0 now is late: reported, not counted, but the supply gauge is corrected.
    assert add_event(st, {"run": "r", "zone": 1, "t": 55, "ts": 1_055_000, "msps": 1000.0, "kind": "idle", "delta": 1})
    rows = close_until(st, "r", 1, 10_000_000)  # far ahead: the quiet minutes run out
    assert [r["minute"] for r in rows] == [1, 2, 3]
    assert rows[0]["late"] == 1 and rows[0]["idle_end"] == 2 and rows[0]["requests"] == 0
    assert not st["ends"]


# ------------------------------------------------ a full run, reconciled
SMALL = SimConfig().with_(**{
    "demand.duration_s": 1800.0, "demand.warmup_s": 300.0, "demand.requests_per_hour": 900.0,
    "drivers.num_drivers": 80, "dispatch.strategy": "lsa", "dispatch.interval_s": 10.0,
})


@pytest.fixture(scope="module")
def world():
    sim, _ = run_lockstep(SMALL)
    msgs = [decode(p) for topic, _, _, _, _, p in sim.bus.log if topic in (RIDER_EVENTS, DRIVER_EVENTS)]
    zones = ZoneIndex.load(str(REAL_ZONES)) if REAL_ZONES.exists() else SQUARES
    return sim, msgs, zones


def _totals(rows):
    c = Counter()
    for r in rows:
        for k in ("requests", "matches", "cancels_no_match", "cancels_eta", "pickups", "dropoffs"):
            c[k] += r[k]
    return c


def test_features_reconcile_with_the_simulation(world):
    sim, msgs, zones = world
    rows, late, states = run_reference(msgs, zones)
    assert late == []
    reasons = Counter(r.cancel_reason for r in sim.riders if r.state is RiderState.CANCELLED)
    done = sum(r.state is RiderState.DONE for r in sim.riders)
    assert _totals(rows) == Counter(requests=len(sim.riders), matches=done, pickups=done, dropoffs=done,
                                    cancels_no_match=reasons["no_match"], cancels_eta=reasons["eta_quote"])
    # Every driver ends idle somewhere, and the per-zone supply gauges add up to the whole fleet.
    assert sum(st["idle_base"] for st in states.values()) == SMALL.drivers.num_drivers


def test_out_of_order_arrival_within_the_bound_loses_nothing(world):
    sim, msgs, zones = world
    ordered, _, _ = run_reference(msgs, zones)
    # Delay 20% of events by up to 3 s of event time, then deliver in arrival order.
    rng = random.Random(1)
    arrival = sorted(msgs, key=lambda m: m["ts"] + (rng.uniform(0, 3000) if rng.random() < 0.2 else 0))
    rows, late, _ = run_reference(arrival, zones, out_of_order_ms=3000)
    assert late == [] and _totals(rows) == _totals(ordered)
    # With no allowance, the same arrival order produces late events; counted plus late still add up.
    rows0, late0, _ = run_reference(arrival, zones, out_of_order_ms=0)
    assert late0
    lost = Counter({"request": "requests", "match": "matches", "pickup": "pickups", "dropoff": "dropoffs"}.get(
        e["kind"]) for e in late0)
    lost.pop(None, None)
    total = _totals(rows0)
    for k in ("requests", "matches", "pickups", "dropoffs"):
        assert total[k] + lost[k] == _totals(ordered)[k]


def test_entity_keys_ignore_pings_and_control():
    assert entity_key(msg("ping", 1, driver=1, pos=WEST)) is None
    assert entity_key(msg("tick", 1)) is None
    assert entity_key(msg("status", 1, driver=4, state="idle", pos=WEST)) == "r|d|4"
    assert entity_key(msg("cancelled", 1, rider=9, reason="no_match")) == "r|r|9"


def test_repositioning_drivers_are_free_where_they_are_heading_and_offline_ones_are_not():
    st, ev = enrich(None, msg("status", 0, driver=3, state="idle", pos=WEST), SQUARES)
    assert [(e["zone"], e["delta"]) for e in ev] == [(1, 1)]
    st, ev = enrich(st, msg("status", 10, driver=3, state="repositioning", pos=EAST), SQUARES)  # heads east
    assert [(e["zone"], e["delta"]) for e in ev] == [(1, -1), (2, 1)]
    st, ev = enrich(st, msg("status", 20, driver=3, state="offline", pos=EAST), SQUARES)
    assert [(e["zone"], e["delta"]) for e in ev] == [(2, -1)]
