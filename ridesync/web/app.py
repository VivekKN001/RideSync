"""Live map server: follows the newest run in Kafka and streams its state to the browser.

    python -m ridesync.web                  # http://localhost:8000

A background thread reads rider-events, driver-events (including location pings)
and zone-features from the end of each topic, and keeps a small picture of the
newest run: where every driver is and what it is doing, who is waiting, recent
cancellations, and each zone's latest demand per free driver (from Flink). The
page connects over a WebSocket and gets a snapshot four times a second.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # module level: FastAPI resolves annotations here
from fastapi.responses import HTMLResponse, JSONResponse

from ..live.schema import DRIVER_EVENTS, RIDER_EVENTS, ZONE_FEATURES
from ..stream.zones import ZONES_JSON

STATIC = Path(__file__).with_name("static")
STATE_CODE = {"idle": 0, "en_route": 1, "on_trip": 2}
CANCEL_SHOW_S = 90.0  # simulated seconds a cancellation stays on the map
MATCH_SHOW_S = 60.0   # simulated seconds a match stays in the snapshot (the page animates each one once)


class LiveView:
    """The newest run's current state, updated from Kafka messages. Thread-safe snapshots."""

    def __init__(self):
        self.lock = threading.Lock()
        self._reset(None, -1)

    def _reset(self, run: Optional[str], started_ms: int) -> None:
        self.run, self.started_ms = run, started_ms
        self.start: Optional[str] = None  # ISO time of simulated t = 0, from run_start
        self.t = 0.0
        self.drivers: Dict[int, list] = {}      # id -> [lat, lon, state code, to_lat, to_lon]
        self.waiting: Dict[int, list] = {}      # rider id -> [lat, lon, requested at t]
        self.origins: Dict[int, list] = {}      # rider id -> [lat, lon] (for placing cancellations)
        self.cancels: List[list] = []           # [lat, lon, t]
        self.matches: List[list] = []           # [rider id, lat, lon, t]
        self.pressure: Dict[int, dict] = {}     # zone -> latest closed minute's numbers
        self.counts = {"requests": 0, "completed": 0, "cancelled": 0}
        self.ended = False

    def apply(self, v: dict) -> None:
        typ, run = v.get("type"), v.get("run")
        with self.lock:
            if typ == "run_start" and v.get("started_ms", 0) > self.started_ms:
                self._reset(run, v["started_ms"])
                self.start = (v.get("config") or {}).get("start")  # wall-clock time of t = 0, for the page's clock
            if self.run is None and run:  # joined mid-run: adopt the first run we see
                self._reset(run, 0)
            if run != self.run:
                return
            self.t = max(self.t, v.get("t", 0.0)) if typ != "zone_minute" else self.t
            if typ == "run_end":
                self.ended = True
            elif typ == "ping":
                d = self.drivers.setdefault(v["driver"], [0.0, 0.0, 0, None, None])
                d[0], d[1] = v["pos"]
            elif typ == "status":
                d = self.drivers.setdefault(v["driver"], [v["pos"][0], v["pos"][1], 0, None, None])
                code = STATE_CODE[v["state"]]
                d[2] = code
                if code == 0:
                    d[0], d[1], d[3], d[4] = v["pos"][0], v["pos"][1], None, None
                elif code == 1:
                    d[3], d[4] = v["pos"]  # en route: the leg ends at the pickup
                else:
                    d[3] = d[4] = None
            elif typ == "requested":
                self.counts["requests"] += 1
                self.origins[v["rider"]] = list(v["origin"])
                self.waiting[v["rider"]] = [*v["origin"], v["t"]]
            elif typ == "matched":
                w = self.waiting.pop(v["rider"], None)
                if w:
                    self.matches.append([v["rider"], w[0], w[1], v["t"]])
            elif typ == "cancelled":
                self.counts["cancelled"] += 1
                self.waiting.pop(v["rider"], None)
                o = self.origins.pop(v["rider"], None)
                if o:
                    self.cancels.append([o[0], o[1], v["t"]])
            elif typ == "dropped_off":
                self.counts["completed"] += 1
                self.origins.pop(v["rider"], None)
            elif typ == "zone_minute":
                self.pressure[v["zone"]] = {
                    "minute": v["minute"], "requests": v["requests"], "free": v["idle_end"],
                    "ratio": v["requests"] / (v["idle_end"] + 1),
                }

    def snapshot(self) -> dict:
        with self.lock:
            self.cancels = [c for c in self.cancels if self.t - c[2] < CANCEL_SHOW_S]
            self.matches = [m for m in self.matches if self.t - m[3] < MATCH_SHOW_S]
            return {
                "run": self.run, "start": self.start, "t": self.t, "ended": self.ended, "counts": dict(self.counts),
                "drivers": [[k, *d] for k, d in self.drivers.items()],
                "waiting": [[k, *w] for k, w in self.waiting.items()],
                "matches": [m[:3] for m in self.matches],
                "cancels": [[c[0], c[1], (self.t - c[2]) / CANCEL_SHOW_S] for c in self.cancels],
                "zones": {str(z): p["ratio"] for z, p in self.pressure.items()},
            }


