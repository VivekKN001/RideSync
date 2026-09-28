# M6: matcher ETA belief vs world truth (`straight` base)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.267). Optimal @30 s, cancellation-aware. Deltas paired against `global_multiplier` (mean ± 95% CI).
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Caveat: simulated riders cancel on a long *quote* but never while the driver is en route, so an optimistic belief is not punished for being late. More cancellations under honest ETAs can be that artifact alone; compare quote accuracy first.

## 400 drivers

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 266 |  | +260 | 78.9 | 12.8 |  | 512 |  | 525 | 979 |  |
| learned_eta | 74 | -191 ± 2 | +12 | 12.7 | 19.9 | +7.0 ± 0.4 | 332 | -179 ± 4 | 367 | 900 | -79 ± 5 |

