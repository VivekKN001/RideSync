# M6b: surge pricing when drivers respond

Demand: `data/processed/trips_2026-01-14_1700_3h_manhattan_f0.1.parquet`. Rider elasticity 0.5. Fares: FareConfig(base=3.9676138537218772, per_mile=1.272669613204483, per_min=0.8429035882837667, min_fare=7.79, road_factor=1.3592535903145837).
Supply response: reserve 20% of the fleet, logging on with probability 1 − m^−ε at each price update (medium ε = 1, strong 2) after a median 300 s, off after 1200 s idle unsurged; chasing with probability strength × price gap (medium 0.5, strong 1) to the best price within 600 s.

6 seeds. Deltas are paired against `no_surge` at the same fleet and seed (mean ± 95% CI, Student t over seeds); the last column against `surge_fixed`. `served` = completed trips / app opens. `online` = drivers working, on average. `earnings/h` = fares × multiplier per online driver-hour.

## 300 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 88.3 |  | 0.0 | 11.7 | 270 | 873 |  | 1.00 | 300 | 59.7 | 0 | 0 |  |
| reposition | 89.2 | +0.9 ± 0.5 | 0.0 | 10.8 | 261 | 882 | +9 ± 5 | 1.00 | 300 | 60.3 | 0 | 0 | +45 ± 7 |
| surge_fixed | 84.6 | -3.7 ± 0.5 | 8.9 | 7.1 | 235 | 837 | -36 ± 5 | 1.41 | 300 | 80.9 | 0 | 0 |  |
| surge_logon | 90.3 | +2.0 ± 0.3 | 4.9 | 5.0 | 209 | 893 | +20 ± 3 | 1.22 | 334 | 67.4 | 46 | 0 | +56 ± 4 |
| surge_chase | 85.5 | -2.8 ± 0.3 | 8.2 | 6.9 | 229 | 845 | -28 ± 3 | 1.37 | 300 | 79.6 | 0 | 41 | +9 ± 4 |
| surge_both | 90.7 | +2.4 ± 0.4 | 4.6 | 4.9 | 206 | 897 | +24 ± 4 | 1.20 | 334 | 67.2 | 46 | 37 | +60 ± 3 |
| surge_strong | 91.3 | +3.0 ± 0.4 | 4.2 | 4.7 | 203 | 903 | +30 ± 4 | 1.18 | 337 | 66.1 | 48 | 62 | +66 ± 4 |
| surge_forecast_both | 90.9 | +2.6 ± 0.5 | 4.6 | 4.7 | 206 | 899 | +26 ± 5 | 1.19 | 334 | 66.4 | 46 | 36 | +63 ± 6 |

## 400 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 95.6 |  | 0.0 | 4.4 | 189 | 945 |  | 1.00 | 400 | 48.7 | 0 | 0 |  |
| reposition | 97.7 | +2.2 ± 0.3 | 0.0 | 2.3 | 146 | 967 | +22 ± 3 | 1.00 | 400 | 49.8 | 0 | 0 | +34 ± 5 |
| surge_fixed | 94.3 | -1.3 ± 0.5 | 2.1 | 3.7 | 183 | 933 | -12 ± 5 | 1.08 | 400 | 52.7 | 0 | 0 |  |
| surge_logon | 95.5 | -0.1 ± 0.6 | 1.6 | 3.0 | 174 | 944 | -1 ± 6 | 1.06 | 415 | 50.5 | 28 | 0 | +12 ± 6 |
| surge_chase | 94.6 | -0.9 ± 0.6 | 2.0 | 3.5 | 180 | 936 | -9 ± 6 | 1.07 | 400 | 52.5 | 0 | 22 | +3 ± 1 |
| surge_both | 95.7 | +0.2 ± 0.7 | 1.4 | 2.9 | 174 | 947 | +2 ± 7 | 1.06 | 415 | 50.5 | 26 | 17 | +14 ± 5 |
| surge_strong | 95.9 | +0.3 ± 0.7 | 1.2 | 2.9 | 171 | 948 | +3 ± 7 | 1.05 | 418 | 49.9 | 31 | 27 | +16 ± 5 |
| surge_forecast_both | 95.7 | +0.1 ± 0.6 | 1.4 | 2.9 | 174 | 947 | +1 ± 6 | 1.05 | 413 | 50.4 | 25 | 17 | +14 ± 5 |

## 500 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 97.3 |  | 0.0 | 2.7 | 159 | 962 |  | 1.00 | 500 | 39.7 | 0 | 0 |  |
| reposition | 98.9 | +1.6 ± 0.1 | 0.0 | 1.1 | 114 | 979 | +16 ± 1 | 1.00 | 500 | 40.5 | 0 | 0 | +20 ± 2 |
| surge_fixed | 96.9 | -0.4 ± 0.2 | 0.9 | 2.3 | 156 | 958 | -4 ± 2 | 1.03 | 500 | 41.2 | 0 | 0 |  |
| surge_logon | 97.4 | +0.1 ± 0.3 | 0.7 | 1.9 | 152 | 963 | +1 ± 3 | 1.03 | 508 | 40.5 | 14 | 0 | +5 ± 4 |
| surge_chase | 97.0 | -0.3 ± 0.2 | 0.8 | 2.2 | 155 | 960 | -3 ± 2 | 1.03 | 500 | 41.1 | 0 | 10 | +2 ± 1 |
| surge_both | 97.6 | +0.3 ± 0.4 | 0.7 | 1.8 | 152 | 965 | +3 ± 4 | 1.03 | 508 | 40.6 | 13 | 10 | +7 ± 4 |
| surge_strong | 97.6 | +0.3 ± 0.4 | 0.6 | 1.8 | 151 | 965 | +3 ± 4 | 1.02 | 509 | 40.5 | 15 | 15 | +7 ± 4 |
| surge_forecast_both | 97.5 | +0.2 ± 0.4 | 0.7 | 1.9 | 152 | 964 | +2 ± 4 | 1.02 | 507 | 40.5 | 13 | 8 | +6 ± 4 |

