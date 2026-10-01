# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-04-22_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.270). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 141 |  | +136 | 53.8 | 57.9 |  | 56.5 | 284 |  | 240 | 470 |  |
| dist_hour_table | 73 | -67 ± 2 | +33 | 14.6 | 34.8 | -23.1 ± 1.8 | 18.5 | 364 | +80 ± 5 | 354 | 727 | +258 ± 20 |
| learned_eta | 64 | -77 ± 3 | -5 | 6.7 | 28.7 | -29.2 ± 1.3 | 6.5 | 331 | +47 ± 6 | 353 | 795 | +325 ± 15 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 141 | +67 ± 2 | +136 | 53.8 | 57.9 | +23.1 ± 1.8 | 56.5 | 284 | -80 ± 5 | 240 | 470 | -258 ± 20 |
| dist_hour_table | 73 |  | +33 | 14.6 | 34.8 |  | 18.5 | 364 |  | 354 | 727 |  |
| learned_eta | 64 | -10 ± 3 | -5 | 6.7 | 28.7 | -6.1 ± 1.6 | 6.5 | 331 | -33 ± 4 | 353 | 795 | +68 ± 18 |

