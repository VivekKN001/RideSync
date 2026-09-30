# M8C: matcher ETA belief vs world truth (`straight` base, `trips_2026-01-14_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.274). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 120 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 105 |  | +104 | 33.9 | 67.3 |  | 67.1 | 209 |  | 158 | 323 |  |
| hour_table | 100 | -4 ± 2 | +99 | 30.9 | 66.9 | -0.4 ± 0.9 | 66.5 | 211 | +3 ± 3 | 157 | 327 | +4 ± 8 |
| zone_hour_table | 101 | -4 ± 2 | +101 | 31.3 | 66.9 | -0.5 ± 1.2 | 66.8 | 210 | +1 ± 2 | 156 | 328 | +5 ± 12 |
| dist_hour_table | 53 | -52 ± 2 | +2 | 4.8 | 31.3 | -36.1 ± 1.7 | 19.2 | 315 | +106 ± 5 | 291 | 680 | +357 ± 17 |
| learned_eta | 55 | -50 ± 1 | -11 | 3.4 | 24.4 | -43.0 ± 1.3 | 10.7 | 304 | +96 ± 5 | 304 | 748 | +425 ± 13 |

## 400 drivers, lateness tolerance median 120 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 105 | +52 ± 2 | +104 | 33.9 | 67.3 | +36.1 ± 1.7 | 67.1 | 209 | -106 ± 5 | 158 | 323 | -357 ± 17 |
| hour_table | 100 | +47 ± 3 | +99 | 30.9 | 66.9 | +35.7 ± 1.8 | 66.5 | 211 | -104 ± 6 | 157 | 327 | -353 ± 18 |
| zone_hour_table | 101 | +48 ± 2 | +101 | 31.3 | 66.9 | +35.6 ± 1.6 | 66.8 | 210 | -105 ± 5 | 156 | 328 | -352 ± 16 |
| dist_hour_table | 53 |  | +2 | 4.8 | 31.3 |  | 19.2 | 315 |  | 291 | 680 |  |
| learned_eta | 55 | +1 ± 1 | -11 | 3.4 | 24.4 | -6.9 ± 1.2 | 10.7 | 304 | -11 ± 6 | 304 | 748 | +68 ± 11 |

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 135 |  | +134 | 51.0 | 53.6 |  | 53.1 | 261 |  | 211 | 459 |  |
| hour_table | 134 | -1 ± 5 | +133 | 50.2 | 52.7 | -1.0 ± 0.9 | 52.0 | 264 | +2 ± 4 | 215 | 468 | +10 ± 9 |
| zone_hour_table | 133 | -3 ± 2 | +132 | 49.5 | 53.1 | -0.6 ± 0.9 | 52.6 | 262 | +1 ± 4 | 211 | 464 | +6 ± 8 |
| dist_hour_table | 63 | -72 ± 4 | +15 | 9.7 | 26.1 | -27.6 ± 0.4 | 12.8 | 328 | +67 ± 10 | 316 | 731 | +273 ± 4 |
| learned_eta | 60 | -75 ± 4 | -4 | 6.4 | 20.6 | -33.1 ± 0.6 | 6.2 | 310 | +49 ± 8 | 319 | 786 | +327 ± 6 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 135 | +72 ± 4 | +134 | 51.0 | 53.6 | +27.6 ± 0.4 | 53.1 | 261 | -67 ± 10 | 211 | 459 | -273 ± 4 |
| hour_table | 134 | +71 ± 2 | +133 | 50.2 | 52.7 | +26.6 ± 0.5 | 52.0 | 264 | -64 ± 8 | 215 | 468 | -263 ± 5 |
| zone_hour_table | 133 | +70 ± 3 | +132 | 49.5 | 53.1 | +27.0 ± 0.6 | 52.6 | 262 | -66 ± 7 | 211 | 464 | -267 ± 6 |
| dist_hour_table | 63 |  | +15 | 9.7 | 26.1 |  | 12.8 | 328 |  | 316 | 731 |  |
| learned_eta | 60 | -3 ± 1 | -4 | 6.4 | 20.6 | -5.5 ± 0.5 | 6.2 | 310 | -18 ± 6 | 319 | 786 | +54 ± 5 |

## 400 drivers, lateness tolerance median 300 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 180 |  | +178 | 67.9 | 33.5 |  | 32.0 | 336 |  | 298 | 658 |  |
| hour_table | 178 | -2 ± 1 | +176 | 67.3 | 33.3 | -0.2 ± 0.6 | 31.5 | 340 | +4 ± 2 | 302 | 660 | +2 ± 6 |
| zone_hour_table | 178 | -3 ± 4 | +176 | 67.3 | 33.1 | -0.4 ± 0.8 | 31.7 | 340 | +4 ± 3 | 301 | 662 | +4 ± 8 |
| dist_hour_table | 76 | -105 ± 3 | +30 | 16.1 | 21.5 | -12.0 ± 0.8 | 6.5 | 341 | +5 ± 5 | 346 | 777 | +118 ± 8 |
| learned_eta | 66 | -115 ± 2 | +5 | 9.6 | 17.3 | -16.1 ± 0.6 | 2.3 | 316 | -20 ± 6 | 337 | 818 | +159 ± 6 |

## 400 drivers, lateness tolerance median 300 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 180 | +105 ± 3 | +178 | 67.9 | 33.5 | +12.0 ± 0.8 | 32.0 | 336 | -5 ± 5 | 298 | 658 | -118 ± 8 |
| hour_table | 178 | +103 ± 3 | +176 | 67.3 | 33.3 | +11.8 ± 0.9 | 31.5 | 340 | -1 ± 5 | 302 | 660 | -117 ± 9 |
| zone_hour_table | 178 | +102 ± 4 | +176 | 67.3 | 33.1 | +11.6 ± 0.4 | 31.7 | 340 | -1 ± 7 | 301 | 662 | -115 ± 4 |
| dist_hour_table | 76 |  | +30 | 16.1 | 21.5 |  | 6.5 | 341 |  | 346 | 777 |  |
| learned_eta | 66 | -10 ± 2 | +5 | 9.6 | 17.3 | -4.1 ± 0.6 | 2.3 | 316 | -25 ± 6 | 337 | 818 | +41 ± 6 |

