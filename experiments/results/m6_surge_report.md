# M6: surge pricing (Manhattan TLC replay)

Fares fitted to TLC: FareConfig(base=4.095667063723759, per_mile=1.9818404923299766, per_min=0.6756793423110916, min_fare=8.21, road_factor=1.3451330952425717).
Policy: every 300 s, pressure = (demand over 900 s + waiting) / free supply, pooled over zones within 2000 m; multiplier = 1 + 0.2 × (pressure − 4), steps of 0.25, cap 2.5. Riders who decline leave with probability 0.5, else retry once after a median 180 s.

Deltas are paired against `no_surge` at the same fleet, elasticity and seed (mean ± 95% CI).
`served` = completed trips / app opens. `cancel` is per request. Revenue is fare × multiplier.

## 300 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 78.2 |  | 0.0 | 21.8 |  | 320 |  | 879 |  | 17,863 |  | 1.00 | 0 |
| surge_reactive | 75.6 | -2.6 ± 0.3 | 11.6 | 14.5 | -7.3 ± 0.3 | 298 | -23 ± 3 | 849 | -29 ± 3 | 35,881 | +18018 ± 215 | 2.09 | 86 |
| surge_forecast | 75.7 | -2.5 ± 0.4 | 11.6 | 14.4 | -7.4 ± 0.4 | 298 | -22 ± 5 | 850 | -28 ± 5 | 36,013 | +18150 ± 384 | 2.10 | 87 |

## 300 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 78.2 |  | 0.0 | 21.8 |  | 320 |  | 879 |  | 17,863 |  | 1.00 | 0 |
| surge_reactive | 74.4 | -3.8 ± 0.2 | 16.6 | 10.8 | -11.0 ± 0.3 | 274 | -46 ± 5 | 836 | -43 ± 3 | 32,003 | +14140 ± 198 | 1.90 | 79 |
| surge_forecast | 74.4 | -3.8 ± 0.4 | 16.6 | 10.8 | -11.0 ± 0.5 | 275 | -46 ± 4 | 836 | -43 ± 4 | 31,687 | +13824 ± 383 | 1.88 | 80 |

## 300 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 78.2 |  | 0.0 | 21.8 |  | 320 |  | 879 |  | 17,863 |  | 1.00 | 0 |
| surge_reactive | 73.2 | -5.0 ± 0.4 | 20.6 | 7.8 | -14.0 ± 0.4 | 247 | -73 ± 4 | 823 | -56 ± 5 | 26,749 | +8886 ± 359 | 1.61 | 67 |
| surge_forecast | 73.2 | -5.0 ± 0.5 | 20.5 | 8.0 | -13.8 ± 0.3 | 246 | -74 ± 4 | 822 | -56 ± 6 | 26,427 | +8564 ± 270 | 1.59 | 67 |

## 400 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 93.5 |  | 0.0 | 6.5 |  | 227 |  | 1050 |  | 21,391 |  | 1.00 | 0 |
| surge_reactive | 91.6 | -1.9 ± 0.3 | 3.3 | 5.2 | -1.3 ± 0.3 | 211 | -16 ± 4 | 1029 | -21 ± 4 | 26,722 | +5332 ± 425 | 1.27 | 34 |
| surge_forecast | 91.6 | -1.9 ± 0.3 | 3.3 | 5.2 | -1.3 ± 0.3 | 211 | -15 ± 4 | 1030 | -21 ± 4 | 26,666 | +5275 ± 427 | 1.27 | 33 |

## 400 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 93.5 |  | 0.0 | 6.5 |  | 227 |  | 1050 |  | 21,391 |  | 1.00 | 0 |
| surge_reactive | 90.7 | -2.8 ± 0.4 | 5.0 | 4.5 | -2.0 ± 0.3 | 203 | -23 ± 4 | 1019 | -31 ± 4 | 25,409 | +4019 ± 328 | 1.22 | 29 |
| surge_forecast | 90.7 | -2.8 ± 0.4 | 4.7 | 4.9 | -1.6 ± 0.4 | 204 | -23 ± 5 | 1019 | -32 ± 4 | 25,211 | +3820 ± 402 | 1.21 | 28 |

## 400 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 93.5 |  | 0.0 | 6.5 |  | 227 |  | 1050 |  | 21,391 |  | 1.00 | 0 |
| surge_reactive | 89.9 | -3.6 ± 0.4 | 6.5 | 3.9 | -2.6 ± 0.4 | 198 | -29 ± 5 | 1010 | -41 ± 4 | 23,935 | +2544 ± 221 | 1.16 | 25 |
| surge_forecast | 89.9 | -3.6 ± 0.4 | 6.1 | 4.2 | -2.3 ± 0.3 | 198 | -29 ± 4 | 1010 | -40 ± 5 | 23,884 | +2494 ± 261 | 1.16 | 24 |

## 500 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 96.5 |  | 0.0 | 3.5 |  | 179 |  | 1084 |  | 22,137 |  | 1.00 | 0 |
| surge_reactive | 95.9 | -0.6 ± 0.2 | 0.9 | 3.3 | -0.2 ± 0.2 | 176 | -3 ± 2 | 1077 | -7 ± 3 | 23,737 | +1600 ± 203 | 1.07 | 9 |
| surge_forecast | 95.9 | -0.6 ± 0.3 | 0.8 | 3.3 | -0.2 ± 0.2 | 177 | -2 ± 1 | 1078 | -6 ± 3 | 23,610 | +1473 ± 249 | 1.06 | 9 |

## 500 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 96.5 |  | 0.0 | 3.5 |  | 179 |  | 1084 |  | 22,137 |  | 1.00 | 0 |
| surge_reactive | 95.5 | -1.0 ± 0.3 | 1.4 | 3.1 | -0.4 ± 0.2 | 174 | -5 ± 2 | 1073 | -11 ± 3 | 23,323 | +1185 ± 151 | 1.06 | 9 |
| surge_forecast | 95.8 | -0.6 ± 0.3 | 1.2 | 3.0 | -0.5 ± 0.2 | 175 | -4 ± 2 | 1077 | -7 ± 3 | 23,326 | +1188 ± 158 | 1.06 | 8 |

## 500 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 96.5 |  | 0.0 | 3.5 |  | 179 |  | 1084 |  | 22,137 |  | 1.00 | 0 |
| surge_reactive | 95.2 | -1.3 ± 0.4 | 2.0 | 2.9 | -0.6 ± 0.2 | 173 | -6 ± 2 | 1070 | -14 ± 4 | 22,974 | +837 ± 184 | 1.05 | 8 |
| surge_forecast | 95.5 | -1.0 ± 0.3 | 1.8 | 2.7 | -0.8 ± 0.2 | 175 | -4 ± 2 | 1073 | -11 ± 4 | 22,946 | +809 ± 120 | 1.04 | 7 |

