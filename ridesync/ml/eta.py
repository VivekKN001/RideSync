"""ETA correction (M6): a learned multiplier on top of any travel-time model.

The base model (the calibrated straight line, or OSRM times the global multiplier) gets the average
right but not where and when it is wrong: Midtown at 18:00 is slower than the Upper West Side at
noon. The model learns ``log(observed / base)`` from TLC trip times with the features

    log base seconds, log straight-line metres, pickup zone, dropoff zone, hour of day, weekday

and ``CorrectedModel`` multiplies the base's times by ``exp(prediction)``. It learns from trips
(pickup to dropoff with a passenger) and is applied to every drive, including drives to a pickup,
for which no data exists: an assumption, stated in FINDINGS.

TLC gives zones, not points. Training therefore places each trip end on one of a fixed set of
points per zone (``zone_points``), so the base times form one small matrix that is computed once,
also with OSRM. The random placement puts a floor under the error, which ``evaluate`` reports.

``NoisyModel`` is the world side of the M6 experiment: each route's duration gets lognormal noise,
seeded by the route's endpoints (not call order), so every arm sees the same noise on the same drive.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from ..geo import Route, TravelTimeModel, haversine_m, haversine_pairs_m

FEATURES = ["log_base_s", "log_dist_m", "pu_zone", "do_zone", "hour", "dow"]
CATEGORICAL = [FEATURES.index("pu_zone"), FEATURES.index("do_zone")]
MODEL_PATH = "data/models/eta_{base}.joblib"
POINTS_PATH = "data/models/zone_points.parquet"
FACTOR_CLIP = (0.4, 4.0)  # a prediction outside this is a model error, not traffic


def eta_features(base_s: np.ndarray, dist_m: np.ndarray, pu_idx: np.ndarray, do_idx: np.ndarray,
                 hour: np.ndarray, dow: np.ndarray) -> np.ndarray:
    n = len(base_s)
    return np.column_stack([
        np.log(np.maximum(base_s, 1.0)), np.log(np.maximum(dist_m, 1.0)),
        pu_idx.astype(float), do_idx.astype(float),
        np.broadcast_to(np.asarray(hour, dtype=float), (n,)), np.broadcast_to(np.asarray(dow, dtype=float), (n,)),
    ])


# ------------------------------------------------------------------ wrappers
class CorrectedModel:
    """``base`` times exp(model prediction). Needs the absolute time for hour/weekday features:
    ``start`` is simulated t = 0, and ``set_time`` moves the clock (``build_batch`` calls it)."""

    def __init__(self, base: TravelTimeModel, bundle: dict, zones, start: Optional[datetime] = None):
        self.base = base
        self.model = bundle["model"]
        self.zone_col = {int(z): i for i, z in enumerate(bundle["zones"])}
        self.zones = zones  # ridesync.stream.zones.ZoneIndex
        self.start = start
        self.t = 0.0
        self._zone_cache: Dict[Tuple[float, float], float] = {}
        self.fallbacks = getattr(base, "fallbacks", 0)

    def set_time(self, t: float) -> None:
        self.t = t

    def _clock(self) -> Tuple[float, float]:
        if self.start is None:
            return np.nan, np.nan  # unknown date: the trees send these down their "missing" branches
        now = self.start + timedelta(seconds=self.t)
        return now.hour + now.minute / 60.0, float(now.weekday())

    def _zone_idx(self, pts: np.ndarray) -> np.ndarray:
        out = np.empty(len(pts))
        for i, (lat, lon) in enumerate(pts):
            key = (round(float(lat), 4), round(float(lon), 4))  # ~10 m: idle drivers don't move
            v = self._zone_cache.get(key)
            if v is None:
                if len(self._zone_cache) > 200_000:
                    self._zone_cache.clear()
                v = self._zone_cache[key] = float(self.zone_col.get(self.zones.zone_of(lat, lon), np.nan))
            out[i] = v
        return out

    def factor(self, base_s: np.ndarray, origins: np.ndarray, dests: np.ndarray) -> np.ndarray:
        """Correction factors for base times (N, M) between origins (N, 2) and dests (M, 2)."""
        n, m = base_s.shape
        ok = np.isfinite(base_s)
        f = np.ones_like(base_s)
        if not ok.any():
            return f
        oi, dj = np.nonzero(ok)
        zo, zd = self._zone_idx(origins), self._zone_idx(dests)
        dist = haversine_m(origins, dests)
        hour, dow = self._clock()
        X = eta_features(base_s[ok], dist[ok], zo[oi], zd[dj], hour, dow)
        f[ok] = np.clip(np.exp(self.model.predict(X)), *FACTOR_CLIP)
        return f

    def matrix(self, origins: np.ndarray, dests: np.ndarray) -> np.ndarray:
        origins, dests = np.atleast_2d(origins), np.atleast_2d(dests)
        base = self.base.matrix(origins, dests)
        return base * self.factor(base, origins, dests)

    def route(self, a: np.ndarray, b: np.ndarray) -> Route:
        r = self.base.route(a, b)
        if r.duration_s <= 0:
            return r
        f = float(self.factor(np.array([[r.duration_s]]), np.atleast_2d(a), np.atleast_2d(b))[0, 0])
        return Route(r.duration_s * f, r.path, r.cum_s * f)


class NoisyModel:
    """Real drives vary: each route's duration times exp(sigma * z), z ~ N(0, 1) seeded by its endpoints.

    ``matrix`` stays noise-free: it is what anyone can expect, so a quote made from it is off by the noise.
    """

    def __init__(self, inner: TravelTimeModel, sigma: float, seed: int = 0):
        self.inner = inner
        self.sigma = sigma
        self.seed = seed

    def set_time(self, t: float) -> None:
        if hasattr(self.inner, "set_time"):
            self.inner.set_time(t)

    @property
    def fallbacks(self) -> int:
        return getattr(self.inner, "fallbacks", 0)

    def matrix(self, origins: np.ndarray, dests: np.ndarray) -> np.ndarray:
        return self.inner.matrix(origins, dests)

    def route(self, a: np.ndarray, b: np.ndarray) -> Route:
        r = self.inner.route(a, b)
        if r.duration_s <= 0 or self.sigma <= 0:
            return r
        key = [int(round((float(v) + 180.0) * 1e5)) for v in (*np.ravel(a), *np.ravel(b))]
        f = float(np.exp(self.sigma * np.random.default_rng([self.seed, 7, *key]).standard_normal()))
        return Route(r.duration_s * f, r.path, r.cum_s * f)


def load_bundle(path: str) -> dict:
    import joblib

    return joblib.load(path)


def wrap(base: TravelTimeModel, bundle: Optional[dict], noise_sigma: float, start: Optional[datetime],
         seed: int = 0, zones_path: str = "data/processed/taxi_zones.json") -> TravelTimeModel:
    """The travel model a ``TravelConfig`` describes on top of its base: correction, then noise."""
    model = base
    if bundle is not None:
        from ..stream.zones import ZoneIndex

        model = CorrectedModel(base, bundle, ZoneIndex.load(zones_path), start)
    if noise_sigma > 0:
        model = NoisyModel(model, noise_sigma, seed)
    return model


# ------------------------------------------------------------------ training data
def zone_points(zones_ids: Sequence[int], per_zone: int = 8, seed: int = 0, path: str = POINTS_PATH):
    """Fixed random points inside each zone (cached): columns zone, k, lat, lon."""
    import pandas as pd

    p = Path(path)
    if p.exists():
        pts = pd.read_parquet(p)
        if set(pts["zone"]) >= set(zones_ids) and pts.groupby("zone").size().min() >= per_zone:
            return pts
    from ..data.tlc import load_zones, sample_points_in_zones

    ids = np.repeat(np.asarray(zones_ids, dtype=int), per_zone)
    xy = sample_points_in_zones(load_zones(), ids, np.random.default_rng(seed))
    pts = pd.DataFrame({"zone": ids, "k": np.tile(np.arange(per_zone), len(zones_ids)), "lat": xy[:, 0], "lon": xy[:, 1]})
    p.parent.mkdir(parents=True, exist_ok=True)
    pts.to_parquet(p, index=False)
    return pts


def base_matrix(points: np.ndarray, base: TravelTimeModel, cache: Optional[str] = None) -> np.ndarray:
    """Base travel times between all pool points, cached to ``cache`` (the OSRM table takes a minute)."""
    if cache and Path(cache).exists():
        m = np.load(cache)
        if m.shape == (len(points), len(points)):
            return m
    m = base.matrix(points, points)
    if cache:
        Path(cache).parent.mkdir(parents=True, exist_ok=True)
        np.save(cache, m)
    return m


@dataclass
class TripSample:
    base_s: np.ndarray
    base2_s: np.ndarray  # the same trip placed on other random points: the placement noise floor
    dist_m: np.ndarray
    pu_idx: np.ndarray
    do_idx: np.ndarray
    hour: np.ndarray
    dow: np.ndarray
    observed_s: np.ndarray
    train: np.ndarray

    def X(self, mask=None) -> np.ndarray:
        m = slice(None) if mask is None else mask
        return eta_features(self.base_s[m], self.dist_m[m], self.pu_idx[m], self.do_idx[m], self.hour[m], self.dow[m])


def place_trips(trips, pts, P: np.ndarray, zones: Sequence[int], month: str, seed: int = 0) -> TripSample:
    """Put each trip's ends on random pool points of their zones; look up base times and distances."""
    from .common import is_train_day

    rng = np.random.default_rng(seed)
    per_zone = int(pts.groupby("zone").size().min())
    first = {int(z): int(i) for z, i in pts.reset_index().groupby("zone")["index"].min().items()}
    xy = pts[["lat", "lon"]].to_numpy()
    zi = {int(z): i for i, z in enumerate(zones)}

    def pick(zone_ids):
        base = np.array([first[int(z)] for z in zone_ids])
        return base + rng.integers(0, per_zone, len(zone_ids)), base + rng.integers(0, per_zone, len(zone_ids))

    pu, pu2 = pick(trips["PULocationID"].to_numpy())
    do, do2 = pick(trips["DOLocationID"].to_numpy())
    t = trips["request_datetime"]
    return TripSample(
        base_s=P[pu, do], base2_s=P[pu2, do2], dist_m=haversine_pairs_m(xy[pu], xy[do]),
        pu_idx=trips["PULocationID"].map(zi).to_numpy(float), do_idx=trips["DOLocationID"].map(zi).to_numpy(float),
        hour=(t.dt.hour + t.dt.minute / 60.0).to_numpy(float), dow=t.dt.weekday.to_numpy(float),
        observed_s=trips["trip_time"].to_numpy(float), train=is_train_day(t, month).to_numpy(),
    )


