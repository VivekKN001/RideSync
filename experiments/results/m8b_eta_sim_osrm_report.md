# M8B: matcher ETA belief vs world truth (`osrm` base, `trips_2026-07-15_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `osrm` × learned correction × lognormal noise (sigma 0.268). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Caveat: simulated riders cancel on a long *quote* but never while the driver is en route, so an optimistic belief is not punished for being late. More cancellations under honest ETAs can be that artifact alone; compare quote accuracy first.

## 400 drivers: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 276 |  | +265 | 74.4 | 25.1 |  | 0.0 | 527 |  | 590 | 846 |  |
| hour_table | 287 | +12 ± 3 | +279 | 76.6 | 24.2 | -0.9 ± 0.4 | 0.0 | 539 | +11 ± 4 | 598 | 856 | +10 ± 5 |
| zone_hour_table | 282 | +6 ± 4 | +274 | 76.8 | 23.3 | -1.8 ± 0.6 | 0.0 | 540 | +13 ± 5 | 599 | 866 | +21 ± 7 |
| dist_hour_table | 217 | -59 ± 3 | +194 | 59.2 | 29.9 | +4.8 ± 0.2 | 0.0 | 481 | -46 ± 5 | 573 | 791 | -54 ± 3 |
| learned_eta | 87 | -189 ± 4 | +14 | 15.7 | 35.9 | +10.7 ± 1.3 | 0.0 | 351 | -176 ± 8 | 423 | 724 | -121 ± 15 |

## 400 drivers: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 276 | +59 ± 3 | +265 | 74.4 | 25.1 | -4.8 ± 0.2 | 0.0 | 527 | +46 ± 5 | 590 | 846 | +54 ± 3 |
| hour_table | 287 | +70 ± 3 | +279 | 76.6 | 24.2 | -5.7 ± 0.6 | 0.0 | 539 | +58 ± 5 | 598 | 856 | +64 ± 7 |
| zone_hour_table | 282 | +65 ± 7 | +274 | 76.8 | 23.3 | -6.6 ± 0.7 | 0.0 | 540 | +59 ± 7 | 599 | 866 | +75 ± 8 |
| dist_hour_table | 217 |  | +194 | 59.2 | 29.9 |  | 0.0 | 481 |  | 573 | 791 |  |
| learned_eta | 87 | -130 ± 4 | +14 | 15.7 | 35.9 | +6.0 ± 1.4 | 0.0 | 351 | -130 ± 8 | 423 | 724 | -67 ± 16 |

