# M6: ETA correction on the `osrm` base model (TLC 2024-03, Manhattan trips)

Train: days 1-21 (420,050 trips), test: days 22-31 (199,924 trips). Errors are on observed pickup-to-dropoff times (`trip_time`).
Trip ends are placed on random points in their zones. Placing the same trip twice already changes the base time by a median 14.4%: part of every error below is that, not the model.
Residual log-error sigma of the corrected model: 0.310 (robust, from the IQR: 0.270).

| method | mae_s | mape | median_ape | p90_ape | bias_s |
|---|---|---|---|---|---|
| base model alone (global calibration) | 329 | 40.7% | 30.6% | 84.2% | +66 |
| base x global median factor | 307 | 36.8% | 28.6% | 73.6% | -9 |
| base x pickup-zone x hour table | 281 | 33.9% | 25.7% | 68.4% | -2 |
| base x learned correction (GBT) | 202 | 24.5% | 18.1% | 50.4% | -34 |
