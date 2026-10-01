# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-01-28_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.274). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 139 |  | +139 | 52.4 | 57.2 |  | 56.9 | 266 |  | 207 | 429 |  |
| dist_hour_table | 65 | -74 ± 3 | +26 | 12.5 | 34.5 | -22.7 ± 1.1 | 21.1 | 353 | +87 ± 7 | 320 | 656 | +228 ± 11 |
| learned_eta | 59 | -80 ± 4 | -4 | 5.9 | 31.1 | -26.1 ± 1.5 | 5.5 | 318 | +52 ± 4 | 319 | 690 | +261 ± 15 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 139 | +74 ± 3 | +139 | 52.4 | 57.2 | +22.7 ± 1.1 | 56.9 | 266 | -87 ± 7 | 207 | 429 | -228 ± 11 |
| dist_hour_table | 65 |  | +26 | 12.5 | 34.5 |  | 21.1 | 353 |  | 320 | 656 |  |
| learned_eta | 59 | -5 ± 2 | -4 | 5.9 | 31.1 | -3.4 ± 0.8 | 5.5 | 318 | -34 ± 6 | 319 | 690 | +34 ± 8 |

