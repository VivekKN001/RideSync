"""Fare model (M6): fit ``FareConfig`` to TLC ``base_passenger_fare``.

    fare = max(min_fare, base + per_mile * miles + per_min * minutes)

TLC fares already include Uber's and Lyft's own surge, so the fit uses weekday late mornings and
early afternoons (10:00-15:59), when surge is rarest, and a median (quantile) regression, which the
few surged trips left barely move. ``road_factor`` turns straight-line distance into trip miles; it
is fitted on the same zone points the ETA model uses. Prices drift, so the fit uses only the last
``fit_months`` of the training period (``data/monthly`` fare samples) and is tested on the test
period; Uber and Lyft also get fits of their own for comparison. Fees, including NYC's congestion
pricing charge (``cbd_congestion_fee``, from January 2025), are reported over the test period.
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


COMPANIES = {"HV0003": "Uber", "HV0005": "Lyft"}
FEES = ["tolls", "bcf", "sales_tax", "congestion_surcharge", "cbd_congestion_fee"]


def _fit_quantile(miles: np.ndarray, minutes: np.ndarray, y: np.ndarray):
    from sklearn.linear_model import QuantileRegressor

    return QuantileRegressor(quantile=0.5, alpha=0.0, solver="highs").fit(np.column_stack([miles, minutes]), y)


def _predict(fit: dict, miles: np.ndarray, minutes: np.ndarray) -> np.ndarray:
    return np.maximum(fit["min_fare"], fit["base"] + fit["per_mile"] * miles + fit["per_min"] * minutes)


def _errors(y: np.ndarray, pred: np.ndarray) -> dict:
    ape = np.abs(pred - y) / y
    return {"mae": float(np.mean(np.abs(pred - y))), "median_ape": float(np.median(ape)),
            "p90_ape": float(np.percentile(ape, 90)), "bias": float(np.mean(pred - y)), "n": int(len(y))}


def fee_summary(months, root=None) -> dict:
    """Mean fees per valid trip over whole months, from the exact sums in each month's ``fees.json``."""
    from .common import MONTHLY

    root = root or MONTHLY
    tot: dict = {}
    for m in months:
        for k, v in json.loads((root / m / "fees.json").read_text()).items():
            tot[k] = tot.get(k, 0) + v
    n = max(tot.get("trips", 0), 1)
    out = {f: tot.get(f"{f}_sum", 0.0) / n for f in FEES}
    out["fees_share_of_fare"] = sum(tot.get(f"{f}_sum", 0.0) for f in FEES) / max(tot.get("fare_sum", 0.0), 1e-9)
    out["cbd_charged_share"] = tot.get("cbd_congestion_fee_charged", 0) / n
    out["trips"] = int(tot.get("trips", 0))
    return out


def train(train_spec: str = "2025-01:2026-06", test_spec: str = "2026-07", fit_months: int = 3, n: int = 30000,
          seed: int = 0) -> dict:
    """Fit on calm hours of the last ``fit_months`` of training, overall (the simulator's fares) and per company;
    evaluate on the test period. Writes ``FARE_PATH`` and returns the fit with an ``evaluation`` table and ``fees``."""
    from ..geo import haversine_pairs_m
    from .common import Period, load_table, service_zones, split
    from .eta import zone_points

    tr, te = split(train_spec, test_spec)
    fit_period = Period.parse(":".join([tr.months()[-min(fit_months, len(tr.months()))], tr.months()[-1]]))
    fit_period = Period(max(fit_period.start, tr.start), tr.end)
    zones = service_zones()
    df = load_table(fit_period.months() + te.months(), "fare")
    t = df["request_datetime"]
    df = df[fit_period.mask(t) | te.mask(t)].reset_index(drop=True)
    t = df["request_datetime"]
    calm = (t.dt.weekday < 5) & (t.dt.hour >= 10) & (t.dt.hour < 16)
    valid = (df["base_passenger_fare"] > 0) & (df["trip_miles"] > 0.1) & (df["trip_time"] > 60)
    train_day = fit_period.mask(t)
    rng = np.random.default_rng(seed)

    def sample(mask, k=n):
        idx = np.flatnonzero(mask.to_numpy())
        return df.iloc[rng.choice(idx, size=min(k, len(idx)), replace=False)]

    def fit_on(d) -> dict:
        q = _fit_quantile(d["trip_miles"].to_numpy(), d["trip_time"].to_numpy() / 60.0, d["base_passenger_fare"].to_numpy())
        return {"base": float(q.intercept_), "per_mile": float(q.coef_[0]), "per_min": float(q.coef_[1]),
                "min_fare": float(np.percentile(d["base_passenger_fare"], 2))}

    def evaluate(fit, d) -> dict:
        return _errors(d["base_passenger_fare"].to_numpy(),
                       _predict(fit, d["trip_miles"].to_numpy(), d["trip_time"].to_numpy() / 60.0))

    d = sample(calm & valid & train_day)
    fit = fit_on(d)
    test_calm, test_all = sample(calm & valid & ~train_day), sample(valid & ~train_day)
    median_fare = float(d["base_passenger_fare"].median())
    rows = [
        {"model": "one median fare for every trip", "test": "calm hours",
         **_errors(test_calm["base_passenger_fare"].to_numpy(), np.full(len(test_calm), median_fare))},
        {"model": "fitted fare, Uber + Lyft (simulator)", "test": "calm hours", **evaluate(fit, test_calm)},
        {"model": "fitted fare, Uber + Lyft (simulator)", "test": "all hours (incl. their surge)", **evaluate(fit, test_all)},
    ]
    companies = {}
    for code, name in COMPANIES.items():
        is_co = df["hvfhs_license_num"] == code
        if (is_co & calm & valid & train_day).sum() < 1000:
            continue
        cf = fit_on(sample(is_co & calm & valid & train_day))
        companies[name] = cf
        tc = sample(is_co & calm & valid & ~train_day)
        rows.append({"model": f"{name} trips, Uber + Lyft fit", "test": "calm hours", **evaluate(fit, tc)})
        rows.append({"model": f"{name} trips, own {name} fit", "test": "calm hours", **evaluate(cf, tc)})

    # Straight-line -> road miles, from the zone points (one random point per trip end).
    pts = zone_points(zones)
    by_zone = {int(z): g[["lat", "lon"]].to_numpy() for z, g in pts.groupby("zone")}
    pu = np.array([by_zone[int(z)][rng.integers(len(by_zone[int(z)]))] for z in d["PULocationID"]])
    do = np.array([by_zone[int(z)][rng.integers(len(by_zone[int(z)]))] for z in d["DOLocationID"]])
    straight = haversine_pairs_m(pu, do)
    road_factor = float(np.median(d["trip_miles"].to_numpy() * 1609.344 / np.maximum(straight, 50.0)))

    # What riders pay on top of the fare, over the test period. Taxes and fees are not platform revenue,
    # so the simulator's revenue stays fare x multiplier; these are for the report.
    fees = fee_summary(te.months())
    ok = df[valid & ~train_day]
    fees["rider_total_median"] = float((ok["base_passenger_fare"] + ok[FEES].fillna(0.0).sum(axis=1)).median())

    out = {**fit, "road_factor": road_factor, "n": int(len(d)), "median_fare": median_fare,
           "mae": rows[1]["mae"], "all_hours_median_fare": float(ok["base_passenger_fare"].median()),
           "fit_period": str(fit_period), "test": str(te),
           "companies": companies, "fees": fees, "evaluation": rows}
    Path(FARE_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(FARE_PATH).write_text(json.dumps(out, indent=2))
    return out
