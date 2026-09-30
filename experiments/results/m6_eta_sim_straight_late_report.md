# M6: matcher ETA belief vs world truth (`straight` base)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.267). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 120 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 105 |  | +104 | 32.8 | 69.0 |  | 68.8 | 211 |  | 160 | 348 |  |
| hour_table | 104 | -0 ± 3 | +103 | 32.8 | 69.1 | +0.1 ± 0.6 | 68.9 | 209 | -2 ± 2 | 158 | 347 | -1 ± 7 |
| zone_hour_table | 104 | -1 ± 2 | +104 | 33.0 | 69.4 | +0.4 ± 0.9 | 69.3 | 206 | -5 ± 2 | 154 | 344 | -4 ± 10 |
| dist_hour_table | 55 | -50 ± 2 | +6 | 5.9 | 35.7 | -33.3 ± 0.9 | 23.5 | 327 | +116 ± 2 | 299 | 722 | +374 ± 10 |
| learned_eta | 55 | -49 ± 3 | -13 | 3.1 | 28.0 | -41.0 ± 0.7 | 10.7 | 314 | +103 ± 6 | 318 | 809 | +461 ± 8 |

## 400 drivers, lateness tolerance median 120 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 105 | +50 ± 2 | +104 | 32.8 | 69.0 | +33.3 ± 0.9 | 68.8 | 211 | -116 ± 2 | 160 | 348 | -374 ± 10 |
| hour_table | 104 | +49 ± 2 | +103 | 32.8 | 69.1 | +33.3 ± 1.3 | 68.9 | 209 | -118 ± 3 | 158 | 347 | -375 ± 15 |
| zone_hour_table | 104 | +49 ± 1 | +104 | 33.0 | 69.4 | +33.6 ± 1.1 | 69.3 | 206 | -121 ± 2 | 154 | 344 | -378 ± 13 |
| dist_hour_table | 55 |  | +6 | 5.9 | 35.7 |  | 23.5 | 327 |  | 299 | 722 |  |
| learned_eta | 55 | +0 ± 1 | -13 | 3.1 | 28.0 | -7.7 ± 0.4 | 10.7 | 314 | -12 ± 8 | 318 | 809 | +87 ± 5 |

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 |  | +137 | 52.3 | 55.4 |  | 54.8 | 268 |  | 220 | 501 |  |
| hour_table | 139 | +0 ± 2 | +137 | 52.4 | 56.1 | +0.7 ± 0.8 | 55.6 | 266 | -2 ± 3 | 216 | 494 | -8 ± 9 |
| zone_hour_table | 140 | +2 ± 4 | +140 | 53.7 | 57.1 | +1.8 ± 1.4 | 56.9 | 266 | -2 ± 4 | 215 | 482 | -20 ± 16 |
| dist_hour_table | 67 | -71 ± 2 | +21 | 12.0 | 31.3 | -24.1 ± 1.3 | 17.0 | 345 | +78 ± 3 | 334 | 772 | +271 ± 15 |
| learned_eta | 61 | -77 ± 2 | -6 | 6.0 | 24.6 | -30.8 ± 1.6 | 6.2 | 322 | +54 ± 5 | 335 | 847 | +346 ± 18 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 | +71 ± 2 | +137 | 52.3 | 55.4 | +24.1 ± 1.3 | 54.8 | 268 | -78 ± 3 | 220 | 501 | -271 ± 15 |
| hour_table | 139 | +71 ± 3 | +137 | 52.4 | 56.1 | +24.8 ± 1.1 | 55.6 | 266 | -80 ± 4 | 216 | 494 | -279 ± 12 |
| zone_hour_table | 140 | +73 ± 3 | +140 | 53.7 | 57.1 | +25.9 ± 0.8 | 56.9 | 266 | -80 ± 3 | 215 | 482 | -291 ± 9 |
| dist_hour_table | 67 |  | +21 | 12.0 | 31.3 |  | 17.0 | 345 |  | 334 | 772 |  |
| learned_eta | 61 | -6 ± 2 | -6 | 6.0 | 24.6 | -6.7 ± 1.4 | 6.2 | 322 | -23 ± 4 | 335 | 847 | +75 ± 16 |

## 400 drivers, lateness tolerance median 300 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 188 |  | +185 | 69.5 | 37.2 |  | 35.4 | 355 |  | 317 | 705 |  |
| hour_table | 191 | +3 ± 4 | +188 | 70.6 | 37.4 | +0.1 ± 0.7 | 35.8 | 354 | -1 ± 3 | 316 | 704 | -1 ± 8 |
| zone_hour_table | 192 | +4 ± 4 | +190 | 71.9 | 37.5 | +0.3 ± 0.8 | 36.2 | 357 | +2 ± 3 | 318 | 702 | -3 ± 9 |
| dist_hour_table | 87 | -101 ± 3 | +43 | 21.0 | 25.5 | -11.7 ± 0.5 | 8.6 | 368 | +13 ± 6 | 379 | 837 | +132 ± 6 |
| learned_eta | 68 | -120 ± 2 | +4 | 9.8 | 21.6 | -15.7 ± 0.9 | 2.4 | 328 | -27 ± 7 | 353 | 881 | +176 ± 10 |

## 400 drivers, lateness tolerance median 300 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 188 | +101 ± 3 | +185 | 69.5 | 37.2 | +11.7 ± 0.5 | 35.4 | 355 | -13 ± 6 | 317 | 705 | -132 ± 6 |
| hour_table | 191 | +104 ± 3 | +188 | 70.6 | 37.4 | +11.9 ± 0.5 | 35.8 | 354 | -14 ± 7 | 316 | 704 | -133 ± 6 |
| zone_hour_table | 192 | +105 ± 4 | +190 | 71.9 | 37.5 | +12.0 ± 0.6 | 36.2 | 357 | -10 ± 6 | 318 | 702 | -135 ± 7 |
| dist_hour_table | 87 |  | +43 | 21.0 | 25.5 |  | 8.6 | 368 |  | 379 | 837 |  |
| learned_eta | 68 | -19 ± 2 | +4 | 9.8 | 21.6 | -3.9 ± 1.2 | 2.4 | 328 | -39 ± 6 | 353 | 881 | +44 ± 13 |

