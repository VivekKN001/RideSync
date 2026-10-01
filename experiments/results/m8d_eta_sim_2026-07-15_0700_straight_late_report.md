# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-07-15_0700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.275). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 128 |  | +117 | 45.5 | 58.5 |  | 49.3 | 325 |  | 285 | 434 |  |
| dist_hour_table | 73 | -55 ± 2 | +36 | 15.2 | 42.7 | -15.8 ± 1.2 | 16.7 | 357 | +32 ± 2 | 346 | 600 | +165 ± 12 |
| learned_eta | 65 | -63 ± 2 | -7 | 6.9 | 42.3 | -16.2 ± 1.3 | 5.7 | 340 | +15 ± 7 | 355 | 604 | +169 ± 14 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 128 | +55 ± 2 | +117 | 45.5 | 58.5 | +15.8 ± 1.2 | 49.3 | 325 | -32 ± 2 | 285 | 434 | -165 ± 12 |
| dist_hour_table | 73 |  | +36 | 15.2 | 42.7 |  | 16.7 | 357 |  | 346 | 600 |  |
| learned_eta | 65 | -8 ± 1 | -7 | 6.9 | 42.3 | -0.4 ± 0.8 | 5.7 | 340 | -17 ± 7 | 355 | 604 | +4 ± 9 |

