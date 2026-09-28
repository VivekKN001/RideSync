"""Topics and message schema for the live system.

Every message is a JSON object with ``v`` (schema version), ``type``, ``run``
(the simulation run it belongs to) and ``t`` (event time in simulated seconds
since the run started). Simulator messages also carry ``ts``, the event time
as epoch milliseconds (the wall-clock moment the event was due, so it keeps
increasing across runs), and ``msps``, wall milliseconds per simulated second. The ``type`` is also sent as a Kafka header, so a
consumer can skip high-volume types (location pings) without decoding them.

Topic               key        types
------------------  ---------  ----------------------------------------------------------
rider-events        rider id   quoted (surge pricing only), requested, matched, picked_up, dropped_off, cancelled
driver-events       driver id  status, ping
dispatch-offers     driver id  offer
offer-responses     rider id   offer_response
dispatch-batches    run id     batch
zone-features       run|zone   zone_minute (Flink: per taxi zone, per simulated minute)
late-events         run|zone   the late event, as received
zone-prices         run id     prices (surge multiplier per zone, from the simulator or ridesync.live.pricing)

``rider-events`` and ``driver-events`` also carry control messages written to
*every* partition: ``run_start`` (with the run's dispatch config), ``tick``
and ``run_end``. The matcher takes the minimum ``t`` of the latest control
message across all partitions as its watermark: every event at or before the
watermark has been read. That is the same idea as a Flink watermark, done per
partition because Kafka only orders messages within a partition.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import List, Literal, Optional, TypedDict

from ..matching import CancelBelief, CostParams
from ..sim.config import DispatchConfig, TravelConfig

VERSION = 1

RIDER_EVENTS = "rider-events"
DRIVER_EVENTS = "driver-events"
DISPATCH_OFFERS = "dispatch-offers"
OFFER_RESPONSES = "offer-responses"
DISPATCH_BATCHES = "dispatch-batches"
ZONE_FEATURES = "zone-features"   # written by the Flink job (ridesync.stream)
LATE_EVENTS = "late-events"       # world events that arrived after their window closed
ZONE_PRICES = "zone-prices"       # M6 surge prices
ALL_TOPICS = (RIDER_EVENTS, DRIVER_EVENTS, DISPATCH_OFFERS, OFFER_RESPONSES, DISPATCH_BATCHES, ZONE_FEATURES,
              LATE_EVENTS, ZONE_PRICES)
WORLD_TOPICS = (RIDER_EVENTS, DRIVER_EVENTS)  # carry run_start / tick / run_end on every partition

CONTROL_TYPES = frozenset({"run_start", "tick", "run_end"})


class _Base(TypedDict, total=False):
    v: int
    type: str
    run: str
    t: float
    ts: int        # simulator messages: event time, epoch ms
    msps: float    # simulator messages: wall ms per simulated second


class RunStart(_Base):
    started_ms: int     # wall clock at run start; a newer run replaces an older one
    config: dict        # {"dispatch": ..., "travel": ..., "offer_timeout_s": ...}, see run_config()


class RiderEvent(_Base, total=False):
    rider: int
    origin: List[float]       # requested
    dest: List[float]         # requested
    request_t: float          # requested
    driver: int               # matched, picked_up, dropped_off
    quoted_eta_s: float       # matched
    reason: str               # cancelled: "no_match" | "eta_quote"
    multiplier: float         # quoted: surge multiplier shown when the rider opened the app
    accepted: bool            # quoted: the rider requested at that price
    attempt: int              # quoted: 0 = first app open, 1 = the retry


class DriverStatus(_Base):
    driver: int
    seq: int                  # per driver, increasing: orders statuses that share a timestamp
    state: Literal["idle", "en_route", "on_trip"]
    pos: List[float]          # where the current leg ends (an idle driver's location)
    free_at: float            # when the current leg ends
    has_next: bool            # a next rider is queued after this trip
    rider: Optional[int]


class DriverPing(_Base):
    driver: int
    pos: List[float]          # current position along the leg


class Offer(_Base):
    wall: float               # wall clock when sent (latency diagnostics only; ticks carry one too)
    offer_id: str
    batch_t: float
    rider: int
    driver: int
    eta_s: float


class OfferResponse(_Base, total=False):
    offer_id: str
    rider: int
    driver: int
    outcome: Literal["accepted", "declined", "quote_cancelled", "rejected"]
    reason: str               # rejected: "rider_gone" | "driver_busy" | "expired"


class BatchRecord(_Base):
    batch_t: float
    seq: int
    riders: int
    drivers: int
    offers: int
    solve_ms: float
    cost: Optional[float]
    shadow_cost: Optional[float]
    skipped: int              # batch boundaries skipped so far because the matcher fell behind
    tick_lag_ms: Optional[float]  # wall time from the simulator sending the tick to this batch being solved
    # (ts, from _Base: wall clock when the batch was solved)


class Prices(_Base):
    prices: dict              # {zone id (str): multiplier}
    demand: dict              # {zone id (str): expected app opens over the pricing horizon}
    supply: dict              # {zone id (str): free drivers}
    source: str               # "simulator" or "service:<reactive|forecast>"


def encode(msg: dict) -> bytes:
    return json.dumps(msg, separators=(",", ":")).encode()


def decode(raw: bytes) -> dict:
    return json.loads(raw)


# ------------------------------------------------------------------ config
def run_config(dispatch: DispatchConfig, travel: TravelConfig, offer_timeout_s: float,
               extra: Optional[dict] = None) -> dict:
    """``travel`` is what the matcher should assume (the belief model). ``extra`` carries M6 context:
    the run's wall-clock start, sample fraction and pricing config (the pricing service reads them)."""
    return {"dispatch": asdict(dispatch), "travel": asdict(travel), "offer_timeout_s": offer_timeout_s, **(extra or {})}


def dispatch_from_dict(d: dict) -> DispatchConfig:
    cost = dict(d["cost"])
    cost["cancel"] = CancelBelief(**cost["cancel"]) if cost.get("cancel") else None
    return DispatchConfig(**{**d, "cost": CostParams(**cost)})


def travel_from_dict(d: dict) -> TravelConfig:
    return TravelConfig(**d)
