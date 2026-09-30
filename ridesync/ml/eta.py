"""ETA correction (M6): a learned multiplier on top of any travel-time model.

The base model (the calibrated straight line, or OSRM times the global multiplier) gets the average
right but not where and when it is wrong: Midtown at 18:00 is slower than the Upper West Side at
noon. The model learns ``log(observed / base)`` from TLC trip times with the features

    log base seconds, log straight-line metres, pickup zone, dropoff zone, hour of day, weekday, month,
    and live traffic: recent speeds city-wide and around both zones (``TrafficFeed``)

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

from ..env import MODELS_DIR
from ..geo import Route, TravelTimeModel, haversine_m, haversine_pairs_m

FEATURES = ["log_base_s", "log_dist_m", "pu_zone", "do_zone", "hour", "dow", "month"]
TRAFFIC_FEATURES = ["city_mph_30", "city_trips_30", "pu_mph_60", "do_mph_60"]
CATEGORICAL = [FEATURES.index("pu_zone"), FEATURES.index("do_zone")]
MODEL_PATH = MODELS_DIR + "/eta_{base}.joblib"
POINTS_PATH = "data/models/zone_points.parquet"
FACTOR_CLIP = (0.4, 4.0)  # a prediction outside this is a model error, not traffic


def eta_features(base_s: np.ndarray, dist_m: np.ndarray, pu_idx: np.ndarray, do_idx: np.ndarray,
                 hour: np.ndarray, dow: np.ndarray, month: np.ndarray, traffic: Optional[np.ndarray] = None) -> np.ndarray:
    """The model's input columns: ``FEATURES``, then ``TRAFFIC_FEATURES`` when ``traffic`` (n, 4) is given."""
    n = len(base_s)
    cols = [
        np.log(np.maximum(base_s, 1.0)), np.log(np.maximum(dist_m, 1.0)),
        pu_idx.astype(float), do_idx.astype(float),
        np.broadcast_to(np.asarray(hour, dtype=float), (n,)), np.broadcast_to(np.asarray(dow, dtype=float), (n,)),
        np.broadcast_to(np.asarray(month, dtype=float), (n,)),
    ]
    if traffic is not None:
        cols += [traffic[:, k] for k in range(traffic.shape[1])]
    return np.column_stack(cols)


