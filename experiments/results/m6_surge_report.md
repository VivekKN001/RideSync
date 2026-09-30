# M6: surge pricing (Manhattan TLC replay)

Fares fitted to TLC: FareConfig(base=4.0892413438816355, per_mile=1.964759067091339, per_min=0.6853549779102025, min_fare=8.23, road_factor=1.3441557477218717).
Policy: every 300 s, pressure = (demand over 900 s + waiting) / free supply, pooled over zones within 2000 m; multiplier = 1 + 0.2 × (pressure − 4), steps of 0.25, cap 2.5. Riders who decline leave with probability 0.5, else retry once after a median 180 s.

Deltas are paired against `no_surge` at the same fleet, elasticity and seed (mean ± 95% CI, Student t over seeds).
`served` = completed trips / app opens. `cancel` is per request. Revenue is fare × multiplier.

## 300 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 78.2 |  | 0.0 | 21.8 |  | 320 |  | 879 |  | 17,963 |  | 1.00 | 0 |
| surge_reactive | 75.6 | -2.6 ± 0.4 | 11.6 | 14.5 | -7.3 ± 0.4 | 298 | -23 ± 4 | 849 | -29 ± 4 | 36,083 | +18119 ± 283 | 2.09 | 86 |
| surge_forecast | 75.7 | -2.5 ± 0.6 | 11.6 | 14.4 | -7.4 ± 0.5 | 298 | -22 ± 7 | 850 | -28 ± 7 | 36,215 | +18251 ± 506 | 2.10 | 87 |

## 300 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 78.2 |  | 0.0 | 21.8 |  | 320 |  | 879 |  | 17,963 |  | 1.00 | 0 |
| surge_reactive | 74.4 | -3.8 ± 0.3 | 16.6 | 10.8 | -11.0 ± 0.4 | 274 | -46 ± 6 | 836 | -43 ± 4 | 32,182 | +14219 ± 261 | 1.90 | 79 |
| surge_forecast | 74.4 | -3.8 ± 0.5 | 16.6 | 10.8 | -11.0 ± 0.7 | 275 | -46 ± 5 | 836 | -43 ± 6 | 31,865 | +13902 ± 505 | 1.88 | 80 |

## 300 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 78.2 |  | 0.0 | 21.8 |  | 320 |  | 879 |  | 17,963 |  | 1.00 | 0 |
| surge_reactive | 73.2 | -5.0 ± 0.5 | 20.6 | 7.8 | -14.0 ± 0.5 | 247 | -73 ± 6 | 823 | -56 ± 6 | 26,899 | +8936 ± 474 | 1.61 | 67 |
| surge_forecast | 73.2 | -5.0 ± 0.6 | 20.5 | 8.0 | -13.8 ± 0.4 | 246 | -74 ± 6 | 822 | -56 ± 7 | 26,576 | +8612 ± 356 | 1.59 | 67 |

## 400 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 93.5 |  | 0.0 | 6.5 |  | 227 |  | 1050 |  | 21,511 |  | 1.00 | 0 |
| surge_reactive | 91.6 | -1.9 ± 0.4 | 3.3 | 5.2 | -1.3 ± 0.4 | 211 | -16 ± 6 | 1029 | -21 ± 5 | 26,873 | +5362 ± 560 | 1.27 | 34 |
| surge_forecast | 91.6 | -1.9 ± 0.4 | 3.3 | 5.2 | -1.3 ± 0.4 | 211 | -15 ± 5 | 1030 | -21 ± 5 | 26,816 | +5305 ± 562 | 1.27 | 33 |

## 400 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 93.5 |  | 0.0 | 6.5 |  | 227 |  | 1050 |  | 21,511 |  | 1.00 | 0 |
| surge_reactive | 90.7 | -2.8 ± 0.5 | 5.0 | 4.5 | -2.0 ± 0.4 | 203 | -23 ± 5 | 1019 | -31 ± 5 | 25,552 | +4041 ± 432 | 1.22 | 29 |
| surge_forecast | 90.7 | -2.8 ± 0.5 | 4.7 | 4.9 | -1.6 ± 0.6 | 204 | -23 ± 7 | 1019 | -32 ± 5 | 25,352 | +3842 ± 530 | 1.21 | 28 |

## 400 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 93.5 |  | 0.0 | 6.5 |  | 227 |  | 1050 |  | 21,511 |  | 1.00 | 0 |
| surge_reactive | 89.9 | -3.6 ± 0.5 | 6.5 | 3.9 | -2.6 ± 0.5 | 198 | -29 ± 7 | 1010 | -41 ± 5 | 24,070 | +2559 ± 292 | 1.16 | 25 |
| surge_forecast | 89.9 | -3.6 ± 0.6 | 6.1 | 4.2 | -2.3 ± 0.4 | 198 | -29 ± 5 | 1010 | -40 ± 6 | 24,019 | +2508 ± 344 | 1.16 | 24 |

## 500 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 96.5 |  | 0.0 | 3.5 |  | 179 |  | 1084 |  | 22,262 |  | 1.00 | 0 |
| surge_reactive | 95.9 | -0.6 ± 0.3 | 0.9 | 3.3 | -0.2 ± 0.2 | 176 | -3 ± 3 | 1077 | -7 ± 4 | 23,872 | +1610 ± 268 | 1.07 | 9 |
| surge_forecast | 95.9 | -0.6 ± 0.4 | 0.8 | 3.3 | -0.2 ± 0.3 | 177 | -2 ± 2 | 1078 | -6 ± 4 | 23,743 | +1481 ± 329 | 1.06 | 9 |

## 500 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 96.5 |  | 0.0 | 3.5 |  | 179 |  | 1084 |  | 22,262 |  | 1.00 | 0 |
| surge_reactive | 95.5 | -1.0 ± 0.4 | 1.4 | 3.1 | -0.4 ± 0.3 | 174 | -5 ± 2 | 1073 | -11 ± 4 | 23,454 | +1192 ± 200 | 1.06 | 9 |
| surge_forecast | 95.8 | -0.6 ± 0.4 | 1.2 | 3.0 | -0.5 ± 0.2 | 175 | -4 ± 3 | 1077 | -7 ± 4 | 23,457 | +1195 ± 209 | 1.06 | 8 |

## 500 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 96.5 |  | 0.0 | 3.5 |  | 179 |  | 1084 |  | 22,262 |  | 1.00 | 0 |
| surge_reactive | 95.2 | -1.3 ± 0.5 | 2.0 | 2.9 | -0.6 ± 0.3 | 173 | -6 ± 2 | 1070 | -14 ± 5 | 23,104 | +842 ± 243 | 1.05 | 8 |
| surge_forecast | 95.5 | -1.0 ± 0.4 | 1.8 | 2.7 | -0.8 ± 0.3 | 175 | -4 ± 2 | 1073 | -11 ± 5 | 23,076 | +814 ± 158 | 1.04 | 7 |

