"""Live pricing service (M6): Flink zone features in, surge prices per zone out.

    python -m ridesync.live.pricing                 # terminal: runs until Ctrl+C
    python -m ridesync.live.sim --surge forecast --price-service

It follows the newest run whose ``run_start`` asks for service pricing, and uses that run's pricing
config. From every closed zone-minute (``zone-features``) it keeps, per zone:

- app opens (``quotes``) for the demand estimate, reactive or forecast (``ridesync.pricing``);
- free drivers at the end of the latest minute (``idle_end``);
- riders waiting: requests - matches - cancellations, summed over minutes.

Every ``interval_s`` of event time it publishes ``prices`` on ``zone-prices``; the simulator
applies the latest ones to riders who open the app after they arrive. Unlike the simulator's own
pricing it cannot see drivers about to finish a trip, and it lags by the Flink window plus the
watermark allowance: that is the price of running it as a separate service.
"""
from __future__ import annotations

import argparse
import sys
import time
from collections import defaultdict
from dataclasses import fields
from datetime import datetime
from typing import Dict, Optional

from ..pricing import DemandEstimator, zone_prices
from ..sim.config import PricingConfig
from .bus import Bus, Message
from .schema import RIDER_EVENTS, VERSION, ZONE_FEATURES, ZONE_PRICES

# From rider-events the service only needs run_start; skip the rest without decoding it.
SKIP = ("quoted", "requested", "matched", "picked_up", "dropped_off", "cancelled", "tick", "run_end")


class PricingService:
    def __init__(self, bus: Bus, forecaster=None):
        self.bus = bus
        self.consumer = bus.consumer([RIDER_EVENTS, ZONE_FEATURES], from_beginning=False, skip_types=SKIP)
        self.producer = bus.producer()
        self.forecaster = forecaster
        self.run: Optional[str] = None
        self.started_ms = -1
        self.published = 0

    def _start_run(self, v: dict) -> None:
        cfg = v.get("config") or {}
        self.started_ms = v["started_ms"]
        p = cfg.get("pricing") or {}
        if not p.get("enabled") or cfg.get("price_source") != "service":
            self.run = None  # this run prices itself (or not at all)
            return
        self.run = v["run"]
        known = {f.name for f in fields(PricingConfig)}
        self.cfg = PricingConfig(**{k: val for k, val in p.items() if k in known})
        start = datetime.fromisoformat(cfg["start"]) if cfg.get("start") else None
        fc = self.forecaster if self.cfg.demand == "forecast" else None
        if self.cfg.demand == "forecast" and fc is None:
            from ..ml.demand import load_or_none

            fc = self.forecaster = load_or_none(self.cfg.forecast_path)
        self.est = DemandEstimator(self.cfg, start, float(cfg.get("sample_frac") or 1.0), fc)
        self.idle: Dict[int, tuple] = {}             # zone -> (minute, free drivers at its end)
        self.waiting: Dict[int, float] = defaultdict(float)
        self.next_t = self.cfg.interval_s
        print(f"pricing: run {self.run}, {self.cfg.demand} demand", flush=True)

    def handle(self, m: Message) -> None:
        v = m.value
        typ = v.get("type")
        if typ == "run_start":
            if v.get("started_ms", 0) > self.started_ms:
                self._start_run(v)
            return
        if typ != "zone_minute" or self.run is None or v.get("run") != self.run:
            return
        z = int(v["zone"])
        if z == 0:
            return  # outside every zone
        self.est.add_open(z, v["t"] + 59.0, v.get("quotes", 0))
        if z not in self.idle or v["minute"] >= self.idle[z][0]:
            self.idle[z] = (v["minute"], v["idle_end"])
        self.waiting[z] = max(0.0, self.waiting[z] + v["requests"] - v["matches"] - v["cancels_no_match"] - v["cancels_eta"])
        while v["t"] >= self.next_t:  # a minute at or after the boundary closed: price as of the boundary
            self._publish(self.next_t, v["ts"])
            self.next_t += self.cfg.interval_s

    def _publish(self, t: float, ts: int) -> None:
        supply = {z: float(n) for z, (_, n) in self.idle.items()}
        zones = set(supply) | set(self.waiting) | set(self.est.recent)
        if self.est.fc is not None:
            zones |= set(self.est.fc.zones)
        zones = sorted(zones)
        demand = self.est.estimate(zones, t)
        prices = zone_prices(zones, demand, self.waiting, supply, self.cfg)
        self.producer.produce(ZONE_PRICES, self.run, {
            "v": VERSION, "type": "prices", "run": self.run, "t": t, "ts": ts,
            "prices": {str(z): p for z, p in prices.items()},
            "demand": {str(z): round(demand.get(z, 0.0), 3) for z in zones},
            "supply": {str(z): supply.get(z, 0.0) for z in zones},
            "source": f"service:{self.cfg.demand}",
        })
        self.published += 1

    def step(self, timeout_s: float = 0.0) -> int:
        msgs = self.consumer.poll(timeout_s)
        for m in msgs:
            self.handle(m)
        if msgs:
            self.producer.flush()
        return len(msgs)


def main(argv=None) -> None:
    from .kafka_bus import KafkaBus
    from .topics import ensure_topics

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--bootstrap", default="localhost:9092")
    ap.add_argument("--prefix", default="")
    args = ap.parse_args(argv)
    ensure_topics(args.bootstrap, prefix=args.prefix)
    svc = PricingService(KafkaBus(args.bootstrap, args.prefix))
    print("pricing: waiting for a run with --price-service", flush=True)
    last = time.monotonic()
    try:
        while True:
            svc.step(0.1)
            if time.monotonic() - last > 10:
                last = time.monotonic()
                if svc.run:
                    print(f"pricing: run {svc.run} next={svc.next_t:.0f}s published={svc.published}", flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        svc.producer.flush()
        svc.consumer.close()
    sys.exit(0)


if __name__ == "__main__":
    main()
