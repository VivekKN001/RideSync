# M6: surge pricing (Manhattan TLC replay)

Fares fitted to TLC: FareConfig(base=4.095667063723759, per_mile=1.9818404923299766, per_min=0.6756793423110916, min_fare=8.21, road_factor=1.3451330952425717).
Policy: every 300 s, pressure = (demand over 900 s + waiting) / free supply; multiplier = 1 + 0.5 × (pressure − 1), steps of 0.25, cap 2.5. Riders who decline leave with probability 0.5, else retry once after a median 180 s.

Deltas are paired against `no_surge` at the same fleet, elasticity and seed (mean ± 95% CI).
`served` = completed trips / app opens. `cancel` is per request. Revenue is fare × multiplier.

## 300 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 78.2 |  | 0.0 | 21.8 |  | 320 |  | 879 |  | 17,863 |  | 1.00 | 0 |
| surge_reactive | 75.7 | -2.5 ± 0.3 | 11.8 | 14.2 | -7.6 ± 0.2 | 294 | -26 ± 5 | 850 | -29 ± 3 | 36,686 | +18823 ± 275 | 2.14 | 87 |
| surge_forecast | 75.5 | -2.7 ± 0.4 | 12.3 | 13.9 | -7.9 ± 0.4 | 291 | -29 ± 5 | 848 | -30 ± 4 | 37,386 | +19523 ± 148 | 2.19 | 91 |

## 300 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 78.2 |  | 0.0 | 21.8 |  | 320 |  | 879 |  | 17,863 |  | 1.00 | 0 |
| surge_reactive | 73.2 | -5.0 ± 0.2 | 19.0 | 9.7 | -12.1 ± 0.4 | 259 | -61 ± 5 | 822 | -57 ± 2 | 33,949 | +16086 ± 126 | 2.04 | 83 |
| surge_forecast | 73.0 | -5.2 ± 0.3 | 19.5 | 9.4 | -12.4 ± 0.7 | 253 | -67 ± 6 | 820 | -58 ± 3 | 34,418 | +16555 ± 215 | 2.08 | 87 |

## 300 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 78.2 |  | 0.0 | 21.8 |  | 320 |  | 879 |  | 17,863 |  | 1.00 | 0 |
| surge_reactive | 68.9 | -9.3 ± 0.6 | 27.0 | 5.6 | -16.2 ± 0.7 | 208 | -112 ± 4 | 774 | -104 ± 7 | 29,017 | +11155 ± 457 | 1.85 | 74 |
| surge_forecast | 68.7 | -9.5 ± 0.4 | 27.4 | 5.4 | -16.4 ± 0.7 | 205 | -115 ± 6 | 772 | -107 ± 4 | 29,211 | +11348 ± 323 | 1.87 | 79 |

## 400 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 93.5 |  | 0.0 | 6.5 |  | 227 |  | 1050 |  | 21,391 |  | 1.00 | 0 |
| surge_reactive | 87.2 | -6.2 ± 0.2 | 8.9 | 4.3 | -2.3 ± 0.3 | 194 | -33 ± 6 | 980 | -70 ± 2 | 35,665 | +14274 ± 252 | 1.80 | 68 |
| surge_forecast | 87.3 | -6.2 ± 0.3 | 8.9 | 4.2 | -2.3 ± 0.3 | 194 | -32 ± 5 | 981 | -69 ± 4 | 35,825 | +14434 ± 377 | 1.81 | 71 |

## 400 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 93.5 |  | 0.0 | 6.5 |  | 227 |  | 1050 |  | 21,391 |  | 1.00 | 0 |
| surge_reactive | 83.1 | -10.4 ± 0.3 | 13.8 | 3.6 | -2.9 ± 0.4 | 175 | -52 ± 4 | 934 | -117 ± 4 | 32,054 | +10663 ± 437 | 1.69 | 62 |
| surge_forecast | 83.5 | -10.0 ± 0.5 | 13.7 | 3.3 | -3.3 ± 0.4 | 174 | -53 ± 4 | 938 | -113 ± 5 | 32,353 | +10962 ± 516 | 1.70 | 65 |

## 400 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 93.5 |  | 0.0 | 6.5 |  | 227 |  | 1050 |  | 21,391 |  | 1.00 | 0 |
| surge_reactive | 78.2 | -15.2 ± 0.5 | 19.8 | 2.4 | -4.1 ± 0.5 | 152 | -74 ± 3 | 879 | -171 ± 6 | 27,881 | +6490 ± 415 | 1.56 | 54 |
| surge_forecast | 78.8 | -14.7 ± 0.5 | 19.3 | 2.4 | -4.1 ± 0.6 | 152 | -75 ± 4 | 885 | -165 ± 6 | 27,932 | +6541 ± 543 | 1.56 | 57 |

## 500 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 96.5 |  | 0.0 | 3.5 |  | 179 |  | 1084 |  | 22,137 |  | 1.00 | 0 |
| surge_reactive | 91.2 | -5.3 ± 0.4 | 6.6 | 2.4 | -1.1 ± 0.3 | 157 | -22 ± 3 | 1024 | -60 ± 5 | 33,244 | +11107 ± 439 | 1.60 | 54 |
| surge_forecast | 91.1 | -5.4 ± 0.5 | 6.7 | 2.4 | -1.1 ± 0.3 | 157 | -22 ± 2 | 1023 | -61 ± 5 | 33,204 | +11067 ± 643 | 1.60 | 56 |

## 500 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 96.5 |  | 0.0 | 3.5 |  | 179 |  | 1084 |  | 22,137 |  | 1.00 | 0 |
| surge_reactive | 87.5 | -8.9 ± 0.4 | 10.7 | 2.0 | -1.5 ± 0.2 | 143 | -36 ± 2 | 984 | -100 ± 4 | 30,361 | +8223 ± 476 | 1.52 | 49 |
| surge_forecast | 87.8 | -8.7 ± 0.4 | 10.5 | 1.9 | -1.7 ± 0.4 | 144 | -35 ± 2 | 987 | -97 ± 5 | 30,437 | +8299 ± 668 | 1.52 | 51 |

## 500 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 96.5 |  | 0.0 | 3.5 |  | 179 |  | 1084 |  | 22,137 |  | 1.00 | 0 |
| surge_reactive | 83.6 | -12.9 ± 0.4 | 15.3 | 1.4 | -2.1 ± 0.3 | 130 | -49 ± 3 | 939 | -145 ± 4 | 27,120 | +4982 ± 373 | 1.41 | 43 |
| surge_forecast | 83.9 | -12.6 ± 0.4 | 14.9 | 1.4 | -2.1 ± 0.4 | 129 | -51 ± 3 | 943 | -141 ± 5 | 26,934 | +4797 ± 489 | 1.40 | 45 |

