# M8C: matcher ETA belief vs world truth (`straight` base, `trips_2026-04-15_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.270). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 120 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 107 |  | +106 | 34.9 | 72.2 |  | 71.7 | 222 |  | 167 | 287 |  |
| hour_table | 108 | +1 ± 2 | +107 | 35.4 | 73.3 | +1.1 ± 0.7 | 72.8 | 214 | -7 ± 2 | 158 | 276 | -12 ± 7 |
| zone_hour_table | 108 | +1 ± 3 | +108 | 35.3 | 73.8 | +1.6 ± 1.0 | 73.7 | 213 | -9 ± 4 | 156 | 271 | -17 ± 10 |
| dist_hour_table | 56 | -51 ± 2 | +23 | 7.5 | 42.1 | -30.0 ± 0.4 | 29.3 | 342 | +120 ± 3 | 308 | 598 | +310 ± 4 |
| learned_eta | 58 | -49 ± 2 | -15 | 3.4 | 34.0 | -38.1 ± 0.7 | 10.5 | 324 | +102 ± 4 | 331 | 681 | +394 ± 8 |

## 400 drivers, lateness tolerance median 120 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 107 | +51 ± 2 | +106 | 34.9 | 72.2 | +30.0 ± 0.4 | 71.7 | 222 | -120 ± 3 | 167 | 287 | -310 ± 4 |
| hour_table | 108 | +52 ± 1 | +107 | 35.4 | 73.3 | +31.2 ± 1.1 | 72.8 | 214 | -128 ± 3 | 158 | 276 | -322 ± 11 |
| zone_hour_table | 108 | +52 ± 2 | +108 | 35.3 | 73.8 | +31.7 ± 1.1 | 73.7 | 213 | -129 ± 3 | 156 | 271 | -327 ± 11 |
| dist_hour_table | 56 |  | +23 | 7.5 | 42.1 |  | 29.3 | 342 |  | 308 | 598 |  |
| learned_eta | 58 | +2 ± 2 | -15 | 3.4 | 34.0 | -8.1 ± 0.6 | 10.5 | 324 | -18 ± 4 | 331 | 681 | +83 ± 6 |

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 144 |  | +142 | 55.8 | 60.2 |  | 59.0 | 281 |  | 229 | 411 |  |
| hour_table | 147 | +3 ± 3 | +146 | 56.1 | 62.4 | +2.2 ± 1.3 | 61.7 | 275 | -6 ± 3 | 221 | 388 | -23 ± 13 |
| zone_hour_table | 148 | +4 ± 3 | +148 | 56.8 | 62.3 | +2.1 ± 1.0 | 62.0 | 275 | -6 ± 3 | 221 | 390 | -21 ± 10 |
| dist_hour_table | 72 | -72 ± 5 | +39 | 15.7 | 35.6 | -24.6 ± 1.1 | 20.6 | 364 | +83 ± 6 | 347 | 665 | +254 ± 12 |
| learned_eta | 64 | -80 ± 4 | -6 | 6.9 | 30.9 | -29.4 ± 1.5 | 6.0 | 329 | +48 ± 5 | 349 | 714 | +303 ± 15 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 144 | +72 ± 5 | +142 | 55.8 | 60.2 | +24.6 ± 1.1 | 59.0 | 281 | -83 ± 6 | 229 | 411 | -254 ± 12 |
| hour_table | 147 | +75 ± 2 | +146 | 56.1 | 62.4 | +26.8 ± 1.3 | 61.7 | 275 | -89 ± 5 | 221 | 388 | -277 ± 13 |
| zone_hour_table | 148 | +76 ± 4 | +148 | 56.8 | 62.3 | +26.6 ± 0.6 | 62.0 | 275 | -89 ± 6 | 221 | 390 | -275 ± 6 |
| dist_hour_table | 72 |  | +39 | 15.7 | 35.6 |  | 20.6 | 364 |  | 347 | 665 |  |
| learned_eta | 64 | -8 ± 2 | -6 | 6.9 | 30.9 | -4.8 ± 0.9 | 6.0 | 329 | -35 ± 6 | 349 | 714 | +49 ± 9 |

## 400 drivers, lateness tolerance median 300 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 202 |  | +200 | 73.3 | 41.5 |  | 38.9 | 381 |  | 343 | 604 |  |
| hour_table | 206 | +4 ± 5 | +205 | 74.6 | 42.8 | +1.3 ± 0.8 | 40.7 | 373 | -9 ± 5 | 334 | 591 | -13 ± 8 |
| zone_hour_table | 209 | +7 ± 7 | +208 | 75.9 | 43.3 | +1.8 ± 0.7 | 41.8 | 378 | -4 ± 9 | 338 | 585 | -18 ± 7 |
| dist_hour_table | 95 | -107 ± 6 | +64 | 25.5 | 29.6 | -11.9 ± 1.3 | 11.3 | 388 | +7 ± 7 | 398 | 727 | +123 ± 14 |
| learned_eta | 70 | -132 ± 5 | +3 | 10.5 | 28.5 | -13.0 ± 0.7 | 2.4 | 335 | -47 ± 12 | 367 | 738 | +134 ± 7 |

## 400 drivers, lateness tolerance median 300 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 202 | +107 ± 6 | +200 | 73.3 | 41.5 | +11.9 ± 1.3 | 38.9 | 381 | -7 ± 7 | 343 | 604 | -123 ± 14 |
| hour_table | 206 | +111 ± 5 | +205 | 74.6 | 42.8 | +13.2 ± 1.5 | 40.7 | 373 | -15 ± 5 | 334 | 591 | -136 ± 15 |
| zone_hour_table | 209 | +114 ± 3 | +208 | 75.9 | 43.3 | +13.7 ± 1.6 | 41.8 | 378 | -11 ± 3 | 338 | 585 | -142 ± 16 |
| dist_hour_table | 95 |  | +64 | 25.5 | 29.6 |  | 11.3 | 388 |  | 398 | 727 |  |
| learned_eta | 70 | -25 ± 3 | +3 | 10.5 | 28.5 | -1.1 ± 0.6 | 2.4 | 335 | -53 ± 7 | 367 | 738 | +11 ± 7 |

