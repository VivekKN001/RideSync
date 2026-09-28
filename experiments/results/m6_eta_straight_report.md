# M6: ETA correction on the `straight` base model (TLC 2024-03, Manhattan trips)

Train: days 1-21 (420,020 trips), test: days 22-31 (199,899 trips). Errors are on observed pickup-to-dropoff times (`trip_time`).
Trip ends are placed on random points in their zones. Placing the same trip twice already changes the base time by a median 13.9%: part of every error below is that, not the model.
Residual log-error sigma of the corrected model: 0.312 (robust, from the IQR: 0.273).

| method | mae_s | mape | median_ape | p90_ape | bias_s |
|---|---|---|---|---|---|
| base model alone (global calibration) | 462 | 51.5% | 36.6% | 114.7% | +206 |
| base x global median factor | 411 | 45.3% | 34.1% | 93.4% | +92 |
| base x pickup-zone x hour table | 355 | 39.6% | 30.5% | 80.0% | +69 |
| base x learned correction (GBT) | 205 | 24.7% | 18.3% | 51.1% | -29 |
