# M8C_2025-10: ETA correction on the `straight` base model (TLC, Manhattan trips)

Train: 2024-10-01 to 2025-09-30 (1,094,876 trips), test: 2025-10-01 to 2025-10-31 (92,993 trips). Errors are on observed pickup-to-dropoff times (`trip_time`).
Trip ends are placed on random points in their zones. Placing the same trip twice already changes the base time by a median 13.9%: part of every error below is that, not the model.
Residual log-error sigma of the corrected model: 0.314 (robust, from the IQR: 0.276).

| method | mae_s | mape | median_ape | p90_ape | bias_s |
|---|---|---|---|---|---|
| base model alone (global calibration) | 504 | 53.1% | 36.9% | 119.2% | +223 |
| base x global median factor | 424 | 43.3% | 33.9% | 84.4% | +10 |
| base x hour-of-day table | 398 | 40.5% | 31.8% | 79.2% | +10 |
| base x pickup-zone x hour table | 362 | 37.2% | 29.9% | 73.2% | -12 |
| base x distance-band x hour table | 298 | 32.0% | 24.7% | 62.1% | -116 |
| base x learned correction (GBT), no live traffic | 232 | 25.4% | 19.0% | 51.9% | -50 |
| base x learned correction (GBT) + live traffic | 224 | 24.8% | 18.4% | 50.8% | -41 |

## ETA range

Quantile-loss trees for the 10% and 90% points of the same correction give a range to quote ("8-11 min"). On the test days 79.3% of trips land inside it (target 80%; 9.9% faster, 10.8% slower). Median width 10.5 min, 73% of the point ETA.
