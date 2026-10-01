"""Driver repositioning (M7): where idle drivers should wait.

Pure policy functions, like ``ridesync.pricing``: the simulator hands them its drivers and demand
estimates and gets back moves, ``(driver id, target zone)``. See ``RepositionConfig`` for the knobs.

- ``drift_moves``: what drivers do on their own, without a platform telling them: after a while idle,
  head for the nearest zone that is usually busy at this time of the week. Nobody coordinates, so
  drivers can bunch in the same hot zones.
- ``plan_moves``: the platform's plan. Share the free drivers out in proportion to expected demand,
  then fill each zone's shortfall from zones with a surplus, choosing who goes where by minimum total
  drive time (the same assignment solver as dispatch).

Both only move drivers idle for ``min_idle_s``, at most ``max_share`` of the idle fleet per round, on
drives of at most ``max_move_s``. So the two policies spend a similar move budget and differ in *where*.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Mapping, Sequence, Tuple

import numpy as np

if TYPE_CHECKING:
    from .geo import TravelTimeModel
    from .ml.demand import DemandForecaster
    from .sim.config import RepositionConfig

Move = Tuple[int, int]  # (driver id, target zone)


@dataclass
class Mover:
    """An idle driver the policy may move."""

    id: int
    pos: np.ndarray
    zone: int
    idle_s: float


def zone_targets(zones_index, points_path: str) -> Dict[int, np.ndarray]:
    """One point per zone to drive to: of the zone's fixed sample points (the ETA training pool),
    the one nearest its centre. A plain centroid can fall in a park or the river."""
    import pandas as pd

    from .ml.common import service_zones
    from .ml.eta import zone_points

    pts = zone_points(service_zones(), path=points_path)
    out = {}
    for z, g in pts.groupby("zone"):
        xy = g[["lat", "lon"]].to_numpy()
        c = zones_index.centroids.get(int(z))
        i = 0 if c is None else int(np.argmin(((xy - np.asarray(c)) ** 2).sum(axis=1)))
        out[int(z)] = xy[i]
    return out


def historical_demand(fc: "DemandForecaster", when: datetime, train_days: int = 21) -> Dict[int, float]:
    """Mean requests per zone in this 15-minute slot of the week, over the training days only:
    what an experienced driver knows about where it is usually busy."""
    from .ml.demand import PER_DAY, PER_WEEK

    b = int(np.floor(fc.bucket_of(when)))
    past = np.arange(b % PER_WEEK, min(train_days * PER_DAY, fc.counts.shape[1]), PER_WEEK)
    if len(past) == 0:
        return {}
    mean = fc.counts[:, past].mean(axis=1)
    return {int(z): float(mean[i]) for i, z in enumerate(fc.zones)}


def _budget(n_idle: int, cfg: "RepositionConfig") -> int:
    return int(np.floor(cfg.max_share * n_idle + 1e-9))


def drift_moves(movers: Sequence[Mover], usual: Mapping[int, float], targets: Mapping[int, np.ndarray],
                travel: "TravelTimeModel", cfg: "RepositionConfig", n_idle: int) -> List[Move]:
    """Each driver idle long enough, outside a usually-busy zone, goes to the nearest one (by drive time)."""
    zones = [z for z in targets if z in usual]
    if not zones or not movers:
        return []
    cut = np.quantile([usual[z] for z in zones], cfg.hot_quantile)
    hot = [z for z in zones if usual[z] >= cut and usual[z] > 0]
    hot_set = set(hot)
    cands = [m for m in sorted(movers, key=lambda m: -m.idle_s)
             if m.idle_s >= cfg.min_idle_s and m.zone not in hot_set][:_budget(n_idle, cfg)]
    if not cands or not hot:
        return []
    T = travel.matrix(np.array([m.pos for m in cands]), np.array([targets[z] for z in hot]))
    moves = []
    for i, m in enumerate(cands):
        j = int(np.argmin(T[i]))
        if np.isfinite(T[i, j]) and T[i, j] <= cfg.max_move_s:
            moves.append((m.id, hot[j]))
    return moves


def plan_round(drivers, now: float, zone_of, estimator, targets: Mapping[int, np.ndarray], travel: "TravelTimeModel",
               cfg: "RepositionConfig", chain_horizon_s: float) -> List[Move]:
    """One round of the platform's plan from a view of the fleet: the offline engine's own drivers or the live
    matcher's rebuilt ones, so both plan identically. A driver needs ``id``, ``state``, ``pos``, ``state_since``,
    ``free_at``, ``has_next`` and ``move_zone`` (where a repositioning driver is heading)."""
    from .dispatch import DriverState

    idle = [d for d in drivers if d.state is DriverState.IDLE]
    movers = [Mover(d.id, d.pos, zone_of(d.pos), now - d.state_since) for d in idle]
    if hasattr(travel, "set_time"):
        travel.set_time(now)
    supply: Dict[int, float] = {}
    for d in drivers:
        if d.state is DriverState.IDLE:
            z = zone_of(d.pos)
        elif d.state is DriverState.REPOSITIONING:  # already on its way: counts where it is going
            z = d.move_zone
        elif (chain_horizon_s > 0 and d.state is DriverState.ON_TRIP and not d.has_next
              and d.free_at - now <= chain_horizon_s):
            z = zone_of(d.pos)
        else:
            continue
        supply[z] = supply.get(z, 0) + 1
    demand = estimator.estimate(sorted(targets), now)
    return plan_moves(movers, supply, demand, targets, travel, cfg, len(idle))


def plan_moves(movers: Sequence[Mover], supply: Mapping[int, float], demand: Mapping[int, float],
               targets: Mapping[int, np.ndarray], travel: "TravelTimeModel", cfg: "RepositionConfig",
               n_idle: int) -> List[Move]:
    """Fill zones short of drivers from zones with a surplus, by minimum total drive time.

    ``supply``: free drivers per zone (idle, repositioning ones at their destination, and on-trip ones
    about to finish). A zone's target is its share of all free drivers, in proportion to ``demand``.
    Each driver short of target is one slot; a zone gives up at most its whole surplus (rounded down),
    longest-idle drivers first.
    """
    from scipy.optimize import linear_sum_assignment

    zones = list(targets)
    D = np.array([max(demand.get(z, 0.0), 0.0) for z in zones])
    S = np.array([float(supply.get(z, 0.0)) for z in zones])
    if D.sum() <= 0 or not movers:
        return []
    gap = S.sum() * D / D.sum() - S  # > 0: short of drivers
    slots = [z for z, g in zip(zones, gap) for _ in range(int(np.floor(g + 0.5)))]
    if not slots:
        return []
    surplus = {z: int(np.floor(-g + 1e-9)) for z, g in zip(zones, gap) if -g >= 1.0}
    taken: Dict[int, int] = {}
    cands = []
    for m in sorted(movers, key=lambda m: -m.idle_s):
        if m.idle_s >= cfg.min_idle_s and taken.get(m.zone, 0) < surplus.get(m.zone, 0):
            taken[m.zone] = taken.get(m.zone, 0) + 1
            cands.append(m)
    cands = cands[:_budget(n_idle, cfg)]
    if not cands:
        return []
    T = travel.matrix(np.array([m.pos for m in cands]), np.array([targets[z] for z in slots]))
    big = 1e9
    C = np.where(np.isfinite(T) & (T <= cfg.max_move_s), T, big)
    rows, cols = linear_sum_assignment(C)
    return [(cands[i].id, slots[j]) for i, j in zip(rows, cols) if C[i, j] < big]
