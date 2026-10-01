# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2025-10-18_2000_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.276). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 137 |  | +132 | 51.2 | 57.3 |  | 56.0 | 281 |  | 237 | 523 |  |
| dist_hour_table | 81 | -56 ± 3 | +50 | 19.7 | 38.2 | -19.1 ± 1.3 | 25.8 | 375 | +94 ± 6 | 356 | 757 | +234 ± 16 |
| learned_eta | 67 | -70 ± 2 | -6 | 7.3 | 30.6 | -26.7 ± 1.7 | 6.6 | 341 | +60 ± 9 | 368 | 849 | +326 ± 21 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 137 | +56 ± 3 | +132 | 51.2 | 57.3 | +19.1 ± 1.3 | 56.0 | 281 | -94 ± 6 | 237 | 523 | -234 ± 16 |
| dist_hour_table | 81 |  | +50 | 19.7 | 38.2 |  | 25.8 | 375 |  | 356 | 757 |  |
| learned_eta | 67 | -14 ± 2 | -6 | 7.3 | 30.6 | -7.6 ± 0.8 | 6.6 | 341 | -34 ± 7 | 368 | 849 | +93 ± 9 |

