# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2025-10-01_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.276). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 141 |  | +138 | 53.3 | 58.2 |  | 57.1 | 281 |  | 231 | 399 |  |
| dist_hour_table | 71 | -70 ± 3 | +39 | 15.5 | 32.9 | -25.3 ± 1.3 | 19.3 | 355 | +74 ± 5 | 336 | 641 | +242 ± 12 |
| learned_eta | 64 | -78 ± 4 | -7 | 6.5 | 28.8 | -29.4 ± 1.7 | 6.1 | 322 | +42 ± 6 | 338 | 680 | +281 ± 16 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 141 | +70 ± 3 | +138 | 53.3 | 58.2 | +25.3 ± 1.3 | 57.1 | 281 | -74 ± 5 | 231 | 399 | -242 ± 12 |
| dist_hour_table | 71 |  | +39 | 15.5 | 32.9 |  | 19.3 | 355 |  | 336 | 641 |  |
| learned_eta | 64 | -8 ± 2 | -7 | 6.5 | 28.8 | -4.1 ± 0.8 | 6.1 | 322 | -32 ± 5 | 338 | 680 | +39 ± 7 |

