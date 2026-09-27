"""Topics and message schema for the live system.

Every message is a JSON object with ``v`` (schema version), ``type``, ``run``
(the simulation run it belongs to) and ``t`` (event time in simulated seconds
since the run started). The ``type`` is also sent as a Kafka header, so a
consumer can skip high-volume types (location pings) without decoding them.

Topic               key        types
------------------  ---------  ----------------------------------------------------------
rider-events        rider id   requested, matched, picked_up, dropped_off, cancelled
driver-events       driver id  status, ping
dispatch-offers     driver id  offer
offer-responses     rider id   offer_response
dispatch-batches    run id     batch

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
ALL_TOPICS = (RIDER_EVENTS, DRIVER_EVENTS, DISPATCH_OFFERS, OFFER_RESPONSES, DISPATCH_BATCHES)
WORLD_TOPICS = (RIDER_EVENTS, DRIVER_EVENTS)  # carry run_start / tick / run_end on every partition

CONTROL_TYPES = frozenset({"run_start", "tick", "run_end"})


class _Base(TypedDict):
    v: int
    type: str
    run: str
    t: float


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


class DriverStatus(_Base):
    driver: int
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


def encode(msg: dict) -> bytes:
    return json.dumps(msg, separators=(",", ":")).encode()


def decode(raw: bytes) -> dict:
    return json.loads(raw)


# ------------------------------------------------------------------ config
def run_config(dispatch: DispatchConfig, travel: TravelConfig, offer_timeout_s: float) -> dict:
    return {"dispatch": asdict(dispatch), "travel": asdict(travel), "offer_timeout_s": offer_timeout_s}


def dispatch_from_dict(d: dict) -> DispatchConfig:
    cost = dict(d["cost"])
    cost["cancel"] = CancelBelief(**cost["cancel"]) if cost.get("cancel") else None
    return DispatchConfig(**{**d, "cost": CostParams(**cost)})


def travel_from_dict(d: dict) -> TravelConfig:
    return TravelConfig(**d)
