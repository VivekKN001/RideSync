"""Generate the Grafana dashboard JSON (docker/grafana/dashboards/ridesync.json).

    python docker/grafana/make_dashboard.py

Every panel is filtered by the ``run`` variable. Its default, "latest", follows
whichever run started most recently, so the dashboard tracks a live run without
touching it. Time series use the events' wall-clock time (``ts``).
"""
import json
from pathlib import Path

CH = {"type": "grafana-clickhouse-datasource", "uid": "clickhouse"}
PG = {"type": "grafana-postgresql-datasource", "uid": "postgres"}
RUN = ("run = (SELECT if('${run}' = 'latest', argMax(run, started_ms), '${run}') "
       "FROM run_markers WHERE kind = 'run_start')")
PG_RUN = ("run_id = CASE WHEN '${run}' = 'latest' "
          "THEN (SELECT run_id FROM runs ORDER BY started_at DESC NULLS LAST LIMIT 1) ELSE '${run}' END")

panels = []


def place(w, h):
    """Left-to-right, wrapping at 24 columns."""
    x = sum(p["gridPos"]["w"] for p in panels if p["gridPos"]["y"] == place.y)
    if x + w > 24:
        place.y += place.row_h
        x, place.row_h = 0, 0
    place.row_h = max(place.row_h, h)
    return {"x": x, "y": place.y, "w": w, "h": h}


place.y, place.row_h = 0, 0


def ch(sql, fmt):
    return {"refId": "A", "datasource": CH, "editorType": "sql", "rawSql": sql,
            "format": 0 if fmt == "timeseries" else 1, "queryType": fmt}


def stat(title, sql, unit="none", decimals=None, w=4, desc="", text=False):
    reduce = {"calcs": ["lastNotNull"]}
    if text:  # a stat panel shows only numeric fields unless told otherwise
        reduce["fields"] = "/.*/"
    p = {"type": "stat", "title": title, "description": desc, "datasource": CH, "gridPos": place(w, 4),
         "targets": [ch(sql, "table")],
         "options": {"colorMode": "none", "graphMode": "none", "reduceOptions": reduce},
         "fieldConfig": {"defaults": {"unit": unit}, "overrides": []}}
    if decimals is not None:
        p["fieldConfig"]["defaults"]["decimals"] = decimals
    panels.append(p)


def series(title, sql, w=12, h=8, unit="none", desc="", stack=False, draw="line"):
    panels.append({
        "type": "timeseries", "title": title, "description": desc, "datasource": CH, "gridPos": place(w, h),
        "targets": [ch(sql, "timeseries")],
        "fieldConfig": {"defaults": {"unit": unit, "custom": {
            "drawStyle": draw, "lineWidth": 2, "fillOpacity": 12 if stack else 0, "showPoints": "never",
            "stacking": {"mode": "normal" if stack else "none"}}}, "overrides": []},
        "options": {"legend": {"displayMode": "list", "placement": "bottom"}, "tooltip": {"mode": "multi"}},
    })


def table(title, target, ds, w=12, h=9, desc=""):
    panels.append({"type": "table", "title": title, "description": desc, "datasource": ds, "gridPos": place(w, h),
                   "targets": [target], "options": {"showHeader": True, "cellHeight": "sm"},
                   "fieldConfig": {"defaults": {}, "overrides": []}})


# ---------------------------------------------------------------- headline
stat("Simulated clock", "SELECT formatDateTime(parseDateTimeBestEffortOrZero((SELECT any(JSONExtractString(config, 'start')) "
     f"FROM run_markers WHERE kind = 'run_start' AND {RUN})) + toIntervalSecond(toInt32(max(t))), '%H:%i') "
     f"AS clock FROM rider_events WHERE {RUN}", desc="Wall-clock time of the replayed day (the run's start + simulated time).",
     text=True)
