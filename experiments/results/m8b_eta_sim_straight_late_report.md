# M8B: matcher ETA belief vs world truth (`straight` base, `trips_2026-07-15_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.275). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 120 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 104 |  | +102 | 33.2 | 70.7 |  | 70.3 | 222 |  | 168 | 331 |  |
| hour_table | 105 | +1 ± 2 | +103 | 33.4 | 71.5 | +0.8 ± 0.8 | 71.3 | 214 | -8 ± 2 | 160 | 322 | -9 ± 9 |
| zone_hour_table | 105 | +2 ± 2 | +105 | 33.6 | 72.3 | +1.6 ± 0.8 | 72.1 | 213 | -9 ± 3 | 156 | 313 | -18 ± 9 |
| dist_hour_table | 57 | -47 ± 2 | +18 | 7.1 | 41.6 | -29.1 ± 0.9 | 28.2 | 341 | +120 ± 4 | 305 | 660 | +329 ± 10 |
| learned_eta | 57 | -47 ± 2 | -15 | 3.4 | 33.4 | -37.2 ± 0.9 | 10.7 | 322 | +100 ± 5 | 324 | 752 | +421 ± 10 |

## 400 drivers, lateness tolerance median 120 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 104 | +47 ± 2 | +102 | 33.2 | 70.7 | +29.1 ± 0.9 | 70.3 | 222 | -120 ± 4 | 168 | 331 | -329 ± 10 |
| hour_table | 105 | +48 ± 2 | +103 | 33.4 | 71.5 | +30.0 ± 0.7 | 71.3 | 214 | -127 ± 4 | 160 | 322 | -338 ± 8 |
| zone_hour_table | 105 | +49 ± 2 | +105 | 33.6 | 72.3 | +30.7 ± 0.4 | 72.1 | 213 | -128 ± 5 | 156 | 313 | -347 ± 5 |
| dist_hour_table | 57 |  | +18 | 7.1 | 41.6 |  | 28.2 | 341 |  | 305 | 660 |  |
| learned_eta | 57 | +1 ± 0 | -15 | 3.4 | 33.4 | -8.1 ± 0.5 | 10.7 | 322 | -20 ± 3 | 324 | 752 | +92 ± 6 |

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 137 |  | +133 | 50.4 | 58.6 |  | 57.5 | 281 |  | 227 | 468 |  |
| hour_table | 142 | +6 ± 3 | +139 | 53.1 | 59.3 | +0.7 ± 0.9 | 58.6 | 273 | -7 ± 3 | 224 | 460 | -8 ± 11 |
| zone_hour_table | 142 | +5 ± 2 | +140 | 53.4 | 60.0 | +1.5 ± 1.2 | 59.5 | 275 | -6 ± 2 | 221 | 452 | -16 ± 13 |
| dist_hour_table | 72 | -65 ± 2 | +36 | 15.5 | 36.3 | -22.2 ± 1.0 | 20.5 | 363 | +82 ± 5 | 345 | 719 | +251 ± 11 |
| learned_eta | 62 | -74 ± 3 | -7 | 6.3 | 30.6 | -28.0 ± 1.0 | 6.4 | 328 | +47 ± 4 | 341 | 784 | +316 ± 11 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 137 | +65 ± 2 | +133 | 50.4 | 58.6 | +22.2 ± 1.0 | 57.5 | 281 | -82 ± 5 | 227 | 468 | -251 ± 11 |
| hour_table | 142 | +70 ± 2 | +139 | 53.1 | 59.3 | +22.9 ± 1.0 | 58.6 | 273 | -90 ± 6 | 224 | 460 | -259 ± 11 |
| zone_hour_table | 142 | +70 ± 2 | +140 | 53.4 | 60.0 | +23.7 ± 1.0 | 59.5 | 275 | -88 ± 4 | 221 | 452 | -268 ± 12 |
| dist_hour_table | 72 |  | +36 | 15.5 | 36.3 |  | 20.5 | 363 |  | 345 | 719 |  |
| learned_eta | 62 | -10 ± 2 | -7 | 6.3 | 30.6 | -5.7 ± 0.6 | 6.4 | 328 | -35 ± 4 | 341 | 784 | +65 ± 7 |

## 400 drivers, lateness tolerance median 300 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 189 |  | +184 | 68.2 | 41.1 |  | 37.7 | 378 |  | 335 | 665 |  |
| hour_table | 196 | +7 ± 2 | +192 | 70.6 | 42.0 | +0.9 ± 0.4 | 39.3 | 370 | -8 ± 1 | 329 | 655 | -10 ± 4 |
| zone_hour_table | 195 | +6 ± 2 | +193 | 71.4 | 41.8 | +0.6 ± 0.5 | 39.3 | 372 | -6 ± 4 | 329 | 657 | -7 ± 5 |
| dist_hour_table | 94 | -95 ± 2 | +60 | 24.9 | 31.1 | -10.1 ± 0.8 | 11.6 | 387 | +9 ± 5 | 392 | 778 | +114 ± 9 |
| learned_eta | 70 | -119 ± 2 | +4 | 10.5 | 27.8 | -13.4 ± 0.6 | 2.5 | 335 | -43 ± 5 | 361 | 816 | +151 ± 7 |

## 400 drivers, lateness tolerance median 300 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 189 | +95 ± 2 | +184 | 68.2 | 41.1 | +10.1 ± 0.8 | 37.7 | 378 | -9 ± 5 | 335 | 665 | -114 ± 9 |
| hour_table | 196 | +102 ± 3 | +192 | 70.6 | 42.0 | +10.9 ± 0.8 | 39.3 | 370 | -17 ± 4 | 329 | 655 | -124 ± 9 |
| zone_hour_table | 195 | +102 ± 3 | +193 | 71.4 | 41.8 | +10.7 ± 0.4 | 39.3 | 372 | -15 ± 8 | 329 | 657 | -121 ± 4 |
| dist_hour_table | 94 |  | +60 | 24.9 | 31.1 |  | 11.6 | 387 |  | 392 | 778 |  |
| learned_eta | 70 | -24 ± 2 | +4 | 10.5 | 27.8 | -3.3 ± 0.5 | 2.5 | 335 | -52 ± 5 | 361 | 816 | +37 ± 6 |

