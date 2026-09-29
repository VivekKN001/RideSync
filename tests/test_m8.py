"""M8: many months of data. Periods, the monthly reduce, loading months back, no leakage."""
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from ridesync.data.fetch import expand_months
from ridesync.data.monthly import count_matrix, is_done, reduce_month
from ridesync.ml.common import Period, load_counts, load_table, split
from ridesync.ml.demand import PER_DAY, buckets_of

ZONES = [10, 20, 30]


def test_expand_months():
    assert expand_months(["2024-03"]) == ["2024-03"]
    assert expand_months(["2025-11:2026-02", "2024-01"]) == ["2025-11", "2025-12", "2026-01", "2026-02", "2024-01"]


def test_periods_and_split():
    p = Period.parse("2025-01:2026-06")
    assert p.start == pd.Timestamp("2025-01-01") and p.end == pd.Timestamp("2026-07-01") and len(p.months()) == 18
    d = Period.parse("2024-03-22:2024-03-31")
    assert d.months() == ["2024-03"] and d.end == pd.Timestamp("2024-04-01")
    ts = pd.Series(pd.to_datetime(["2024-03-21 23:59", "2024-03-22 00:00", "2024-04-01 00:00"]))
    assert d.mask(ts).tolist() == [False, True, False]
    tr, te = split("2025-01:2026-06", "2026-07")
    assert te.start == tr.end
    with pytest.raises(ValueError):
        split("2025-01:2026-07", "2026-07")  # the test month inside training: leakage
    with pytest.raises(ValueError):
        split("2026-07", "2026-06")  # testing on the past


def _fake_month(path, month, n=4000, seed=0, cbd=True):
    """A raw TLC month in miniature: trips between ZONES plus some that the reduce must drop."""
    rng = np.random.default_rng(seed)
    start = pd.Timestamp(f"{month}-01")
    days = start.days_in_month
    req = start + pd.to_timedelta(rng.uniform(0, days * 86400, n), unit="s")
    pu, do = rng.choice(ZONES, n), rng.choice(ZONES, n)
    tt = rng.integers(120, 1800, n)
    df = pd.DataFrame({
        "hvfhs_license_num": rng.choice(["HV0003", "HV0005"], n), "request_datetime": req,
        "dropoff_datetime": req + pd.to_timedelta(tt + 300, unit="s"), "PULocationID": pu.astype("int32"),
        "DOLocationID": do.astype("int32"), "trip_miles": rng.uniform(0.5, 5, n), "trip_time": tt,
        "base_passenger_fare": rng.uniform(8, 40, n), "tolls": 0.0, "bcf": 0.5, "sales_tax": 1.0,
        "congestion_surcharge": 2.75, "shared_request_flag": "N",
    })
    if cbd:
        df["cbd_congestion_fee"] = 1.5
    extra = pd.DataFrame({  # outside the area, a shared ride, and a request in the next month
        **{c: [df[c].iloc[0]] * 3 for c in df.columns},
    })
    extra["PULocationID"] = np.array([99, 10, 10], dtype="int32")
    extra["shared_request_flag"] = ["N", "Y", "N"]
    extra["request_datetime"] = [req[0], req[0], start + pd.offsets.MonthBegin(1)]
    extra["DOLocationID"] = np.array([20, 20, 20], dtype="int32")
    pd.concat([df, extra], ignore_index=True).to_parquet(path, index=False)
    return df


def test_reduce_month_writes_small_tables_and_skips_when_done(tmp_path):
    raw = tmp_path / "raw.parquet"
    df = _fake_month(raw, "2025-02", cbd=False)
    keep = df[df["PULocationID"] != df["DOLocationID"]]
    meta = reduce_month("2025-02", per_day=20, fare_per_day=10, root=tmp_path, raw_path=raw, zones=ZONES)
    assert meta["requests"] == len(keep) and meta["days"] == 28 and is_done("2025-02", tmp_path)
    C = np.load(tmp_path / "2025-02" / "counts.npy")
    assert C.shape == (3, 28 * PER_DAY) and C.sum() == len(keep)
    eta = pd.read_parquet(tmp_path / "2025-02" / "eta.parquet")
    assert eta.groupby(eta["request_datetime"].dt.day).size().max() <= 20
    assert {"city_mph_30", "pu_mph_60"} <= set(eta.columns)
    fare = pd.read_parquet(tmp_path / "2025-02" / "fare.parquet")
    assert fare["cbd_congestion_fee"].isna().all()  # before congestion pricing the column doesn't exist
    assert not is_done("2025-03", tmp_path)


def test_count_matrix_buckets():
    df = pd.DataFrame({"request_datetime": pd.to_datetime(["2025-02-01 00:10", "2025-02-01 00:20", "2025-02-02 00:00"]),
                       "PULocationID": [20, 20, 30]})
    C = count_matrix(df, ZONES, pd.Timestamp("2025-02-01"), 28)
    assert C[1, 0] == 1 and C[1, 1] == 1 and C[2, PER_DAY] == 1 and C.sum() == 3


def test_months_load_back_side_by_side(tmp_path):
    for i, m in enumerate(["2025-12", "2026-01"]):
        _fake_month(tmp_path / f"{m}.parquet", m, n=500, seed=i)
        reduce_month(m, per_day=5, fare_per_day=5, root=tmp_path, raw_path=tmp_path / f"{m}.parquet", zones=ZONES)
    C, origin = load_counts(["2025-12", "2026-01"], ZONES, tmp_path)
    assert origin == pd.Timestamp("2025-12-01") and C.shape == (3, 62 * PER_DAY)
    jan = buckets_of(Period.parse("2026-01"), origin)
    assert jan[0] == 31 * PER_DAY and C[:, jan].sum() == np.load(tmp_path / "2026-01" / "counts.npy").sum()
    fares = load_table(["2025-12", "2026-01"], "fare", tmp_path)
    assert fares["request_datetime"].dt.month.isin([12, 1]).all()
    with pytest.raises(ValueError):
        load_counts(["2025-12"], [10, 20], tmp_path)  # other zones than it was reduced with
    with pytest.raises(FileNotFoundError):
        load_counts(["2026-02"], ZONES, tmp_path)


def test_traffic_feeds_join_across_months(tmp_path):
    from ridesync.ml.eta import load_feed

    for i, m in enumerate(["2025-12", "2026-01"]):
        _fake_month(tmp_path / f"{m}.parquet", m, n=3000, seed=i)
        reduce_month(m, per_day=5, fare_per_day=5, root=tmp_path, raw_path=tmp_path / f"{m}.parquet", zones=ZONES)
    feed = load_feed(["2025-12", "2026-01"], tmp_path)
    assert feed.t0 == datetime(2025, 12, 1)
    dec = 31 * 86400 // feed.BUCKET_S
    assert len(feed.city_n) > dec
    one = load_feed(["2026-01"], tmp_path)
    k = 500  # a January bucket reads the same from the joined feed and from January's own
    assert feed.city_n[dec + k] == one.city_n[k]
