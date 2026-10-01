# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2025-10-29_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.276). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 142 |  | +139 | 53.9 | 60.2 |  | 58.8 | 290 |  | 239 | 491 |  |
| dist_hour_table | 75 | -67 ± 3 | +37 | 16.2 | 39.4 | -20.8 ± 1.2 | 20.8 | 375 | +86 ± 6 | 366 | 746 | +256 ± 14 |
| learned_eta | 66 | -76 ± 2 | -7 | 7.1 | 33.7 | -26.5 ± 1.1 | 6.0 | 336 | +47 ± 9 | 360 | 817 | +326 ± 13 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 142 | +67 ± 3 | +139 | 53.9 | 60.2 | +20.8 ± 1.2 | 58.8 | 290 | -86 ± 6 | 239 | 491 | -256 ± 14 |
| dist_hour_table | 75 |  | +37 | 16.2 | 39.4 |  | 20.8 | 375 |  | 366 | 746 |  |
| learned_eta | 66 | -9 ± 4 | -7 | 7.1 | 33.7 | -5.7 ± 0.6 | 6.0 | 336 | -39 ± 6 | 360 | 817 | +71 ± 7 |

