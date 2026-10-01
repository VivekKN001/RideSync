# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-04-29_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.270). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 140 |  | +137 | 52.4 | 59.8 |  | 58.6 | 287 |  | 235 | 447 |  |
| dist_hour_table | 74 | -67 ± 4 | +36 | 15.3 | 36.6 | -23.2 ± 1.3 | 19.8 | 363 | +76 ± 7 | 349 | 704 | +257 ± 14 |
| learned_eta | 64 | -77 ± 3 | -6 | 6.6 | 31.8 | -28.0 ± 1.2 | 6.1 | 332 | +44 ± 7 | 351 | 757 | +310 ± 14 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 140 | +67 ± 4 | +137 | 52.4 | 59.8 | +23.2 ± 1.3 | 58.6 | 287 | -76 ± 7 | 235 | 447 | -257 ± 14 |
| dist_hour_table | 74 |  | +36 | 15.3 | 36.6 |  | 19.8 | 363 |  | 349 | 704 |  |
| learned_eta | 64 | -10 ± 1 | -6 | 6.6 | 31.8 | -4.8 ± 0.8 | 6.1 | 332 | -32 ± 7 | 351 | 757 | +53 ± 9 |

