# M8B: matcher ETA belief vs world truth (`straight` base, `trips_2026-07-15_1700_3h_manhattan_f0.1.parquet`)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.275). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Caveat: simulated riders cancel on a long *quote* but never while the driver is en route, so an optimistic belief is not punished for being late. More cancellations under honest ETAs can be that artifact alone; compare quote accuracy first.

## 400 drivers: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 288 |  | +282 | 80.5 | 18.6 |  | 0.0 | 528 |  | 552 | 919 |  |
| hour_table | 297 | +9 ± 2 | +292 | 82.2 | 18.2 | -0.4 ± 0.3 | 0.0 | 537 | +8 ± 7 | 558 | 925 | +5 ± 3 |
| zone_hour_table | 293 | +5 ± 5 | +290 | 81.5 | 17.3 | -1.3 ± 0.4 | 0.0 | 535 | +6 ± 8 | 556 | 934 | +14 ± 4 |
| dist_hour_table | 138 | -150 ± 4 | +105 | 35.5 | 24.8 | +6.2 ± 0.6 | 0.0 | 414 | -114 ± 7 | 472 | 849 | -70 ± 7 |
| learned_eta | 77 | -210 ± 3 | +12 | 13.5 | 26.2 | +7.5 ± 0.6 | 0.0 | 338 | -190 ± 7 | 376 | 834 | -85 ± 7 |

## 400 drivers: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 288 | +150 ± 4 | +282 | 80.5 | 18.6 | -6.2 ± 0.6 | 0.0 | 528 | +114 ± 7 | 552 | 919 | +70 ± 7 |
| hour_table | 297 | +158 ± 4 | +292 | 82.2 | 18.2 | -6.7 ± 0.5 | 0.0 | 537 | +123 ± 4 | 558 | 925 | +76 ± 5 |
| zone_hour_table | 293 | +155 ± 4 | +290 | 81.5 | 17.3 | -7.5 ± 0.5 | 0.0 | 535 | +121 ± 4 | 556 | 934 | +85 ± 5 |
| dist_hour_table | 138 |  | +105 | 35.5 | 24.8 |  | 0.0 | 414 |  | 472 | 849 |  |
| learned_eta | 77 | -61 ± 3 | +12 | 13.5 | 26.2 | +1.3 ± 0.8 | 0.0 | 338 | -75 ± 3 | 376 | 834 | -15 ± 9 |

