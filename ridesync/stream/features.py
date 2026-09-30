"""Per-zone, per-minute features from the world's event stream.

Pure Python with explicit state, so it is unit-tested on its own; the Flink
job (``ridesync.stream.job``) only supplies keyed state, timers and Kafka.

Stage 1, keyed by rider or driver (``enrich``): attach a taxi zone to every
event and turn it into *zone events*.
- A rider's events all count in the zone they requested from (demand side).
- With surge pricing (M6), a ``quoted`` event (the rider opened the app and saw a price) counts as
  one app open (``quotes``, first attempt only) and, if they didn't request, one ``declines``. It
  needs no rider state: the quote carries its own origin.
- A driver status turns into supply changes: +1 free driver in a zone when the
  driver becomes idle there, -1 when it leaves idle.
- Out of order: a driver status older than the last one applied is ignored
  (the newer state already supersedes it). "Older" compares (time, seq): a
  driver can change state twice in one instant (trip ends, next pickup starts). Rider events that arrive before the
  rider's request are held until the request shows up.

Stage 2, keyed by (run, zone) (``add_event`` / ``close_until``): count per
simulated minute. A window closes when the watermark passes its end, and its
row is emitted. An event for a window that is already closed is *late*: it is
reported separately and counted in the next row's ``late`` field. A late
supply change still corrects the free-driver count going forward.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .zones import ZoneIndex

WINDOW_S = 60.0
QUIET_WINDOWS = 3  # keep emitting rows for a zone this many minutes after its last event
RIDER_TYPES = frozenset({"quoted", "requested", "matched", "picked_up", "dropped_off", "cancelled"})
COUNTERS = ("requests", "matches", "cancels_no_match", "cancels_eta", "pickups", "dropoffs",
            "match_wait_sum", "eta_sum", "pickup_wait_sum", "idle_delta", "quotes", "declines")


def entity_key(msg: dict) -> Optional[str]:
    """Stage-1 key, or None for messages the feature job ignores (pings and control messages)."""
    typ = msg.get("type")
    if typ in RIDER_TYPES:
        return f"{msg['run']}|r|{msg['rider']}"
    if typ == "status":
        return f"{msg['run']}|d|{msg['driver']}"
    return None


def zone_key(ev: dict) -> str:
    return f"{ev['run']}|{ev['zone']}"


# ------------------------------------------------------------------ stage 1
def enrich(state: Optional[dict], msg: dict, zones: ZoneIndex) -> Tuple[Optional[dict], List[dict]]:
    """One entity's next message -> (new state, zone events). State None means nothing to keep."""
    if msg["type"] == "status":
        return _enrich_driver(state, msg, zones)
    return _enrich_rider(state, msg, zones)


def _base(msg: dict, zone: int) -> dict:
    return {"run": msg["run"], "zone": zone, "t": msg["t"], "ts": msg["ts"], "msps": msg["msps"]}


def _enrich_driver(state: Optional[dict], msg: dict, zones: ZoneIndex) -> Tuple[Optional[dict], List[dict]]:
    order = (msg["t"], msg.get("seq", 0))
    if state is not None and order <= (state["t"], state.get("seq", 0)):
        return state, []  # superseded by a newer status we already applied
    idle = msg["state"] == "idle"
    zone = zones.zone_of(msg["pos"][0], msg["pos"][1])
    was_idle, old_zone = (state["idle"], state["zone"]) if state else (False, None)
    out = []
    if was_idle and not (idle and old_zone == zone):
        out.append({**_base(msg, old_zone), "kind": "idle", "delta": -1})
    if idle and not (was_idle and old_zone == zone):
        out.append({**_base(msg, zone), "kind": "idle", "delta": 1})
    return {"t": msg["t"], "seq": msg.get("seq", 0), "idle": idle, "zone": zone}, out


def _enrich_rider(state: Optional[dict], msg: dict, zones: ZoneIndex) -> Tuple[Optional[dict], List[dict]]:
    typ = msg["type"]
    if typ == "quoted":
        zone = zones.zone_of(msg["origin"][0], msg["origin"][1])
        return state, [{**_base(msg, zone), "kind": "quote", "first": msg["attempt"] == 0,
                        "accepted": msg["accepted"]}]
    if typ == "requested":
        zone = zones.zone_of(msg["origin"][0], msg["origin"][1])
        pending = state.get("pending", []) if state else []
        state = {"zone": zone, "request_t": msg["request_t"]}
        out = [{**_base(msg, zone), "kind": "request"}]
        for early in sorted(pending, key=lambda m: m["t"]):  # events that overtook the request
            state, more = _rider_event(state, early)
            out += more
            if state is None:
                break
        return state, out
    if state is None or "zone" not in state:
        held = (state or {}).get("pending", [])
        return {"pending": held + [msg]}, []
    return _rider_event(state, msg)


def _rider_event(state: dict, msg: dict) -> Tuple[Optional[dict], List[dict]]:
    typ, ev = msg["type"], _base(msg, state["zone"])
    if typ == "matched":
        return state, [{**ev, "kind": "match", "wait_s": msg["t"] - state["request_t"], "eta_s": msg["quoted_eta_s"]}]
    if typ == "picked_up":
        return state, [{**ev, "kind": "pickup", "wait_s": msg["t"] - state["request_t"]}]
    if typ == "cancelled":
        return None, [{**ev, "kind": "cancel", "reason": msg["reason"]}]  # the rider is finished
    if typ == "dropped_off":
        return None, [{**ev, "kind": "dropoff"}]
    return state, []


# ------------------------------------------------------------------ stage 2
def new_zone_state() -> dict:
    return {"open": {}, "ends": {}, "closed_upto": -1, "idle_base": 0, "last_active": -1, "late": 0, "msps": 1000.0}


