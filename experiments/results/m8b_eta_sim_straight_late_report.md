# M8B: matcher ETA belief vs world truth (`straight` base, `trips_2026-07-15_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.275). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 120 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 104 |  | +102 | 33.2 | 70.7 |  | 70.3 | 222 |  | 168 | 331 |  |
| hour_table | 105 | +1 ± 3 | +103 | 33.4 | 71.5 | +0.8 ± 1.1 | 71.3 | 214 | -8 ± 3 | 160 | 322 | -9 ± 12 |
| zone_hour_table | 105 | +2 ± 3 | +105 | 33.6 | 72.3 | +1.6 ± 1.0 | 72.1 | 213 | -9 ± 4 | 156 | 313 | -18 ± 11 |
| dist_hour_table | 57 | -47 ± 3 | +18 | 7.1 | 41.6 | -29.1 ± 1.2 | 28.2 | 341 | +120 ± 5 | 305 | 660 | +329 ± 13 |
| learned_eta | 57 | -47 ± 3 | -15 | 3.4 | 33.4 | -37.2 ± 1.2 | 10.7 | 322 | +100 ± 6 | 324 | 752 | +421 ± 13 |

## 400 drivers, lateness tolerance median 120 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 104 | +47 ± 3 | +102 | 33.2 | 70.7 | +29.1 ± 1.2 | 70.3 | 222 | -120 ± 5 | 168 | 331 | -329 ± 13 |
| hour_table | 105 | +48 ± 3 | +103 | 33.4 | 71.5 | +30.0 ± 0.9 | 71.3 | 214 | -127 ± 6 | 160 | 322 | -338 ± 10 |
| zone_hour_table | 105 | +49 ± 2 | +105 | 33.6 | 72.3 | +30.7 ± 0.6 | 72.1 | 213 | -128 ± 7 | 156 | 313 | -347 ± 6 |
| dist_hour_table | 57 |  | +18 | 7.1 | 41.6 |  | 28.2 | 341 |  | 305 | 660 |  |
| learned_eta | 57 | +1 ± 0 | -15 | 3.4 | 33.4 | -8.1 ± 0.7 | 10.7 | 322 | -20 ± 4 | 324 | 752 | +92 ± 8 |

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 137 |  | +133 | 50.4 | 58.6 |  | 57.5 | 281 |  | 227 | 468 |  |
| hour_table | 142 | +6 ± 4 | +139 | 53.1 | 59.3 | +0.7 ± 1.2 | 58.6 | 273 | -7 ± 4 | 224 | 460 | -8 ± 14 |
| zone_hour_table | 142 | +5 ± 3 | +140 | 53.4 | 60.0 | +1.5 ± 1.5 | 59.5 | 275 | -6 ± 3 | 221 | 452 | -16 ± 17 |
| dist_hour_table | 72 | -65 ± 3 | +36 | 15.5 | 36.3 | -22.2 ± 1.3 | 20.5 | 363 | +82 ± 7 | 345 | 719 | +251 ± 15 |
| learned_eta | 62 | -74 ± 4 | -7 | 6.3 | 30.6 | -28.0 ± 1.3 | 6.4 | 328 | +47 ± 5 | 341 | 784 | +316 ± 14 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 137 | +65 ± 3 | +133 | 50.4 | 58.6 | +22.2 ± 1.3 | 57.5 | 281 | -82 ± 7 | 227 | 468 | -251 ± 15 |
| hour_table | 142 | +70 ± 3 | +139 | 53.1 | 59.3 | +22.9 ± 1.3 | 58.6 | 273 | -90 ± 7 | 224 | 460 | -259 ± 15 |
| zone_hour_table | 142 | +70 ± 2 | +140 | 53.4 | 60.0 | +23.7 ± 1.3 | 59.5 | 275 | -88 ± 6 | 221 | 452 | -268 ± 15 |
| dist_hour_table | 72 |  | +36 | 15.5 | 36.3 |  | 20.5 | 363 |  | 345 | 719 |  |
| learned_eta | 62 | -10 ± 2 | -7 | 6.3 | 30.6 | -5.7 ± 0.8 | 6.4 | 328 | -35 ± 5 | 341 | 784 | +65 ± 10 |

## 400 drivers, lateness tolerance median 300 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 189 |  | +184 | 68.2 | 41.1 |  | 37.7 | 378 |  | 335 | 665 |  |
| hour_table | 196 | +7 ± 3 | +192 | 70.6 | 42.0 | +0.9 ± 0.5 | 39.3 | 370 | -8 ± 2 | 329 | 655 | -10 ± 5 |
| zone_hour_table | 195 | +6 ± 2 | +193 | 71.4 | 41.8 | +0.6 ± 0.6 | 39.3 | 372 | -6 ± 5 | 329 | 657 | -7 ± 7 |
| dist_hour_table | 94 | -95 ± 3 | +60 | 24.9 | 31.1 | -10.1 ± 1.0 | 11.6 | 387 | +9 ± 7 | 392 | 778 | +114 ± 11 |
| learned_eta | 70 | -119 ± 3 | +4 | 10.5 | 27.8 | -13.4 ± 0.8 | 2.5 | 335 | -43 ± 6 | 361 | 816 | +151 ± 9 |

## 400 drivers, lateness tolerance median 300 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 189 | +95 ± 3 | +184 | 68.2 | 41.1 | +10.1 ± 1.0 | 37.7 | 378 | -9 ± 7 | 335 | 665 | -114 ± 11 |
| hour_table | 196 | +102 ± 4 | +192 | 70.6 | 42.0 | +10.9 ± 1.1 | 39.3 | 370 | -17 ± 6 | 329 | 655 | -124 ± 12 |
| zone_hour_table | 195 | +102 ± 4 | +193 | 71.4 | 41.8 | +10.7 ± 0.5 | 39.3 | 372 | -15 ± 11 | 329 | 657 | -121 ± 6 |
| dist_hour_table | 94 |  | +60 | 24.9 | 31.1 |  | 11.6 | 387 |  | 392 | 778 |  |
| learned_eta | 70 | -24 ± 3 | +4 | 10.5 | 27.8 | -3.3 ± 0.7 | 2.5 | 335 | -52 ± 6 | 361 | 816 | +37 ± 8 |

