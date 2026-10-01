# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-07-22_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.275). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 139 |  | +138 | 52.7 | 59.0 |  | 57.9 | 276 |  | 218 | 398 |  |
| dist_hour_table | 69 | -70 ± 5 | +39 | 14.9 | 35.8 | -23.2 ± 1.0 | 22.0 | 356 | +81 ± 8 | 328 | 622 | +225 ± 9 |
| learned_eta | 61 | -78 ± 3 | -4 | 6.6 | 30.6 | -28.3 ± 1.0 | 6.0 | 322 | +47 ± 9 | 333 | 672 | +275 ± 10 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 139 | +70 ± 5 | +138 | 52.7 | 59.0 | +23.2 ± 1.0 | 57.9 | 276 | -81 ± 8 | 218 | 398 | -225 ± 9 |
| dist_hour_table | 69 |  | +39 | 14.9 | 35.8 |  | 22.0 | 356 |  | 328 | 622 |  |
| learned_eta | 61 | -8 ± 2 | -4 | 6.6 | 30.6 | -5.1 ± 1.4 | 6.0 | 322 | -34 ± 5 | 333 | 672 | +50 ± 14 |

