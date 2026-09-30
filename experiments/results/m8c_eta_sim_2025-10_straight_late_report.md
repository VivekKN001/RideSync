# M8C: matcher ETA belief vs world truth (`straight` base, `trips_2025-10-15_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.276). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 120 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 106 |  | +104 | 33.8 | 71.8 |  | 71.3 | 224 |  | 171 | 339 |  |
| hour_table | 107 | +2 ± 2 | +106 | 35.2 | 72.7 | +0.9 ± 0.7 | 72.4 | 214 | -10 ± 2 | 161 | 328 | -10 ± 8 |
| zone_hour_table | 108 | +2 ± 3 | +108 | 35.2 | 73.8 | +2.0 ± 1.4 | 73.7 | 212 | -12 ± 2 | 155 | 315 | -24 ± 17 |
| dist_hour_table | 60 | -46 ± 3 | +18 | 7.7 | 42.9 | -28.9 ± 1.3 | 28.4 | 348 | +124 ± 3 | 321 | 686 | +347 ± 15 |
| learned_eta | 59 | -46 ± 3 | -17 | 3.4 | 34.5 | -37.3 ± 1.2 | 10.6 | 327 | +103 ± 5 | 337 | 786 | +448 ± 14 |

## 400 drivers, lateness tolerance median 120 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 106 | +46 ± 3 | +104 | 33.8 | 71.8 | +28.9 ± 1.3 | 71.3 | 224 | -124 ± 3 | 171 | 339 | -347 ± 15 |
| hour_table | 107 | +48 ± 3 | +106 | 35.2 | 72.7 | +29.8 ± 1.2 | 72.4 | 214 | -134 ± 3 | 161 | 328 | -358 ± 14 |
| zone_hour_table | 108 | +48 ± 3 | +108 | 35.2 | 73.8 | +30.9 ± 0.7 | 73.7 | 212 | -136 ± 3 | 155 | 315 | -371 ± 8 |
| dist_hour_table | 60 |  | +18 | 7.7 | 42.9 |  | 28.4 | 348 |  | 321 | 686 |  |
| learned_eta | 59 | -0 ± 1 | -17 | 3.4 | 34.5 | -8.4 ± 0.4 | 10.6 | 327 | -21 ± 7 | 337 | 786 | +100 ± 5 |

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 141 |  | +138 | 53.8 | 59.3 |  | 58.2 | 287 |  | 238 | 489 |  |
| hour_table | 146 | +5 ± 3 | +144 | 55.7 | 60.9 | +1.7 ± 1.0 | 60.1 | 275 | -12 ± 3 | 228 | 469 | -20 ± 12 |
| zone_hour_table | 148 | +7 ± 3 | +148 | 57.2 | 61.8 | +2.6 ± 1.1 | 61.6 | 276 | -11 ± 4 | 226 | 458 | -31 ± 13 |
| dist_hour_table | 75 | -66 ± 4 | +35 | 16.0 | 37.9 | -21.3 ± 1.0 | 20.6 | 372 | +86 ± 7 | 363 | 745 | +256 ± 13 |
| learned_eta | 64 | -77 ± 4 | -6 | 6.8 | 31.8 | -27.4 ± 1.0 | 6.3 | 338 | +51 ± 5 | 359 | 818 | +329 ± 12 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 141 | +66 ± 4 | +138 | 53.8 | 59.3 | +21.3 ± 1.0 | 58.2 | 287 | -86 ± 7 | 238 | 489 | -256 ± 13 |
| hour_table | 146 | +71 ± 3 | +144 | 55.7 | 60.9 | +23.0 ± 1.1 | 60.1 | 275 | -97 ± 5 | 228 | 469 | -276 ± 13 |
| zone_hour_table | 148 | +73 ± 3 | +148 | 57.2 | 61.8 | +23.9 ± 0.8 | 61.6 | 276 | -96 ± 7 | 226 | 458 | -287 ± 10 |
| dist_hour_table | 75 |  | +35 | 16.0 | 37.9 |  | 20.6 | 372 |  | 363 | 745 |  |
| learned_eta | 64 | -11 ± 2 | -6 | 6.8 | 31.8 | -6.1 ± 0.5 | 6.3 | 338 | -35 ± 2 | 359 | 818 | +73 ± 5 |

## 400 drivers, lateness tolerance median 300 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 195 |  | +190 | 70.5 | 42.1 |  | 38.5 | 395 |  | 362 | 695 |  |
| hour_table | 202 | +7 ± 3 | +198 | 72.7 | 43.8 | +1.6 ± 1.1 | 40.8 | 385 | -10 ± 3 | 350 | 675 | -20 ± 13 |
| zone_hour_table | 201 | +6 ± 2 | +198 | 73.2 | 42.9 | +0.8 ± 0.6 | 40.5 | 389 | -6 ± 3 | 353 | 686 | -9 ± 8 |
| dist_hour_table | 99 | -96 ± 4 | +61 | 26.2 | 32.9 | -9.3 ± 1.2 | 11.0 | 399 | +3 ± 7 | 421 | 806 | +111 ± 14 |
| learned_eta | 72 | -123 ± 5 | +4 | 10.8 | 29.5 | -12.7 ± 0.9 | 2.6 | 342 | -53 ± 10 | 375 | 847 | +152 ± 11 |

## 400 drivers, lateness tolerance median 300 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 195 | +96 ± 4 | +190 | 70.5 | 42.1 | +9.3 ± 1.2 | 38.5 | 395 | -3 ± 7 | 362 | 695 | -111 ± 14 |
| hour_table | 202 | +103 ± 5 | +198 | 72.7 | 43.8 | +10.9 ± 1.5 | 40.8 | 385 | -14 ± 5 | 350 | 675 | -131 ± 18 |
| zone_hour_table | 201 | +103 ± 4 | +198 | 73.2 | 42.9 | +10.0 ± 1.0 | 40.5 | 389 | -10 ± 9 | 353 | 686 | -120 ± 11 |
| dist_hour_table | 99 |  | +61 | 26.2 | 32.9 |  | 11.0 | 399 |  | 421 | 806 |  |
| learned_eta | 72 | -27 ± 3 | +4 | 10.8 | 29.5 | -3.4 ± 0.8 | 2.6 | 342 | -56 ± 4 | 375 | 847 | +41 ± 9 |

