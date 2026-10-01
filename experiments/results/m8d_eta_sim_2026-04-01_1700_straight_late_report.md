# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-04-01_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.270). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 |  | +137 | 51.4 | 57.6 |  | 56.9 | 268 |  | 214 | 356 |  |
| dist_hour_table | 69 | -69 ± 3 | +40 | 15.1 | 32.1 | -25.5 ± 1.2 | 20.1 | 348 | +80 ± 3 | 321 | 570 | +214 ± 10 |
| learned_eta | 60 | -78 ± 3 | -5 | 5.9 | 27.6 | -30.0 ± 1.0 | 5.9 | 317 | +49 ± 6 | 323 | 608 | +252 ± 8 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 | +69 ± 3 | +137 | 51.4 | 57.6 | +25.5 ± 1.2 | 56.9 | 268 | -80 ± 3 | 214 | 356 | -214 ± 10 |
| dist_hour_table | 69 |  | +40 | 15.1 | 32.1 |  | 20.1 | 348 |  | 321 | 570 |  |
| learned_eta | 60 | -9 ± 2 | -5 | 5.9 | 27.6 | -4.5 ± 0.7 | 5.9 | 317 | -31 ± 4 | 323 | 608 | +38 ± 6 |

