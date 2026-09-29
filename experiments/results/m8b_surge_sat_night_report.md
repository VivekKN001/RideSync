# M6: surge pricing (Manhattan TLC replay)

Fares fitted to TLC: FareConfig(base=3.886696530557615, per_mile=1.456611025630024, per_min=0.8478498611528298, min_fare=7.7098, road_factor=1.3453195064940768).
Policy: every 300 s, pressure = (demand over 900 s + waiting) / free supply, pooled over zones within 2000 m; multiplier = 1 + 0.2 × (pressure − 4), steps of 0.25, cap 2.5. Riders who decline leave with probability 0.5, else retry once after a median 180 s.

Deltas are paired against `no_surge` at the same fleet, elasticity and seed (mean ± 95% CI).
`served` = completed trips / app opens. `cancel` is per request. Revenue is fare × multiplier.

## 300 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 71.0 |  | 0.0 | 29.0 |  | 326 |  | 837 |  | 19,399 |  | 1.00 | 0 |
| surge_reactive | 68.9 | -2.1 ± 0.4 | 12.3 | 21.5 | -7.6 ± 0.4 | 317 | -9 ± 2 | 813 | -25 ± 4 | 40,809 | +21411 ± 450 | 2.17 | 88 |
| surge_forecast | 69.0 | -2.0 ± 0.2 | 12.1 | 21.5 | -7.6 ± 0.3 | 314 | -11 ± 4 | 814 | -23 ± 2 | 40,309 | +20910 ± 435 | 2.15 | 88 |

## 300 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 71.0 |  | 0.0 | 29.0 |  | 326 |  | 837 |  | 19,399 |  | 1.00 | 0 |
| surge_reactive | 67.5 | -3.5 ± 0.4 | 19.2 | 16.5 | -12.5 ± 0.6 | 297 | -28 ± 3 | 796 | -41 ± 5 | 37,467 | +18069 ± 187 | 2.04 | 82 |
| surge_forecast | 67.5 | -3.5 ± 0.6 | 19.2 | 16.5 | -12.6 ± 0.5 | 299 | -26 ± 3 | 797 | -41 ± 7 | 37,407 | +18009 ± 323 | 2.02 | 82 |

## 300 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 71.0 |  | 0.0 | 29.0 |  | 326 |  | 837 |  | 19,399 |  | 1.00 | 0 |
| surge_reactive | 65.9 | -5.1 ± 0.5 | 25.8 | 11.1 | -17.9 ± 0.6 | 267 | -59 ± 5 | 778 | -60 ± 6 | 32,362 | +12964 ± 558 | 1.80 | 73 |
| surge_forecast | 66.3 | -4.7 ± 0.6 | 25.4 | 11.2 | -17.8 ± 0.6 | 272 | -54 ± 4 | 782 | -55 ± 7 | 32,302 | +12903 ± 529 | 1.78 | 74 |

## 400 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 87.1 |  | 0.0 | 12.9 |  | 272 |  | 1028 |  | 23,894 |  | 1.00 | 0 |
| surge_reactive | 84.9 | -2.2 ± 0.4 | 6.8 | 8.9 | -4.0 ± 0.8 | 244 | -28 ± 2 | 1002 | -26 ± 4 | 36,641 | +12747 ± 543 | 1.57 | 54 |
| surge_forecast | 85.1 | -2.0 ± 0.3 | 6.5 | 9.0 | -3.9 ± 0.7 | 245 | -27 ± 3 | 1004 | -24 ± 3 | 35,996 | +12102 ± 417 | 1.53 | 53 |

## 400 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 87.1 |  | 0.0 | 12.9 |  | 272 |  | 1028 |  | 23,894 |  | 1.00 | 0 |
| surge_reactive | 83.8 | -3.3 ± 0.3 | 9.9 | 7.0 | -5.9 ± 0.4 | 231 | -41 ± 4 | 989 | -39 ± 4 | 33,267 | +9373 ± 644 | 1.45 | 48 |
| surge_forecast | 83.9 | -3.2 ± 0.3 | 9.3 | 7.5 | -5.4 ± 0.5 | 235 | -37 ± 4 | 990 | -37 ± 4 | 32,996 | +9103 ± 582 | 1.43 | 47 |

## 400 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 87.1 |  | 0.0 | 12.9 |  | 272 |  | 1028 |  | 23,894 |  | 1.00 | 0 |
| surge_reactive | 83.0 | -4.1 ± 0.4 | 12.1 | 5.5 | -7.4 ± 0.5 | 218 | -54 ± 4 | 980 | -48 ± 5 | 29,746 | +5852 ± 448 | 1.30 | 39 |
| surge_forecast | 83.1 | -4.0 ± 0.3 | 11.3 | 6.2 | -6.7 ± 0.5 | 222 | -50 ± 3 | 981 | -47 ± 3 | 29,385 | +5492 ± 355 | 1.28 | 39 |

## 500 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 94.5 |  | 0.0 | 5.5 |  | 203 |  | 1115 |  | 25,970 |  | 1.00 | 0 |
| surge_reactive | 93.4 | -1.2 ± 0.3 | 2.4 | 4.4 | -1.1 ± 0.3 | 190 | -12 ± 3 | 1102 | -14 ± 4 | 30,526 | +4555 ± 595 | 1.18 | 22 |
| surge_forecast | 93.4 | -1.1 ± 0.3 | 2.2 | 4.5 | -1.0 ± 0.3 | 193 | -9 ± 1 | 1102 | -14 ± 3 | 30,045 | +4074 ± 593 | 1.16 | 20 |

## 500 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 94.5 |  | 0.0 | 5.5 |  | 203 |  | 1115 |  | 25,970 |  | 1.00 | 0 |
| surge_reactive | 92.8 | -1.7 ± 0.3 | 3.4 | 4.0 | -1.5 ± 0.4 | 184 | -18 ± 3 | 1095 | -20 ± 3 | 29,243 | +3272 ± 433 | 1.14 | 18 |
| surge_forecast | 93.0 | -1.5 ± 0.4 | 3.0 | 4.1 | -1.4 ± 0.4 | 188 | -15 ± 3 | 1097 | -18 ± 4 | 28,988 | +3018 ± 444 | 1.13 | 17 |

## 500 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 94.5 |  | 0.0 | 5.5 |  | 203 |  | 1115 |  | 25,970 |  | 1.00 | 0 |
| surge_reactive | 92.4 | -2.1 ± 0.3 | 4.5 | 3.3 | -2.2 ± 0.5 | 180 | -23 ± 4 | 1090 | -25 ± 3 | 28,163 | +2192 ± 298 | 1.11 | 16 |
| surge_forecast | 92.5 | -2.0 ± 0.1 | 4.0 | 3.6 | -1.9 ± 0.5 | 182 | -20 ± 3 | 1092 | -23 ± 2 | 27,814 | +1844 ± 261 | 1.09 | 14 |

