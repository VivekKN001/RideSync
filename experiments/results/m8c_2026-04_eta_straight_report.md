# M8C_2026-04: ETA correction on the `straight` base model (TLC, Manhattan trips)

Train: 2025-04-01 to 2026-03-31 (1,094,888 trips), test: 2026-04-01 to 2026-04-30 (89,990 trips). Errors are on observed pickup-to-dropoff times (`trip_time`).
Trip ends are placed on random points in their zones. Placing the same trip twice already changes the base time by a median 14.0%: part of every error below is that, not the model.
Residual log-error sigma of the corrected model: 0.309 (robust, from the IQR: 0.270).

| method | mae_s | mape | median_ape | p90_ape | bias_s |
|---|---|---|---|---|---|
| base model alone (global calibration) | 503 | 54.8% | 37.4% | 124.3% | +260 |
| base x global median factor | 418 | 44.8% | 33.8% | 90.2% | +69 |
| base x hour-of-day table | 397 | 42.3% | 32.2% | 85.3% | +69 |
| base x pickup-zone x hour table | 360 | 38.6% | 30.1% | 77.0% | +45 |
| base x distance-band x hour table | 276 | 32.7% | 24.2% | 65.9% | -62 |
| base x learned correction (GBT), no live traffic | 218 | 24.4% | 18.6% | 48.9% | -68 |
| base x learned correction (GBT) + live traffic | 210 | 24.3% | 18.0% | 49.5% | -39 |

## ETA range

Quantile-loss trees for the 10% and 90% points of the same correction give a range to quote ("8-11 min"). On the test days 79.8% of trips land inside it (target 80%; 9.6% faster, 10.6% slower). Median width 9.9 min, 72% of the point ETA.
