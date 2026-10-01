# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-04-08_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.270). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 141 |  | +139 | 53.8 | 56.6 |  | 55.9 | 279 |  | 234 | 477 |  |
| dist_hour_table | 72 | -69 ± 5 | +26 | 13.2 | 31.9 | -24.7 ± 2.4 | 16.8 | 354 | +75 ± 8 | 347 | 749 | +272 ± 27 |
| learned_eta | 63 | -78 ± 5 | -5 | 6.3 | 25.2 | -31.4 ± 2.0 | 6.4 | 327 | +48 ± 7 | 349 | 823 | +345 ± 22 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 141 | +69 ± 5 | +139 | 53.8 | 56.6 | +24.7 ± 2.4 | 55.9 | 279 | -75 ± 8 | 234 | 477 | -272 ± 27 |
| dist_hour_table | 72 |  | +26 | 13.2 | 31.9 |  | 16.8 | 354 |  | 347 | 749 |  |
| learned_eta | 63 | -9 ± 0 | -5 | 6.3 | 25.2 | -6.7 ± 0.6 | 6.4 | 327 | -27 ± 3 | 349 | 823 | +74 ± 7 |

