"""Travel-time model selection. The simulator and matcher only see ``TravelTimeModel``."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from ..geo import StraightLineModel, TravelTimeModel

if TYPE_CHECKING:  # the sim package imports this module, so no runtime import back into it
    from ..sim.config import TravelConfig


CALIBRATION = "data/processed/calibration.json"


def travel_from_calibration(kind: str, osrm_url: str = "http://localhost:5000", path: str = CALIBRATION) -> "TravelConfig":
    """Travel config fitted to TLC trip times by ``python -m ridesync.routing.calibrate``."""
    import json
    from pathlib import Path

    from ..sim.config import TravelConfig

    cal = json.loads(Path(path).read_text())
    if kind == "straight":
        s = cal["straight"]
        return TravelConfig(model="straight", speed_mps=s["speed_mps"], detour=s["detour"])
    if kind != "osrm":
        raise ValueError(f"unknown travel model {kind!r}; use 'straight' or 'osrm'")
    if "osrm" not in cal:
        raise RuntimeError("no OSRM calibration yet: run `python -m ridesync.routing.calibrate --slice ... --osrm URL`")
    return TravelConfig(model="osrm", osrm_url=osrm_url, time_multiplier=cal["osrm"]["time_multiplier"])


def _base_model(cfg: "TravelConfig") -> TravelTimeModel:
    if cfg.model == "straight":
        return StraightLineModel(cfg.speed_mps, cfg.detour)
    if cfg.model == "osrm":
        from .osrm import OSRMModel

        return OSRMModel(base_url=cfg.osrm_url, time_multiplier=cfg.time_multiplier)
    raise ValueError(f"unknown travel model {cfg.model!r}; use 'straight' or 'osrm'")


def make_travel_model(cfg: "TravelConfig", start: Optional[datetime] = None, seed: int = 0) -> TravelTimeModel:
    """The base model, then the M6 ETA correction and per-trip noise if the config asks for them.

    ``start`` is the wall-clock time of simulated t = 0 (the correction uses time of day); ``seed``
    seeds the noise.
    """
    model = _base_model(cfg)
    if cfg.eta_model is None and cfg.noise_sigma <= 0:
        return model
    from ..ml.eta import check_base, load_bundle, wrap

    bundle = load_bundle(cfg.eta_model) if cfg.eta_model else None
    if bundle is not None:
        check_base(bundle, cfg)
    return wrap(model, bundle, cfg.noise_sigma, start, seed)