def _errors(obs: np.ndarray, pred: np.ndarray) -> dict:
    ape = np.abs(pred - obs) / obs
    return {"mae_s": float(np.mean(np.abs(pred - obs))), "mape": float(np.mean(ape)),
            "median_ape": float(np.median(ape)), "p90_ape": float(np.percentile(ape, 90)),
            "bias_s": float(np.mean(pred - obs))}


def fit_and_evaluate(s: TripSample, max_iter: int = 300) -> Tuple[object, List[dict], dict]:
    """Fit on training days; compare with the base alone and a pickup-zone x hour table on test days."""
    from sklearn.ensemble import HistGradientBoostingRegressor

    ok = np.isfinite(s.base_s) & (s.base_s > 30) & np.isfinite(s.base2_s) & ~np.isnan(s.pu_idx) & ~np.isnan(s.do_idx)
    tr, te = ok & s.train, ok & ~s.train
    y = np.log(s.observed_s / s.base_s)
    model = HistGradientBoostingRegressor(
        loss="squared_error", learning_rate=0.05, max_iter=max_iter, max_leaf_nodes=63, min_samples_leaf=100,
        l2_regularization=1.0, categorical_features=CATEGORICAL, early_stopping=False, random_state=0,
    ).fit(s.X(tr), y[tr])

    obs, base = s.observed_s[te], s.base_s[te]
    pred_model = base * np.clip(np.exp(model.predict(s.X(te))), *FACTOR_CLIP)
    # Baselines: one global factor (the base is already calibrated, so this is ~1), and a lookup table.
    g = float(np.exp(np.median(y[tr])))
    key_tr = s.pu_idx[tr] * 24 + np.floor(s.hour[tr])
    key_te = s.pu_idx[te] * 24 + np.floor(s.hour[te])
    table: Dict[float, float] = {}
    for k in np.unique(key_tr):
        sel = key_tr == k
        if sel.sum() >= 30:
            table[float(k)] = float(np.exp(np.median(y[tr][sel])))
    pred_table = base * np.array([table.get(float(k), g) for k in key_te])
    rows = [
        {"method": "base model alone (global calibration)", **_errors(obs, base)},
        {"method": "base x global median factor", **_errors(obs, base * g)},
        {"method": "base x pickup-zone x hour table", **_errors(obs, pred_table)},
        {"method": "base x learned correction (GBT)", **_errors(obs, pred_model)},
    ]
    resid = np.log(obs / pred_model)
    extra = {
        "train_trips": int(tr.sum()), "test_trips": int(te.sum()), "global_factor": g,
        # Two random placements of the same trip disagree by this much before any model is involved.
        "placement_median_ape": float(np.median(np.abs(s.base2_s[te] - base) / base)),
        "residual_sigma": float(np.std(resid)),
        "residual_iqr_sigma": float((np.percentile(resid, 75) - np.percentile(resid, 25)) / 1.349),
    }
    return model, rows, extra


