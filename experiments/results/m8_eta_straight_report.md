# M8: ETA correction on the `straight` base model (TLC, Manhattan trips)

Train: 2025-01-01 to 2026-06-30 (1,637,829 trips), test: 2026-07-01 to 2026-07-31 (92,991 trips). Errors are on observed pickup-to-dropoff times (`trip_time`).
Trip ends are placed on random points in their zones. Placing the same trip twice already changes the base time by a median 13.9%: part of every error below is that, not the model.
Residual log-error sigma of the corrected model: 0.313 (robust, from the IQR: 0.275).

| method | mae_s | mape | median_ape | p90_ape | bias_s |
|---|---|---|---|---|---|
| base model alone (global calibration) | 505 | 55.6% | 38.7% | 126.5% | +255 |
| base x global median factor | 420 | 45.3% | 34.3% | 92.2% | +68 |
| base x hour-of-day table | 400 | 42.9% | 32.7% | 86.4% | +68 |
| base x pickup-zone x hour table | 359 | 38.9% | 30.7% | 78.0% | +43 |
| base x distance-band x hour table | 279 | 33.4% | 24.5% | 67.5% | -59 |
| base x learned correction (GBT), no live traffic | 221 | 24.9% | 19.0% | 50.2% | -70 |
| base x learned correction (GBT) + live traffic | 211 | 24.8% | 18.4% | 51.1% | -32 |

## ETA range

Quantile-loss trees for the 10% and 90% points of the same correction give a range to quote ("8-11 min"). On the test days 79.5% of trips land inside it (target 80%; 10.4% faster, 10.2% slower). Median width 9.9 min, 72% of the point ETA.
