# M6: matcher ETA belief vs world truth (`straight` base)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.267). Optimal @30 s, cancellation-aware. Deltas are paired (mean ± 95% CI, Student t over seeds) against the arm named in each table's heading.
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Caveat: simulated riders cancel on a long *quote* but never while the driver is en route, so an optimistic belief is not punished for being late. More cancellations under honest ETAs can be that artifact alone; compare quote accuracy first.

## 400 drivers: against `global_multiplier`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 266 |  | +260 | 78.9 | 12.8 |  | 0.0 | 512 |  | 525 | 979 |  |
| hour_table | 270 | +4 ± 5 | +265 | 79.9 | 12.6 | -0.2 ± 0.5 | 0.0 | 515 | +4 ± 6 | 527 | 982 | +3 ± 6 |
| zone_hour_table | 268 | +3 ± 4 | +264 | 80.3 | 12.2 | -0.7 ± 0.5 | 0.0 | 509 | -2 ± 4 | 524 | 987 | +7 ± 6 |
| dist_hour_table | 118 | -147 ± 5 | +78 | 29.5 | 20.8 | +8.0 ± 0.6 | 0.0 | 390 | -122 ± 5 | 440 | 890 | -90 ± 7 |
| learned_eta | 74 | -191 ± 3 | +12 | 12.7 | 19.9 | +7.0 ± 0.6 | 0.0 | 332 | -179 ± 5 | 367 | 900 | -79 ± 6 |

## 400 drivers: against `dist_hour_table`

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 266 | +147 ± 5 | +260 | 78.9 | 12.8 | -8.0 ± 0.6 | 0.0 | 512 | +122 ± 5 | 525 | 979 | +90 ± 7 |
| hour_table | 270 | +152 ± 6 | +265 | 79.9 | 12.6 | -8.2 ± 0.4 | 0.0 | 515 | +125 ± 10 | 527 | 982 | +93 ± 4 |
| zone_hour_table | 268 | +150 ± 5 | +264 | 80.3 | 12.2 | -8.7 ± 0.6 | 0.0 | 509 | +119 ± 5 | 524 | 987 | +97 ± 7 |
| dist_hour_table | 118 |  | +78 | 29.5 | 20.8 |  | 0.0 | 390 |  | 440 | 890 |  |
| learned_eta | 74 | -44 ± 3 | +12 | 12.7 | 19.9 | -0.9 ± 0.6 | 0.0 | 332 | -58 ± 4 | 367 | 900 | +11 ± 7 |

