"""Demand forecast: ride requests per taxi zone per 15 minutes.

Data is the TLC month, counted per (zone, 15-minute bucket) with the same filter as the demand
slices, at full scale (not sampled). For a target bucket ``b`` forecast ``k`` buckets ahead, the
last bucket we know is ``s = b - k``. Features:

- ``lag1..lag4``: counts of buckets s, s-1, s-2, s-3, and their mean
- ``yday``, ``lweek``, ``lyear``: the same bucket one day, one week and 52 weeks before the target
- ``zone`` (categorical), ``tod`` (bucket of the day), ``dow``, ``month``, ``holiday`` (US federal)

Nothing at or after ``s + 1`` is read, which ``test_m6`` checks by blanking the future. The model is
a gradient-boosted tree ensemble with Poisson loss, one per horizon (15, 30 and 60 minutes ahead).

Since M8 the counts span many months (``data/monthly``); the model trains on one period and is tested
on a later one (``ridesync.ml.common.split``). In a simulation, the history before t = 0 is real; buckets from t = 0 on come from what
the simulation has seen so far (scaled back up by the sample fraction), and the bucket in progress
and everything after it are unknown.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

BUCKET_S = 900.0
PER_DAY = 96
PER_WEEK = 7 * PER_DAY
PER_YEAR = 52 * PER_WEEK  # 364 days: the same weekday a year before
HORIZONS = (1, 2, 4)
FEATURES = ["lag1", "lag2", "lag3", "lag4", "mean4", "yday", "lweek", "lyear", "zone", "tod", "dow", "month", "holiday"]
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


@lru_cache(maxsize=8)
def _calendar(origin: date, n_days: int) -> np.ndarray:
    """(n_days, 2): month and US federal holiday flag of each day from ``origin``."""
    import pandas as pd
    from pandas.tseries.holiday import USFederalHolidayCalendar

    days = pd.date_range(origin, periods=n_days, freq="D")
    hol = USFederalHolidayCalendar().holidays(days[0], days[-1])
    return np.column_stack([days.month.to_numpy(float), days.isin(hol).astype(float)])


def features(C: np.ndarray, targets: np.ndarray, k: int, origin_dow: int, origin: Optional[date] = None) -> np.ndarray:
    """Feature rows for every zone and target bucket, zone-major: row z * len(targets) + j.

    Reads only buckets <= targets - k (plus the day/week/year-before buckets, which are older for
    k <= 96). ``origin`` (the date of bucket 0) gives month and holiday; without it they are NaN.
    """
    targets = np.asarray(targets, dtype=int)
    s = targets - k
    lags = np.stack([_take(C, s - i) for i in range(4)], axis=-1)  # (Z, n, 4)
    n_known = np.sum(~np.isnan(lags), axis=-1)
    with np.errstate(invalid="ignore"):
        mean4 = np.where(n_known > 0, np.nansum(lags, axis=-1) / np.maximum(n_known, 1), np.nan)
    Z, n = C.shape[0], len(targets)
    day = targets // PER_DAY
    if origin is not None and n:
        cal = _calendar(date(origin.year, origin.month, origin.day), int(max(day.max(), 0)) + 1)
        month, holiday = cal[np.maximum(day, 0), 0], cal[np.maximum(day, 0), 1]
    else:
        month = holiday = np.full(n, np.nan)
    cols = [lags[..., 0], lags[..., 1], lags[..., 2], lags[..., 3], mean4,
            _take(C, targets - PER_DAY), _take(C, targets - PER_WEEK), _take(C, targets - PER_YEAR),
            np.repeat(np.arange(Z, dtype=float)[:, None], n, axis=1),
            np.broadcast_to((targets % PER_DAY).astype(float), (Z, n)),
            np.broadcast_to(((origin_dow + day) % 7).astype(float), (Z, n)),
            np.broadcast_to(month, (Z, n)), np.broadcast_to(holiday, (Z, n))]
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
        p0 = self.models[1].predict(features(C, np.array([b0]), 1, self.origin_dow, self._origin))
        p1 = self.models[2].predict(features(C, np.array([b0 + 1]), 2, self.origin_dow, self._origin))
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
        joblib.dump({"models": self.models, "zones": self.zones, "origin": self.origin, "counts": self.counts,
                     "features": FEATURES}, path)

    @classmethod
    def load(cls, path: str = MODEL_PATH) -> "DemandForecaster":
        import joblib

        d = joblib.load(path)
        if d.get("features") != FEATURES:
            raise ValueError(f"{path} was trained with other features: retrain with `python -m ridesync.ml.train demand`")
        return cls(d["models"], d["zones"], d["origin"], d["counts"])


def make_regressor(max_iter: int = 300):
    from sklearn.ensemble import HistGradientBoostingRegressor

    return HistGradientBoostingRegressor(
        loss="poisson", learning_rate=0.05, max_iter=max_iter, max_leaf_nodes=63, min_samples_leaf=40,
        l2_regularization=1.0, categorical_features=[ZONE_COL], early_stopping=False, random_state=0,
    )


def fit(C: np.ndarray, origin: datetime, train_b: np.ndarray, horizons: Sequence[int] = HORIZONS,
        max_iter: int = 300) -> Dict[int, object]:
    """One model per horizon, trained on the buckets ``train_b``."""
    models = {}
    for k in horizons:
        X = features(C, train_b, k, origin.weekday(), origin).astype(np.float32)
        X[:, np.isnan(X).all(axis=0)] = 0.0  # e.g. no year before the data: a constant column the trees ignore
        models[k] = make_regressor(max_iter).fit(X, C[:, train_b].reshape(-1))
        del X
    return models


def evaluate(models: Mapping[int, object], C: np.ndarray, origin: datetime, train_b: np.ndarray,
             test_b: np.ndarray, baselines: bool = True, label: str = "model (GBT, Poisson)") -> List[dict]:
    """WAPE and MAE on the buckets ``test_b``, with the baselines (``train_b`` feeds the historical mean)."""
    y = C[:, test_b].reshape(-1)
    base_hist = hist_mean(C, test_b, train_b, origin.weekday()) if baselines else None
    rows = []
    for k, model in sorted(models.items()):
        X = features(C, test_b, k, origin.weekday(), origin)
        preds = {label: model.predict(X.astype(np.float32))}
        if baselines:
            preds.update({"last value": X[:, FEATURES.index("lag1")],
                          "same time last week": X[:, FEATURES.index("lweek")],
                          "same time last year (52 weeks)": X[:, FEATURES.index("lyear")],
                          "zone x weekday x time mean": base_hist})
        for name, p in preds.items():
            rows.append({"horizon_min": int(k * BUCKET_S / 60), "method": name, "wape": wape(y, p), "mae": mae(y, p)})
    return rows


def fit_and_evaluate(C: np.ndarray, zones: Sequence[int], origin: datetime, train_b: np.ndarray, test_b: np.ndarray,
                     horizons: Sequence[int] = HORIZONS, max_iter: int = 300) -> Tuple[DemandForecaster, List[dict]]:
    """Train one model per horizon on ``train_b``, evaluate on ``test_b`` against baselines."""
    models = fit(C, origin, np.asarray(train_b), horizons, max_iter)
    rows = evaluate(models, C, origin, np.asarray(train_b), np.asarray(test_b))
    return DemandForecaster(models, list(map(int, zones)), origin.isoformat(), C), rows


def buckets_of(period, origin) -> np.ndarray:
    """Bucket numbers of a ``common.Period`` counted from ``origin``."""
    a = int((period.start - origin).total_seconds() // BUCKET_S)
    b = int((period.end - origin).total_seconds() // BUCKET_S)
    return np.arange(a, b)


def history_counts(first_month: str, last_month: str, zones: Sequence[int], lookback_months: int = 12):
    """Counts from up to ``lookback_months`` before ``first_month`` (as far back as months are reduced, for
    the year-before feature) through ``last_month``: (C, origin Timestamp)."""
    import pandas as pd

    from .common import MONTHLY, Period, load_counts

    months = Period.parse(f"{first_month}:{last_month}").months()
    m = pd.Period(first_month, "M")
    for _ in range(lookback_months):
        m -= 1
        if not (MONTHLY / str(m) / "meta.json").exists():
            break
        months.insert(0, str(m))
    return load_counts(months, zones)


def train(train_spec: str, test_spec: str, max_iter: int = 300) -> Tuple[DemandForecaster, List[dict], dict]:
    """Load the monthly counts, fit on the training period, evaluate on the test period.
    Returns (forecaster, evaluation rows, data summary)."""
    from .common import service_zones, split

    tr, te = split(train_spec, test_spec)
    zones = service_zones()
    C, origin = history_counts(tr.months()[0], te.months()[-1], zones)
    train_b, test_b = buckets_of(tr, origin), buckets_of(te, origin)
    fc, rows = fit_and_evaluate(C, zones, origin.to_pydatetime(), train_b, test_b, max_iter=max_iter)
    summary = {"requests": int(C[:, train_b].sum() + C[:, test_b].sum()), "zones": len(zones),
               "train": str(tr), "test": str(te), "train_buckets": len(train_b), "test_buckets": len(test_b),
               "history_from": str(origin.date()),
               "mean_per_zone_bucket": float(C[:, train_b].mean()), "test_mean_per_zone_bucket": float(C[:, test_b].mean())}
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
