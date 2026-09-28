"""Discrete-event simulator for the offline (deterministic) mode.

The world (riders, drivers, movement, cancellations) runs on a virtual clock
and calls the same matching strategies the live matcher service will use.

Lifecycle
---------
Rider:  WAITING -> MATCHED -> ON_TRIP -> DONE, or WAITING -> CANCELLED
        With surge pricing (M6) a rider first sees a price and may not request: PENDING -> PRICED_OUT,
        or PENDING again (one retry a few minutes later).
Driver: IDLE -> EN_ROUTE -> ON_TRIP -> IDLE (an ON_TRIP driver may hold a queued next rider)

Two travel models (M6): ``travel`` is how long drives really take (the world), and ``belief`` is
what the matcher assumes when it builds ETA matrices and quotes. They are the same object unless
the config sets ``belief``.

Commitment policy: a match is never revisited once it's made. Drivers who
finish their current trip within ``chain_horizon_s`` count as supply. Their
pickup ETA is the time left on the trip plus the drive from the dropoff point.

Batch building and solving live in ``ridesync.dispatch``, which the live
matcher service calls too. The ``_publish_*`` hooks are no-ops here; the live
simulator (``ridesync.live.world``) overrides them to emit events.
"""
from __future__ import annotations

import heapq
from collections import Counter
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Dict, Optional, Set

import numpy as np

from ..dispatch import DispatchStats, DriverState, build_batch, solve_batch
from ..geo import Route, TravelTimeModel
from ..data.slices import run_start_and_frac
from ..matching import get_strategy
from ..pricing import DemandEstimator, conversion, zone_prices
from ..routing import make_travel_model
from .config import SimConfig
from .demand import RiderSpec, generate_riders, initial_driver_positions


class RiderState(Enum):
    PENDING = "pending"  # not yet requested
    WAITING = "waiting"
    MATCHED = "matched"
    ON_TRIP = "on_trip"
    DONE = "done"
    CANCELLED = "cancelled"
    PRICED_OUT = "priced_out"  # saw a surge price and left without requesting


@dataclass
class Rider:
    spec: RiderSpec
    state: RiderState = RiderState.PENDING
    matched_t: Optional[float] = None
    pickup_t: Optional[float] = None
    dropoff_t: Optional[float] = None
    quoted_eta_s: Optional[float] = None
    driver_id: Optional[int] = None
    cancel_reason: Optional[str] = None
    cancel_t: Optional[float] = None
    # Surge pricing (M6). spec.request_t moves to the retry time when a rider tries again; open_t doesn't.
    open_t: float = -1.0
    attempt: int = 0
    price: float = 1.0
    zone: Optional[int] = None

    def __post_init__(self):
        if self.open_t < 0:
            self.open_t = self.spec.request_t


@dataclass
class Leg:
    """A route started at time t0."""

    route: Route
    t0: float

    @property
    def end(self) -> np.ndarray:
        return self.route.end

    @property
    def t1(self) -> float:
        return self.t0 + self.route.duration_s

    def position(self, t: float) -> np.ndarray:
        return self.route.position(t - self.t0)


@dataclass
class Driver:
    id: int
    leg: Leg
    state: DriverState = DriverState.IDLE
    state_since: float = 0.0
    rider_id: Optional[int] = None
    next_rider_id: Optional[int] = None
    time_in: Dict[DriverState, float] = field(default_factory=lambda: {s: 0.0 for s in DriverState})

    # ``ridesync.dispatch.DriverView``. Idle legs are stationary, so for an idle driver this is its location.
    @property
    def pos(self) -> np.ndarray:
        return self.leg.end

    @property
    def free_at(self) -> float:
        return self.leg.t1

    @property
    def has_next(self) -> bool:
        return self.next_rider_id is not None


# Event kinds, ordered so that at equal timestamps world events run before dispatch,
# and new prices apply before the requests at the same instant.
REQUEST, PATIENCE, ARRIVE, TRIP_DONE, DISPATCH = range(5)
PRICE = -1


