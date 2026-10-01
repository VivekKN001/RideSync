# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-07-18_2000_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.275). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 135 |  | +129 | 50.3 | 55.8 |  | 54.1 | 278 |  | 234 | 521 |  |
| dist_hour_table | 79 | -55 ± 3 | +48 | 18.6 | 36.6 | -19.2 ± 1.2 | 24.8 | 367 | +89 ± 5 | 343 | 748 | +227 ± 14 |
| learned_eta | 64 | -70 ± 2 | -6 | 6.8 | 28.6 | -27.2 ± 1.5 | 6.3 | 333 | +55 ± 6 | 351 | 843 | +322 ± 18 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 135 | +55 ± 3 | +129 | 50.3 | 55.8 | +19.2 ± 1.2 | 54.1 | 278 | -89 ± 5 | 234 | 521 | -227 ± 14 |
| dist_hour_table | 79 |  | +48 | 18.6 | 36.6 |  | 24.8 | 367 |  | 343 | 748 |  |
| learned_eta | 64 | -15 ± 2 | -6 | 6.8 | 28.6 | -8.1 ± 0.9 | 6.3 | 333 | -35 ± 8 | 351 | 843 | +95 ± 10 |

