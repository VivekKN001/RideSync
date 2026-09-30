# M8: ETA correction on the `osrm` base model (TLC, Manhattan trips)

Train: 2025-01-01 to 2026-06-30 (1,637,948 trips), test: 2026-07-01 to 2026-07-31 (92,998 trips). Errors are on observed pickup-to-dropoff times (`trip_time`).
Trip ends are placed on random points in their zones. Placing the same trip twice already changes the base time by a median 14.5%: part of every error below is that, not the model.
Residual log-error sigma of the corrected model: 0.310 (robust, from the IQR: 0.268).

| method | mae_s | mape | median_ape | p90_ape | bias_s |
|---|---|---|---|---|---|
| base model alone (global calibration) | 363 | 44.4% | 32.9% | 93.0% | +106 |
| base x global median factor | 320 | 37.1% | 29.1% | 73.0% | -34 |
| base x hour-of-day table | 302 | 35.1% | 27.1% | 69.7% | -30 |
| base x pickup-zone x hour table | 292 | 33.9% | 26.0% | 67.6% | -28 |
| base x distance-band x hour table | 284 | 34.5% | 24.9% | 68.7% | -55 |
| base x learned correction (GBT), no live traffic | 216 | 24.4% | 18.6% | 49.1% | -77 |
| base x learned correction (GBT) + live traffic | 206 | 24.4% | 18.0% | 49.7% | -39 |

## ETA range

Quantile-loss trees for the 10% and 90% points of the same correction give a range to quote ("8-11 min"). On the test days 79.3% of trips land inside it (target 80%; 10.5% faster, 10.2% slower). Median width 9.8 min, 73% of the point ETA.
