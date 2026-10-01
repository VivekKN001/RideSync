# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-01-07_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.274). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 137 |  | +136 | 51.8 | 53.8 |  | 53.6 | 258 |  | 207 | 428 |  |
| dist_hour_table | 63 | -74 ± 3 | +17 | 10.5 | 26.7 | -27.1 ± 1.0 | 14.0 | 334 | +76 ± 8 | 321 | 679 | +251 ± 9 |
| learned_eta | 60 | -76 ± 3 | -4 | 6.1 | 21.1 | -32.8 ± 0.6 | 6.3 | 310 | +52 ± 5 | 319 | 732 | +304 ± 5 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 137 | +74 ± 3 | +136 | 51.8 | 53.8 | +27.1 ± 1.0 | 53.6 | 258 | -76 ± 8 | 207 | 428 | -251 ± 9 |
| dist_hour_table | 63 |  | +17 | 10.5 | 26.7 |  | 14.0 | 334 |  | 321 | 679 |  |
| learned_eta | 60 | -3 ± 2 | -4 | 6.1 | 21.1 | -5.7 ± 1.0 | 6.3 | 310 | -23 ± 6 | 319 | 732 | +52 ± 9 |

