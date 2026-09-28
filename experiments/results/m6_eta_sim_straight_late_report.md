# M6: matcher ETA belief vs world truth (`straight` base)

World: calibrated `straight` × learned correction × lognormal noise (sigma 0.267). Optimal @30 s, cancellation-aware. Deltas paired against `global_multiplier` (mean ± 95% CI).
`|ETA error|` = |actual match-to-pickup time − quoted ETA|; `late > 2 min` = share of pickups more than 2 min later than quoted.
Riders also give up on a late driver: once the quote plus their tolerance (lognormal, median below, sigma 0.5) has passed without a pickup, they cancel (`late cancel`). Quote accuracy is over completed pickups only.

## 400 drivers, lateness tolerance median 120 s

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 105 |  | +104 | 32.8 | 69.0 |  | 68.8 | 211 |  | 160 | 348 |  |
| learned_eta | 55 | -49 ± 2 | -13 | 3.1 | 28.0 | -41.0 ± 0.6 | 10.7 | 314 | +103 ± 4 | 318 | 809 | +461 ± 6 |

## 400 drivers, lateness tolerance median 180 s

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 138 |  | +137 | 52.3 | 55.4 |  | 54.8 | 268 |  | 220 | 501 |  |
| learned_eta | 61 | -77 ± 1 | -6 | 6.0 | 24.6 | -30.8 ± 1.2 | 6.2 | 322 | +54 ± 4 | 335 | 847 | +346 ± 14 |

## 400 drivers, lateness tolerance median 300 s

| arm | |ETA error| s | Δ | mean error s | late > 2 min % | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | trips/h | Δ trips/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global_multiplier | 188 |  | +185 | 69.5 | 37.2 |  | 35.4 | 355 |  | 317 | 705 |  |
| learned_eta | 68 | -120 ± 2 | +4 | 9.8 | 21.6 | -15.7 ± 0.7 | 2.4 | 328 | -27 ± 6 | 353 | 881 | +176 ± 8 |