class Simulation:
    def __init__(self, cfg: SimConfig, travel: Optional[TravelTimeModel] = None):
        self.cfg = cfg
        self.start, self.sample_frac = run_start_and_frac(cfg.demand)
        self.travel = travel or make_travel_model(cfg.travel, self.start, cfg.seed)
        self.belief = self.travel if cfg.belief is None else make_travel_model(cfg.belief, self.start, cfg.seed)
        self.strategy = get_strategy(cfg.dispatch.strategy)
        shadow = cfg.dispatch.shadow_strategy
        self.shadow = get_strategy(shadow) if shadow else None
        self.riders = [Rider(spec) for spec in generate_riders(cfg)]
        self.drivers = [
            Driver(i, Leg(Route.stationary(p), 0.0)) for i, p in enumerate(initial_driver_positions(cfg))
        ]
        self.window = (cfg.demand.warmup_s, cfg.demand.duration_s)
        self.now = 0.0
        self.waiting: Dict[int, Rider] = {}
        self.declined: Dict[int, Set[int]] = {}  # rider id -> drivers who declined them
        self.stats = DispatchStats()
        self._events: list = []
        self._seq = 0
        self._dispatch_queued = False
        self.prices: Dict[int, float] = {}  # zone -> current multiplier; missing = 1
        self.price_log: list = []           # (t, prices, demand estimate, supply) per price update
        self.pricing_on = cfg.pricing.enabled
        if self.pricing_on:
            from ..stream.zones import ZoneIndex

            fc = None
            if cfg.pricing.demand == "forecast":
                from ..ml.demand import load_or_none

                fc = load_or_none(cfg.pricing.forecast_path)
            self.zones = ZoneIndex.load(cfg.pricing.zones_path)
            self.neighbours = self.zones.neighbours(cfg.pricing.pool_radius_m) if cfg.pricing.pool_radius_m > 0 else None
            self.estimator = DemandEstimator(cfg.pricing, self.start, self.sample_frac, fc)

    # ----------------------------------------------------------------- events
    def _schedule(self, t: float, kind: int, *args) -> None:
        heapq.heappush(self._events, (t, kind, self._seq, args))
        self._seq += 1

    def _event_driven(self) -> bool:
        return self.cfg.dispatch.interval_s <= 0

    def _request_dispatch(self) -> None:
        if self._event_driven() and not self._dispatch_queued:
            self._dispatch_queued = True
            self._schedule(self.now, DISPATCH)

    def run(self) -> "Simulation":
        for r in self.riders:
            self._schedule(r.spec.request_t, REQUEST, r.spec.id)
        if not self._event_driven():
            self._schedule(self.cfg.dispatch.interval_s, DISPATCH)
        self._schedule_pricing()

        handlers = self._handlers()
        while self._events:
            t, kind, _, args = heapq.heappop(self._events)
            self.now = t
            handlers[kind](*args)

        self._finish()
        return self

    def _finish(self) -> None:
        end = max(self.now, self.window[1])
        for d in self.drivers:
            self._accrue(d, end)

    # --------------------------------------------------------- live hooks
    def _publish_rider(self, r: Rider, kind: str) -> None:
        """A rider lifecycle event happened (requested, matched, picked_up, dropped_off, cancelled)."""

    def _publish_driver(self, d: Driver) -> None:
        """A driver's state, leg or queued next rider changed."""

    def _publish_quote(self, r: Rider, m: float, accepted: bool) -> None:
        """A rider opening the app saw multiplier m and did or didn't request (surge pricing only)."""

    def _publish_prices(self, prices: Dict[int, float], demand: Dict[int, float], supply: Dict[int, float]) -> None:
        """New zone prices (surge pricing only)."""

    # -------------------------------------------------------------- handlers
    def _handlers(self) -> dict:
        return {
            REQUEST: self._on_request,
            PATIENCE: self._on_patience,
            ARRIVE: self._on_arrive,
            TRIP_DONE: self._on_trip_done,
            DISPATCH: self._on_dispatch,
            PRICE: self._on_price,
        }

    def _on_request(self, rid: int) -> None:
        r = self.riders[rid]
        if self.pricing_on and not self._quote(r):
            return
        r.state = RiderState.WAITING
        self.waiting[rid] = r
        self._publish_rider(r, "requested")
        self._schedule(self.now + r.spec.patience_s, PATIENCE, rid)
        self._request_dispatch()

    def _on_patience(self, rid: int) -> None:
        r = self.riders[rid]
        if r.state is RiderState.WAITING:
            self._cancel(r, "no_match")

    def _on_arrive(self, did: int, rid: int) -> None:
        d, r = self.drivers[did], self.riders[rid]
        r.state, r.pickup_t = RiderState.ON_TRIP, self.now
        d.leg = Leg(self._route(d.leg.end, r.spec.dest), self.now)
        self._set_state(d, DriverState.ON_TRIP)
        self._publish_rider(r, "picked_up")
        self._publish_driver(d)
        self._schedule(d.leg.t1, TRIP_DONE, did, rid)

    def _on_trip_done(self, did: int, rid: int) -> None:
        d, r = self.drivers[did], self.riders[rid]
        r.state, r.dropoff_t = RiderState.DONE, self.now
        self._publish_rider(r, "dropped_off")
        d.rider_id = None
        d.leg = Leg(Route.stationary(d.leg.end), self.now)
        if d.next_rider_id is not None:
            nxt = self.riders[d.next_rider_id]
            d.next_rider_id = None
            if nxt.state is RiderState.MATCHED:
                self._start_pickup(d, nxt)
                return
        self._set_state(d, DriverState.IDLE)
        self._publish_driver(d)
        self._request_dispatch()

    def _on_dispatch(self) -> None:
        self._dispatch_queued = False
        self._dispatch()
        if not self._event_driven() and (self.now < self.cfg.demand.duration_s or self.waiting):
            self._schedule(self.now + self.cfg.dispatch.interval_s, DISPATCH)

    # --------------------------------------------------------------- dispatch
    def _dispatch(self) -> None:
        if not self.waiting:
            return
        riders = list(self.waiting.values())
        batch = build_batch(
            self.now,
            [r.spec.id for r in riders],
            np.array([r.spec.origin for r in riders]),
            [r.spec.request_t for r in riders],
            self.drivers,
            self.declined,
            self.belief,
            self.cfg.dispatch,
        )
        if batch is None:
            return
        result = solve_batch(batch, self.strategy, self.shadow)
        self.stats.record_batch(len(batch.rider_ids), len(batch.driver_ids), result.solve_ms,
                                result.cost, result.shadow_cost)
        for rid, did, eta_s in result.pairs:
            self._offer(self.riders[rid], self.drivers[did], eta_s)

    def _accepts(self, r: Rider, d: Driver) -> bool:
        # Deterministic per (seed, rider, driver): every strategy faces the same driver choices.
        u = np.random.default_rng([self.cfg.seed, 3, r.spec.id, d.id]).random()
        return u < self.cfg.drivers.accept_prob

    def _offer(self, r: Rider, d: Driver, eta_s: float) -> str:
        """Offer r to d. Returns the outcome: "declined", "quote_cancelled" or "accepted"."""
        self.stats.offers += 1
        if not self._accepts(r, d):
            self.stats.declines += 1
            self.declined.setdefault(r.spec.id, set()).add(d.id)
            return "declined"
        del self.waiting[r.spec.id]
        r.matched_t, r.quoted_eta_s, r.driver_id = self.now, eta_s, d.id
        if eta_s > r.spec.eta_tolerance_s:
            self._cancel(r, "eta_quote")
            return "quote_cancelled"
        r.state = RiderState.MATCHED
        self._publish_rider(r, "matched")
        if d.state is DriverState.IDLE:
            self._start_pickup(d, r)
        else:
            d.next_rider_id = r.spec.id
            self._publish_driver(d)
        return "accepted"

    # ---------------------------------------------------------------- pricing
    def _schedule_pricing(self) -> None:
        if self.pricing_on:
            self._schedule(0.0, PRICE)

    def _zone_of(self, p: np.ndarray) -> int:
        return self.zones.zone_of(float(p[0]), float(p[1]))

    def _on_price(self) -> None:
        pc = self.cfg.pricing
        horizon = self.cfg.dispatch.chain_horizon_s
        supply: Counter = Counter()
        for d in self.drivers:
            if d.state is DriverState.IDLE or (
                    horizon > 0 and d.state is DriverState.ON_TRIP and not d.has_next and d.free_at - self.now <= horizon):
                supply[self._zone_of(d.pos)] += 1
        waiting = Counter(r.zone for r in self.waiting.values())
        zones = (set(supply) | set(waiting) | set(self.estimator.recent)) - {0}  # 0 = outside every zone
        if self.estimator.fc is not None:
            zones |= set(self.estimator.fc.zones)
        zones = sorted(zones)
        demand = self.estimator.estimate(zones, self.now)
        self.prices = zone_prices(zones, demand, waiting, supply, pc, self.neighbours)
        self.price_log.append((self.now, self.prices, demand, dict(supply)))
        self._publish_prices(self.prices, demand, {z: float(supply.get(z, 0)) for z in zones})
        if self.now + pc.interval_s < self.cfg.demand.duration_s:
            self._schedule(self.now + pc.interval_s, PRICE)

    def _quote(self, r: Rider) -> bool:
        """Show the rider the zone's price. Returns True if they request now."""
        pc = self.cfg.pricing
        if r.attempt == 0:
            r.zone = self._zone_of(r.spec.origin)
            self.estimator.add_open(r.zone, self.now)
        m = self.prices.get(r.zone, 1.0)
        r.price = m
        # Draws are seeded per rider and attempt, so every pricing arm faces the same riders.
        u = 0.0 if m <= 1.0 else np.random.default_rng([self.cfg.seed, 4, r.spec.id, r.attempt]).random()
        accepted = u < conversion(m, pc.elasticity)
        self._publish_quote(r, m, accepted)
        if accepted:
            return True
        leaves = np.random.default_rng([self.cfg.seed, 5, r.spec.id]).random() < pc.leave_prob
        if r.attempt == 0 and pc.retry and not leaves:
            z = np.random.default_rng([self.cfg.seed, 6, r.spec.id]).standard_normal()
            r.attempt = 1
            r.spec = replace(r.spec, request_t=self.now + pc.retry_median_s * float(np.exp(pc.retry_sigma * z)))
            self._schedule(r.spec.request_t, REQUEST, r.spec.id)
        else:
            r.state, r.cancel_t = RiderState.PRICED_OUT, self.now
        return False

    # ------------------------------------------------------------ transitions
    def _route(self, a: np.ndarray, b: np.ndarray) -> Route:
        if hasattr(self.travel, "set_time"):
            self.travel.set_time(self.now)
        return self.travel.route(a, b)

    def _start_pickup(self, d: Driver, r: Rider) -> None:
        d.leg = Leg(self._route(d.leg.position(self.now), r.spec.origin), self.now)
        d.rider_id = r.spec.id
        self._set_state(d, DriverState.EN_ROUTE)
        self._publish_driver(d)
        self._schedule(d.leg.t1, ARRIVE, d.id, r.spec.id)

    def _cancel(self, r: Rider, reason: str) -> None:
        self.waiting.pop(r.spec.id, None)
        r.state, r.cancel_reason, r.cancel_t = RiderState.CANCELLED, reason, self.now
        self._publish_rider(r, "cancelled")

    def _set_state(self, d: Driver, state: DriverState) -> None:
        self._accrue(d, self.now)
        d.state = state

    def _accrue(self, d: Driver, until: float) -> None:
        """Add time spent in the current state, clipped to the measurement window."""
        lo, hi = self.window
        overlap = min(until, hi) - max(d.state_since, lo)
        if overlap > 0:
            d.time_in[d.state] += overlap
        d.state_since = until


def simulate(cfg: SimConfig, travel: Optional[TravelTimeModel] = None) -> Simulation:
    return Simulation(cfg, travel).run()
