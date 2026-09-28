"""Demand forecast: ride requests per taxi zone per 15 minutes.

Data is the TLC month, counted per (zone, 15-minute bucket) with the same filter as the demand
slices, at full scale (not sampled). For a target bucket ``b`` forecast ``k`` buckets ahead, the
last bucket we know is ``s = b - k``. Features:

- ``lag1..lag4``: counts of buckets s, s-1, s-2, s-3, and their mean
- ``yday``, ``lweek``: the same bucket one day and one week before the target
- ``zone`` (categorical), ``tod`` (bucket of the day), ``dow``

Nothing at or after ``s + 1`` is read, which ``test_m6`` checks by blanking the future. The model is
a gradient-boosted tree ensemble with Poisson loss, one per horizon (15, 30 and 60 minutes ahead).

In a simulation, the history before t = 0 is the real month; buckets from t = 0 on come from what
the simulation has seen so far (scaled back up by the sample fraction), and the bucket in progress
and everything after it are unknown.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

BUCKET_S = 900.0
PER_DAY = 96
PER_WEEK = 7 * PER_DAY
HORIZONS = (1, 2, 4)
FEATURES = ["lag1", "lag2", "lag3", "lag4", "mean4", "yday", "lweek", "zone", "tod", "dow"]
ZONE_COL = FEATURES.index("zone")
MODEL_PATH = "data/models/demand.joblib"


# ------------------------------------------------------------------ features
def count_matrix(bucket: np.ndarray, zone_idx: np.ndarray, n_zones: int, n_buckets: int) -> np.ndarray:
    """(Z, B) request counts from each request's bucket and zone index."""
    ok = (bucket >= 0) & (bucket < n_buckets) & (zone_idx >= 0)
    flat = np.bincount(zone_idx[ok] * n_buckets + bucket[ok], minlength=n_zones * n_buckets)
    return flat.reshape(n_zones, n_buckets).astype(float)


def _take(C: np.ndarray, b: np.ndarray) -> np.ndarray:
    """C[:, b] with NaN where b is outside the matrix. (Z, len(b))."""
    out = np.full((C.shape[0], len(b)), np.nan)
    ok = (b >= 0) & (b < C.shape[1])
    out[:, ok] = C[:, b[ok]]
    return out


