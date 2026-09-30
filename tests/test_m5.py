"""M5: the Postgres trip ledger and the live map's view of a run."""
import socket
import uuid

import pytest

from ridesync.env import pg_dsn
from ridesync.sinks.postgres import UPSERT_TRIP, statement_for, write
from ridesync.web.app import LiveView


def ev(typ, t, **kw):
    return {"type": typ, "run": "r1", "t": float(t), "ts": 1_700_000_000_000 + int(t * 1000), **kw}


REQ = ev("requested", 5, rider=7, origin=[40.75, -73.98], dest=[40.76, -73.97], request_t=5.0)


def test_ledger_statements():
    sql, row = statement_for(REQ)
    assert sql == UPSERT_TRIP and row["status"] == "requested" and row["origin_lat"] == 40.75
    assert row["requested_at"] is not None and row["matched_s"] is None
    _, row = statement_for(ev("cancelled", 300, rider=7, reason="no_match"))
    assert row["status"] == "cancelled" and row["finished_s"] == 300 and row["cancel_reason"] == "no_match"
    assert statement_for(ev("tick", 10)) is None
    assert statement_for(ev("run_start", 0, started_ms=1, config={}))[1]["run_id"] == "r1"


def _pg_up():
    try:
        with socket.create_connection(("localhost", 5432), timeout=0.5):
            return True
    except OSError:
        return False


@pytest.mark.skipif(not _pg_up(), reason="no Postgres on localhost:5432 (docker compose up -d postgres)")
def test_ledger_upserts_never_move_a_trip_backwards():
    psycopg = pytest.importorskip("psycopg")
    run = f"test-{uuid.uuid4().hex[:8]}"
    msgs = [dict(m, run=run) for m in [
        ev("matched", 40, rider=7, driver=3, quoted_eta_s=120.0),   # overtook the request
        REQ,
        ev("picked_up", 160, rider=7, driver=3),
        ev("dropped_off", 900, rider=7, driver=3),
        ev("matched", 40, rider=7, driver=3, quoted_eta_s=120.0),   # redelivered
    ]]
    with psycopg.connect(pg_dsn(), autocommit=True) as conn:
        try:
            write(conn, msgs)
            row = conn.execute("SELECT status, requested_s, matched_s, picked_up_s, finished_s, driver_id, quoted_eta_s "
                               "FROM trips WHERE run_id = %s AND rider_id = 7", (run,)).fetchone()
            assert row == ("dropped_off", 5.0, 40.0, 160.0, 900.0, 3, 120.0)
        finally:
            conn.execute("DELETE FROM trips WHERE run_id = %s", (run,))


def test_live_view_follows_the_newest_run():
    v = LiveView()
    v.apply(ev("run_start", 0, started_ms=100))
    v.apply(ev("status", 0, driver=1, seq=1, state="idle", pos=[40.7, -74.0]))
    v.apply(REQ)
    v.apply(ev("status", 30, driver=1, seq=2, state="en_route", pos=[40.75, -73.98]))
    v.apply(ev("ping", 35, driver=1, pos=[40.72, -73.99]))
    v.apply(ev("matched", 30, rider=7, driver=1, quoted_eta_s=90.0))
    snap = v.snapshot()
    assert snap["run"] == "r1" and snap["waiting"] == []
    assert snap["matches"] == [[7, *REQ["origin"]]]  # where the page draws the match ripple
    assert snap["drivers"] == [[1, 40.72, -73.99, 1, 40.75, -73.98]]  # moving, with a line to the pickup
    v.apply({**ev("zone_minute", 0, zone=230, minute=0, requests=4, idle_end=1), "type": "zone_minute"})
    assert v.snapshot()["zones"] == {"230": 2.0}
    v.apply({**ev("run_start", 0, started_ms=50), "run": "older"})  # an older run doesn't take over
    assert v.snapshot()["run"] == "r1"
    v.apply({**ev("run_start", 0, started_ms=200), "run": "r2"})
    assert v.snapshot()["run"] == "r2" and v.snapshot()["drivers"] == []


def test_live_view_waiting_riders_and_matches():
    v = LiveView()
    v.apply(ev("run_start", 0, started_ms=100, config={"start": "2026-07-15T17:00:00"}))
    assert v.snapshot()["start"] == "2026-07-15T17:00:00"  # the page's clock reads the replayed day from here
    v.apply(REQ)
    assert v.snapshot()["waiting"] == [[7, 40.75, -73.98, 5.0]]  # id, position, requested at (for the wait colour)
    v.apply(ev("matched", 30, rider=7, driver=1, quoted_eta_s=90.0))
    v.apply(ev("matched", 31, rider=99, driver=2, quoted_eta_s=90.0))  # never seen waiting: nothing to show
    assert v.snapshot()["matches"] == [[7, 40.75, -73.98]]
    v.apply(ev("ping", 95, driver=1, pos=[40.72, -73.99]))
    assert v.snapshot()["matches"] == []  # older than MATCH_SHOW_S
