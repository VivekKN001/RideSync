# M6: matcher ETA belief vs world truth (`straight` base)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.267). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 120 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 105 |  | +104 | 32.8 | 69.0 |  | 68.8 | 211 |  | 160 | 348 |  |
| hour_table | 104 | -0 ± 2 | +103 | 32.8 | 69.1 | +0.1 ± 0.5 | 68.9 | 209 | -2 ± 1 | 158 | 347 | -1 ± 5 |
| zone_hour_table | 104 | -1 ± 2 | +104 | 33.0 | 69.4 | +0.4 ± 0.7 | 69.3 | 206 | -5 ± 1 | 154 | 344 | -4 ± 8 |
| dist_hour_table | 55 | -50 ± 1 | +6 | 5.9 | 35.7 | -33.3 ± 0.7 | 23.5 | 327 | +116 ± 2 | 299 | 722 | +374 ± 8 |
| learned_eta | 55 | -49 ± 2 | -13 | 3.1 | 28.0 | -41.0 ± 0.6 | 10.7 | 314 | +103 ± 4 | 318 | 809 | +461 ± 6 |

## 400 drivers, lateness tolerance median 120 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 105 | +50 ± 1 | +104 | 32.8 | 69.0 | +33.3 ± 0.7 | 68.8 | 211 | -116 ± 2 | 160 | 348 | -374 ± 8 |
| hour_table | 104 | +49 ± 2 | +103 | 32.8 | 69.1 | +33.3 ± 1.0 | 68.9 | 209 | -118 ± 3 | 158 | 347 | -375 ± 11 |
| zone_hour_table | 104 | +49 ± 1 | +104 | 33.0 | 69.4 | +33.6 ± 0.9 | 69.3 | 206 | -121 ± 2 | 154 | 344 | -378 ± 10 |
| dist_hour_table | 55 |  | +6 | 5.9 | 35.7 |  | 23.5 | 327 |  | 299 | 722 |  |
| learned_eta | 55 | +0 ± 1 | -13 | 3.1 | 28.0 | -7.7 ± 0.3 | 10.7 | 314 | -12 ± 6 | 318 | 809 | +87 ± 4 |

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 |  | +137 | 52.3 | 55.4 |  | 54.8 | 268 |  | 220 | 501 |  |
| hour_table | 139 | +0 ± 2 | +137 | 52.4 | 56.1 | +0.7 ± 0.6 | 55.6 | 266 | -2 ± 2 | 216 | 494 | -8 ± 7 |
| zone_hour_table | 140 | +2 ± 3 | +140 | 53.7 | 57.1 | +1.8 ± 1.1 | 56.9 | 266 | -2 ± 3 | 215 | 482 | -20 ± 12 |
| dist_hour_table | 67 | -71 ± 1 | +21 | 12.0 | 31.3 | -24.1 ± 1.0 | 17.0 | 345 | +78 ± 2 | 334 | 772 | +271 ± 11 |
| learned_eta | 61 | -77 ± 1 | -6 | 6.0 | 24.6 | -30.8 ± 1.2 | 6.2 | 322 | +54 ± 4 | 335 | 847 | +346 ± 14 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 | +71 ± 1 | +137 | 52.3 | 55.4 | +24.1 ± 1.0 | 54.8 | 268 | -78 ± 2 | 220 | 501 | -271 ± 11 |
| hour_table | 139 | +71 ± 2 | +137 | 52.4 | 56.1 | +24.8 ± 0.8 | 55.6 | 266 | -80 ± 3 | 216 | 494 | -279 ± 9 |
| zone_hour_table | 140 | +73 ± 3 | +140 | 53.7 | 57.1 | +25.9 ± 0.6 | 56.9 | 266 | -80 ± 3 | 215 | 482 | -291 ± 7 |
| dist_hour_table | 67 |  | +21 | 12.0 | 31.3 |  | 17.0 | 345 |  | 334 | 772 |  |
| learned_eta | 61 | -6 ± 1 | -6 | 6.0 | 24.6 | -6.7 ± 1.1 | 6.2 | 322 | -23 ± 3 | 335 | 847 | +75 ± 12 |

## 400 drivers, lateness tolerance median 300 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 188 |  | +185 | 69.5 | 37.2 |  | 35.4 | 355 |  | 317 | 705 |  |
| hour_table | 191 | +3 ± 3 | +188 | 70.6 | 37.4 | +0.1 ± 0.5 | 35.8 | 354 | -1 ± 2 | 316 | 704 | -1 ± 6 |
| zone_hour_table | 192 | +4 ± 3 | +190 | 71.9 | 37.5 | +0.3 ± 0.6 | 36.2 | 357 | +2 ± 2 | 318 | 702 | -3 ± 7 |
| dist_hour_table | 87 | -101 ± 2 | +43 | 21.0 | 25.5 | -11.7 ± 0.4 | 8.6 | 368 | +13 ± 4 | 379 | 837 | +132 ± 4 |
| learned_eta | 68 | -120 ± 2 | +4 | 9.8 | 21.6 | -15.7 ± 0.7 | 2.4 | 328 | -27 ± 6 | 353 | 881 | +176 ± 8 |

## 400 drivers, lateness tolerance median 300 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 188 | +101 ± 2 | +185 | 69.5 | 37.2 | +11.7 ± 0.4 | 35.4 | 355 | -13 ± 4 | 317 | 705 | -132 ± 4 |
| hour_table | 191 | +104 ± 3 | +188 | 70.6 | 37.4 | +11.9 ± 0.4 | 35.8 | 354 | -14 ± 5 | 316 | 704 | -133 ± 4 |
| zone_hour_table | 192 | +105 ± 3 | +190 | 71.9 | 37.5 | +12.0 ± 0.5 | 36.2 | 357 | -10 ± 5 | 318 | 702 | -135 ± 5 |
| dist_hour_table | 87 |  | +43 | 21.0 | 25.5 |  | 8.6 | 368 |  | 379 | 837 |  |
| learned_eta | 68 | -19 ± 2 | +4 | 9.8 | 21.6 | -3.9 ± 0.9 | 2.4 | 328 | -39 ± 4 | 353 | 881 | +44 ± 10 |

