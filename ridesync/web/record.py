"""Record a run for the static replay: the live map, playing a file instead of a WebSocket.

    python -m ridesync.web.record                       # -> docs/demo/ (index.html, replay.json.gz, zones.geojson)
    python -m ridesync.web.record --drivers 350 --every 5

The run is the in-memory demo's (``ridesync.web.demo``), unpaced: simulator, matcher and Flink's feature
code in one process. Every ``--every`` simulated seconds the map's own snapshot is stored, until demand
ends. The folder is a static site: GitHub Pages serves it (.github/workflows/pages.yml).

The file is gzip-compressed JSON. Positions are integers in 1e-5 degrees (about 1 m) from an origin, and
driver positions are stored as the change since the previous frame, so the many drivers that stand
still cost a few bytes. ``decode`` is the reference for the page's decoder.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List

from .app import LiveView, manhattan_geojson, render_page
from .demo import Stopped, load_zones, run_once

FORMAT = 1
SCALE = 1e5  # 1e-5 degrees
REPO = "https://github.com/VivekKN001/RideSync"
SITE_FILES = ("index.html", "replay.json.gz", "zones.geojson")  # all it writes: other files in --out are left alone


class Recorder:
    """Encodes LiveView snapshots into replay frames."""

    def __init__(self, origin=(40.758, -73.9855)):
        self.lat0, self.lon0 = origin
        self.frames: List[dict] = []
        self.meta: Dict = {}
        self._prev: Dict[int, tuple] = {}
        self._matched: set = set()

    def q(self, lat: float, lon: float) -> List[int]:
        return [round((lat - self.lat0) * SCALE), round((lon - self.lon0) * SCALE)]

    def add(self, s: dict) -> None:
        if not self.meta:
            self.meta = {"run": s["run"], "start": s["start"]}
        drivers = sorted(s["drivers"])
        d, en_route = [], []
        prev = self._prev
        for i, lat, lon, state, to_lat, to_lon in drivers:
            qlat, qlon = self.q(lat, lon)
            plat, plon = prev.get(i, (0, 0))
            d += [i, qlat - plat, qlon - plon, state]
            prev[i] = (qlat, qlon)
            if state in (1, 3) and to_lat is not None:  # to the pickup, or to where it is repositioning
                en_route.append([i, *self.q(to_lat, to_lon)])
        new_matches = [m for m in s["matches"] if m[0] not in self._matched]
        self._matched.update(m[0] for m in new_matches)
        c = s["counts"]
        self.frames.append({
            "t": round(s["t"]),
            "c": [c["requests"], c["completed"], c["cancelled"]],
            "d": d,
            "e": en_route,
            "w": [[w[0], *self.q(w[1], w[2]), round(w[3])] for w in s["waiting"]],
            "m": [[m[0], *self.q(m[1], m[2])] for m in new_matches],
            "x": [[*self.q(x[0], x[1]), round(x[2] * 100)] for x in s["cancels"]],
            "z": {z: round(r, 2) for z, r in s["zones"].items() if r > 1},
        })

    def document(self, step_s: float) -> dict:
        return {"format": FORMAT, **self.meta, "step": step_s, "scale": SCALE, "origin": [self.lat0, self.lon0],
                "frames": self.frames}


def decode(doc: dict) -> List[dict]:
    """Replay document -> the page's snapshot frames (what the WebSocket would have sent)."""
    lat0, lon0 = doc["origin"]
    k = 1 / doc["scale"]
    pos: Dict[int, List[int]] = {}
    out = []
    for f in doc["frames"]:
        d = f["d"]
        targets = {e[0]: (lat0 + e[1] * k, lon0 + e[2] * k) for e in f["e"]}
        drivers = []
        for j in range(0, len(d), 4):
            i, dlat, dlon, state = d[j:j + 4]
            p = pos.setdefault(i, [0, 0])
            p[0] += dlat
            p[1] += dlon
            to = targets.get(i, (None, None))
            drivers.append([i, lat0 + p[0] * k, lon0 + p[1] * k, state, *to])
        out.append({
            "run": doc["run"], "start": doc["start"], "t": f["t"], "ended": False,
            "counts": dict(zip(("requests", "completed", "cancelled"), f["c"])),
            "drivers": drivers,
            "waiting": [[w[0], lat0 + w[1] * k, lon0 + w[2] * k, w[3]] for w in f["w"]],
            "matches": [[m[0], lat0 + m[1] * k, lon0 + m[2] * k] for m in f["m"]],
            "cancels": [[lat0 + x[0] * k, lon0 + x[1] * k, x[2] / 100] for x in f["x"]],
            "zones": f["z"],
        })
    return out


def record(cfg, step_s: float = 5.0) -> dict:
    """Run ``cfg`` unpaced and return the replay document, from t = 0 until demand ends."""
    view, rec, stop = LiveView(), Recorder(), threading.Event()
    end = cfg.demand.duration_s
    next_t = [0.0]

    def on_tick(t: float) -> None:
        if t > end:
            stop.set()
        elif t >= next_t[0]:
            rec.add(view.snapshot())
            next_t[0] += step_s

    try:
        run_once(cfg, view, 0.0, stop, load_zones(), on_tick)
    except Stopped:
        pass
    doc = rec.document(step_s)
    d = cfg.dispatch
    strategy = "optimal" if d.strategy == "lsa" else d.strategy
    doc["note"] = f"{cfg.drivers.num_drivers} drivers · {strategy} matching every {d.interval_s:g} s"
    if cfg.reposition.policy != "none":
        doc["note"] += f" · {cfg.reposition.policy} repositioning"
    return doc


def write_site(doc: dict, out: Path) -> Dict[str, int]:
    """The static replay site: page, recording and zones. Returns file sizes in bytes."""
    out.mkdir(parents=True, exist_ok=True)
    data = json.dumps(doc, separators=(",", ":")).encode()
    (out / "replay.json.gz").write_bytes(gzip.compress(data, compresslevel=9, mtime=0))
    (out / "zones.geojson").write_text(json.dumps(manhattan_geojson(), separators=(",", ":")), encoding="utf-8")
    page = render_page("recorded run", {"How it works": REPO, "Results": f"{REPO}#results"}, "replay.json.gz")
    (out / "index.html").write_text(page, encoding="utf-8", newline="\n")
    return {"raw json": len(data), **{n: (out / n).stat().st_size for n in SITE_FILES}}


def main(argv=None) -> None:
    from ..live.sim import add_args, config_from_args

    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_args(ap)
    ap.set_defaults(drivers=400)
    ap.add_argument("--every", type=float, default=5.0, help="simulated seconds between frames")
    ap.add_argument("--out", type=Path, default=Path("docs/demo"))
    args = ap.parse_args(argv)
    t0 = time.time()
    doc = record(config_from_args(args), args.every)
    sizes = write_site(doc, args.out)
    print(f"{len(doc['frames'])} frames in {time.time() - t0:.0f} s -> {args.out}")
    for name, n in sizes.items():
        print(f"  {name:<16} {n / 1e6:6.2f} MB")


if __name__ == "__main__":
    main()
