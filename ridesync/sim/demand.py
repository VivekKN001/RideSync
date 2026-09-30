"""Synthetic demand: Poisson ride requests with origins and destinations drawn from city hotspots.

Riders are generated up front from their own RNG stream, so every strategy
under the same seed sees the exact same riders (common random numbers). That
makes paired comparisons between strategies far less noisy.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

import numpy as np

from ..geo import haversine_pairs_m
from .config import CityConfig, SimConfig

KM_PER_DEG_LAT = 111.32


@dataclass
class RiderSpec:
    id: int
    request_t: float
    origin: np.ndarray
    dest: np.ndarray
    patience_s: float
    eta_tolerance_s: float


def _km_to_latlon(city: CityConfig, dx_km: np.ndarray, dy_km: np.ndarray) -> np.ndarray:
    lat0, lon0 = city.center
    lat = lat0 + dy_km / KM_PER_DEG_LAT
    lon = lon0 + dx_km / (KM_PER_DEG_LAT * np.cos(np.radians(lat0)))
    return np.column_stack([lat, lon])


def sample_points(city: CityConfig, n: int, rng: np.random.Generator) -> np.ndarray:
    """Draw n points from the hotspot mixture plus uniform background, clipped to the city box."""
    weights = np.array([h.weight for h in city.hotspots] + [city.background_weight])
    comp = rng.choice(len(weights), size=n, p=weights / weights.sum())
    dx = rng.uniform(-city.half_width_km, city.half_width_km, n)
    dy = rng.uniform(-city.half_height_km, city.half_height_km, n)
    for k, h in enumerate(city.hotspots):
        idx = comp == k
        dx[idx] = rng.normal(h.dx_km, h.sigma_km, idx.sum())
        dy[idx] = rng.normal(h.dy_km, h.sigma_km, idx.sum())
    dx = np.clip(dx, -city.half_width_km, city.half_width_km)
    dy = np.clip(dy, -city.half_height_km, city.half_height_km)
    return _km_to_latlon(city, dx, dy)


@lru_cache(maxsize=4)
def _load_trips(path: str):
    import pandas as pd

    return pd.read_parquet(path)


def _patience(cfg: SimConfig, n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    rb = cfg.riders
    patience = rb.patience_median_s * np.exp(rng.normal(0, rb.patience_sigma, n))
    tolerance = rb.eta_tolerance_median_s * np.exp(rng.normal(0, rb.eta_tolerance_sigma, n))
    return patience, tolerance


def replay_riders(cfg: SimConfig) -> list[RiderSpec]:
    """Riders from a TLC slice. Rider behaviour (patience, ETA tolerance) is still synthetic and seeded."""
    trips = _load_trips(cfg.demand.trips_path)
    trips = trips[(trips["request_s"] >= 0) & (trips["request_s"] < cfg.demand.duration_s)]
    rng = np.random.default_rng([cfg.seed, 1])
    patience, tolerance = _patience(cfg, len(trips), rng)
    origins = trips[["pu_lat", "pu_lon"]].to_numpy()
    dests = trips[["do_lat", "do_lon"]].to_numpy()
    times = trips["request_s"].to_numpy()
    return [
        RiderSpec(i, float(times[i]), origins[i], dests[i], float(patience[i]), float(tolerance[i]))
        for i in range(len(trips))
    ]


def generate_riders(cfg: SimConfig) -> list[RiderSpec]:
    if cfg.demand.trips_path:
        return replay_riders(cfg)
    rng = np.random.default_rng([cfg.seed, 1])
    d = cfg.demand

    rate_per_s = d.requests_per_hour / 3600.0
    n_guess = int(rate_per_s * d.duration_s * 1.2) + 50
    times = np.cumsum(rng.exponential(1.0 / rate_per_s, n_guess))
    times = times[times < d.duration_s]
    n = len(times)

    origins = sample_points(cfg.city, n, rng)
    dests = sample_points(cfg.city, n, rng)
    too_short = haversine_pairs_m(origins, dests) < d.min_trip_m
    while too_short.any():
        dests[too_short] = sample_points(cfg.city, int(too_short.sum()), rng)
        too_short = haversine_pairs_m(origins, dests) < d.min_trip_m

    patience, tolerance = _patience(cfg, n, rng)

    return [
        RiderSpec(i, float(times[i]), origins[i], dests[i], float(patience[i]), float(tolerance[i]))
        for i in range(n)
    ]


def initial_driver_positions(cfg: SimConfig, n: Optional[int] = None, stream: int = 2) -> np.ndarray:
    """Where drivers start. ``n``/``stream`` place extra drivers (the M6b reserve) from their own random
    stream, so the fleet's positions don't change."""
    rng = np.random.default_rng([cfg.seed, stream])
    n = cfg.drivers.num_drivers if n is None else n
    if cfg.demand.trips_path:
        # Start drivers where the demand is: at dropoffs of real trips from the same slice.
        trips = _load_trips(cfg.demand.trips_path)
        pick = rng.integers(0, len(trips), n)
        return trips[["do_lat", "do_lon"]].to_numpy()[pick]
    return sample_points(cfg.city, n, rng)
