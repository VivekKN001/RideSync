"""Run the live simulator and matcher in one process over an in-memory bus, with zero latency.

At every tick the matcher runs until it has nothing left to do, and the offers
it sends are applied at the tick's own time. This is exactly what the offline
engine does, so a lockstep run must give identical results to ``simulate``.
The test suite checks that, which proves the live code path (events,
serialization, the matcher's rebuilt view of the world, watermarks) loses
nothing. Any difference in a real Kafka run then comes from latency alone.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Optional, Tuple

from ..geo import TravelTimeModel
from ..sim.config import SimConfig
from .bus import InMemoryBus
from .matcher import Matcher
from .world import LiveConfig, LiveSimulation


def run_lockstep(
    cfg: SimConfig,
    partitions: int = 1,
    live: Optional[LiveConfig] = None,
    travel: Optional[TravelTimeModel] = None,
    bus: Optional[InMemoryBus] = None,
) -> Tuple[LiveSimulation, Matcher]:
    """``bus`` overrides the default ``InMemoryBus(partitions)`` (tests pass one that reorders delivery)."""
    live = replace(live or LiveConfig(ping_s=0.0), speed=0.0, tick_s=cfg.dispatch.interval_s)
    bus = bus if bus is not None else InMemoryBus(partitions)
    sim = LiveSimulation(cfg, bus, live, travel)
    matcher = Matcher(bus, travel=sim.travel)

    def settle() -> None:
        while matcher.step() + sim.poll(0.0):
            pass

    sim.lockstep = settle
    sim.run()
    settle()
    return sim, matcher
