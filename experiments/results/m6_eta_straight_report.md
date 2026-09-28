# M6: ETA correction on the `straight` base model (TLC 2024-03, Manhattan trips)

Train: days 1-21 (420,031 trips), test: days 22-31 (199,916 trips). Errors are on observed pickup-to-dropoff times (`trip_time`).
Trip ends are placed on random points in their zones. Placing the same trip twice already changes the base time by a median 13.9%: part of every error below is that, not the model.
Residual log-error sigma of the corrected model: 0.309 (robust, from the IQR: 0.267).

| method | mae_s | mape | median_ape | p90_ape | bias_s |
|---|---|---|---|---|---|
| base model alone (global calibration) | 464 | 51.8% | 36.6% | 115.4% | +207 |
| base x global median factor | 413 | 45.6% | 34.1% | 94.0% | +93 |
| base x pickup-zone x hour table | 359 | 39.9% | 30.7% | 80.8% | +71 |
| base x learned correction (GBT), no live traffic | 205 | 24.8% | 18.3% | 51.2% | -29 |
| base x learned correction (GBT) + live traffic | 201 | 24.2% | 17.9% | 49.9% | -34 |