def features(C: np.ndarray, targets: np.ndarray, k: int, origin_dow: int) -> np.ndarray:
    """Feature rows for every zone and target bucket, zone-major: row z * len(targets) + j.

    Reads only buckets <= targets - k (plus the day/week-before buckets, which are older for k <= 96).
    """
    targets = np.asarray(targets, dtype=int)
    s = targets - k
    lags = np.stack([_take(C, s - i) for i in range(4)], axis=-1)  # (Z, n, 4)
    n_known = np.sum(~np.isnan(lags), axis=-1)
    with np.errstate(invalid="ignore"):
        mean4 = np.where(n_known > 0, np.nansum(lags, axis=-1) / np.maximum(n_known, 1), np.nan)
    Z, n = C.shape[0], len(targets)
    cols = [lags[..., 0], lags[..., 1], lags[..., 2], lags[..., 3], mean4,
            _take(C, targets - PER_DAY), _take(C, targets - PER_WEEK),
            np.repeat(np.arange(Z, dtype=float)[:, None], n, axis=1),
            np.broadcast_to((targets % PER_DAY).astype(float), (Z, n)),
            np.broadcast_to(((origin_dow + targets // PER_DAY) % 7).astype(float), (Z, n))]
    return np.stack(cols, axis=-1).reshape(Z * n, len(FEATURES))


def hist_mean(C: np.ndarray, targets: np.ndarray, train_buckets: np.ndarray, origin_dow: int) -> np.ndarray:
    """Baseline: each zone's mean count over training buckets with the same weekday and time of day."""
    def key(b):
        return ((origin_dow + b // PER_DAY) % 7) * PER_DAY + b % PER_DAY

    tk = key(train_buckets)
    sums = np.zeros((C.shape[0], PER_WEEK))
    cnt = np.zeros(PER_WEEK)
    np.add.at(sums.T, tk, C[:, train_buckets].T)
    np.add.at(cnt, tk, 1)
    with np.errstate(invalid="ignore"):
        mean = sums / cnt
    return mean[:, key(np.asarray(targets))].reshape(-1)


def wape(y: np.ndarray, p: np.ndarray) -> float:
    ok = ~np.isnan(p)
    return float(np.abs(y[ok] - p[ok]).sum() / max(y[ok].sum(), 1e-9))


def mae(y: np.ndarray, p: np.ndarray) -> float:
    ok = ~np.isnan(p)
    return float(np.abs(y[ok] - p[ok]).mean())


# ------------------------------------------------------------------ forecaster
@dataclass
class DemandForecaster:
    models: Dict[int, object]  # horizon (buckets) -> fitted regressor
    zones: List[int]           # taxi zone ids; row order of ``counts``
    origin: str                # ISO time of bucket 0
    counts: np.ndarray         # (Z, B) real counts of the whole month (history for lags)

    def __post_init__(self):
        self.zone_row = {z: i for i, z in enumerate(self.zones)}
        self._origin = datetime.fromisoformat(self.origin)
        self.origin_dow = self._origin.weekday()

    def bucket_of(self, when: datetime) -> float:
        return (when - self._origin).total_seconds() / BUCKET_S

    def predict_buckets(self, b0: int, observed: Mapping[int, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """Forecast counts per zone for bucket b0 (1 ahead) and b0 + 1 (2 ahead), full scale.

        Buckets >= b0 are unknown. ``observed`` overrides history for buckets the caller has seen
        itself: {bucket: (Z,) counts}.
        """
        C = self.counts.copy()
        C[:, b0:] = np.nan
        for b, row in observed.items():
            if 0 <= b < min(b0, C.shape[1]):
                C[:, b] = row
        p0 = self.models[1].predict(features(C, np.array([b0]), 1, self.origin_dow))
        p1 = self.models[2].predict(features(C, np.array([b0 + 1]), 2, self.origin_dow))
        return np.maximum(p0, 0.0), np.maximum(p1, 0.0)

    def expected(self, now: datetime, horizon_s: float, observed: Mapping[int, np.ndarray]) -> np.ndarray:
        """Expected requests per zone over [now, now + horizon_s), full scale. horizon_s <= one bucket."""
        if horizon_s > BUCKET_S:
            raise ValueError(f"forecast horizon is at most {BUCKET_S:.0f} s")
        bnow = self.bucket_of(now)
        b0 = int(np.floor(bnow))
        rest = b0 + 1 - bnow            # share of the current bucket still ahead
        h = horizon_s / BUCKET_S
        p0, p1 = self.predict_buckets(b0, observed)
        return p0 * min(rest, h) + p1 * max(h - rest, 0.0)

    def save(self, path: str = MODEL_PATH) -> None:
        import joblib

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"models": self.models, "zones": self.zones, "origin": self.origin, "counts": self.counts}, path)

    @classmethod
    def load(cls, path: str = MODEL_PATH) -> "DemandForecaster":
        import joblib

        d = joblib.load(path)
        return cls(d["models"], d["zones"], d["origin"], d["counts"])


def make_regressor(max_iter: int = 300):
    from sklearn.ensemble import HistGradientBoostingRegressor

    return HistGradientBoostingRegressor(
        loss="poisson", learning_rate=0.05, max_iter=max_iter, max_leaf_nodes=63, min_samples_leaf=40,
        l2_regularization=1.0, categorical_features=[ZONE_COL], early_stopping=False, random_state=0,
    )


def fit_and_evaluate(C: np.ndarray, zones: Sequence[int], origin: datetime, train_days: int,
                     horizons: Sequence[int] = HORIZONS, max_iter: int = 300) -> Tuple[DemandForecaster, List[dict]]:
    """Train one model per horizon on the first ``train_days`` days, evaluate on the rest against baselines."""
    B = C.shape[1]
    dow0 = origin.weekday()
    train_b = np.arange(0, train_days * PER_DAY)
    test_b = np.arange(train_days * PER_DAY, B)
    y_te = C[:, test_b].reshape(-1)
    base_hist = hist_mean(C, test_b, train_b, dow0)
    models, rows = {}, []
    for k in horizons:
        X_tr = features(C, train_b, k, dow0)
        model = make_regressor(max_iter).fit(X_tr, C[:, train_b].reshape(-1))
        models[k] = model
        X_te = features(C, test_b, k, dow0)
        preds = {
            "model (GBT, Poisson)": model.predict(X_te),
            "last value": X_te[:, FEATURES.index("lag1")],
            "same time last week": X_te[:, FEATURES.index("lweek")],
            "zone x weekday x time mean": base_hist,
        }
        for name, p in preds.items():
            rows.append({"horizon_min": int(k * BUCKET_S / 60), "method": name, "wape": wape(y_te, p), "mae": mae(y_te, p)})
    fc = DemandForecaster(models, list(map(int, zones)), origin.isoformat(), C)
    return fc, rows


def train(month: str = "2024-03", max_iter: int = 300) -> Tuple[DemandForecaster, List[dict], dict]:
    """Count the month, fit, evaluate. Returns (forecaster, evaluation rows, data summary)."""
    import pandas as pd

    from .common import TRAIN_DAYS, month_start, read_service_trips, service_zones

    zones = service_zones()
    df = read_service_trips(month, ["request_datetime", "PULocationID"], zones)
    origin = month_start(month)
    n_buckets = origin.days_in_month * PER_DAY
    bucket = ((df["request_datetime"] - origin).dt.total_seconds() // BUCKET_S).to_numpy().astype(int)
    row = pd.Series(range(len(zones)), index=zones)
    zidx = df["PULocationID"].map(row).fillna(-1).to_numpy().astype(int)
    C = count_matrix(bucket, zidx, len(zones), n_buckets)
    fc, rows = fit_and_evaluate(C, zones, origin.to_pydatetime(), TRAIN_DAYS, max_iter=max_iter)
    summary = {"requests": int(C.sum()), "zones": len(zones), "buckets": n_buckets,
               "mean_per_zone_bucket": float(C.mean()), "test_mean_per_zone_bucket": float(C[:, TRAIN_DAYS * PER_DAY:].mean())}
    return fc, rows, summary


def observed_rows(counts: Mapping[Tuple[int, int], float], zone_row: Mapping[int, int], n_zones: int,
                  scale: float) -> Dict[int, np.ndarray]:
    """{(zone id, bucket): count} -> {bucket: (Z,) counts * scale}, dropping zones the model doesn't know."""
    out: Dict[int, np.ndarray] = {}
    for (zone, b), c in counts.items():
        i = zone_row.get(zone)
        if i is None:
            continue
        out.setdefault(b, np.zeros(n_zones))[i] += c * scale
    return out


def load_or_none(path: Optional[str]) -> Optional[DemandForecaster]:
    return DemandForecaster.load(path) if path and Path(path).exists() else None
