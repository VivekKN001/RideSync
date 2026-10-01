# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-04-18_2000_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.270). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 142 |  | +136 | 53.8 | 60.7 |  | 59.2 | 295 |  | 251 | 528 |  |
| dist_hour_table | 87 | -55 ± 3 | +53 | 21.7 | 45.1 | -15.6 ± 2.3 | 27.8 | 403 | +107 ± 10 | 392 | 738 | +209 ± 30 |
| learned_eta | 65 | -77 ± 3 | -6 | 6.9 | 36.7 | -23.9 ± 2.0 | 5.9 | 350 | +55 ± 8 | 374 | 850 | +321 ± 27 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 142 | +55 ± 3 | +136 | 53.8 | 60.7 | +15.6 ± 2.3 | 59.2 | 295 | -107 ± 10 | 251 | 528 | -209 ± 30 |
| dist_hour_table | 87 |  | +53 | 21.7 | 45.1 |  | 27.8 | 403 |  | 392 | 738 |  |
| learned_eta | 65 | -21 ± 2 | -6 | 6.9 | 36.7 | -8.3 ± 1.0 | 5.9 | 350 | -53 ± 7 | 374 | 850 | +112 ± 13 |

