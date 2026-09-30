# M6b: surge pricing when drivers respond

Demand: `data/processed/trips_2026-07-15_1700_3h_manhattan_f0.1.parquet`. Rider elasticity 0.5. Fares: FareConfig(base=3.886696530557615, per_mile=1.456611025630024, per_min=0.8478498611528298, min_fare=7.7098, road_factor=1.3453195064940768).
Supply response: reserve 20% of the fleet, logging on with probability 1 − m^−ε at each price update (medium ε = 1, strong 2) after a median 300 s, off after 1200 s idle unsurged; chasing with probability strength × price gap (medium 0.5, strong 1) to the best price within 600 s.

6 seeds. Deltas are paired against `no_surge` at the same fleet and seed (mean ± 95% CI, Student t over seeds); the last column against `surge_fixed`. `served` = completed trips / app opens. `online` = drivers working, on average. `earnings/h` = fares × multiplier per online driver-hour.

## 300 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 73.7 |  | 0.0 | 26.3 | 320 | 833 |  | 1.00 | 300 | 63.2 | 0 | 0 |  |
| reposition | 73.8 | +0.0 ± 0.7 | 0.0 | 26.2 | 316 | 833 | +0 ± 8 | 1.00 | 300 | 63.3 | 0 | 0 | +37 ± 9 |
| surge_fixed | 70.5 | -3.2 ± 0.2 | 17.4 | 14.7 | 285 | 796 | -37 ± 2 | 1.92 | 300 | 115.0 | 0 | 0 |  |
| surge_logon | 81.6 | +7.8 ± 0.6 | 10.7 | 8.6 | 245 | 921 | +88 ± 7 | 1.53 | 353 | 90.7 | 71 | 0 | +125 ± 8 |
| surge_chase | 70.6 | -3.1 ± 0.4 | 17.5 | 14.5 | 285 | 798 | -36 ± 5 | 1.93 | 300 | 115.3 | 0 | 17 | +1 ± 5 |
| surge_both | 81.7 | +8.0 ± 0.7 | 10.6 | 8.6 | 245 | 923 | +90 ± 8 | 1.52 | 352 | 90.0 | 71 | 29 | +127 ± 9 |
| surge_strong | 81.9 | +8.2 ± 0.7 | 10.4 | 8.6 | 243 | 926 | +93 ± 8 | 1.50 | 355 | 88.9 | 76 | 54 | +129 ± 8 |
| surge_forecast_both | 81.9 | +8.2 ± 0.6 | 10.0 | 9.0 | 249 | 925 | +92 ± 7 | 1.49 | 352 | 88.7 | 70 | 25 | +129 ± 6 |

## 400 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 90.5 |  | 0.0 | 9.5 | 249 | 1022 |  | 1.00 | 400 | 58.4 | 0 | 0 |  |
| reposition | 91.5 | +1.0 ± 0.3 | 0.0 | 8.5 | 242 | 1033 | +11 ± 4 | 1.00 | 400 | 59.1 | 0 | 0 | +39 ± 7 |
| surge_fixed | 88.0 | -2.5 ± 0.5 | 6.2 | 6.2 | 220 | 994 | -28 ± 5 | 1.28 | 400 | 72.4 | 0 | 0 |  |
| surge_logon | 92.1 | +1.6 ± 0.2 | 3.5 | 4.6 | 198 | 1040 | +18 ± 2 | 1.14 | 437 | 62.4 | 54 | 0 | +46 ± 5 |
| surge_chase | 88.0 | -2.5 ± 0.7 | 6.2 | 6.2 | 219 | 994 | -28 ± 8 | 1.28 | 400 | 72.3 | 0 | 29 | -1 ± 5 |
| surge_both | 92.2 | +1.7 ± 0.5 | 3.4 | 4.5 | 197 | 1042 | +19 ± 6 | 1.14 | 438 | 62.0 | 54 | 24 | +47 ± 8 |
| surge_strong | 92.6 | +2.1 ± 0.5 | 3.1 | 4.4 | 197 | 1046 | +23 ± 6 | 1.13 | 440 | 61.6 | 58 | 42 | +51 ± 6 |
| surge_forecast_both | 92.2 | +1.7 ± 0.3 | 3.1 | 4.9 | 200 | 1041 | +19 ± 4 | 1.12 | 435 | 61.5 | 52 | 18 | +47 ± 7 |

## 500 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 95.7 |  | 0.0 | 4.3 | 192 | 1081 |  | 1.00 | 500 | 49.4 | 0 | 0 |  |
| reposition | 97.5 | +1.8 ± 0.2 | 0.0 | 2.5 | 156 | 1101 | +20 ± 3 | 1.00 | 500 | 50.4 | 0 | 0 | +34 ± 5 |
| surge_fixed | 94.5 | -1.2 ± 0.3 | 1.9 | 3.7 | 185 | 1067 | -14 ± 3 | 1.07 | 500 | 52.4 | 0 | 0 |  |
| surge_logon | 95.6 | -0.1 ± 0.3 | 1.3 | 3.1 | 177 | 1080 | -1 ± 3 | 1.05 | 516 | 50.3 | 32 | 0 | +13 ± 3 |
| surge_chase | 94.7 | -1.0 ± 0.2 | 1.8 | 3.6 | 183 | 1070 | -12 ± 2 | 1.07 | 500 | 52.4 | 0 | 17 | +2 ± 2 |
| surge_both | 95.7 | -0.0 ± 0.2 | 1.2 | 3.1 | 175 | 1081 | -0 ± 3 | 1.04 | 516 | 50.2 | 32 | 12 | +14 ± 2 |
| surge_strong | 96.0 | +0.2 ± 0.3 | 1.1 | 3.0 | 173 | 1084 | +3 ± 3 | 1.04 | 519 | 49.8 | 36 | 18 | +17 ± 5 |
| surge_forecast_both | 95.7 | -0.1 ± 0.2 | 1.0 | 3.3 | 178 | 1081 | -1 ± 2 | 1.04 | 513 | 50.1 | 28 | 7 | +13 ± 2 |

