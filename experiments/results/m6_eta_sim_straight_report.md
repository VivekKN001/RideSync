# M6: matcher ETA belief vs world truth (`straight` base)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.273). Optimal @30 s, cancellation-aware. Deltas paired against `global_multiplier` (mean ± 95% CI).
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Caveat: simulated riders cancel on a long *quote* but never while the driver is en route, so an optimistic belief is not punished for being late. More cancellations under honest ETAs can be that artifact alone; compare quote accuracy first.

## 400 drivers

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 271 |  | +266 | 79.1 | 13.3 |  | 525 |  | 540 | 974 |  |
| learned_eta | 76 | -195 ± 3 | +12 | 13.0 | 21.2 | +7.9 ± 0.6 | 334 | -191 ± 6 | 372 | 885 | -89 ± 7 |

