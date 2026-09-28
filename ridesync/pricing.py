"""Surge pricing (M6): the policy, the rider's response, and demand estimates per zone.

Shared by the offline simulator (``ridesync.sim.engine``) and the live pricing service
(``ridesync.live.pricing``). They feed it different views of the world: the simulator knows its
state exactly, and the service only sees Flink's per-minute zone features. The rules are the same.
See ``PricingConfig`` for the policy itself.
"""
from __future__ import annotations

import math
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Deque, Dict, Mapping, Optional, Sequence, Tuple

import numpy as np

if TYPE_CHECKING:
    from .ml.demand import DemandForecaster
    from .sim.config import FareConfig, PricingConfig


def fares(cfg: "FareConfig", straight_m: np.ndarray, trip_s: np.ndarray) -> np.ndarray:
    """Pre-surge fare per trip from straight-line metres and seconds on the trip (see ``FareConfig``)."""
    miles = straight_m * cfg.road_factor / 1609.344
    return np.maximum(cfg.min_fare, cfg.base + cfg.per_mile * miles + cfg.per_min * trip_s / 60.0)


def multiplier(pressure: float, cfg: "PricingConfig") -> float:
    """1 + slope * (pressure - threshold), floored to the price step and clipped to [1, cap]."""
    raw = 1.0 + cfg.slope * (pressure - cfg.threshold)
    stepped = 1.0 + math.floor(max(raw - 1.0, 0.0) / cfg.step + 1e-9) * cfg.step
    return float(min(max(stepped, 1.0), cfg.cap))


def pressure(demand: float, waiting: float, supply: float) -> float:
    return (demand + waiting) / max(supply, 1.0)


def conversion(m: float, elasticity: float) -> float:
    """Probability that a rider shown multiplier m requests the ride."""
    return 1.0 if m <= 1.0 else float(m ** -elasticity)


def zone_prices(zones, demand: Mapping[int, float], waiting: Mapping[int, float], supply: Mapping[int, float],
                cfg: "PricingConfig", neighbours: Optional[Mapping[int, Sequence[int]]] = None) -> Dict[int, float]:
    """Multiplier per zone. Zones without demand or waiting riders stay at 1.

    With ``neighbours`` (zone -> nearby zones, itself included) a zone's pressure pools demand, waiting
    riders and supply over its neighbourhood: a free driver one zone over can still take the ride.
    """
    if not neighbours:
        return {z: multiplier(pressure(demand.get(z, 0.0), waiting.get(z, 0.0), supply.get(z, 0.0)), cfg) for z in zones}
    out = {}
    for z in zones:
        nb = neighbours.get(z) or (z,)
        out[z] = multiplier(pressure(sum(demand.get(y, 0.0) for y in nb), sum(waiting.get(y, 0.0) for y in nb),
                                     sum(supply.get(y, 0.0) for y in nb)), cfg)
    return out


class DemandEstimator:
    """Expected app opens per zone over the next ``horizon_s``, from opens seen so far.

    - ``reactive``: opens in the zone during the last ``horizon_s`` (persistence).
    - ``forecast``: the demand model, given the real history before the run and the opens this run
      has seen since (per 15-minute bucket, scaled up to full scale by 1 / sample_frac); the result
      is scaled back down.

    Times are simulated seconds since the run started at ``start``.
    """

    def __init__(self, cfg: "PricingConfig", start: Optional[datetime], sample_frac: float,
                 forecaster: Optional["DemandForecaster"] = None):
        self.cfg = cfg
        self.mode = cfg.demand
        self.start = start
        self.frac = sample_frac
        self.recent: Dict[int, Deque[float]] = defaultdict(deque)   # zone -> open times within the horizon
        self.buckets: Dict[Tuple[int, int], float] = defaultdict(float)  # (zone, run bucket) -> opens
        self.fc = forecaster
        if self.mode == "forecast":
            if forecaster is None:
                raise RuntimeError(f"forecast pricing needs a demand model at {cfg.forecast_path}: "
                                   "run `python -m ridesync.ml.train demand`")
            if start is None:
                raise ValueError("forecast pricing needs the run's start time (demand.start or a TLC slice)")
            from .ml.demand import BUCKET_S

            b = forecaster.bucket_of(start)
            if abs(b - round(b)) > 1e-6:
                raise ValueError(f"run start {start} is not on a {BUCKET_S / 60:.0f}-minute boundary")
            self.b_start = int(round(b))
        elif self.mode != "reactive":
            raise ValueError(f"unknown demand estimate {self.mode!r}; use 'reactive' or 'forecast'")

    def add_open(self, zone: int, t: float, count: float = 1.0) -> None:
        from .ml.demand import BUCKET_S

        q = self.recent[zone]
        for _ in range(int(round(count))):
            q.append(t)
        self.buckets[(zone, int(t // BUCKET_S))] += count

    def estimate(self, zones, now: float) -> Dict[int, float]:
        if self.mode == "reactive":
            lo = now - self.cfg.horizon_s
            out = {}
            for z in zones:
                q = self.recent.get(z)
                while q and q[0] <= lo:
                    q.popleft()
                out[z] = float(len(q)) if q else 0.0
            return out
        return self._forecast(zones, now)

    def _forecast(self, zones, now: float) -> Dict[int, float]:
        from .ml.demand import BUCKET_S, observed_rows

        fc = self.fc
        cur = int(now // BUCKET_S)
        seen = {(z, self.b_start + b): c for (z, b), c in self.buckets.items() if b < cur}
        observed = observed_rows(seen, fc.zone_row, len(fc.zones), 1.0 / self.frac)
        for b in range(self.b_start, self.b_start + cur):  # a run bucket with no opens at all is still data
            observed.setdefault(b, np.zeros(len(fc.zones)))
        exp = fc.expected(self.start + timedelta(seconds=now), self.cfg.horizon_s, observed) * self.frac
        return {z: float(exp[fc.zone_row[z]]) if z in fc.zone_row else 0.0 for z in zones}
