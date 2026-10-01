# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-04-15_0700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.270). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 134 |  | +127 | 49.9 | 58.2 |  | 53.9 | 303 |  | 256 | 405 |  |
| dist_hour_table | 71 | -63 ± 3 | +39 | 15.3 | 38.4 | -19.8 ± 1.4 | 17.9 | 352 | +49 ± 4 | 333 | 597 | +192 ± 14 |
| learned_eta | 62 | -72 ± 4 | -7 | 6.4 | 37.8 | -20.4 ± 2.1 | 5.4 | 329 | +26 ± 3 | 344 | 603 | +198 ± 21 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 134 | +63 ± 3 | +127 | 49.9 | 58.2 | +19.8 ± 1.4 | 53.9 | 303 | -49 ± 4 | 256 | 405 | -192 ± 14 |
| dist_hour_table | 71 |  | +39 | 15.3 | 38.4 |  | 17.9 | 352 |  | 333 | 597 |  |
| learned_eta | 62 | -9 ± 2 | -7 | 6.4 | 37.8 | -0.6 ± 1.1 | 5.4 | 329 | -23 ± 6 | 344 | 603 | +6 ± 11 |

