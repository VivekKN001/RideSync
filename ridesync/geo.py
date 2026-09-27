"""Geometry and travel-time models.

Points are ``(lat, lon)`` in degrees. Every travel-time model exposes the same
two calls, ``matrix`` (for matching) and ``route`` (for moving vehicles). The
straight-line model and the OSRM model (``ridesync.routing``) can be swapped
without touching the simulator or the matcher.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

EARTH_RADIUS_M = 6_371_000.0


def haversine_m(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Pairwise great-circle distance in metres between (N, 2) and (M, 2) point arrays."""
    a = np.radians(np.atleast_2d(a))[:, None, :]
    b = np.radians(np.atleast_2d(b))[None, :, :]
    dlat = b[..., 0] - a[..., 0]
    dlon = b[..., 1] - a[..., 1]
    h = np.sin(dlat / 2) ** 2 + np.cos(a[..., 0]) * np.cos(b[..., 0]) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(np.clip(h, 0.0, 1.0)))


def haversine_pairs_m(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Element-wise distance in metres between matching rows of two (N, 2) arrays."""
    a, b = np.radians(a), np.radians(b)
    dlat, dlon = b[:, 0] - a[:, 0], b[:, 1] - a[:, 1]
    h = np.sin(dlat / 2) ** 2 + np.cos(a[:, 0]) * np.cos(b[:, 0]) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(np.clip(h, 0.0, 1.0)))


@dataclass(frozen=True)
class Route:
    """A drivable path with the time at which each vertex is reached.

    ``path`` is (K, 2) lat/lon with K >= 2; ``cum_s`` is (K,) non-decreasing,
    running from 0 to ``duration_s``.
    """

    duration_s: float
    path: np.ndarray
    cum_s: np.ndarray

    @property
    def start(self) -> np.ndarray:
        return self.path[0]

    @property
    def end(self) -> np.ndarray:
        return self.path[-1]

    def position(self, elapsed_s: float) -> np.ndarray:
        if self.duration_s <= 0:
            return self.end
        e = min(max(elapsed_s, 0.0), self.duration_s)
        return np.array([np.interp(e, self.cum_s, self.path[:, 0]), np.interp(e, self.cum_s, self.path[:, 1])])

    @staticmethod
    def straight(a: np.ndarray, b: np.ndarray, duration_s: float) -> "Route":
        return Route(float(duration_s), np.vstack([a, b]).astype(float), np.array([0.0, float(duration_s)]))

    @staticmethod
    def stationary(p: np.ndarray) -> "Route":
        return Route.straight(p, p, 0.0)


class TravelTimeModel(Protocol):
    def matrix(self, origins: np.ndarray, dests: np.ndarray) -> np.ndarray:
        """(N, M) travel time in seconds; inf where unroutable."""

    def route(self, a: np.ndarray, b: np.ndarray) -> Route:
        """Path and timing from a to b."""


@dataclass(frozen=True)
class StraightLineModel:
    """Great-circle distance times a road detour factor, driven at a constant speed.

    A detour factor of about 1.3-1.4 is typical for urban grids.
    """

    speed_mps: float = 7.0  # ~25 km/h average urban speed
    detour: float = 1.35

    def matrix(self, origins: np.ndarray, dests: np.ndarray) -> np.ndarray:
        return haversine_m(origins, dests) * self.detour / self.speed_mps

    def route(self, a: np.ndarray, b: np.ndarray) -> Route:
        return Route.straight(a, b, float(self.matrix(a, b)[0, 0]))
