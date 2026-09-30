# M6b: surge pricing when drivers respond

Demand: `data/processed/trips_2026-07-18_2000_3h_manhattan_f0.1.parquet`. Rider elasticity 0.5. Fares: FareConfig(base=3.886696530557615, per_mile=1.456611025630024, per_min=0.8478498611528298, min_fare=7.7098, road_factor=1.3453195064940768).
Supply response: reserve 20% of the fleet, logging on with probability 1 − m^−ε at each price update (medium ε = 1, strong 2) after a median 300 s, off after 1200 s idle unsurged; chasing with probability strength × price gap (medium 0.5, strong 1) to the best price within 600 s.

6 seeds. Deltas are paired against `no_surge` at the same fleet and seed (mean ± 95% CI, Student t over seeds); the last column against `surge_fixed`. `served` = completed trips / app opens. `online` = drivers working, on average. `earnings/h` = fares × multiplier per online driver-hour.

## 300 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 71.0 |  | 0.0 | 29.0 | 326 | 837 |  | 1.00 | 300 | 64.7 | 0 | 0 |  |
| reposition | 70.8 | -0.1 ± 0.5 | 0.0 | 29.2 | 325 | 836 | -1 ± 6 | 1.00 | 300 | 64.9 | 0 | 0 | +40 ± 4 |
| surge_fixed | 67.5 | -3.5 ± 0.6 | 19.2 | 16.5 | 297 | 796 | -41 ± 7 | 2.04 | 300 | 124.9 | 0 | 0 |  |
| surge_logon | 77.8 | +6.8 ± 0.7 | 14.1 | 9.4 | 260 | 918 | +80 ± 9 | 1.71 | 354 | 103.0 | 63 | 0 | +122 ± 10 |
| surge_chase | 67.4 | -3.6 ± 0.6 | 19.4 | 16.4 | 300 | 795 | -42 ± 7 | 2.05 | 300 | 125.5 | 0 | 15 | -1 ± 3 |
| surge_both | 77.8 | +6.9 ± 0.7 | 14.0 | 9.4 | 258 | 918 | +81 ± 8 | 1.70 | 354 | 102.5 | 63 | 29 | +123 ± 9 |
| surge_strong | 78.1 | +7.1 ± 0.9 | 13.8 | 9.4 | 256 | 921 | +84 ± 10 | 1.68 | 357 | 101.5 | 63 | 50 | +125 ± 11 |
| surge_forecast_both | 77.8 | +6.8 ± 0.7 | 13.6 | 10.0 | 259 | 918 | +80 ± 8 | 1.67 | 354 | 101.2 | 62 | 27 | +122 ± 9 |

## 400 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 87.1 |  | 0.0 | 12.9 | 272 | 1028 |  | 1.00 | 400 | 59.7 | 0 | 0 |  |
| reposition | 88.1 | +1.0 ± 0.7 | 0.0 | 11.9 | 264 | 1039 | +12 ± 8 | 1.00 | 400 | 60.4 | 0 | 0 | +50 ± 10 |
| surge_fixed | 83.8 | -3.3 ± 0.5 | 9.9 | 7.0 | 231 | 989 | -39 ± 5 | 1.45 | 400 | 83.2 | 0 | 0 |  |
| surge_logon | 90.0 | +2.9 ± 0.7 | 5.5 | 4.8 | 206 | 1062 | +34 ± 8 | 1.23 | 442 | 69.3 | 70 | 0 | +73 ± 8 |
| surge_chase | 84.1 | -3.0 ± 0.6 | 9.6 | 7.0 | 230 | 993 | -35 ± 7 | 1.44 | 400 | 83.2 | 0 | 30 | +4 ± 7 |
| surge_both | 90.2 | +3.1 ± 0.5 | 5.3 | 4.7 | 203 | 1065 | +37 ± 6 | 1.22 | 443 | 68.7 | 69 | 29 | +76 ± 7 |
| surge_strong | 90.5 | +3.4 ± 0.6 | 5.1 | 4.7 | 202 | 1068 | +40 ± 7 | 1.22 | 445 | 68.4 | 73 | 51 | +79 ± 10 |
| surge_forecast_both | 90.4 | +3.3 ± 0.5 | 4.8 | 5.0 | 208 | 1067 | +39 ± 6 | 1.20 | 441 | 68.1 | 65 | 20 | +78 ± 8 |

## 500 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 94.5 |  | 0.0 | 5.5 | 203 | 1115 |  | 1.00 | 500 | 51.9 | 0 | 0 |  |
| reposition | 96.0 | +1.5 ± 0.2 | 0.0 | 4.0 | 178 | 1133 | +18 ± 2 | 1.00 | 500 | 52.9 | 0 | 0 | +38 ± 5 |
| surge_fixed | 92.8 | -1.7 ± 0.3 | 3.4 | 4.0 | 184 | 1095 | -20 ± 4 | 1.14 | 500 | 58.5 | 0 | 0 |  |
| surge_logon | 95.2 | +0.7 ± 0.5 | 1.9 | 2.9 | 171 | 1124 | +9 ± 6 | 1.09 | 529 | 54.0 | 48 | 0 | +29 ± 4 |
| surge_chase | 93.0 | -1.5 ± 0.4 | 3.3 | 3.8 | 184 | 1097 | -18 ± 5 | 1.14 | 500 | 58.5 | 0 | 21 | +2 ± 3 |
| surge_both | 95.3 | +0.8 ± 0.5 | 1.8 | 2.9 | 171 | 1125 | +10 ± 5 | 1.08 | 529 | 53.9 | 48 | 17 | +30 ± 3 |
| surge_strong | 95.7 | +1.2 ± 0.5 | 1.6 | 2.8 | 169 | 1129 | +14 ± 5 | 1.07 | 531 | 53.4 | 50 | 28 | +34 ± 4 |
| surge_forecast_both | 95.4 | +0.9 ± 0.7 | 1.5 | 3.1 | 174 | 1126 | +11 ± 9 | 1.07 | 527 | 53.5 | 45 | 12 | +31 ± 6 |

