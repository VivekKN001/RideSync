"""One dispatch batch, shared by the offline simulator and the live matcher service.

Both build a batch from the same inputs: the waiting riders, a view of every
driver, and the (rider, driver) pairs that were already declined. Given the same
state, offline and live dispatch make identical decisions.

What dispatch knows about a driver (``DriverView``) is deliberately small, just
what a driver status event carries: state, where the current leg ends
(``pos``), when it ends (``free_at``), and whether a next rider is already
queued. Idle drivers are stationary, so ``pos`` is their exact location.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, List, Mapping, Optional, Protocol, Sequence, Set, Tuple

import numpy as np

from ..geo import TravelTimeModel, haversine_m
from ..matching import MatchingProblem, make_problem
from ..matching.strategies import Strategy

if TYPE_CHECKING:  # the sim package imports this module, so no runtime import back into it
    from ..sim.config import DispatchConfig


class DriverState(Enum):
    IDLE = "idle"
    EN_ROUTE = "en_route"
    ON_TRIP = "on_trip"
    REPOSITIONING = "repositioning"  # M7: driving empty toward demand; free to dispatch on the way


class DriverView(Protocol):
    id: int
    state: DriverState

    @property
    def pos(self) -> np.ndarray:
        """End of the current leg: an idle driver's location, an on-trip driver's dropoff point."""

    @property
    def free_at(self) -> float:
        """Time the current leg ends."""

    @property
    def has_next(self) -> bool:
        """A next rider is already queued for after the current trip."""


def select_supply(drivers: Sequence[DriverView], now: float, horizon_s: float) -> Tuple[List[int], np.ndarray, np.ndarray]:
    """Idle and repositioning drivers, plus on-trip drivers finishing within the chaining horizon.

    Returns driver ids, positions (D, 2) and ETA offsets (D,): the time left on the current trip.
    A repositioning driver (M7, offline engine only) is where it is now on its way, via ``position_at``.
    """
    ids, positions, offsets = [], [], []
    for d in drivers:
        if d.state is DriverState.IDLE:
            ids.append(d.id)
            positions.append(d.pos)
            offsets.append(0.0)
        elif d.state is DriverState.REPOSITIONING:
            ids.append(d.id)
            positions.append(d.position_at(now))
            offsets.append(0.0)
        elif horizon_s > 0 and d.state is DriverState.ON_TRIP and not d.has_next and d.free_at - now <= horizon_s:
            ids.append(d.id)
            positions.append(d.pos)
            offsets.append(d.free_at - now)
    return ids, np.array(positions).reshape(-1, 2), np.array(offsets)


def eta_matrix(travel: TravelTimeModel, positions: np.ndarray, origins: np.ndarray, offsets: np.ndarray,
               max_candidates: int) -> np.ndarray:
    """(R, D) pickup ETA. With pruning, only each rider's k straight-line-nearest drivers are routed."""
    k = max_candidates
    if k <= 0 or k >= len(positions):
        return travel.matrix(positions, origins).T + offsets[None, :]
    dist = haversine_m(origins, positions)                      # (R, D)
    nearest = np.argpartition(dist, k - 1, axis=1)[:, :k]      # (R, k)
    cols = np.unique(nearest)
    sub = travel.matrix(positions[cols], origins).T + offsets[cols][None, :]  # (R, |cols|)
    keep = np.zeros(dist.shape, dtype=bool)
    np.put_along_axis(keep, nearest, True, axis=1)
    eta = np.full(dist.shape, np.inf)
    eta[:, cols] = np.where(keep[:, cols], sub, np.inf)
    return eta


@dataclass
class Batch:
    now: float
    rider_ids: List[int]
    driver_ids: List[int]
    eta: np.ndarray            # (R, D) with declined pairs masked to inf
    problem: MatchingProblem


def build_batch(
    now: float,
    rider_ids: Sequence[int],
    origins: np.ndarray,
    request_t: Sequence[float],
    drivers: Sequence[DriverView],
    declined: Mapping[int, Set[int]],
    travel: TravelTimeModel,
    cfg: "DispatchConfig",
) -> Optional[Batch]:
    """The batch for riders in the given order, or None when there are no riders or no available drivers."""
    if not rider_ids:
        return None
    driver_ids, positions, offsets = select_supply(drivers, now, cfg.chain_horizon_s)
    if not driver_ids:
        return None
    origins = np.asarray(origins, dtype=float).reshape(-1, 2)
    if hasattr(travel, "set_time"):  # time-of-day aware models (M6 ETA correction)
        travel.set_time(now)
    eta = eta_matrix(travel, positions, origins, offsets, cfg.max_candidates)
    if declined:
        col = {did: j for j, did in enumerate(driver_ids)}
        for i, rid in enumerate(rider_ids):
            for did in declined.get(rid, ()):
                if did in col:
                    eta[i, col[did]] = np.inf
    request_t = np.asarray(request_t, dtype=float)
    problem = make_problem(eta, waited_s=now - request_t, request_times=request_t, params=cfg.cost)
    return Batch(now, list(rider_ids), driver_ids, eta, problem)


@dataclass
class BatchResult:
    pairs: List[Tuple[int, int, float]]  # (rider id, driver id, quoted pickup ETA s), in solver order
    solve_ms: float
    cost: Optional[float] = None         # objective of the chosen solution (only with a shadow strategy)
    shadow_cost: Optional[float] = None  # objective the shadow strategy would get on the same batch


def solve_batch(batch: Batch, strategy: Strategy, shadow: Optional[Strategy] = None) -> BatchResult:
    t0 = time.perf_counter()
    pairs = strategy(batch.problem)
    solve_ms = (time.perf_counter() - t0) * 1000
    result = BatchResult(
        [(batch.rider_ids[i], batch.driver_ids[j], float(batch.eta[i, j])) for i, j in pairs], solve_ms
    )
    if shadow is not None:
        result.cost = batch.problem.total_cost(pairs)
        result.shadow_cost = batch.problem.total_cost(shadow(batch.problem))
    return result


@dataclass
class DispatchStats:
    batches: int = 0
    batch_riders: List[int] = field(default_factory=list)
    batch_drivers: List[int] = field(default_factory=list)
    solve_ms: List[float] = field(default_factory=list)
    offers: int = 0
    declines: int = 0
    batch_cost: List[float] = field(default_factory=list)         # objective of the chosen solution
    shadow_batch_cost: List[float] = field(default_factory=list)  # objective the shadow strategy would get

    def record_batch(self, riders: int, drivers: int, solve_ms: float,
                     cost: Optional[float] = None, shadow_cost: Optional[float] = None) -> None:
        self.batches += 1
        self.batch_riders.append(riders)
        self.batch_drivers.append(drivers)
        self.solve_ms.append(solve_ms)
        if shadow_cost is not None:
            self.batch_cost.append(cost)
            self.shadow_batch_cost.append(shadow_cost)
