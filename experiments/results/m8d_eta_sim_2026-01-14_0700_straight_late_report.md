# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-01-14_0700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.274). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 129 |  | +124 | 47.1 | 55.5 |  | 51.6 | 297 |  | 249 | 431 |  |
| dist_hour_table | 66 | -63 ± 3 | +22 | 12.2 | 37.1 | -18.3 ± 1.3 | 15.3 | 341 | +44 ± 7 | 325 | 608 | +177 ± 13 |
| learned_eta | 63 | -66 ± 3 | -5 | 6.9 | 35.0 | -20.5 ± 1.7 | 5.9 | 327 | +30 ± 5 | 345 | 629 | +198 ± 17 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 129 | +63 ± 3 | +124 | 47.1 | 55.5 | +18.3 ± 1.3 | 51.6 | 297 | -44 ± 7 | 249 | 431 | -177 ± 13 |
| dist_hour_table | 66 |  | +22 | 12.2 | 37.1 |  | 15.3 | 341 |  | 325 | 608 |  |
| learned_eta | 63 | -3 ± 2 | -5 | 6.9 | 35.0 | -2.2 ± 0.9 | 5.9 | 327 | -14 ± 4 | 345 | 629 | +21 ± 9 |