stat("Ride requests", f"SELECT countIf(type = 'requested') AS requests FROM rider_events WHERE {RUN}")
stat("Trips completed", f"SELECT countIf(type = 'dropped_off') AS completed FROM rider_events WHERE {RUN}")
stat("Riders who cancelled", f"SELECT countIf(type = 'cancelled') / greatest(countIf(type = 'requested'), 1) "
     f"AS cancel_rate FROM rider_events WHERE {RUN}", unit="percentunit", decimals=1)
stat("Waiting at the last batch", f"SELECT riders FROM dispatch_batches WHERE {RUN} ORDER BY batch_t DESC LIMIT 1",
     desc="Riders the matcher considered in its most recent batch.")
stat("Average quoted pickup", f"SELECT avgIf(quoted_eta_s, type = 'matched') AS quoted FROM rider_events WHERE {RUN}",
     unit="s", decimals=0)

# ------------------------------------------------------------ flow over time
series("Demand and outcomes per simulated minute (from Flink)",
       f"SELECT max(ts) AS time, sum(requests) AS Requests, sum(matches) AS Matches, "
       f"sum(cancels_no_match + cancels_eta) AS Cancellations "
       f"FROM zone_features FINAL WHERE {RUN} GROUP BY minute ORDER BY time",
       desc="Per-minute totals across all zones, computed by the Flink job; a minute appears once it closes.")
series("Riders waiting vs drivers available, per batch",
       f"SELECT ts AS time, riders AS `Riders waiting`, drivers AS `Drivers available` "
       f"FROM dispatch_batches WHERE {RUN} ORDER BY ts")
series("Offer outcomes (per 10 s)",
       f"SELECT toStartOfInterval(ts, INTERVAL 10 SECOND) AS time, countIf(outcome = 'accepted') AS Accepted, "
       f"countIf(outcome = 'declined') AS `Declined by driver`, countIf(outcome = 'quote_cancelled') AS "
       f"`Rider refused ETA`, countIf(outcome = 'rejected') AS `Rejected as stale` "
       f"FROM offer_responses WHERE {RUN} GROUP BY time ORDER BY time", stack=True, draw="bars")
series("Matcher: solve time and tick-to-batch latency",
       f"SELECT ts AS time, solve_ms AS `Solve (ms)`, tick_lag_ms AS `Tick to solved (ms)` "
       f"FROM dispatch_batches WHERE {RUN} ORDER BY ts", unit="ms")

# ------------------------------------------------------------------- zones
table("Zones under pressure, last 5 closed minutes",
      ch(f"SELECT z.name AS Zone, sum(f.requests) AS Requests, sum(f.matches) AS Matches, "
         f"sum(f.cancels_no_match + f.cancels_eta) AS Cancelled, argMax(f.idle_end, f.minute) AS `Free drivers`, "
         f"round(sum(f.requests) / (argMax(f.idle_end, f.minute) + 1), 2) AS `Demand per free driver` "
         f"FROM zone_features AS f FINAL LEFT JOIN zones AS z ON z.id = f.zone "
         f"WHERE f.{RUN} AND f.minute + 5 > (SELECT max(minute) FROM zone_features WHERE {RUN}) "
         f"GROUP BY z.name ORDER BY `Demand per free driver` DESC LIMIT 15", "table"), CH,
      desc="Requests per free driver is the raw signal a surge-pricing policy (M6) would act on.")
stat("Late events (Flink)", f"SELECT count() AS late FROM late_events WHERE {RUN}", w=6,
     desc="Events that arrived after their minute had already closed; reported, not counted.")
stat("Batches skipped by the matcher", f"SELECT max(skipped) AS skipped FROM dispatch_batches WHERE {RUN}", w=6)

# ------------------------------------------------------------ surge (M6)
series("Surge multiplier across zones (M6)",
       f"SELECT max(ts) AS time, max(multiplier) AS Highest, "
       f"sum(multiplier * demand) / greatest(sum(demand), 1e-9) AS `Demand-weighted mean` "
       f"FROM zone_prices WHERE {RUN} GROUP BY t ORDER BY time",
       desc="Empty unless the run has surge pricing (python -m ridesync.live.sim --surge reactive|forecast).")
