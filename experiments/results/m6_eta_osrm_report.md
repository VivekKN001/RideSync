# M6: ETA correction on the `osrm` base model (TLC 2024-03, Manhattan trips)

Train: days 1-21 (420,047 trips), test: days 22-31 (199,929 trips). Errors are on observed pickup-to-dropoff times (`trip_time`).
Trip ends are placed on random points in their zones. Placing the same trip twice already changes the base time by a median 14.4%: part of every error below is that, not the model.
Residual log-error sigma of the corrected model: 0.307 (robust, from the IQR: 0.264).

| method | mae_s | mape | median_ape | p90_ape | bias_s |
|---|---|---|---|---|---|
| base model alone (global calibration) | 329 | 40.8% | 30.6% | 84.3% | +67 |
| base x global median factor | 308 | 37.0% | 28.6% | 73.9% | -7 |
| base x hour-of-day table | 289 | 34.9% | 26.7% | 69.9% | -4 |
| base x pickup-zone x hour table | 282 | 34.2% | 26.0% | 68.8% | +0 |
| base x distance-band x hour table | 269 | 34.3% | 24.1% | 69.8% | -27 |
| base x learned correction (GBT), no live traffic | 203 | 24.6% | 18.1% | 50.5% | -34 |
| base x learned correction (GBT) + live traffic | 198 | 24.0% | 17.7% | 49.3% | -40 |

## ETA range

Quantile-loss trees for the 10% and 90% points of the same correction give a range to quote ("8-11 min"). On the test days 77.8% of trips land inside it (target 80%; 11.2% faster, 11.0% slower). Median width 9.2 min, 70% of the point ETA.
