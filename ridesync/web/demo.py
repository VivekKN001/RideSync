"""The live map without Kafka, Flink or Docker: simulator and matcher in one process.

    python -m ridesync.web --demo                     # http://localhost:8000, July 2026 evening at 30x, looping
    python -m ridesync.web --demo --speed 60 --drivers 350

The live simulator and the matcher talk over an in-memory bus, as in the lockstep runner
(``ridesync.live.lockstep``), and a tick waits for the wall clock before the next one, so the run plays at
``speed`` simulated seconds per second. Every world event also goes to the map's ``LiveView``, and zone
pressure comes from the Flink job's own feature code (``FeatureStream``) run in-process. The page can't
tell the difference from the full stack.

``ridesync.web.record`` uses the same run, unpaced, to record the static replay.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from ..live.bus import InMemoryBus
from ..live.matcher import Matcher
from ..live.schema import DRIVER_EVENTS, RIDER_EVENTS
from ..live.world import LiveConfig, LiveSimulation
from ..sim.config import SimConfig
from ..stream.features import FeatureStream
from ..stream.zones import ZONES_JSON, ZoneIndex

PING_S = 5.0   # driver location pings, simulated seconds (the live default)
PAUSE_S = 8.0  # wall seconds the finished run stays on screen before the next loop


class Stopped(Exception):
    """The server is shutting down."""


class FeedBus(InMemoryBus):
    """In-memory bus that also hands every world event to ``sink``.

    Pings go to the sink only: the matcher skips them, and keeping them would add about a million
    messages per 3-hour run to the log.
    """

    def __init__(self, sink: Callable[[dict], None]):
        super().__init__(partitions=1)
        self.sink = sink

    def produce(self, topic: str, key: str, value: dict, partition: Optional[int] = None) -> None:
        if topic in (RIDER_EVENTS, DRIVER_EVENTS):
            self.sink(value)
        if value["type"] != "ping":
            super().produce(topic, key, value, partition)


class MapFeed:
    """World events -> the map's view, plus the zone_minute rows Flink would have written."""

    def __init__(self, view, zones: Optional[ZoneIndex]):
        self.view = view
        self.features = FeatureStream(zones) if zones is not None else None

    def __call__(self, msg: dict) -> None:
        self.view.apply(msg)
        if self.features is not None:
            for row in self.features.feed(msg):
                self.view.apply(row)


def load_zones(path: str = ZONES_JSON) -> Optional[ZoneIndex]:
    """Taxi zones for zone pressure, or None (the map then shows no pressure) if they haven't been built."""
    return ZoneIndex.load(path) if Path(path).exists() else None


def run_once(cfg: SimConfig, view, speed: float, stop: threading.Event, zones: Optional[ZoneIndex] = None,
             on_tick: Optional[Callable[[float], None]] = None) -> LiveSimulation:
    """One run into ``view``. ``speed`` <= 0 runs unpaced. Raises Stopped when ``stop`` is set."""
    bus = FeedBus(MapFeed(view, zones))
    sim = LiveSimulation(cfg, bus, LiveConfig(speed=0.0, tick_s=1.0, ping_s=PING_S))
    matcher = Matcher(bus, travel=sim.travel)
    wall0 = time.monotonic()

    def settle() -> None:
        while matcher.step() + sim.poll(0.0):
            pass

    def tick() -> None:
        settle()
        if on_tick is not None:
            on_tick(sim.now)
        ahead = sim.now / speed - (time.monotonic() - wall0) if speed > 0 else 0.0
        if stop.wait(ahead) if ahead > 0 else stop.is_set():
            raise Stopped

    sim.lockstep = tick
    sim.run()
    settle()
    return sim


@dataclass
class DemoLoop:
    """Plays ``cfg`` into ``view`` over and over, on a daemon thread."""
    cfg: SimConfig
    view: object
    speed: float = 30.0

    def __post_init__(self):
        self.stop = threading.Event()
        self.zones = load_zones()

    def _loop(self) -> None:
        while not self.stop.is_set():
            try:
                run_once(self.cfg, self.view, self.speed, self.stop, self.zones)
            except Stopped:
                return
            self.stop.wait(PAUSE_S)

    def start(self) -> None:
        threading.Thread(target=self._loop, name="ridesync-demo", daemon=True).start()