class TrafficFeed:
    """Recent road speeds, measured from trips that have already finished: a stand-in for a live feed.

    Time is cut into 5-minute buckets. A request in bucket b sees only trips that dropped off in the
    buckets before b, so neither its own trip nor any later one leaks in. Per request:

    - ``city_mph_30``, ``city_trips_30``: speed (trip miles / trip hours, summed) and count of all trips
      finished in the last 30 minutes. The count is a congestion proxy of its own.
    - ``pu_mph_60``, ``do_mph_60``: speed of trips that started in the pickup zone, or ended in the
      dropoff zone, over the last 60 minutes.

    A speed from fewer than ``MIN_TRIPS`` trips, or a time outside the table, is NaN (the trees have
    a branch for missing values). Built from full-scale TLC trips, so a 10% simulation still sees the
    real city's traffic, as a deployed service would.
    """

    BUCKET_S = 300
    CITY_BUCKETS, ZONE_BUCKETS = 6, 12
    MIN_TRIPS = 5

    def __init__(self, t0: datetime, city_mph: np.ndarray, city_n: np.ndarray, pu_mph: np.ndarray, do_mph: np.ndarray):
        self.t0 = t0
        self.city_mph, self.city_n, self.pu_mph, self.do_mph = city_mph, city_n, pu_mph, do_mph

    @classmethod
    def from_trips(cls, trips, zones: Sequence[int], t0: datetime) -> "TrafficFeed":
        """``trips``: dropoff_datetime, PULocationID, DOLocationID, trip_miles, trip_time (s)."""
        zi = {int(z): i for i, z in enumerate(zones)}
        b = ((trips["dropoff_datetime"] - t0).dt.total_seconds().to_numpy() // cls.BUCKET_S).astype(np.int64)
        ok = b >= 0
        nb = int(b[ok].max()) + 2 if ok.any() else 1
        miles, secs = trips["trip_miles"].to_numpy(float), trips["trip_time"].to_numpy(float)

        def windowed(idx_z, k):
            """Per request bucket (and zone), sums over the k buckets before it: miles, seconds, trips."""
            shape = (nb,) if idx_z is None else (nb, len(zones))
            out = []
            for w in (miles, secs, np.ones_like(miles)):
                acc = np.zeros(shape)
                sel = ok if idx_z is None else ok & ~np.isnan(idx_z)
                if idx_z is None:
                    np.add.at(acc, b[sel], w[sel])
                else:
                    np.add.at(acc, (b[sel], idx_z[sel].astype(np.int64)), w[sel])
                cum = np.concatenate([np.zeros((1,) + shape[1:]), np.cumsum(acc, axis=0)])  # cum[i] = buckets < i
                lo = np.maximum(np.arange(nb) - k, 0)
                out.append(cum[np.arange(nb)] - cum[lo])
            return out

        def mph(m, s, n):
            with np.errstate(divide="ignore", invalid="ignore"):
                v = m / (s / 3600.0)
            return np.where(n >= cls.MIN_TRIPS, v, np.nan).astype(np.float32)

        pu = trips["PULocationID"].map(zi).to_numpy(float)
        do = trips["DOLocationID"].map(zi).to_numpy(float)
        cm, cs, cn = windowed(None, cls.CITY_BUCKETS)
        return cls(t0, mph(cm, cs, cn), cn.astype(np.float32),
                   mph(*windowed(pu, cls.ZONE_BUCKETS)), mph(*windowed(do, cls.ZONE_BUCKETS)))

    def lookup(self, seconds_since_t0: np.ndarray, pu_idx: np.ndarray, do_idx: np.ndarray) -> np.ndarray:
        """(n, 4) traffic features for requests at the given times and zone columns."""
        n = len(pu_idx)
        b = np.floor(np.broadcast_to(np.asarray(seconds_since_t0, dtype=float), (n,)) / self.BUCKET_S)
        out = np.full((n, 4), np.nan)
        inb = np.isfinite(b) & (b >= 0) & (b < len(self.city_n))
        bi = np.where(inb, b, 0).astype(np.int64)
        out[inb, 0] = self.city_mph[bi[inb]]
        out[inb, 1] = self.city_n[bi[inb]]
        for col, idx, table in ((2, pu_idx, self.pu_mph), (3, do_idx, self.do_mph)):
            m = inb & ~np.isnan(idx)
            out[m, col] = table[bi[m], idx[m].astype(np.int64)]
        return out

    def to_dict(self) -> dict:
        return {"t0": self.t0, "city_mph": self.city_mph, "city_n": self.city_n, "pu_mph": self.pu_mph, "do_mph": self.do_mph}

    @classmethod
    def from_dict(cls, d: dict) -> "TrafficFeed":
        return cls(d["t0"], d["city_mph"], d["city_n"], d["pu_mph"], d["do_mph"])


# ------------------------------------------------------------------ wrappers
class CorrectedModel:
    """``base`` times exp(model prediction). Needs the absolute time for hour/weekday features:
    ``start`` is simulated t = 0, and ``set_time`` moves the clock (``build_batch`` calls it)."""

    def __init__(self, base: TravelTimeModel, bundle: dict, zones, start: Optional[datetime] = None):
        feats = bundle.get("features")
        if feats is not None and feats not in (FEATURES, FEATURES + TRAFFIC_FEATURES):
            raise ValueError(f"this ETA bundle was trained with features {feats}, not {FEATURES}: "
                             "retrain with `python -m ridesync.ml.train eta`")
        self.base = base
        self.bundle = bundle
        self.model = bundle["model"]
        self.zone_col = {int(z): i for i, z in enumerate(bundle["zones"])}
        self.zones = zones  # ridesync.stream.zones.ZoneIndex
        self.start = start
        self.traffic = TrafficFeed.from_dict(bundle["traffic"]) if "traffic" in bundle else None
        self.t = 0.0
        self._zone_cache: Dict[Tuple[float, float], float] = {}
        self.fallbacks = getattr(base, "fallbacks", 0)

    def set_time(self, t: float) -> None:
        self.t = t

    def _clock(self) -> Tuple[float, float, float]:
        if self.start is None:
            return np.nan, np.nan, np.nan  # unknown date: the trees send these down their "missing" branches
        now = self.start + timedelta(seconds=self.t)
        return now.hour + now.minute / 60.0, float(now.weekday()), float(now.month)

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

    def factor(self, base_s: np.ndarray, origins: np.ndarray, dests: np.ndarray, model=None) -> np.ndarray:
        """Correction factors for base times (N, M) between origins (N, 2) and dests (M, 2).
        ``model``: another regressor on the same features (a range quantile); default the point model."""
        n, m = base_s.shape
        ok = np.isfinite(base_s)
        f = np.ones_like(base_s)
        if not ok.any():
            return f
        oi, dj = np.nonzero(ok)
        zo, zd = self._zone_idx(origins), self._zone_idx(dests)
        dist = haversine_m(origins, dests)
        hour, dow, month = self._clock()
        traffic = None
        if self.traffic is not None:
            since = np.nan if self.start is None else (self.start - self.traffic.t0).total_seconds() + self.t
            traffic = self.traffic.lookup(since, zo[oi], zd[dj])
        X = eta_features(base_s[ok], dist[ok], zo[oi], zd[dj], hour, dow, month, traffic)
        f[ok] = np.clip(np.exp((model or self.model).predict(X)), *FACTOR_CLIP)
        return f

    def eta_range(self, origins: np.ndarray, dests: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """(low, high) drive times, (N, M): the bundle's 10th and 90th percentile (``INTERVAL``).
        Only for bundles trained with ranges; a quote like "8-11 min" shows these two numbers."""
        qm = self.bundle.get("interval_models")
        if not qm:
            raise ValueError("this ETA bundle has no range models: retrain with `python -m ridesync.ml.train eta`")
        origins, dests = np.atleast_2d(origins), np.atleast_2d(dests)
        base = self.base.matrix(origins, dests)
        lo, hi = (base * self.factor(base, origins, dests, qm[q]) for q in sorted(qm))
        return np.minimum(lo, hi), np.maximum(lo, hi)

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
    month: np.ndarray
    observed_s: np.ndarray
    train: np.ndarray
    traffic: Optional[np.ndarray] = None  # (n, 4) TRAFFIC_FEATURES at each request

    def X(self, mask=None, traffic: bool = True) -> np.ndarray:
        m = slice(None) if mask is None else mask
        t = self.traffic[m] if traffic and self.traffic is not None else None
        return eta_features(self.base_s[m], self.dist_m[m], self.pu_idx[m], self.do_idx[m], self.hour[m], self.dow[m],
                            self.month[m], t)


def place_trips(trips, pts, P: np.ndarray, zones: Sequence[int], train: np.ndarray, seed: int = 0) -> TripSample:
    """Put each trip's ends on random pool points of their zones; look up base times and distances.
    ``trips`` carries its live-traffic features (``ridesync.data.monthly``); ``train`` marks training rows."""
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
    pu_idx, do_idx = trips["PULocationID"].map(zi).to_numpy(float), trips["DOLocationID"].map(zi).to_numpy(float)
    traffic = trips[TRAFFIC_FEATURES].to_numpy(float) if set(TRAFFIC_FEATURES) <= set(trips.columns) else None
    return TripSample(
        base_s=P[pu, do], base2_s=P[pu2, do2], dist_m=haversine_pairs_m(xy[pu], xy[do]),
        pu_idx=pu_idx, do_idx=do_idx,
        hour=(t.dt.hour + t.dt.minute / 60.0).to_numpy(float), dow=t.dt.weekday.to_numpy(float),
        month=t.dt.month.to_numpy(float), observed_s=trips["trip_time"].to_numpy(float),
        train=np.asarray(train, dtype=bool), traffic=traffic,
    )


def _errors(obs: np.ndarray, pred: np.ndarray) -> dict:
    ape = np.abs(pred - obs) / obs
    return {"mae_s": float(np.mean(np.abs(pred - obs))), "mape": float(np.mean(ape)),
            "median_ape": float(np.median(ape)), "p90_ape": float(np.percentile(ape, 90)),
            "bias_s": float(np.mean(pred - obs))}


def _fit(X: np.ndarray, y: np.ndarray, max_iter: int, quantile: Optional[float] = None):
    from sklearn.ensemble import HistGradientBoostingRegressor

    loss = {"loss": "squared_error"} if quantile is None else {"loss": "quantile", "quantile": quantile}
    return HistGradientBoostingRegressor(
        **loss, learning_rate=0.05, max_iter=max_iter, max_leaf_nodes=63, min_samples_leaf=100,
        l2_regularization=1.0, categorical_features=CATEGORICAL, early_stopping=False, random_state=0,
    ).fit(X, y)


INTERVAL = (0.1, 0.9)  # the quoted range "8-11 min": 80% of drives should land inside it


class LookupCorrection:
    """A lookup-table correction with the learned model's interface (``predict`` on ``eta_features`` rows):
    the median log factor per cell of hour of day, crossed with the pickup zone (``by="zone_hour"``) or
    with a straight-line distance band (``by="dist_hour"``: short drives are slower per km). The simple
    baselines a platform would build first, used as matcher beliefs in the M6 ETA experiment. Unknown
    cells fall back to ``default``."""

    DIST_EDGES_M = (500.0, 1000.0, 1500.0, 2000.0, 3000.0, 4000.0, 6000.0, 9000.0)

    def __init__(self, table: Dict[int, float], by: str, default: float):
        self.table, self.by, self.default = table, by, default

    def key(self, X: np.ndarray) -> np.ndarray:
        h = np.floor(np.nan_to_num(X[:, FEATURES.index("hour")], nan=-1.0))
        if self.by == "hour":
            return h
        if self.by == "zone_hour":
            pu = X[:, FEATURES.index("pu_zone")]
            return np.where(np.isnan(pu), -1, pu) * 24 + h
        band = np.searchsorted(self.DIST_EDGES_M, np.exp(X[:, FEATURES.index("log_dist_m")]))
        return band * 24 + h

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.array([self.table.get(int(k), self.default) for k in self.key(X)])

    @classmethod
    def fit(cls, X: np.ndarray, y: np.ndarray, by: str, min_n: int = 30) -> "LookupCorrection":
        """Median log(observed / base) per cell with at least ``min_n`` trips."""
        tmp = cls({}, by, float(np.median(y)))
        keys = tmp.key(X)
        for k in np.unique(keys):
            sel = keys == k
            if sel.sum() >= min_n:
                tmp.table[int(k)] = float(np.median(y[sel]))
        return tmp


def fit_and_evaluate(s: TripSample, max_iter: int = 300) -> Tuple[object, List[dict], dict]:
    """Fit on training days; compare with the base alone and a pickup-zone x hour table on test days.
    With traffic features, a model without them is fitted too, to show what live traffic adds."""
    ok = np.isfinite(s.base_s) & (s.base_s > 30) & np.isfinite(s.base2_s) & ~np.isnan(s.pu_idx) & ~np.isnan(s.do_idx)
    tr, te = ok & s.train, ok & ~s.train
    y = np.log(s.observed_s / s.base_s)
    model = _fit(s.X(tr), y[tr], max_iter)

    obs, base = s.observed_s[te], s.base_s[te]
    pred_model = base * np.clip(np.exp(model.predict(s.X(te))), *FACTOR_CLIP)
    # Baselines: one global factor (the base is already calibrated, so this is ~1), and lookup tables.
    g = float(np.exp(np.median(y[tr])))
    Xtr, Xte = s.X(tr, traffic=False), s.X(te, traffic=False)
    lookups = {by: LookupCorrection.fit(Xtr, y[tr], by) for by in ("hour", "zone_hour", "dist_hour")}
    pred_table = base * np.exp(lookups["zone_hour"].predict(Xte))
    rows = [
        {"method": "base model alone (global calibration)", **_errors(obs, base)},
        {"method": "base x global median factor", **_errors(obs, base * g)},
        {"method": "base x hour-of-day table", **_errors(obs, base * np.exp(lookups["hour"].predict(Xte)))},
        {"method": "base x pickup-zone x hour table", **_errors(obs, pred_table)},
        {"method": "base x distance-band x hour table", **_errors(obs, base * np.exp(lookups["dist_hour"].predict(Xte)))},
    ]
    if s.traffic is not None:
        static = _fit(s.X(tr, traffic=False), y[tr], max_iter)
        pred_static = base * np.clip(np.exp(static.predict(s.X(te, traffic=False))), *FACTOR_CLIP)
        rows.append({"method": "base x learned correction (GBT), no live traffic", **_errors(obs, pred_static)})
        rows.append({"method": "base x learned correction (GBT) + live traffic", **_errors(obs, pred_model)})
    else:
        rows.append({"method": "base x learned correction (GBT)", **_errors(obs, pred_model)})
    resid = np.log(obs / pred_model)
    # An ETA range: the 10th and 90th percentile of the correction, from quantile-loss trees.
    qmodels = {q: _fit(s.X(tr), y[tr], max_iter, quantile=q) for q in INTERVAL}
    lo, hi = (base * np.exp(qmodels[q].predict(s.X(te))) for q in INTERVAL)
    lo, hi = np.minimum(lo, hi), np.maximum(lo, hi)
    extra = {
        "train_trips": int(tr.sum()), "test_trips": int(te.sum()), "global_factor": g,
        # Two random placements of the same trip disagree by this much before any model is involved.
        "placement_median_ape": float(np.median(np.abs(s.base2_s[te] - base) / base)),
        "residual_sigma": float(np.std(resid)),
        "residual_iqr_sigma": float((np.percentile(resid, 75) - np.percentile(resid, 25)) / 1.349),
        "interval": list(INTERVAL),
        "interval_coverage": float(np.mean((obs >= lo) & (obs <= hi))),
        "interval_below": float(np.mean(obs < lo)), "interval_above": float(np.mean(obs > hi)),
        "interval_median_width_frac": float(np.median((hi - lo) / pred_model)),
        "interval_median_width_s": float(np.median(hi - lo)),
        "interval_models": qmodels,
        "lookups": lookups,
    }
    return model, rows, extra


def load_feed(months: Sequence[str], root: Optional[Path] = None) -> TrafficFeed:
    """The monthly traffic tables of consecutive months as one feed (``ridesync.data.monthly``).
    Months are whole 5-minute buckets, so the tables join end to end."""
    from .common import MONTHLY, monthly_meta

    root = root or MONTHLY
    parts = []
    for m in months:
        monthly_meta(m, root)
        with np.load(root / m / "traffic.npz") as z:
            parts.append({k: z[k] for k in ("t0", "city_mph", "city_n", "pu_mph", "do_mph")})
    t0 = datetime.fromisoformat(str(parts[0]["t0"]))
    joined = []
    for k in ("city_mph", "city_n", "pu_mph", "do_mph"):
        arrs = []
        for i, p in enumerate(parts):
            a = p[k]
            if i + 1 < len(parts):  # trim or pad to the month's length (the last bucket holds late dropoffs)
                start = datetime.fromisoformat(str(p["t0"]))
                n = int((datetime.fromisoformat(str(parts[i + 1]["t0"])) - start).total_seconds() // TrafficFeed.BUCKET_S)
                a = a[:n] if len(a) >= n else np.concatenate([a, np.full((n - len(a),) + a.shape[1:], np.nan, a.dtype)])
            arrs.append(a)
        joined.append(np.concatenate(arrs))
    return TrafficFeed(t0, *joined)


def train(base_kind: str = "straight", train_spec: str = "2025-01:2026-06", test_spec: str = "2026-07",
          per_day: Optional[int] = None, osrm_url: str = "http://localhost:5000", max_iter: int = 300,
          seed: int = 0) -> Tuple[dict, List[dict], dict]:
    """Fit the correction for a base model on the training period's trip samples, test on the test period.
    ``per_day`` subsamples the monthly samples further. Returns (bundle, rows, extra)."""
    from ..routing import make_travel_model, travel_from_calibration
    from .common import load_table, service_zones, split

    tr, te = split(train_spec, test_spec)
    zones = service_zones()
    tcfg = travel_from_calibration(base_kind, osrm_url)
    base = make_travel_model(tcfg)
    pts = zone_points(zones)
    sig = f"{tcfg.speed_mps:.4f}_{tcfg.detour:.2f}" if base_kind == "straight" else f"{tcfg.time_multiplier:.4f}"
    P = base_matrix(pts[["lat", "lon"]].to_numpy(), base, cache=f"{MODELS_DIR}/pool_{base_kind}_{sig}.npy")  # per calibration

    trips = load_table(tr.months() + te.months(), "eta")
    t = trips["request_datetime"]
    trips = trips[tr.mask(t) | te.mask(t)]
    if per_day:
        trips = trips.sample(frac=1.0, random_state=seed)
        trips = trips.groupby(trips["request_datetime"].dt.normalize()).head(per_day)
    trips = trips.reset_index(drop=True)
    sample = place_trips(trips, pts, P, zones, tr.mask(trips["request_datetime"]).to_numpy(), seed)
    model, rows, extra = fit_and_evaluate(sample, max_iter)
    extra.update({"train": str(tr), "test": str(te)})
    base_sig = {"model": tcfg.model, "speed_mps": tcfg.speed_mps, "detour": tcfg.detour,
                "time_multiplier": tcfg.time_multiplier}
    lookups = extra.pop("lookups")
    # The feed covers the test period: simulations run on test days.
    bundle = {"model": model, "zones": list(map(int, zones)), "base": base_sig, "features": FEATURES + TRAFFIC_FEATURES,
              "traffic": load_feed(te.months()).to_dict(), **extra}
    # The lookup baselines as bundles of their own, usable anywhere a correction is (``TravelConfig.eta_model``).
    bundle["baselines"] = {name: {"model": lk, "zones": bundle["zones"], "base": base_sig, "features": FEATURES}
                           for name, lk in lookups.items()}
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
