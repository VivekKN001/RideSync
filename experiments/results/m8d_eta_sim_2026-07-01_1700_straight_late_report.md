# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-07-01_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.275). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 140 |  | +139 | 53.9 | 57.8 |  | 57.0 | 272 |  | 219 | 423 |  |
| dist_hour_table | 70 | -70 ± 2 | +33 | 14.2 | 30.8 | -27.0 ± 0.9 | 18.0 | 348 | +76 ± 3 | 332 | 693 | +270 ± 9 |
| learned_eta | 62 | -79 ± 3 | -5 | 6.5 | 23.8 | -33.9 ± 1.0 | 6.3 | 321 | +49 ± 6 | 335 | 763 | +340 ± 10 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 140 | +70 ± 2 | +139 | 53.9 | 57.8 | +27.0 ± 0.9 | 57.0 | 272 | -76 ± 3 | 219 | 423 | -270 ± 9 |
| dist_hour_table | 70 |  | +33 | 14.2 | 30.8 |  | 18.0 | 348 |  | 332 | 693 |  |
| learned_eta | 62 | -9 ± 3 | -5 | 6.5 | 23.8 | -7.0 ± 0.5 | 6.3 | 321 | -27 ± 5 | 335 | 763 | +70 ± 5 |

