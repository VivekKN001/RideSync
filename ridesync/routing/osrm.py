"""OSRM travel-time model: the real road network behind ``TravelTimeModel``.

- ``matrix`` calls the OSRM ``table`` service, chunked so each request stays
  within the server's ``--max-table-size`` and a sane URL length.
- ``route`` calls the ``route`` service with per-segment durations, so vehicles
  move along the actual street geometry over time. Results are LRU-cached on
  coordinates rounded to about 1 m.
- ``time_multiplier`` scales every OSRM duration. OSRM's car profile uses
  free-flow speeds, while Manhattan's real median trip speed is about 13 km/h.
  The multiplier comes from ``python -m ridesync.routing.calibrate`` against
  observed TLC trip times. M6 replaces it with a learned correction.

If OSRM finds no route between two points (e.g. snapped to a disconnected
pier), ``route`` falls back to a straight line at ``fallback_speed_mps`` and
counts it in ``fallbacks``, so the simulation keeps running while the problem stays visible.
"""
from __future__ import annotations

import time
from collections import OrderedDict

import numpy as np

from ..geo import Route, haversine_m, haversine_pairs_m


def _coords(points: np.ndarray) -> str:
    return ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in points)


class OSRMError(RuntimeError):
    pass


class OSRMModel:
    def __init__(
        self,
        base_url: str = "http://localhost:5000",
        time_multiplier: float = 1.0,
        max_table: int = 100,
        timeout_s: float = 30.0,
        cache_size: int = 100_000,
        fallback_speed_mps: float = 3.5,
        session=None,
        max_retries: int = 3,
    ):
        import requests

        self.base_url = base_url.rstrip("/")
        self.time_multiplier = time_multiplier
        self.max_table = max_table
        self.timeout_s = timeout_s
        self.cache_size = cache_size
        self.fallback_speed_mps = fallback_speed_mps
        self.session = session or requests.Session()
        self._routes: "OrderedDict[tuple, Route]" = OrderedDict()
        self.max_retries = max_retries
        self.requests = 0
        self.retries = 0
        self.fallbacks = 0

    # ---------------------------------------------------------------- HTTP
    def _get(self, service: str, points: np.ndarray, params: dict) -> dict:
        import requests

        url = f"{self.base_url}/{service}/v1/driving/{_coords(points)}"
        self.requests += 1
        # Reused keep-alive connections are sometimes closed by the server (or Docker's port proxy)
        # under load. Requests are idempotent GETs, so retry a few times before giving up.
        for attempt in range(self.max_retries + 1):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout_s)
                break
            except requests.ConnectionError:
                if attempt == self.max_retries:
                    raise
                self.retries += 1
                time.sleep(0.05 * 2 ** attempt)
        body = resp.json()
        code = body.get("code")
        if code in ("Ok", "NoRoute", "NoSegment"):  # the latter two are per-query outcomes, not failures
            return body
        raise OSRMError(f"OSRM {service} failed: {code} {body.get('message', '')}")

    # -------------------------------------------------------------- matrix
    def matrix(self, origins: np.ndarray, dests: np.ndarray) -> np.ndarray:
        origins, dests = np.atleast_2d(origins), np.atleast_2d(dests)
        out = np.full((len(origins), len(dests)), np.inf)
        step = self.max_table
        for i in range(0, len(origins), step):
            src = origins[i:i + step]
            for j in range(0, len(dests), step):
                dst = dests[j:j + step]
                body = self._get("table", np.vstack([src, dst]), {
                    "sources": ";".join(map(str, range(len(src)))),
                    "destinations": ";".join(map(str, range(len(src), len(src) + len(dst)))),
                    "annotations": "duration",
                })
                if body.get("code") != "Ok":
                    continue
                block = np.array(
                    [[np.inf if v is None else v for v in row] for row in body["durations"]], dtype=float
                )
                out[i:i + len(src), j:j + len(dst)] = block * self.time_multiplier
        return out

    # --------------------------------------------------------------- route
    def route(self, a: np.ndarray, b: np.ndarray) -> Route:
        key = (round(float(a[0]), 5), round(float(a[1]), 5), round(float(b[0]), 5), round(float(b[1]), 5))
        hit = self._routes.get(key)
        if hit is not None:
            self._routes.move_to_end(key)
            return hit
        route = self._fetch_route(np.asarray(a, float), np.asarray(b, float))
        self._routes[key] = route
        if len(self._routes) > self.cache_size:
            self._routes.popitem(last=False)
        return route

    def _fetch_route(self, a: np.ndarray, b: np.ndarray) -> Route:
        body = self._get("route", np.vstack([a, b]), {
            "overview": "full", "geometries": "geojson", "annotations": "duration", "steps": "false",
        })
        if body.get("code") != "Ok" or not body.get("routes"):
            self.fallbacks += 1
            return Route.straight(a, b, float(haversine_m(a, b)[0, 0]) / self.fallback_speed_mps)
        r = body["routes"][0]
        path = np.array([[lat, lon] for lon, lat in r["geometry"]["coordinates"]], dtype=float)
        seg = np.array(r["legs"][0].get("annotation", {}).get("duration", []), dtype=float)
        duration = float(r["duration"]) * self.time_multiplier
        if len(path) < 2:
            return Route.straight(a, b, duration)
        if len(seg) == len(path) - 1 and seg.sum() > 0:
            cum = np.concatenate([[0.0], np.cumsum(seg)]) * (duration / seg.sum())
        else:
            # No usable per-segment timing: spread time over the path in proportion to distance.
            d = haversine_pairs_m(path[:-1], path[1:])
            cum = np.concatenate([[0.0], np.cumsum(d)])
            cum = cum * (duration / cum[-1]) if cum[-1] > 0 else np.linspace(0, duration, len(path))
        return Route(duration, path, cum)

