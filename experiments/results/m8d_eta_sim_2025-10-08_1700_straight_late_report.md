# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2025-10-08_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.276). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 142 |  | +139 | 54.1 | 59.1 |  | 58.2 | 290 |  | 243 | 492 |  |
| dist_hour_table | 75 | -67 ± 4 | +31 | 15.0 | 37.6 | -21.5 ± 1.2 | 19.1 | 374 | +84 ± 6 | 372 | 751 | +259 ± 15 |
| learned_eta | 66 | -76 ± 4 | -7 | 7.0 | 31.9 | -27.2 ± 1.5 | 6.6 | 341 | +51 ± 7 | 364 | 820 | +328 ± 18 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 142 | +67 ± 4 | +139 | 54.1 | 59.1 | +21.5 ± 1.2 | 58.2 | 290 | -84 ± 6 | 243 | 492 | -259 ± 15 |
| dist_hour_table | 75 |  | +31 | 15.0 | 37.6 |  | 19.1 | 374 |  | 372 | 751 |  |
| learned_eta | 66 | -9 ± 1 | -7 | 7.0 | 31.9 | -5.7 ± 1.0 | 6.6 | 341 | -33 ± 3 | 364 | 820 | +69 ± 12 |

