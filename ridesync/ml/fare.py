"""Fare model (M6): fit ``FareConfig`` to TLC ``base_passenger_fare``.

    fare = max(min_fare, base + per_mile * miles + per_min * minutes)

TLC fares already include Uber's and Lyft's own surge, so the fit uses weekday late mornings and
early afternoons (10:00-15:59), when surge is rarest, and a median (quantile) regression, which the
few surged trips left barely move. ``road_factor`` turns straight-line distance into trip miles; it
is fitted on the same zone points the ETA model uses.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from ..pricing import fares  # noqa: F401  (re-exported)
from ..sim.config import FareConfig

FARE_PATH = "data/models/fare.json"


def fare_from_file(path: str = FARE_PATH) -> FareConfig:
    d = json.loads(Path(path).read_text())
    return FareConfig(**{k: d[k] for k in asdict(FareConfig()) if k in d})


def train(month: str = "2024-03", n: int = 30000, seed: int = 0) -> dict:
    from sklearn.linear_model import QuantileRegressor

    from ..geo import haversine_pairs_m
    from .common import read_service_trips, service_zones
    from .eta import zone_points

    zones = service_zones()
    df = read_service_trips(month, ["request_datetime", "PULocationID", "DOLocationID", "trip_miles", "trip_time",
                                    "base_passenger_fare"], zones)
    t = df["request_datetime"]
    calm = (t.dt.weekday < 5) & (t.dt.hour >= 10) & (t.dt.hour < 16)
    ok = calm & (df["base_passenger_fare"] > 0) & (df["trip_miles"] > 0.1) & (df["trip_time"] > 60)
    d = df[ok].sample(n=min(n, int(ok.sum())), random_state=seed)
    X = np.column_stack([d["trip_miles"], d["trip_time"] / 60.0])
    y = d["base_passenger_fare"].to_numpy()
    q = QuantileRegressor(quantile=0.5, alpha=0.0, solver="highs").fit(X, y)

    # Straight-line -> road miles, from the zone points (one random point per trip end).
    pts = zone_points(zones)
    rng = np.random.default_rng(seed)
    by_zone = {int(z): g[["lat", "lon"]].to_numpy() for z, g in pts.groupby("zone")}
    pu = np.array([by_zone[int(z)][rng.integers(len(by_zone[int(z)]))] for z in d["PULocationID"]])
    do = np.array([by_zone[int(z)][rng.integers(len(by_zone[int(z)]))] for z in d["DOLocationID"]])
    straight = haversine_pairs_m(pu, do)
    road_factor = float(np.median(d["trip_miles"].to_numpy() * 1609.344 / np.maximum(straight, 50.0)))

    fit = {
        "base": float(q.intercept_), "per_mile": float(q.coef_[0]), "per_min": float(q.coef_[1]),
        "min_fare": float(np.percentile(y, 2)), "road_factor": road_factor,
        "n": int(len(d)), "median_fare": float(np.median(y)),
        "mae": float(np.mean(np.abs(q.predict(X) - y))), "all_hours_median_fare": float(df.loc[df["base_passenger_fare"] > 0, "base_passenger_fare"].median()),
    }
    Path(FARE_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(FARE_PATH).write_text(json.dumps(fit, indent=2))
    return fit
