"""Simulation configuration. Every assumption that affects the metrics lives here."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Optional, Tuple

from ..env import MODELS_DIR
from ..matching.problem import CostParams


@dataclass(frozen=True)
class Hotspot:
    dx_km: float      # east offset from the city centre
    dy_km: float      # north offset from the city centre
    sigma_km: float
    weight: float


@dataclass(frozen=True)
class CityConfig:
    """Synthetic city for M0. Roughly Manhattan-shaped (long north-south) around Midtown."""

    center: Tuple[float, float] = (40.7580, -73.9855)
    half_width_km: float = 3.0
    half_height_km: float = 7.0
    hotspots: Tuple[Hotspot, ...] = (
        Hotspot(0.0, 0.0, 1.0, 0.30),    # Midtown
        Hotspot(-0.8, -5.5, 0.8, 0.20),  # Financial District
        Hotspot(1.0, 3.5, 1.2, 0.15),    # Upper East Side
        Hotspot(-1.2, 3.0, 1.0, 0.10),   # Upper West Side
    )
    background_weight: float = 0.25  # uniform over the whole bounding box


@dataclass(frozen=True)
class DemandConfig:
    requests_per_hour: float = 1200.0
    duration_s: float = 3 * 3600.0
    warmup_s: float = 1800.0  # metrics exclude the first half hour while the system fills up
    min_trip_m: float = 800.0
    # Replay a TLC slice (from `python -m ridesync.data.tlc`) instead of synthetic demand.
    # requests_per_hour and the city hotspots are then ignored; duration_s still cuts the replay.
    trips_path: Optional[str] = None
    # Wall-clock time of simulated t = 0 ("2024-03-13 17:00") and the slice's sample fraction. Read from the
    # slice file name when left unset. The M6 models (time-of-day features, demand forecast) need them.
    start: Optional[str] = None
    sample_frac: Optional[float] = None


@dataclass(frozen=True)
class RiderBehavior:
    """Cancellation model. No public data exists for this, so it is an explicit assumption.

    - Unmatched patience: a rider still waiting for a match after a lognormal time cancels.
    - ETA quote: once matched, a rider cancels right away if the quoted pickup ETA is
      above their tolerance, which is also lognormal.
    - Late driver (``enroute_cancel``, off by default): a matched rider whose driver hasn't arrived by
      the quoted ETA plus a lognormal lateness tolerance cancels, and the driver stops where it is.
      Without it an optimistic quote is never punished: the rider accepts and simply waits longer.
    """

    patience_median_s: float = 300.0
    patience_sigma: float = 0.5
    eta_tolerance_median_s: float = 600.0
    eta_tolerance_sigma: float = 0.4
    enroute_cancel: bool = False
    lateness_tolerance_median_s: float = 180.0
    lateness_tolerance_sigma: float = 0.5


@dataclass(frozen=True)
class DriverConfig:
    num_drivers: int = 300
    accept_prob: float = 0.95  # a declined (rider, driver) pair is never offered again


@dataclass(frozen=True)
class TravelConfig:
    model: str = "straight"  # "straight" or "osrm"
    speed_mps: float = 7.0   # straight-line model only
    detour: float = 1.35     # straight-line model only
    osrm_url: str = "http://localhost:5000"
    time_multiplier: float = 1.0  # OSRM only; from `python -m ridesync.routing.calibrate`
    # M6: a learned correction on top of the model above (`python -m ridesync.ml.train eta`).
    eta_model: Optional[str] = None
    # M6: per-trip randomness of real driving times, as a lognormal sigma on each route's duration.
    # ETA matrices stay noise-free (they are the expectation), so quotes are no longer exact.
    noise_sigma: float = 0.0


@dataclass(frozen=True)
class DispatchConfig:
    strategy: str = "hungarian"
    interval_s: float = 5.0        # 0 = event-driven (dispatch on every request / driver freed)
    chain_horizon_s: float = 120.0  # on-trip drivers finishing within this count as supply; 0 = off
    cost: CostParams = field(default_factory=CostParams)
    # Candidate pruning before computing the ETA matrix: keep each rider's k nearest drivers by
    # straight-line distance (0 = all). Keeps OSRM table requests small; at k >= 20 it rarely drops the best edge.
    max_candidates: int = 0
    # Also solve each batch with this strategy (without acting on it) to measure the per-batch optimality gap.
    shadow_strategy: Optional[str] = None


@dataclass(frozen=True)
class FareConfig:
    """Rider fare before surge: max(min_fare, base + per_mile * miles + per_min * minutes).

    Defaults are placeholders in the range of 2024 Manhattan fares; ``python -m ridesync.ml.train fare``
    fits them to TLC ``base_passenger_fare`` (see ``ridesync.ml.fare.fare_from_file``). Miles are the
    straight-line distance times ``road_factor``, minutes the time actually spent on the trip.
    """

    base: float = 3.0
    per_mile: float = 2.0
    per_min: float = 0.9
    min_fare: float = 10.0
    road_factor: float = 1.35


@dataclass(frozen=True)
class PricingConfig:
    """Surge pricing (M6). Off by default, and when off the simulation is unchanged.

    Every ``interval_s`` each taxi zone gets a multiplier from its pressure,
    ``(expected demand over horizon_s + riders waiting) / max(free supply, 1)``, where supply is idle
    drivers in the zone plus on-trip drivers finishing there within the chaining horizon, all summed over
    the zones within ``pool_radius_m``. The multiplier
    is ``1 + slope * (pressure - threshold)``, floored to ``step`` and clipped to [1, cap].

    Expected demand is either ``reactive`` (app opens in the zone over the last ``horizon_s``) or
    ``forecast`` (the M6 demand model's prediction for the next ``horizon_s``).

    Riders see the price when they open the app and request with probability ``m ** -elasticity``
    (no public data exists for this; the default is in the range Cohen et al. 2016 found for Uber). A
    rider who says no leaves with probability ``leave_prob`` and otherwise, if ``retry``, opens the app
    once more after a lognormal delay and sees the price at that time.
    """

    enabled: bool = False
    demand: str = "reactive"  # "reactive" or "forecast"
    interval_s: float = 300.0
    horizon_s: float = 900.0
    # Pressure pools zones within pool_radius_m (0 = each zone alone). Per zone, a 10% slice has a few
    # riders and 0-1 free drivers, so unpooled pressure is mostly noise and surged ~half the trips even
    # with a third of the fleet idle. Pooled over 2 km, the median pressure is ~2 at 500 drivers and ~20
    # at 300; the threshold and slope put the first 0.25 step at 5.25 and the cap at 11.5.
    pool_radius_m: float = 2000.0
    threshold: float = 4.0
    slope: float = 0.2
    cap: float = 2.5
    step: float = 0.25
    elasticity: float = 0.5
    leave_prob: float = 0.5
    retry: bool = True
    retry_median_s: float = 180.0
    retry_sigma: float = 0.5
    forecast_path: str = f"{MODELS_DIR}/demand.joblib"
    zones_path: str = "data/processed/taxi_zones.json"


@dataclass(frozen=True)
class RepositionConfig:
    """Moving idle drivers toward demand (M7). Off (``policy="none"``) by default: the simulation is unchanged.

    Every ``interval_s`` the policy picks drivers idle for at least ``min_idle_s`` and sends them to a
    point in another zone; at most ``max_share`` of the idle fleet moves per round, and never on a drive
    longer than ``max_move_s``. A moving driver can be dispatched on the way (``ridesync.reposition``).

    - ``drift``: what drivers do by themselves: head for the nearest zone that is usually busy at this
      time of the week (top ``1 - hot_quantile`` of zones by historical demand). No coordination.
    - ``planned``: share the free drivers out in proportion to expected demand over ``horizon_s`` (from
      ``demand``: ``reactive`` or ``forecast``, as for surge pricing) and fill the gaps from zones with
      a surplus, choosing who goes where by minimum total drive time.
    """

    policy: str = "none"      # "none", "drift" or "planned"
    demand: str = "reactive"  # planned only: "reactive" or "forecast"
    interval_s: float = 300.0
    horizon_s: float = 900.0
    min_idle_s: float = 120.0
    max_move_s: float = 600.0
    max_share: float = 0.5
    hot_quantile: float = 0.75
    forecast_path: str = f"{MODELS_DIR}/demand.joblib"
    zones_path: str = "data/processed/taxi_zones.json"
    points_path: str = "data/models/zone_points.parquet"


@dataclass(frozen=True)
class SupplyConfig:
    """Drivers who respond to surge prices (M6b). Off by default: the fleet is fixed and nothing changes.

    No public data gives the size of either response, so both are parameters to vary, like rider elasticity.
    They act at every price update and need ``pricing.enabled``.

    - Logging on: ``reserve_share`` x ``drivers.num_drivers`` extra drivers start offline, placed like the
      fleet. At each price update an offline driver whose zone is surged at multiplier m logs on with
      probability 1 - m^-``log_on_elasticity``, after a delay (lognormal, median ``log_on_delay_s``). A reserve
      driver who has been idle for ``log_off_idle_s`` in an unsurged zone logs off where it is.
    - Chasing: a driver idle for at least ``chase_min_idle_s`` heads for the highest-priced zone it can reach
      within ``chase_max_s`` whose price beats its own zone's by at least one step, with probability
      ``chase_strength`` x the price difference (capped at 1). It moves like M7 repositioning: it can be
      dispatched on the way, and the drive counts as empty driving.
    """

    reserve_share: float = 0.0
    log_on_elasticity: float = 0.0
    log_on_delay_s: float = 300.0
    log_on_delay_sigma: float = 0.5
    log_off_idle_s: float = 1200.0
    chase_strength: float = 0.0
    chase_min_idle_s: float = 60.0
    chase_max_s: float = 600.0
    points_path: str = "data/models/zone_points.parquet"

    @property
    def enabled(self) -> bool:
        return (self.reserve_share > 0 and self.log_on_elasticity > 0) or self.chase_strength > 0


@dataclass(frozen=True)
class SimConfig:
    seed: int = 0
    city: CityConfig = field(default_factory=CityConfig)
    demand: DemandConfig = field(default_factory=DemandConfig)
    riders: RiderBehavior = field(default_factory=RiderBehavior)
    drivers: DriverConfig = field(default_factory=DriverConfig)
    travel: TravelConfig = field(default_factory=TravelConfig)
    dispatch: DispatchConfig = field(default_factory=DispatchConfig)
    # What the matcher believes travel takes, when that differs from the world's ``travel`` (M6). None = same.
    belief: Optional[TravelConfig] = None
    pricing: PricingConfig = field(default_factory=PricingConfig)
    fare: FareConfig = field(default_factory=FareConfig)
    reposition: RepositionConfig = field(default_factory=RepositionConfig)
    supply: SupplyConfig = field(default_factory=SupplyConfig)

    def with_(self, **overrides) -> "SimConfig":
        """Override nested fields with dotted keys, e.g. ``with_(**{"dispatch.interval_s": 2})``."""
        cfg = self
        for key, value in overrides.items():
            head, _, tail = key.partition(".")
            if tail:
                cfg = replace(cfg, **{head: replace(getattr(cfg, head), **{tail: value})})
            else:
                cfg = replace(cfg, **{head: value})
        return cfg