def window_of(t: float) -> int:
    return int(t // WINDOW_S)


def window_end_ts(ev: dict) -> int:
    """Event time (epoch ms) at which the event's minute ends."""
    m = window_of(ev["t"])
    return ev["ts"] + round(((m + 1) * WINDOW_S - ev["t"]) * ev["msps"])


def add_event(st: dict, ev: dict) -> bool:
    """Count a zone event into its minute. Returns True if it is late (its minute already closed)."""
    m = window_of(ev["t"])
    st["msps"] = ev["msps"]
    if m <= st["closed_upto"]:
        st["late"] += 1
        if ev["kind"] == "idle":
            st["idle_base"] += ev["delta"]  # the gauge stays right from here on
        return True
    w = st["open"].get(m)
    if w is None:
        w = st["open"][m] = dict.fromkeys(COUNTERS, 0)
        st["ends"][m] = window_end_ts(ev)
    kind = ev["kind"]
    if kind == "request":
        w["requests"] += 1
    elif kind == "match":
        w["matches"] += 1
        w["match_wait_sum"] += ev["wait_s"]
        w["eta_sum"] += ev["eta_s"]
    elif kind == "cancel":
        w["cancels_no_match" if ev["reason"] == "no_match" else "cancels_eta"] += 1
    elif kind == "pickup":
        w["pickups"] += 1
        w["pickup_wait_sum"] += ev["wait_s"]
    elif kind == "dropoff":
        w["dropoffs"] += 1
    elif kind == "idle":
        w["idle_delta"] += ev["delta"]
    elif kind == "quote":
        w["quotes"] += ev["first"]
        w["declines"] += not ev["accepted"]
    st["last_active"] = max(st["last_active"], m)
    return False


def close_until(st: dict, run: str, zone: int, watermark_ts: int) -> List[dict]:
    """Close every minute whose end is at or before the watermark, oldest first; return their rows.

    After closing, a recently active zone gets an empty next minute, so quiet minutes still report
    free drivers; it stops QUIET_WINDOWS minutes after the zone's last event.
    """
    rows = []
    while True:
        due = [m for m, end in st["ends"].items() if end <= watermark_ts]
        if not due:
            return rows
        m = min(due)
        end = st["ends"].pop(m)
        w = st["open"].pop(m)
        st["idle_base"] += w.pop("idle_delta")
        st["closed_upto"] = m
        rows.append({"type": "zone_minute", "v": 1, "run": run, "zone": zone, "minute": m, "t": m * WINDOW_S,
                     "ts": end, **w, "idle_end": st["idle_base"], "late": st["late"]})
        st["late"] = 0
        nxt = m + 1
        if nxt not in st["open"] and nxt - st["last_active"] <= QUIET_WINDOWS:
            st["open"][nxt] = dict.fromkeys(COUNTERS, 0)
            st["ends"][nxt] = end + round(WINDOW_S * st["msps"])


def next_timer(st: dict) -> Optional[int]:
    return min(st["ends"].values()) if st["ends"] else None


# ------------------------------------------------------------ reference run
class FeatureStream:
    """Both stages, one message at a time, with Flink's bounded-out-of-orderness watermark.

    The watermark is (largest event time seen) - out_of_order_ms. This is what the Flink job computes,
    minus parallelism and fault tolerance. ``run_reference`` runs it over a list; the in-memory demo
    (``ridesync.web.demo``) feeds it live, so the map shows zone pressure without Flink.
    """

    def __init__(self, zones: ZoneIndex, out_of_order_ms: int = 0):
        self.zones, self.out_of_order_ms = zones, out_of_order_ms
        self.entities: Dict[str, dict] = {}
        self.states: Dict[str, dict] = {}
        self.late: List[dict] = []
        self.max_ts: Optional[int] = None

    def feed(self, msg: dict) -> List[dict]:
        """Apply one message; return the zone_minute rows it closes."""
        if "ts" in msg:  # ticks move the watermark too, as they do in Flink
            self.max_ts = msg["ts"] if self.max_ts is None else max(self.max_ts, msg["ts"])
        key = entity_key(msg)
        if key is None or self.max_ts is None:
            return []
        st, events = enrich(self.entities.get(key), msg, self.zones)
        if st is None:
            self.entities.pop(key, None)
        else:
            self.entities[key] = st
        for ev in events:
            zst = self.states.setdefault(zone_key(ev), new_zone_state())
            if add_event(zst, ev):
                self.late.append(ev)
        watermark = self.max_ts - self.out_of_order_ms
        rows = []
        for zk, zst in self.states.items():
            nxt = next_timer(zst)
            if nxt is not None and nxt <= watermark:
                run, zone = zk.rsplit("|", 1)
                rows += close_until(zst, run, int(zone), watermark)
        return rows

    def finish(self) -> List[dict]:
        """End of input: the watermark goes to +infinity."""
        rows = []
        for zk, zst in self.states.items():
            run, zone = zk.rsplit("|", 1)
            while zst["ends"]:
                rows += close_until(zst, run, int(zone), max(zst["ends"].values()))
        return rows


def run_reference(msgs, zones: ZoneIndex, out_of_order_ms: int = 0) -> Tuple[List[dict], List[dict], dict]:
    """``FeatureStream`` over messages in arrival order. Returns (rows, late events, zone states).

    Tests and the late-events experiment use it as the reference for the Flink job.
    """
    fs = FeatureStream(zones, out_of_order_ms)
    rows = []
    for msg in msgs:
        rows += fs.feed(msg)
    rows += fs.finish()
    return rows, fs.late, fs.states
