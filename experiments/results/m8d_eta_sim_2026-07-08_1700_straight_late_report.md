# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-07-08_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.275). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 |  | +136 | 52.5 | 56.6 |  | 56.1 | 270 |  | 216 | 391 |  |
| dist_hour_table | 68 | -70 ± 2 | +34 | 13.6 | 32.5 | -24.1 ± 1.3 | 19.8 | 345 | +75 ± 6 | 318 | 609 | +217 ± 12 |
| learned_eta | 61 | -77 ± 2 | -5 | 6.5 | 26.1 | -30.5 ± 1.3 | 6.2 | 315 | +45 ± 5 | 326 | 667 | +275 ± 12 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 | +70 ± 2 | +136 | 52.5 | 56.6 | +24.1 ± 1.3 | 56.1 | 270 | -75 ± 6 | 216 | 391 | -217 ± 12 |
| dist_hour_table | 68 |  | +34 | 13.6 | 32.5 |  | 19.8 | 345 |  | 318 | 609 |  |
| learned_eta | 61 | -7 ± 2 | -5 | 6.5 | 26.1 | -6.4 ± 1.9 | 6.2 | 315 | -30 ± 1 | 326 | 667 | +58 ± 18 |