series("Expected vs actual app opens, next 15 min (M6)",
       f"SELECT p.time AS time, p.expected AS Expected, a.actual AS Actual FROM "
       f"(SELECT toInt64(t) AS pt, max(ts) AS time, sum(demand) AS expected FROM zone_prices WHERE {RUN} GROUP BY pt) AS p "
       f"LEFT JOIN (SELECT intDiv(toInt64(t), 300) * 300 - arrayJoin([0, 300, 600]) AS pt, sum(quotes) AS actual "
       f"FROM zone_features FINAL WHERE {RUN} GROUP BY pt) AS a ON a.pt = p.pt ORDER BY time",
       desc="Expected: the pricing demand estimate (reactive or forecast) summed over zones, at each 5-minute price "
            "update. Actual: app opens in the 15 minutes that followed (from Flink). Assumes the default 300 s "
            "interval and 900 s horizon.")
table("Surging zones at the latest price update (M6)",
      ch(f"SELECT z.name AS Zone, p.multiplier AS Multiplier, round(p.demand, 1) AS `Expected opens`, "
         f"p.supply AS `Free drivers`, p.source AS Source FROM zone_prices AS p LEFT JOIN zones AS z ON z.id = p.zone "
         f"WHERE p.{RUN} AND p.t = (SELECT max(t) FROM zone_prices WHERE {RUN}) AND p.multiplier > 1 "
         f"ORDER BY p.multiplier DESC, p.demand DESC LIMIT 15", "table"), CH, w=16)
stat("Riders who declined the price", f"SELECT sum(declines) / greatest(sum(quotes), 1) AS declined "
     f"FROM zone_features FINAL WHERE {RUN}", unit="percentunit", decimals=1, w=8,
     desc="Price refusals per app open (a retry that is refused again counts twice), from Flink zone features.")

# ---------------------------------------------------------------- postgres
table("Trip ledger (Postgres), latest updates",
      {"refId": "A", "datasource": PG, "format": "table", "rawQuery": True, "editorMode": "code",
       "rawSql": f"SELECT rider_id AS \"Rider\", status AS \"Status\", driver_id AS \"Driver\", "
                 f"round((quoted_eta_s / 60)::numeric, 1) AS \"Quoted pickup (min)\", "
                 f"round(((coalesce(matched_s, finished_s) - requested_s) / 60)::numeric, 1) AS \"Min to match or cancel\", "
                 f"cancel_reason AS \"Cancel reason\", updated_at AS \"Updated\" "
                 f"FROM trips WHERE {PG_RUN} ORDER BY updated_at DESC LIMIT 25"}, PG, w=16)
table("Trips by status (Postgres)",
      {"refId": "A", "datasource": PG, "format": "table", "rawQuery": True, "editorMode": "code",
       "rawSql": f"SELECT status AS \"Status\", count(*) AS \"Trips\" FROM trips WHERE {PG_RUN} "
                 f"GROUP BY status ORDER BY trip_rank(status), status"}, PG, w=8)

run_var_sql = ("SELECT r FROM (SELECT 'latest' AS r, toInt64(9e18) AS k UNION ALL "
               "SELECT run, max(started_ms) FROM run_markers WHERE kind = 'run_start' GROUP BY run) ORDER BY k DESC")
dashboard = {
    "uid": "ridesync-live", "title": "RideSync live", "tags": ["ridesync"], "timezone": "browser",
    "schemaVersion": 39, "version": 1, "editable": True, "refresh": "5s",
    "time": {"from": "now-30m", "to": "now"},
    "templating": {"list": [{
        "name": "run", "label": "Run", "type": "query", "datasource": CH, "query": run_var_sql,
        "definition": run_var_sql, "refresh": 2, "sort": 0, "current": {"text": "latest", "value": "latest"},
    }]},
    "panels": panels,
}
out = Path(__file__).parent / "dashboards" / "ridesync.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(dashboard, indent=1), encoding="utf-8", newline="\n")
print(f"wrote {out} ({len(panels)} panels)")
