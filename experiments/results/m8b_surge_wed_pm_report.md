# M6: surge pricing (Manhattan TLC replay)

Fares fitted to TLC: FareConfig(base=3.886696530557615, per_mile=1.456611025630024, per_min=0.8478498611528298, min_fare=7.7098, road_factor=1.3453195064940768).
Policy: every 300 s, pressure = (demand over 900 s + waiting) / free supply, pooled over zones within 2000 m; multiplier = 1 + 0.2 × (pressure − 4), steps of 0.25, cap 2.5. Riders who decline leave with probability 0.5, else retry once after a median 180 s.

Deltas are paired against `no_surge` at the same fleet, elasticity and seed (mean ± 95% CI).
`served` = completed trips / app opens. `cancel` is per request. Revenue is fare × multiplier.

## 300 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 73.7 |  | 0.0 | 26.3 |  | 320 |  | 833 |  | 18,946 |  | 1.00 | 0 |
| surge_reactive | 71.8 | -1.9 ± 0.3 | 11.3 | 19.0 | -7.2 ± 0.3 | 302 | -18 ± 6 | 811 | -22 ± 3 | 37,770 | +18824 ± 451 | 2.07 | 81 |
| surge_forecast | 71.7 | -2.1 ± 0.4 | 11.3 | 19.2 | -7.1 ± 0.3 | 306 | -14 ± 5 | 810 | -23 ± 4 | 37,673 | +18727 ± 667 | 2.07 | 81 |

## 300 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 73.7 |  | 0.0 | 26.3 |  | 320 |  | 833 |  | 18,946 |  | 1.00 | 0 |
| surge_reactive | 70.5 | -3.2 ± 0.1 | 17.4 | 14.7 | -11.6 ± 0.3 | 285 | -35 ± 5 | 796 | -37 ± 2 | 34,487 | +15542 ± 329 | 1.92 | 76 |
| surge_forecast | 70.7 | -3.0 ± 0.1 | 17.0 | 14.8 | -11.5 ± 0.3 | 286 | -34 ± 3 | 799 | -34 ± 2 | 34,141 | +15195 ± 424 | 1.89 | 77 |

## 300 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 73.7 |  | 0.0 | 26.3 |  | 320 |  | 833 |  | 18,946 |  | 1.00 | 0 |
| surge_reactive | 69.2 | -4.6 ± 0.3 | 22.2 | 11.0 | -15.3 ± 0.2 | 261 | -59 ± 4 | 782 | -51 ± 4 | 29,499 | +10554 ± 83 | 1.66 | 66 |
| surge_forecast | 69.5 | -4.3 ± 0.3 | 22.1 | 10.9 | -15.4 ± 0.4 | 264 | -56 ± 5 | 785 | -48 ± 3 | 29,306 | +10361 ± 379 | 1.65 | 66 |

## 400 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 90.5 |  | 0.0 | 9.5 |  | 249 |  | 1022 |  | 23,360 |  | 1.00 | 0 |
| surge_reactive | 88.8 | -1.7 ± 0.3 | 4.4 | 7.1 | -2.4 ± 0.4 | 228 | -22 ± 3 | 1003 | -19 ± 3 | 30,978 | +7618 ± 480 | 1.36 | 38 |
| surge_forecast | 88.9 | -1.6 ± 0.3 | 4.1 | 7.3 | -2.2 ± 0.3 | 231 | -19 ± 2 | 1004 | -18 ± 3 | 30,309 | +6950 ± 298 | 1.33 | 36 |

## 400 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 90.5 |  | 0.0 | 9.5 |  | 249 |  | 1022 |  | 23,360 |  | 1.00 | 0 |
| surge_reactive | 88.0 | -2.5 ± 0.4 | 6.2 | 6.2 | -3.3 ± 0.2 | 220 | -30 ± 2 | 994 | -28 ± 4 | 28,979 | +5620 ± 278 | 1.28 | 33 |
| surge_forecast | 88.3 | -2.2 ± 0.4 | 5.6 | 6.5 | -3.0 ± 0.3 | 224 | -26 ± 2 | 997 | -25 ± 4 | 28,439 | +5079 ± 326 | 1.26 | 32 |

## 400 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 90.5 |  | 0.0 | 9.5 |  | 249 |  | 1022 |  | 23,360 |  | 1.00 | 0 |
| surge_reactive | 86.8 | -3.7 ± 0.4 | 8.0 | 5.6 | -3.9 ± 0.2 | 212 | -37 ± 3 | 981 | -41 ± 5 | 26,996 | +3637 ± 370 | 1.21 | 27 |
| surge_forecast | 87.4 | -3.1 ± 0.3 | 7.2 | 5.8 | -3.7 ± 0.3 | 214 | -35 ± 2 | 987 | -35 ± 4 | 26,439 | +3079 ± 241 | 1.18 | 25 |

## 500 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 95.7 |  | 0.0 | 4.3 |  | 192 |  | 1081 |  | 24,698 |  | 1.00 | 0 |
| surge_reactive | 94.9 | -0.8 ± 0.3 | 1.3 | 3.8 | -0.5 ± 0.1 | 187 | -5 ± 2 | 1073 | -9 ± 3 | 26,675 | +1978 ± 189 | 1.08 | 13 |
| surge_forecast | 95.0 | -0.7 ± 0.3 | 1.0 | 4.0 | -0.3 ± 0.2 | 188 | -4 ± 1 | 1073 | -8 ± 3 | 26,352 | +1654 ± 169 | 1.07 | 10 |

## 500 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 95.7 |  | 0.0 | 4.3 |  | 192 |  | 1081 |  | 24,698 |  | 1.00 | 0 |
| surge_reactive | 94.5 | -1.2 ± 0.2 | 1.9 | 3.7 | -0.6 ± 0.2 | 185 | -7 ± 1 | 1067 | -14 ± 2 | 26,176 | +1478 ± 178 | 1.07 | 11 |
| surge_forecast | 94.9 | -0.8 ± 0.1 | 1.5 | 3.7 | -0.6 ± 0.1 | 187 | -5 ± 1 | 1072 | -9 ± 1 | 25,958 | +1260 ± 143 | 1.06 | 9 |

## 500 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 95.7 |  | 0.0 | 4.3 |  | 192 |  | 1081 |  | 24,698 |  | 1.00 | 0 |
| surge_reactive | 94.2 | -1.5 ± 0.2 | 2.5 | 3.4 | -0.9 ± 0.2 | 182 | -10 ± 1 | 1064 | -17 ± 2 | 25,708 | +1010 ± 66 | 1.06 | 9 |
| surge_forecast | 94.4 | -1.3 ± 0.2 | 2.2 | 3.5 | -0.8 ± 0.2 | 185 | -7 ± 1 | 1066 | -15 ± 3 | 25,528 | +830 ± 95 | 1.05 | 8 |

