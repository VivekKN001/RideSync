# M6: surge pricing (Manhattan TLC replay)

Fares fitted to TLC: FareConfig(base=3.886696530557615, per_mile=1.456611025630024, per_min=0.8478498611528298, min_fare=7.7098, road_factor=1.3453195064940768).
Policy: every 300 s, pressure = (demand over 900 s + waiting) / free supply, pooled over zones within 2000 m; multiplier = 1 + 0.2 × (pressure − 4), steps of 0.25, cap 2.5. Riders who decline leave with probability 0.5, else retry once after a median 180 s.

Deltas are paired against `no_surge` at the same fleet, elasticity and seed (mean ± 95% CI, Student t over seeds).
`served` = completed trips / app opens. `cancel` is per request. Revenue is fare × multiplier.

## 300 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 70.6 |  | 0.0 | 29.4 |  | 294 |  | 739 |  | 16,668 |  | 1.00 | 0 |
| surge_reactive | 68.9 | -1.7 ± 0.4 | 7.6 | 25.5 | -3.9 ± 0.6 | 280 | -14 ± 6 | 721 | -18 ± 4 | 25,638 | +8970 ± 640 | 1.55 | 53 |
| surge_forecast | 69.0 | -1.6 ± 0.3 | 7.5 | 25.3 | -4.1 ± 0.6 | 282 | -13 ± 6 | 723 | -16 ± 3 | 25,432 | +8764 ± 394 | 1.53 | 52 |

## 300 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 70.6 |  | 0.0 | 29.4 |  | 294 |  | 739 |  | 16,668 |  | 1.00 | 0 |
| surge_reactive | 68.1 | -2.5 ± 0.5 | 11.8 | 22.8 | -6.6 ± 0.5 | 274 | -20 ± 5 | 713 | -26 ± 5 | 24,249 | +7581 ± 506 | 1.47 | 47 |
| surge_forecast | 68.3 | -2.3 ± 0.5 | 11.7 | 22.6 | -6.8 ± 0.5 | 276 | -19 ± 5 | 714 | -24 ± 5 | 24,152 | +7484 ± 449 | 1.46 | 45 |

## 300 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 70.6 |  | 0.0 | 29.4 |  | 294 |  | 739 |  | 16,668 |  | 1.00 | 0 |
| surge_reactive | 66.9 | -3.7 ± 0.5 | 17.1 | 19.3 | -10.1 ± 0.4 | 263 | -31 ± 5 | 700 | -39 ± 5 | 22,471 | +5804 ± 361 | 1.38 | 38 |
| surge_forecast | 67.3 | -3.3 ± 0.4 | 16.8 | 19.1 | -10.3 ± 0.7 | 264 | -30 ± 6 | 704 | -34 ± 4 | 22,312 | +5644 ± 283 | 1.36 | 38 |

## 400 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 76.5 |  | 0.0 | 23.5 |  | 258 |  | 800 |  | 18,201 |  | 1.00 | 0 |
| surge_reactive | 75.4 | -1.1 ± 0.4 | 4.9 | 20.7 | -2.8 ± 0.5 | 253 | -5 ± 2 | 789 | -12 ± 5 | 24,271 | +6070 ± 293 | 1.31 | 27 |
| surge_forecast | 75.6 | -0.9 ± 0.4 | 4.8 | 20.6 | -2.9 ± 0.4 | 254 | -4 ± 2 | 791 | -9 ± 4 | 24,336 | +6136 ± 220 | 1.31 | 27 |

## 400 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 76.5 |  | 0.0 | 23.5 |  | 258 |  | 800 |  | 18,201 |  | 1.00 | 0 |
| surge_reactive | 75.1 | -1.4 ± 0.4 | 8.0 | 18.4 | -5.1 ± 0.5 | 249 | -9 ± 2 | 786 | -15 ± 4 | 23,752 | +5552 ± 308 | 1.29 | 26 |
| surge_forecast | 75.1 | -1.4 ± 0.6 | 8.0 | 18.3 | -5.2 ± 0.5 | 248 | -10 ± 3 | 786 | -14 ± 6 | 23,660 | +5459 ± 511 | 1.28 | 26 |

## 400 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 76.5 |  | 0.0 | 23.5 |  | 258 |  | 800 |  | 18,201 |  | 1.00 | 0 |
| surge_reactive | 74.1 | -2.4 ± 0.3 | 12.3 | 15.6 | -8.0 ± 0.4 | 239 | -18 ± 3 | 775 | -25 ± 4 | 22,605 | +4405 ± 324 | 1.25 | 23 |
| surge_forecast | 74.1 | -2.4 ± 0.8 | 12.2 | 15.7 | -7.8 ± 0.9 | 239 | -19 ± 2 | 775 | -25 ± 8 | 22,533 | +4332 ± 352 | 1.24 | 23 |

## 500 drivers, elasticity 0.3

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 79.7 |  | 0.0 | 20.3 |  | 246 |  | 834 |  | 19,085 |  | 1.00 | 0 |
| surge_reactive | 79.1 | -0.6 ± 0.4 | 4.0 | 17.7 | -2.7 ± 0.4 | 240 | -6 ± 2 | 827 | -6 ± 4 | 24,503 | +5418 ± 284 | 1.25 | 23 |
| surge_forecast | 79.2 | -0.5 ± 0.4 | 3.9 | 17.6 | -2.7 ± 0.5 | 240 | -6 ± 2 | 829 | -5 ± 4 | 24,403 | +5319 ± 310 | 1.25 | 23 |

## 500 drivers, elasticity 0.5

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 79.7 |  | 0.0 | 20.3 |  | 246 |  | 834 |  | 19,085 |  | 1.00 | 0 |
| surge_reactive | 78.2 | -1.4 ± 0.3 | 6.7 | 16.2 | -4.1 ± 0.4 | 234 | -12 ± 2 | 819 | -15 ± 3 | 23,738 | +4654 ± 371 | 1.23 | 22 |
| surge_forecast | 78.5 | -1.2 ± 0.4 | 6.4 | 16.1 | -4.2 ± 0.4 | 233 | -13 ± 1 | 821 | -13 ± 4 | 23,629 | +4545 ± 326 | 1.22 | 21 |

## 500 drivers, elasticity 0.8

| arm | served % | Δ served pp | priced out % | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | trips/h | Δ trips/h | revenue/h | Δ revenue/h | mean mult | surged trips % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 79.7 |  | 0.0 | 20.3 |  | 246 |  | 834 |  | 19,085 |  | 1.00 | 0 |
| surge_reactive | 77.9 | -1.8 ± 0.4 | 9.8 | 13.7 | -6.6 ± 0.7 | 229 | -17 ± 2 | 815 | -19 ± 5 | 22,851 | +3767 ± 368 | 1.19 | 19 |
| surge_forecast | 78.0 | -1.7 ± 0.4 | 9.7 | 13.6 | -6.7 ± 0.6 | 228 | -18 ± 2 | 816 | -18 ± 5 | 22,753 | +3669 ± 431 | 1.19 | 19 |

