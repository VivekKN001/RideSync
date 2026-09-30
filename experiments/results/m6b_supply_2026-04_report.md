# M6b: surge pricing when drivers respond

Demand: `data/processed/trips_2026-04-15_1700_3h_manhattan_f0.1.parquet`. Rider elasticity 0.5. Fares: FareConfig(base=4.1389496884694035, per_mile=1.6221044383204617, per_min=0.7997393884432867, min_fare=7.55, road_factor=1.3477817988077192).
Supply response: reserve 20% of the fleet, logging on with probability 1 − m^−ε at each price update (medium ε = 1, strong 2) after a median 300 s, off after 1200 s idle unsurged; chasing with probability strength × price gap (medium 0.5, strong 1) to the best price within 600 s.

6 seeds. Deltas are paired against `no_surge` at the same fleet and seed (mean ± 95% CI, Student t over seeds); the last column against `surge_fixed`. `served` = completed trips / app opens. `online` = drivers working, on average. `earnings/h` = fares × multiplier per online driver-hour.

## 300 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 76.4 |  | 0.0 | 23.6 | 321 | 789 |  | 1.00 | 300 | 60.9 | 0 | 0 |  |
| reposition | 76.0 | -0.3 ± 0.4 | 0.0 | 24.0 | 320 | 785 | -4 ± 4 | 1.00 | 300 | 60.8 | 0 | 0 | +39 ± 7 |
| surge_fixed | 72.2 | -4.2 ± 0.8 | 15.6 | 14.4 | 288 | 746 | -43 ± 8 | 1.78 | 300 | 102.5 | 0 | 0 |  |
| surge_logon | 82.2 | +5.8 ± 0.7 | 9.3 | 9.3 | 252 | 849 | +60 ± 8 | 1.43 | 349 | 81.1 | 58 | 0 | +103 ± 7 |
| surge_chase | 72.7 | -3.7 ± 1.0 | 15.5 | 14.1 | 288 | 750 | -39 ± 10 | 1.79 | 300 | 103.4 | 0 | 25 | +4 ± 7 |
| surge_both | 82.6 | +6.2 ± 0.9 | 9.4 | 8.9 | 253 | 853 | +64 ± 10 | 1.43 | 350 | 80.9 | 59 | 33 | +107 ± 6 |
| surge_strong | 83.4 | +7.0 ± 0.9 | 8.7 | 8.7 | 247 | 861 | +72 ± 9 | 1.40 | 353 | 79.0 | 60 | 55 | +115 ± 4 |
| surge_forecast_both | 82.6 | +6.2 ± 0.9 | 9.3 | 8.9 | 253 | 853 | +64 ± 9 | 1.43 | 349 | 80.9 | 59 | 30 | +107 ± 4 |

## 400 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 90.9 |  | 0.0 | 9.1 | 247 | 938 |  | 1.00 | 400 | 54.8 | 0 | 0 |  |
| reposition | 92.7 | +1.8 ± 0.3 | 0.0 | 7.3 | 234 | 957 | +19 ± 3 | 1.00 | 400 | 55.7 | 0 | 0 | +44 ± 5 |
| surge_fixed | 88.4 | -2.5 ± 0.4 | 5.2 | 6.7 | 226 | 913 | -26 ± 4 | 1.22 | 400 | 65.2 | 0 | 0 |  |
| surge_logon | 91.7 | +0.8 ± 0.2 | 3.1 | 5.4 | 213 | 947 | +9 ± 3 | 1.13 | 428 | 58.8 | 44 | 0 | +34 ± 5 |
| surge_chase | 88.7 | -2.2 ± 0.4 | 5.1 | 6.5 | 225 | 916 | -22 ± 5 | 1.22 | 400 | 65.1 | 0 | 29 | +3 ± 4 |
| surge_both | 92.0 | +1.2 ± 0.2 | 3.0 | 5.1 | 211 | 951 | +12 ± 3 | 1.13 | 429 | 58.6 | 44 | 19 | +38 ± 6 |
| surge_strong | 92.4 | +1.6 ± 0.4 | 2.7 | 5.0 | 209 | 955 | +16 ± 5 | 1.11 | 432 | 57.4 | 47 | 36 | +42 ± 5 |
| surge_forecast_both | 92.0 | +1.1 ± 0.4 | 3.0 | 5.2 | 212 | 950 | +11 ± 4 | 1.13 | 427 | 58.7 | 40 | 19 | +37 ± 5 |

## 500 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 95.2 |  | 0.0 | 4.8 | 197 | 984 |  | 1.00 | 500 | 45.9 | 0 | 0 |  |
| reposition | 97.4 | +2.2 ± 0.4 | 0.0 | 2.6 | 153 | 1006 | +23 ± 4 | 1.00 | 500 | 47.0 | 0 | 0 | +33 ± 3 |
| surge_fixed | 94.3 | -1.0 ± 0.4 | 1.5 | 4.3 | 192 | 974 | -10 ± 4 | 1.06 | 500 | 48.4 | 0 | 0 |  |
| surge_logon | 95.1 | -0.1 ± 0.4 | 1.2 | 3.7 | 186 | 983 | -1 ± 4 | 1.05 | 512 | 47.2 | 24 | 0 | +9 ± 4 |
| surge_chase | 94.4 | -0.9 ± 0.4 | 1.5 | 4.2 | 191 | 975 | -9 ± 4 | 1.06 | 500 | 48.3 | 0 | 11 | +1 ± 1 |
| surge_both | 95.1 | -0.2 ± 0.5 | 1.2 | 3.8 | 185 | 982 | -2 ± 5 | 1.05 | 512 | 47.2 | 23 | 9 | +8 ± 4 |
| surge_strong | 95.2 | -0.0 ± 0.4 | 1.2 | 3.7 | 184 | 983 | -0 ± 4 | 1.05 | 515 | 46.9 | 27 | 16 | +10 ± 3 |
| surge_forecast_both | 95.2 | -0.1 ± 0.4 | 1.1 | 3.7 | 185 | 983 | -1 ± 4 | 1.05 | 511 | 47.1 | 21 | 8 | +9 ± 4 |

