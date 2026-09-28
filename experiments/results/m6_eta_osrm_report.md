# M6: ETA correction on the `osrm` base model (TLC 2024-03, Manhattan trips)

Train: days 1-21 (420,047 trips), test: days 22-31 (199,929 trips). Errors are on observed pickup-to-dropoff times (`trip_time`).
Trip ends are placed on random points in their zones. Placing the same trip twice already changes the base time by a median 14.4%: part of every error below is that, not the model.
Residual log-error sigma of the corrected model: 0.307 (robust, from the IQR: 0.264).

| method | mae_s | mape | median_ape | p90_ape | bias_s |
|---|---|---|---|---|---|
| base model alone (global calibration) | 329 | 40.8% | 30.6% | 84.3% | +67 |
| base x global median factor | 308 | 37.0% | 28.6% | 73.9% | -7 |
| base x pickup-zone x hour table | 282 | 34.2% | 26.0% | 68.8% | +0 |
| base x learned correction (GBT), no live traffic | 203 | 24.6% | 18.1% | 50.5% | -34 |
| base x learned correction (GBT) + live traffic | 198 | 24.0% | 17.7% | 49.3% | -40 |
