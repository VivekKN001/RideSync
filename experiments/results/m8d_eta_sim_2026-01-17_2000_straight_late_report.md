# M8D: matcher ETA belief vs world truth (`straight` base, `trips_2026-01-17_2000_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.274). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 180 s: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 131 |  | +128 | 49.1 | 51.4 |  | 50.9 | 260 |  | 216 | 576 |  |
| dist_hour_table | 70 | -61 ± 2 | +29 | 13.5 | 28.5 | -22.9 ± 1.0 | 16.6 | 344 | +84 ± 6 | 331 | 848 | +272 ± 12 |
| learned_eta | 61 | -70 ± 2 | -5 | 6.0 | 22.0 | -29.4 ± 1.0 | 6.4 | 319 | +59 ± 8 | 335 | 924 | +348 ± 12 |

## 400 drivers, lateness tolerance median 180 s: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 131 | +61 ± 2 | +128 | 49.1 | 51.4 | +22.9 ± 1.0 | 50.9 | 260 | -84 ± 6 | 216 | 576 | -272 ± 12 |
| dist_hour_table | 70 |  | +29 | 13.5 | 28.5 |  | 16.6 | 344 |  | 331 | 848 |  |
| learned_eta | 61 | -9 ± 1 | -5 | 6.0 | 22.0 | -6.4 ± 0.6 | 6.4 | 319 | -25 ± 7 | 335 | 924 | +76 ± 7 |