def follow(view: LiveView, bootstrap: str, prefix: str, stop: threading.Event) -> None:
    from ..live.kafka_bus import KafkaBus

    consumer = KafkaBus(bootstrap, prefix).consumer([RIDER_EVENTS, DRIVER_EVENTS, ZONE_FEATURES], from_beginning=False)
    while not stop.is_set():
        for m in consumer.poll(0.2):
            view.apply(m.value)
    consumer.close()


def manhattan_geojson(path: str = ZONES_JSON) -> dict:
    zones = json.loads(Path(path).read_text(encoding="utf-8"))
    feats = []
    for z in zones:
        if z["borough"] != "Manhattan":
            continue
        feats.append({"type": "Feature", "properties": {"id": z["id"], "name": z["name"]},
                      "geometry": {"type": "MultiPolygon",
                                   "coordinates": [[[[lon, lat] for lat, lon in ring]] for ring in z["polygons"]]}})
    return {"type": "FeatureCollection", "features": feats}


def create_app(bootstrap: str = "localhost:9092", prefix: str = "", grafana: str = "http://localhost:3000") -> FastAPI:
    view, stop = LiveView(), threading.Event()
    app = FastAPI(title="RideSync live map")
    geojson = manhattan_geojson()
    page = (STATIC / "index.html").read_text(encoding="utf-8").replace("__GRAFANA__", grafana)

    @app.on_event("startup")
    def _start() -> None:
        threading.Thread(target=follow, args=(view, bootstrap, prefix, stop), daemon=True).start()

    @app.on_event("shutdown")
    def _stop() -> None:
        stop.set()

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return page

    @app.get("/zones.geojson")
    def zones() -> JSONResponse:
        return JSONResponse(geojson)

    @app.websocket("/ws")
    async def ws(socket: WebSocket) -> None:
        await socket.accept()
        try:
            while True:
                await socket.send_text(json.dumps(view.snapshot(), separators=(",", ":")))
                await asyncio.sleep(0.25)
        except (WebSocketDisconnect, RuntimeError):
            pass

    app.state.view = view
    return app


def main(argv=None) -> None:
    import uvicorn

    ap = argparse.ArgumentParser(description="RideSync live map")
    ap.add_argument("--bootstrap", default="localhost:9092")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--grafana", default="http://localhost:3000")
    args = ap.parse_args(argv)
    print(f"live map: http://localhost:{args.port}", flush=True)
    uvicorn.run(create_app(args.bootstrap, args.prefix, args.grafana), host="127.0.0.1", port=args.port,
                log_level="warning")


if __name__ == "__main__":
    main()
