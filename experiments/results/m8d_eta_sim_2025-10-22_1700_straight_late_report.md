# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2025-10-22_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.276). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 143 |  | +142 | 53.9 | 61.0 |  | 60.0 | 287 |  | 235 | 454 |  |
| dist_hour_table | 76 | -68 ± 4 | +37 | 16.3 | 38.6 | -22.4 ± 1.3 | 21.5 | 373 | +86 ± 9 | 361 | 716 | +262 ± 15 |
| learned_eta | 65 | -78 ± 4 | -8 | 6.7 | 33.1 | -27.9 ± 1.9 | 6.4 | 338 | +50 ± 10 | 357 | 780 | +326 ± 22 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 143 | +68 ± 4 | +142 | 53.9 | 61.0 | +22.4 ± 1.3 | 60.0 | 287 | -86 ± 9 | 235 | 454 | -262 ± 15 |
| dist_hour_table | 76 |  | +37 | 16.3 | 38.6 |  | 21.5 | 373 |  | 361 | 716 |  |
| learned_eta | 65 | -10 ± 1 | -8 | 6.7 | 33.1 | -5.5 ± 1.1 | 6.4 | 338 | -36 ± 4 | 357 | 780 | +64 ± 13 |

