# M8B: matcher ETA belief vs world truth (`osrm` base, `trips_2026-07-15_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `osrm` × learned correction × lognormal noise (sigma 0.268). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Caveat: simulated riders cancel on a long *quote* but never while the driver is en route, so an optimistic belief is not punished for being late. More cancellations under honest ETAs can be that artifact alone; compare quote accuracy first.

## 400 drivers: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 276 |  | +265 | 74.4 | 25.1 |  | 0.0 | 527 |  | 590 | 846 |  |
| hour_table | 287 | +12 ± 2 | +279 | 76.6 | 24.2 | -0.9 ± 0.3 | 0.0 | 539 | +11 ± 3 | 598 | 856 | +10 ± 4 |
| zone_hour_table | 282 | +6 ± 3 | +274 | 76.8 | 23.3 | -1.8 ± 0.5 | 0.0 | 540 | +13 ± 4 | 599 | 866 | +21 ± 5 |
| dist_hour_table | 217 | -59 ± 3 | +194 | 59.2 | 29.9 | +4.8 ± 0.2 | 0.0 | 481 | -46 ± 4 | 573 | 791 | -54 ± 2 |
| learned_eta | 87 | -189 ± 3 | +14 | 15.7 | 35.9 | +10.7 ± 1.0 | 0.0 | 351 | -176 ± 6 | 423 | 724 | -121 ± 11 |

## 400 drivers: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 276 | +59 ± 3 | +265 | 74.4 | 25.1 | -4.8 ± 0.2 | 0.0 | 527 | +46 ± 4 | 590 | 846 | +54 ± 2 |
| hour_table | 287 | +70 ± 3 | +279 | 76.6 | 24.2 | -5.7 ± 0.4 | 0.0 | 539 | +58 ± 4 | 598 | 856 | +64 ± 5 |
| zone_hour_table | 282 | +65 ± 5 | +274 | 76.8 | 23.3 | -6.6 ± 0.5 | 0.0 | 540 | +59 ± 5 | 599 | 866 | +75 ± 6 |
| dist_hour_table | 217 |  | +194 | 59.2 | 29.9 |  | 0.0 | 481 |  | 573 | 791 |  |
| learned_eta | 87 | -130 ± 3 | +14 | 15.7 | 35.9 | +6.0 ± 1.1 | 0.0 | 351 | -130 ± 6 | 423 | 724 | -67 ± 12 |

