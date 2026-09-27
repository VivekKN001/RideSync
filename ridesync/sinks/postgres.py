"""Postgres trip ledger: one row per trip, upserted as the trip's events arrive.

    python -m ridesync.sinks.postgres
    python -m ridesync.sinks.postgres --dsn postgresql://ridesync:ridesync@localhost:5432/ridesync

Unlike the matcher, this is a normal consumer group (``postgres-trip-ledger``)
with committed offsets, so after a restart it continues where it stopped.
Offsets are committed only after the database transaction commits: delivery
is at-least-once, every write is an idempotent upsert, and a trip never moves
back to an earlier status, because events can arrive out of order.
"""
from __future__ import annotations

import argparse
import json
import signal
import sys
import time
from typing import Iterable, Optional, Tuple

from ..live.schema import RIDER_EVENTS, decode

DSN = "postgresql://ridesync:ridesync@localhost:5432/ridesync"
STATUS = {"requested": "requested", "matched": "matched", "picked_up": "picked_up",
          "dropped_off": "dropped_off", "cancelled": "cancelled"}
FIELDS = ("requested_s", "matched_s", "picked_up_s", "finished_s", "requested_at", "origin_lat", "origin_lon",
          "dest_lat", "dest_lon", "driver_id", "quoted_eta_s", "cancel_reason")

UPSERT_TRIP = f"""
INSERT INTO trips AS tr (run_id, rider_id, status, {", ".join(FIELDS)}, updated_at)
VALUES (%(run_id)s, %(rider_id)s, %(status)s, {", ".join(f"%({f})s" for f in FIELDS)}, now())
ON CONFLICT (run_id, rider_id) DO UPDATE SET
    status = CASE WHEN trip_rank(EXCLUDED.status) > trip_rank(tr.status) THEN EXCLUDED.status ELSE tr.status END,
    {", ".join(f"{f} = COALESCE(EXCLUDED.{f}, tr.{f})" for f in FIELDS)},
    updated_at = now()
"""
UPSERT_RUN_START = """
INSERT INTO runs (run_id, started_at, config) VALUES (%(run_id)s, to_timestamp(%(started_ms)s / 1000.0), %(config)s)
ON CONFLICT (run_id) DO NOTHING
"""
UPSERT_RUN_END = """
INSERT INTO runs (run_id, ended_at) VALUES (%(run_id)s, to_timestamp(%(ts)s / 1000.0))
ON CONFLICT (run_id) DO UPDATE SET ended_at = EXCLUDED.ended_at
"""


def statement_for(msg: dict) -> Optional[Tuple[str, dict]]:
    """The SQL and parameters for one rider-events message, or None if it doesn't touch the ledger."""
    typ = msg.get("type")
    if typ == "run_start":
        return UPSERT_RUN_START, {"run_id": msg["run"], "started_ms": msg["started_ms"],
                                  "config": json.dumps(msg.get("config"))}
    if typ == "run_end":
        return UPSERT_RUN_END, {"run_id": msg["run"], "ts": msg.get("ts", time.time() * 1000)}
    if typ not in STATUS:
        return None
    row = dict.fromkeys(FIELDS)
    row.update(run_id=msg["run"], rider_id=msg["rider"], status=STATUS[typ])
    if typ == "requested":
        row.update(requested_s=msg["request_t"], origin_lat=msg["origin"][0], origin_lon=msg["origin"][1],
                   dest_lat=msg["dest"][0], dest_lon=msg["dest"][1])
        if "ts" in msg:
            from datetime import datetime, timezone

            row["requested_at"] = datetime.fromtimestamp(msg["ts"] / 1000, tz=timezone.utc)
    elif typ == "matched":
        row.update(matched_s=msg["t"], driver_id=msg["driver"], quoted_eta_s=msg["quoted_eta_s"])
    elif typ == "picked_up":
        row.update(picked_up_s=msg["t"], driver_id=msg["driver"])
    elif typ == "dropped_off":
        row.update(finished_s=msg["t"], driver_id=msg["driver"])
    elif typ == "cancelled":
        row.update(finished_s=msg["t"], cancel_reason=msg["reason"])
    return UPSERT_TRIP, row


def write(conn, msgs: Iterable[dict]) -> int:
    """Apply messages in order in one transaction. Returns the number of statements run."""
    n = 0
    with conn.transaction():
        with conn.cursor() as cur:
            for msg in msgs:
                stmt = statement_for(msg)
                if stmt is not None:
                    cur.execute(*stmt)
                    n += 1
    return n


def main(argv=None) -> None:
    import psycopg
    from confluent_kafka import Consumer, KafkaException

    ap = argparse.ArgumentParser(description="Kafka rider-events -> Postgres trip ledger")
    ap.add_argument("--bootstrap", default="localhost:9092")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--dsn", default=DSN)
    args = ap.parse_args(argv)

    consumer = Consumer({
        "bootstrap.servers": args.bootstrap,
        "group.id": f"{args.prefix}postgres-trip-ledger",
        "enable.auto.commit": False,
        "auto.offset.reset": "earliest",
    })
    consumer.subscribe([args.prefix + RIDER_EVENTS])
    stop = {"now": False}
    signal.signal(signal.SIGINT, lambda *_: stop.update(now=True))
    print("postgres sink: running (Ctrl+C to stop)", flush=True)
    written, last_log = 0, time.monotonic()
    with psycopg.connect(args.dsn, autocommit=True) as conn:
        while not stop["now"]:
            batch = consumer.consume(num_messages=1000, timeout=0.5)
            msgs = []
            for m in batch:
                if m.error():
                    raise KafkaException(m.error())
                msgs.append(decode(m.value()))
            if msgs:
                written += write(conn, msgs)
                consumer.commit(asynchronous=False)  # only after the database commit
            if time.monotonic() - last_log > 10:
                last_log = time.monotonic()
                print(f"postgres sink: {written} upserts so far", flush=True)
    consumer.close()
    sys.exit(0)


if __name__ == "__main__":
    main()
