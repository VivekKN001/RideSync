# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-01-21_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.274). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 140 |  | +139 | 53.4 | 58.2 |  | 57.6 | 277 |  | 223 | 509 |  |
| dist_hour_table | 69 | -71 ± 3 | +18 | 12.0 | 34.8 | -23.3 ± 0.7 | 15.7 | 360 | +83 ± 5 | 355 | 794 | +284 ± 8 |
| learned_eta | 65 | -76 ± 2 | -6 | 6.9 | 29.4 | -28.7 ± 1.0 | 6.1 | 333 | +56 ± 5 | 350 | 859 | +350 ± 12 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 140 | +71 ± 3 | +139 | 53.4 | 58.2 | +23.3 ± 0.7 | 57.6 | 277 | -83 ± 5 | 223 | 509 | -284 ± 8 |
| dist_hour_table | 69 |  | +18 | 12.0 | 34.8 |  | 15.7 | 360 |  | 355 | 794 |  |
| learned_eta | 65 | -4 ± 3 | -6 | 6.9 | 29.4 | -5.4 ± 1.0 | 6.1 | 333 | -27 ± 5 | 350 | 859 | +66 ± 12 |

