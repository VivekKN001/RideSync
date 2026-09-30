# M8C_2026-01: ETA correction on the `straight` base model (TLC, Manhattan trips)

Train: 2025-01-01 to 2025-12-31 (1,094,890 trips), test: 2026-01-01 to 2026-01-31 (92,994 trips). Errors are on observed pickup-to-dropoff times (`trip_time`).
Trip ends are placed on random points in their zones. Placing the same trip twice already changes the base time by a median 14.6%: part of every error below is that, not the model.
Residual log-error sigma of the corrected model: 0.314 (robust, from the IQR: 0.274).

| method | mae_s | mape | median_ape | p90_ape | bias_s |
|---|---|---|---|---|---|
| base model alone (global calibration) | 417 | 47.2% | 34.9% | 99.4% | +114 |
| base x global median factor | 401 | 45.2% | 34.3% | 91.7% | +72 |
| base x hour-of-day table | 384 | 43.1% | 32.8% | 86.9% | +70 |
| base x pickup-zone x hour table | 352 | 40.0% | 31.5% | 79.6% | +45 |
| base x distance-band x hour table | 265 | 34.0% | 24.4% | 70.1% | -36 |
| base x learned correction (GBT), no live traffic | 219 | 25.2% | 19.6% | 50.4% | -98 |
| base x learned correction (GBT) + live traffic | 199 | 24.7% | 18.3% | 50.2% | -40 |

## ETA range

Quantile-loss trees for the 10% and 90% points of the same correction give a range to quote ("8-11 min"). On the test days 79.4% of trips land inside it (target 80%; 10.1% faster, 10.6% slower). Median width 9.3 min, 74% of the point ETA.
