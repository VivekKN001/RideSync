# M6b: surge pricing when drivers respond

Demand: `data/processed/trips_2026-07-15_0700_3h_manhattan_f0.1.parquet`. Rider elasticity 0.5. Fares: FareConfig(base=3.886696530557615, per_mile=1.456611025630024, per_min=0.8478498611528298, min_fare=7.7098, road_factor=1.3453195064940768).
Supply response: reserve 20% of the fleet, logging on with probability 1 − m^−ε at each price update (medium ε = 1, strong 2) after a median 300 s, off after 1200 s idle unsurged; chasing with probability strength × price gap (medium 0.5, strong 1) to the best price within 600 s.

6 seeds. Deltas are paired against `no_surge` at the same fleet and seed (mean ± 95% CI, Student t over seeds); the last column against `surge_fixed`. `served` = completed trips / app opens. `online` = drivers working, on average. `earnings/h` = fares × multiplier per online driver-hour.

## 300 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 70.6 |  | 0.0 | 29.4 | 294 | 739 |  | 1.00 | 300 | 55.6 | 0 | 0 |  |
| reposition | 72.0 | +1.4 ± 0.5 | 0.0 | 28.0 | 286 | 753 | +15 ± 6 | 1.00 | 300 | 56.6 | 0 | 0 | +40 ± 8 |
| surge_fixed | 68.1 | -2.5 ± 0.5 | 11.8 | 22.8 | 274 | 713 | -26 ± 5 | 1.47 | 300 | 80.8 | 0 | 0 |  |
| surge_logon | 72.6 | +2.0 ± 0.6 | 9.6 | 19.7 | 263 | 760 | +21 ± 6 | 1.36 | 329 | 73.7 | 42 | 0 | +47 ± 5 |
| surge_chase | 68.6 | -2.0 ± 0.2 | 11.7 | 22.4 | 275 | 718 | -21 ± 2 | 1.47 | 300 | 81.3 | 0 | 28 | +5 ± 3 |
| surge_both | 73.1 | +2.5 ± 0.7 | 9.2 | 19.5 | 261 | 765 | +26 ± 7 | 1.35 | 329 | 73.5 | 40 | 28 | +52 ± 7 |
| surge_strong | 73.3 | +2.7 ± 0.5 | 9.0 | 19.4 | 261 | 767 | +29 ± 6 | 1.34 | 330 | 72.6 | 44 | 43 | +55 ± 6 |
| surge_forecast_both | 72.9 | +2.3 ± 0.7 | 9.3 | 19.6 | 262 | 763 | +24 ± 7 | 1.34 | 328 | 73.3 | 38 | 25 | +50 ± 7 |

## 400 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 76.5 |  | 0.0 | 23.5 | 258 | 800 |  | 1.00 | 400 | 45.5 | 0 | 0 |  |
| reposition | 81.6 | +5.1 ± 0.8 | 0.0 | 18.4 | 227 | 854 | +53 ± 8 | 1.00 | 400 | 48.8 | 0 | 0 | +68 ± 8 |
| surge_fixed | 75.1 | -1.4 ± 0.4 | 8.0 | 18.4 | 249 | 786 | -15 ± 4 | 1.29 | 400 | 59.4 | 0 | 0 |  |
| surge_logon | 77.1 | +0.6 ± 0.8 | 7.4 | 16.8 | 244 | 806 | +6 ± 8 | 1.28 | 422 | 57.4 | 30 | 0 | +21 ± 8 |
| surge_chase | 75.5 | -1.0 ± 0.7 | 7.8 | 18.1 | 247 | 790 | -10 ± 7 | 1.28 | 400 | 59.2 | 0 | 25 | +4 ± 6 |
| surge_both | 77.6 | +1.1 ± 0.7 | 7.3 | 16.2 | 242 | 812 | +12 ± 8 | 1.27 | 422 | 57.7 | 30 | 26 | +26 ± 6 |
| surge_strong | 77.5 | +1.0 ± 0.8 | 7.1 | 16.5 | 240 | 811 | +11 ± 8 | 1.26 | 423 | 56.8 | 31 | 40 | +25 ± 8 |
| surge_forecast_both | 77.7 | +1.2 ± 0.7 | 7.4 | 16.1 | 244 | 813 | +13 ± 8 | 1.27 | 422 | 57.6 | 30 | 23 | +27 ± 7 |

## 500 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 79.7 |  | 0.0 | 20.3 | 246 | 834 |  | 1.00 | 500 | 38.2 | 0 | 0 |  |
| reposition | 86.4 | +6.7 ± 0.3 | 0.0 | 13.6 | 198 | 904 | +71 ± 3 | 1.00 | 500 | 41.5 | 0 | 0 | +86 ± 6 |
| surge_fixed | 78.2 | -1.4 ± 0.3 | 6.7 | 16.2 | 234 | 819 | -15 ± 3 | 1.23 | 500 | 47.5 | 0 | 0 |  |
| surge_logon | 80.5 | +0.8 ± 0.7 | 6.0 | 14.3 | 231 | 842 | +9 ± 8 | 1.21 | 521 | 46.6 | 33 | 0 | +24 ± 7 |
| surge_chase | 78.9 | -0.8 ± 0.3 | 6.4 | 15.7 | 233 | 826 | -8 ± 3 | 1.22 | 500 | 47.7 | 0 | 24 | +7 ± 1 |
| surge_both | 81.0 | +1.3 ± 0.8 | 5.7 | 14.1 | 227 | 847 | +13 ± 8 | 1.20 | 521 | 46.5 | 33 | 24 | +28 ± 8 |
| surge_strong | 81.2 | +1.5 ± 0.6 | 5.6 | 14.0 | 227 | 849 | +15 ± 6 | 1.19 | 522 | 46.4 | 34 | 33 | +31 ± 7 |
| surge_forecast_both | 80.8 | +1.1 ± 0.8 | 5.6 | 14.4 | 229 | 845 | +11 ± 8 | 1.20 | 521 | 46.2 | 32 | 19 | +26 ± 9 |

