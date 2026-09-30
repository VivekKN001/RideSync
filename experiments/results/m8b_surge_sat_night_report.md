# M6: surge pricing (Manhattan TLC replay)

Fares fitted to TLC: FareConfig(base=3.886696530557615, per_mile=1.456611025630024, per_min=0.8478498611528298, min_fare=7.7098, road_factor=1.3453195064940768).
Policy: every 300 s, pressure = (demand over 900 s + waiting) / free supply, pooled over zones within 2000 m; multiplier = 1 + 0.2 × (pressure − 4), steps of 0.25, cap 2.5. Riders who decline leave with probability 0.5, else retry once after a median 180 s.

Deltas are paired against `no_surge` at the same fleet, elasticity and seed (mean ± 95% CI, Student t over seeds).
`served` = completed trips / app opens. `cancel` is per request. Revenue is fare × multiplier.

## 300 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 71.0 |  | 0.0 | 29.0 |  | 326 |  | 837 |  | 19,399 |  | 1.00 | 0 |
| surge_reactive | 68.9 | -2.1 ± 0.5 | 12.3 | 21.5 | -7.6 ± 0.5 | 317 | -9 ± 2 | 813 | -25 ± 6 | 40,809 | +21411 ± 590 | 2.17 | 88 |
| surge_forecast | 69.0 | -2.0 ± 0.3 | 12.1 | 21.5 | -7.6 ± 0.4 | 314 | -11 ± 6 | 814 | -23 ± 3 | 40,309 | +20910 ± 571 | 2.15 | 88 |

## 300 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 71.0 |  | 0.0 | 29.0 |  | 326 |  | 837 |  | 19,399 |  | 1.00 | 0 |
| surge_reactive | 67.5 | -3.5 ± 0.6 | 19.2 | 16.5 | -12.5 ± 0.8 | 297 | -28 ± 4 | 796 | -41 ± 7 | 37,467 | +18069 ± 246 | 2.04 | 82 |
| surge_forecast | 67.5 | -3.5 ± 0.7 | 19.2 | 16.5 | -12.6 ± 0.7 | 299 | -26 ± 4 | 797 | -41 ± 9 | 37,407 | +18009 ± 423 | 2.02 | 82 |

## 300 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 71.0 |  | 0.0 | 29.0 |  | 326 |  | 837 |  | 19,399 |  | 1.00 | 0 |
| surge_reactive | 65.9 | -5.1 ± 0.7 | 25.8 | 11.1 | -17.9 ± 0.8 | 267 | -59 ± 7 | 778 | -60 ± 8 | 32,362 | +12964 ± 731 | 1.80 | 73 |
| surge_forecast | 66.3 | -4.7 ± 0.8 | 25.4 | 11.2 | -17.8 ± 0.8 | 272 | -54 ± 5 | 782 | -55 ± 10 | 32,302 | +12903 ± 694 | 1.78 | 74 |

## 400 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 87.1 |  | 0.0 | 12.9 |  | 272 |  | 1028 |  | 23,894 |  | 1.00 | 0 |
| surge_reactive | 84.9 | -2.2 ± 0.5 | 6.8 | 8.9 | -4.0 ± 1.0 | 244 | -28 ± 3 | 1002 | -26 ± 6 | 36,641 | +12747 ± 712 | 1.57 | 54 |
| surge_forecast | 85.1 | -2.0 ± 0.4 | 6.5 | 9.0 | -3.9 ± 0.9 | 245 | -27 ± 4 | 1004 | -24 ± 4 | 35,996 | +12102 ± 546 | 1.53 | 53 |

## 400 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 87.1 |  | 0.0 | 12.9 |  | 272 |  | 1028 |  | 23,894 |  | 1.00 | 0 |
| surge_reactive | 83.8 | -3.3 ± 0.5 | 9.9 | 7.0 | -5.9 ± 0.6 | 231 | -41 ± 5 | 989 | -39 ± 5 | 33,267 | +9373 ± 845 | 1.45 | 48 |
| surge_forecast | 83.9 | -3.2 ± 0.4 | 9.3 | 7.5 | -5.4 ± 0.7 | 235 | -37 ± 5 | 990 | -37 ± 5 | 32,996 | +9103 ± 764 | 1.43 | 47 |

## 400 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 87.1 |  | 0.0 | 12.9 |  | 272 |  | 1028 |  | 23,894 |  | 1.00 | 0 |
| surge_reactive | 83.0 | -4.1 ± 0.5 | 12.1 | 5.5 | -7.4 ± 0.7 | 218 | -54 ± 6 | 980 | -48 ± 6 | 29,746 | +5852 ± 588 | 1.30 | 39 |
| surge_forecast | 83.1 | -4.0 ± 0.3 | 11.3 | 6.2 | -6.7 ± 0.6 | 222 | -50 ± 4 | 981 | -47 ± 4 | 29,385 | +5492 ± 466 | 1.28 | 39 |

## 500 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 94.5 |  | 0.0 | 5.5 |  | 203 |  | 1115 |  | 25,970 |  | 1.00 | 0 |
| surge_reactive | 93.4 | -1.2 ± 0.4 | 2.4 | 4.4 | -1.1 ± 0.4 | 190 | -12 ± 3 | 1102 | -14 ± 5 | 30,526 | +4555 ± 780 | 1.18 | 22 |
| surge_forecast | 93.4 | -1.1 ± 0.4 | 2.2 | 4.5 | -1.0 ± 0.4 | 193 | -9 ± 2 | 1102 | -14 ± 4 | 30,045 | +4074 ± 778 | 1.16 | 20 |

## 500 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 94.5 |  | 0.0 | 5.5 |  | 203 |  | 1115 |  | 25,970 |  | 1.00 | 0 |
| surge_reactive | 92.8 | -1.7 ± 0.3 | 3.4 | 4.0 | -1.5 ± 0.5 | 184 | -18 ± 4 | 1095 | -20 ± 4 | 29,243 | +3272 ± 568 | 1.14 | 18 |
| surge_forecast | 93.0 | -1.5 ± 0.5 | 3.0 | 4.1 | -1.4 ± 0.5 | 188 | -15 ± 4 | 1097 | -18 ± 6 | 28,988 | +3018 ± 582 | 1.13 | 17 |

## 500 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 94.5 |  | 0.0 | 5.5 |  | 203 |  | 1115 |  | 25,970 |  | 1.00 | 0 |
| surge_reactive | 92.4 | -2.1 ± 0.4 | 4.5 | 3.3 | -2.2 ± 0.7 | 180 | -23 ± 5 | 1090 | -25 ± 5 | 28,163 | +2192 ± 391 | 1.11 | 16 |
| surge_forecast | 92.5 | -2.0 ± 0.2 | 4.0 | 3.6 | -1.9 ± 0.6 | 182 | -20 ± 4 | 1092 | -23 ± 2 | 27,814 | +1844 ± 343 | 1.09 | 14 |

