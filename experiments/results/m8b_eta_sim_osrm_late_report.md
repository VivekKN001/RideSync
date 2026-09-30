# M8B: matcher ETA belief vs world truth (`osrm` base, `trips_2026-07-15_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `osrm` × learned correction × lognormal noise (sigma 0.268). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 120 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 100 |  | +82 | 30.3 | 77.1 |  | 72.6 | 295 |  | 264 | 259 |  |
| hour_table | 99 | -1 ± 5 | +86 | 31.5 | 78.5 | +1.4 ± 0.7 | 74.7 | 287 | -8 ± 2 | 256 | 243 | -16 ± 8 |
| zone_hour_table | 103 | +4 ± 4 | +94 | 33.9 | 79.3 | +2.2 ± 1.0 | 76.4 | 288 | -7 ± 3 | 241 | 234 | -25 ± 11 |
| dist_hour_table | 81 | -19 ± 2 | +48 | 18.3 | 64.1 | -13.0 ± 0.7 | 51.5 | 356 | +62 ± 3 | 324 | 406 | +147 ± 8 |
| learned_eta | 64 | -35 ± 3 | -19 | 4.0 | 43.7 | -33.4 ± 0.4 | 10.5 | 339 | +45 ± 4 | 372 | 636 | +377 ± 4 |

## 400 drivers, lateness tolerance median 120 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 100 | +19 ± 2 | +82 | 30.3 | 77.1 | +13.0 ± 0.7 | 72.6 | 295 | -62 ± 3 | 264 | 259 | -147 ± 8 |
| hour_table | 99 | +18 ± 5 | +86 | 31.5 | 78.5 | +14.4 ± 0.7 | 74.7 | 287 | -69 ± 3 | 256 | 243 | -163 ± 8 |
| zone_hour_table | 103 | +23 ± 2 | +94 | 33.9 | 79.3 | +15.2 ± 1.0 | 76.4 | 288 | -69 ± 2 | 241 | 234 | -171 ± 11 |
| dist_hour_table | 81 |  | +48 | 18.3 | 64.1 |  | 51.5 | 356 |  | 324 | 406 |  |
| learned_eta | 64 | -16 ± 3 | -19 | 4.0 | 43.7 | -20.4 ± 0.9 | 10.5 | 339 | -17 ± 4 | 372 | 636 | +231 ± 10 |

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 |  | +124 | 49.4 | 65.9 |  | 59.4 | 352 |  | 327 | 385 |  |
| hour_table | 140 | +2 ± 3 | +129 | 50.7 | 66.6 | +0.7 ± 0.4 | 61.1 | 343 | -9 ± 1 | 316 | 377 | -8 ± 4 |
| zone_hour_table | 142 | +3 ± 5 | +131 | 51.6 | 65.6 | -0.3 ± 1.4 | 61.1 | 351 | -1 ± 6 | 324 | 389 | +3 ± 16 |
| dist_hour_table | 107 | -31 ± 2 | +81 | 32.9 | 54.5 | -11.4 ± 1.3 | 40.0 | 396 | +44 ± 3 | 378 | 514 | +128 ± 14 |
| learned_eta | 70 | -68 ± 2 | -9 | 7.6 | 40.4 | -25.5 ± 0.7 | 6.2 | 344 | -8 ± 8 | 389 | 673 | +288 ± 8 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 | +31 ± 2 | +124 | 49.4 | 65.9 | +11.4 ± 1.3 | 59.4 | 352 | -44 ± 3 | 327 | 385 | -128 ± 14 |
| hour_table | 140 | +33 ± 4 | +129 | 50.7 | 66.6 | +12.1 ± 1.4 | 61.1 | 343 | -53 ± 4 | 316 | 377 | -136 ± 16 |
| zone_hour_table | 142 | +35 ± 5 | +131 | 51.6 | 65.6 | +11.1 ± 0.5 | 61.1 | 351 | -45 ± 7 | 324 | 389 | -125 ± 6 |
| dist_hour_table | 107 |  | +81 | 32.9 | 54.5 |  | 40.0 | 396 |  | 378 | 514 |  |
| learned_eta | 70 | -37 ± 2 | -9 | 7.6 | 40.4 | -14.1 ± 1.0 | 6.2 | 344 | -52 ± 5 | 389 | 673 | +159 ± 11 |

## 400 drivers, lateness tolerance median 300 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 189 |  | +177 | 65.1 | 47.6 |  | 38.0 | 433 |  | 417 | 592 |  |
| hour_table | 195 | +6 ± 4 | +185 | 67.3 | 48.5 | +1.0 ± 1.0 | 40.5 | 432 | -1 ± 3 | 416 | 581 | -11 ± 11 |
| zone_hour_table | 193 | +4 ± 4 | +183 | 67.4 | 47.3 | -0.2 ± 1.0 | 39.5 | 434 | +1 ± 3 | 415 | 595 | +2 ± 12 |
| dist_hour_table | 145 | -44 ± 5 | +120 | 47.4 | 42.5 | -5.1 ± 0.8 | 23.1 | 440 | +7 ± 9 | 450 | 650 | +57 ± 9 |
| learned_eta | 78 | -110 ± 4 | +3 | 12.1 | 37.6 | -10.0 ± 0.9 | 2.6 | 349 | -84 ± 6 | 407 | 705 | +113 ± 10 |

## 400 drivers, lateness tolerance median 300 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 189 | +44 ± 5 | +177 | 65.1 | 47.6 | +5.1 ± 0.8 | 38.0 | 433 | -7 ± 9 | 417 | 592 | -57 ± 9 |
| hour_table | 195 | +50 ± 6 | +185 | 67.3 | 48.5 | +6.1 ± 0.9 | 40.5 | 432 | -7 ± 8 | 416 | 581 | -69 ± 11 |
| zone_hour_table | 193 | +48 ± 7 | +183 | 67.4 | 47.3 | +4.9 ± 1.4 | 39.5 | 434 | -5 ± 10 | 415 | 595 | -55 ± 16 |
| dist_hour_table | 145 |  | +120 | 47.4 | 42.5 |  | 23.1 | 440 |  | 450 | 650 |  |
| learned_eta | 78 | -66 ± 3 | +3 | 12.1 | 37.6 | -4.9 ± 1.1 | 2.6 | 349 | -91 ± 4 | 407 | 705 | +55 ± 12 |

