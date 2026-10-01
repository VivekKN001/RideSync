# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-07-29_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.275). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 |  | +135 | 52.1 | 56.5 |  | 55.3 | 271 |  | 221 | 438 |  |
| dist_hour_table | 70 | -68 ± 3 | +35 | 14.2 | 31.8 | -24.8 ± 0.8 | 18.6 | 349 | +79 ± 4 | 329 | 688 | +250 ± 8 |
| learned_eta | 61 | -77 ± 2 | -5 | 6.4 | 25.7 | -30.9 ± 0.9 | 6.4 | 317 | +46 ± 8 | 329 | 749 | +311 ± 9 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 | +68 ± 3 | +135 | 52.1 | 56.5 | +24.8 ± 0.8 | 55.3 | 271 | -79 ± 4 | 221 | 438 | -250 ± 8 |
| dist_hour_table | 70 |  | +35 | 14.2 | 31.8 |  | 18.6 | 349 |  | 329 | 688 |  |
| learned_eta | 61 | -9 ± 3 | -5 | 6.4 | 25.7 | -6.1 ± 1.0 | 6.4 | 317 | -33 ± 5 | 329 | 749 | +61 ± 10 |

