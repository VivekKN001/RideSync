# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2025-10-15_0700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.276). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 131 |  | +124 | 47.6 | 57.5 |  | 53.1 | 311 |  | 267 | 426 |  |
| dist_hour_table | 75 | -56 ± 1 | +43 | 17.2 | 39.5 | -18.0 ± 0.8 | 20.3 | 364 | +52 ± 7 | 345 | 607 | +181 ± 8 |
| learned_eta | 65 | -67 ± 3 | -7 | 7.1 | 39.1 | -18.4 ± 0.8 | 5.7 | 338 | +26 ± 4 | 355 | 611 | +185 ± 8 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 131 | +56 ± 1 | +124 | 47.6 | 57.5 | +18.0 ± 0.8 | 53.1 | 311 | -52 ± 7 | 267 | 426 | -181 ± 8 |
| dist_hour_table | 75 |  | +43 | 17.2 | 39.5 |  | 20.3 | 364 |  | 345 | 607 |  |
| learned_eta | 65 | -10 ± 3 | -7 | 7.1 | 39.1 | -0.4 ± 1.1 | 5.7 | 338 | -26 ± 4 | 355 | 611 | +4 ± 11 |