def train(base_kind: str = "straight", month: str = "2024-03", per_day: int = 20000, osrm_url: str = "http://localhost:5000",
          max_iter: int = 300, seed: int = 0) -> Tuple[dict, List[dict], dict]:
    """Sample trips, place them on zone points, fit the correction for a base model. Returns (bundle, rows, extra)."""
    from ..routing import make_travel_model, travel_from_calibration
    from .common import read_service_trips, service_zones

    zones = service_zones()
    tcfg = travel_from_calibration(base_kind, osrm_url)
    base = make_travel_model(tcfg)
    pts = zone_points(zones)
    P = base_matrix(pts[["lat", "lon"]].to_numpy(), base, cache=f"data/models/pool_{base_kind}.npy")

    trips = read_service_trips(month, ["request_datetime", "PULocationID", "DOLocationID", "trip_time"], zones)
    trips = trips[(trips["trip_time"] > 60) & (trips["trip_time"] < 3 * 3600)]
    trips = trips.sample(frac=1.0, random_state=seed)
    trips = trips.groupby(trips["request_datetime"].dt.day).head(per_day)
    sample = place_trips(trips.reset_index(drop=True), pts, P, zones, month, seed)
    model, rows, extra = fit_and_evaluate(sample, max_iter)
    base_sig = {"model": tcfg.model, "speed_mps": tcfg.speed_mps, "detour": tcfg.detour,
                "time_multiplier": tcfg.time_multiplier}
    bundle = {"model": model, "zones": list(map(int, zones)), "base": base_sig, "features": FEATURES, **extra}
    return bundle, rows, extra


def check_base(bundle: dict, travel_cfg) -> None:
    """A correction only fits the base it was trained on (same model and calibration)."""
    sig = bundle.get("base", {})
    mine = {"model": travel_cfg.model, "speed_mps": travel_cfg.speed_mps, "detour": travel_cfg.detour,
            "time_multiplier": travel_cfg.time_multiplier}
    keys = ["model", "time_multiplier"] if mine["model"] == "osrm" else ["model", "speed_mps", "detour"]
    for k in keys:
        a, b = sig.get(k), mine[k]
        if a is None or (a != b and not (isinstance(a, float) and abs(a - b) < 1e-9)):
            raise ValueError(f"ETA correction was trained on base {sig}, but the travel config is {mine}")
