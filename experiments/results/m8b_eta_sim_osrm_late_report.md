# M8B: matcher ETA belief vs world truth (`osrm` base, `trips_2026-07-15_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `osrm` × learned correction × lognormal noise (sigma 0.268). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 120 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 100 |  | +82 | 30.3 | 77.1 |  | 72.6 | 295 |  | 264 | 259 |  |
| hour_table | 99 | -1 ± 4 | +86 | 31.5 | 78.5 | +1.4 ± 0.5 | 74.7 | 287 | -8 ± 2 | 256 | 243 | -16 ± 6 |
| zone_hour_table | 103 | +4 ± 3 | +94 | 33.9 | 79.3 | +2.2 ± 0.7 | 76.4 | 288 | -7 ± 2 | 241 | 234 | -25 ± 8 |
| dist_hour_table | 81 | -19 ± 2 | +48 | 18.3 | 64.1 | -13.0 ± 0.5 | 51.5 | 356 | +62 ± 2 | 324 | 406 | +147 ± 6 |
| learned_eta | 64 | -35 ± 2 | -19 | 4.0 | 43.7 | -33.4 ± 0.3 | 10.5 | 339 | +45 ± 3 | 372 | 636 | +377 ± 3 |

## 400 drivers, lateness tolerance median 120 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 100 | +19 ± 2 | +82 | 30.3 | 77.1 | +13.0 ± 0.5 | 72.6 | 295 | -62 ± 2 | 264 | 259 | -147 ± 6 |
| hour_table | 99 | +18 ± 4 | +86 | 31.5 | 78.5 | +14.4 ± 0.5 | 74.7 | 287 | -69 ± 2 | 256 | 243 | -163 ± 6 |
| zone_hour_table | 103 | +23 ± 1 | +94 | 33.9 | 79.3 | +15.2 ± 0.8 | 76.4 | 288 | -69 ± 2 | 241 | 234 | -171 ± 9 |
| dist_hour_table | 81 |  | +48 | 18.3 | 64.1 |  | 51.5 | 356 |  | 324 | 406 |  |
| learned_eta | 64 | -16 ± 2 | -19 | 4.0 | 43.7 | -20.4 ± 0.7 | 10.5 | 339 | -17 ± 3 | 372 | 636 | +231 ± 8 |

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 |  | +124 | 49.4 | 65.9 |  | 59.4 | 352 |  | 327 | 385 |  |
| hour_table | 140 | +2 ± 2 | +129 | 50.7 | 66.6 | +0.7 ± 0.3 | 61.1 | 343 | -9 ± 1 | 316 | 377 | -8 ± 3 |
| zone_hour_table | 142 | +3 ± 4 | +131 | 51.6 | 65.6 | -0.3 ± 1.1 | 61.1 | 351 | -1 ± 4 | 324 | 389 | +3 ± 12 |
| dist_hour_table | 107 | -31 ± 1 | +81 | 32.9 | 54.5 | -11.4 ± 1.0 | 40.0 | 396 | +44 ± 3 | 378 | 514 | +128 ± 11 |
| learned_eta | 70 | -68 ± 1 | -9 | 7.6 | 40.4 | -25.5 ± 0.6 | 6.2 | 344 | -8 ± 6 | 389 | 673 | +288 ± 6 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 | +31 ± 1 | +124 | 49.4 | 65.9 | +11.4 ± 1.0 | 59.4 | 352 | -44 ± 3 | 327 | 385 | -128 ± 11 |
| hour_table | 140 | +33 ± 3 | +129 | 50.7 | 66.6 | +12.1 ± 1.1 | 61.1 | 343 | -53 ± 3 | 316 | 377 | -136 ± 12 |
| zone_hour_table | 142 | +35 ± 4 | +131 | 51.6 | 65.6 | +11.1 ± 0.4 | 61.1 | 351 | -45 ± 5 | 324 | 389 | -125 ± 5 |
| dist_hour_table | 107 |  | +81 | 32.9 | 54.5 |  | 40.0 | 396 |  | 378 | 514 |  |
| learned_eta | 70 | -37 ± 2 | -9 | 7.6 | 40.4 | -14.1 ± 0.8 | 6.2 | 344 | -52 ± 4 | 389 | 673 | +159 ± 9 |

## 400 drivers, lateness tolerance median 300 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 189 |  | +177 | 65.1 | 47.6 |  | 38.0 | 433 |  | 417 | 592 |  |
| hour_table | 195 | +6 ± 3 | +185 | 67.3 | 48.5 | +1.0 ± 0.7 | 40.5 | 432 | -1 ± 2 | 416 | 581 | -11 ± 8 |
| zone_hour_table | 193 | +4 ± 3 | +183 | 67.4 | 47.3 | -0.2 ± 0.8 | 39.5 | 434 | +1 ± 3 | 415 | 595 | +2 ± 9 |
| dist_hour_table | 145 | -44 ± 4 | +120 | 47.4 | 42.5 | -5.1 ± 0.6 | 23.1 | 440 | +7 ± 7 | 450 | 650 | +57 ± 7 |
| learned_eta | 78 | -110 ± 3 | +3 | 12.1 | 37.6 | -10.0 ± 0.7 | 2.6 | 349 | -84 ± 5 | 407 | 705 | +113 ± 8 |

## 400 drivers, lateness tolerance median 300 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 189 | +44 ± 4 | +177 | 65.1 | 47.6 | +5.1 ± 0.6 | 38.0 | 433 | -7 ± 7 | 417 | 592 | -57 ± 7 |
| hour_table | 195 | +50 ± 4 | +185 | 67.3 | 48.5 | +6.1 ± 0.7 | 40.5 | 432 | -7 ± 6 | 416 | 581 | -69 ± 8 |
| zone_hour_table | 193 | +48 ± 5 | +183 | 67.4 | 47.3 | +4.9 ± 1.1 | 39.5 | 434 | -5 ± 7 | 415 | 595 | -55 ± 12 |
| dist_hour_table | 145 |  | +120 | 47.4 | 42.5 |  | 23.1 | 440 |  | 450 | 650 |  |
| learned_eta | 78 | -66 ± 3 | +3 | 12.1 | 37.6 | -4.9 ± 0.8 | 2.6 | 349 | -91 ± 3 | 407 | 705 | +55 ± 9 |

