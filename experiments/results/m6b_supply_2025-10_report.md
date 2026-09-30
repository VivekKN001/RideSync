# M6b: surge pricing when drivers respond

Demand: `data/processed/trips_2025-10-15_1700_3h_manhattan_f0.1.parquet`. Rider elasticity 0.5. Fares: FareConfig(base=4.051025517036157, per_mile=1.6411620294599003, per_min=0.7800624907007887, min_fare=7.86, road_factor=1.3505605505929479).
Supply response: reserve 20% of the fleet, logging on with probability 1 − m^−ε at each price update (medium ε = 1, strong 2) after a median 300 s, off after 1200 s idle unsurged; chasing with probability strength × price gap (medium 0.5, strong 1) to the best price within 600 s.

6 seeds. Deltas are paired against `no_surge` at the same fleet and seed (mean ± 95% CI, Student t over seeds); the last column against `surge_fixed`. `served` = completed trips / app opens. `online` = drivers working, on average. `earnings/h` = fares × multiplier per online driver-hour.

## 300 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 68.4 |  | 0.0 | 31.6 | 334 | 821 |  | 1.00 | 300 | 61.7 | 0 | 0 |  |
| reposition | 68.1 | -0.2 ± 0.5 | 0.0 | 31.9 | 335 | 818 | -3 ± 6 | 1.00 | 300 | 61.6 | 0 | 0 | +43 ± 9 |
| surge_fixed | 64.6 | -3.8 ± 0.7 | 20.3 | 19.0 | 311 | 775 | -46 ± 8 | 2.14 | 300 | 124.7 | 0 | 0 |  |
| surge_logon | 75.2 | +6.9 ± 0.3 | 15.0 | 11.5 | 275 | 904 | +82 ± 4 | 1.78 | 353 | 103.2 | 61 | 0 | +128 ± 8 |
| surge_chase | 64.8 | -3.6 ± 0.5 | 20.5 | 18.4 | 312 | 778 | -43 ± 6 | 2.15 | 300 | 125.6 | 0 | 14 | +3 ± 6 |
| surge_both | 75.3 | +7.0 ± 0.4 | 15.1 | 11.3 | 273 | 905 | +84 ± 5 | 1.78 | 353 | 103.3 | 61 | 26 | +130 ± 10 |
| surge_strong | 75.7 | +7.3 ± 0.6 | 14.9 | 11.1 | 273 | 909 | +88 ± 7 | 1.76 | 355 | 101.8 | 60 | 50 | +134 ± 12 |
| surge_forecast_both | 75.4 | +7.0 ± 0.7 | 15.0 | 11.4 | 271 | 905 | +84 ± 9 | 1.76 | 353 | 101.9 | 60 | 30 | +130 ± 13 |

## 400 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 85.4 |  | 0.0 | 14.6 | 288 | 1026 |  | 1.00 | 400 | 58.3 | 0 | 0 |  |
| reposition | 85.9 | +0.5 ± 0.4 | 0.0 | 14.1 | 285 | 1032 | +6 ± 4 | 1.00 | 400 | 58.7 | 0 | 0 | +47 ± 5 |
| surge_fixed | 82.0 | -3.5 ± 0.4 | 10.1 | 8.8 | 249 | 984 | -42 ± 5 | 1.48 | 400 | 82.5 | 0 | 0 |  |
| surge_logon | 88.6 | +3.2 ± 0.9 | 5.9 | 5.8 | 225 | 1064 | +38 ± 11 | 1.27 | 443 | 69.4 | 64 | 0 | +80 ± 10 |
| surge_chase | 82.5 | -3.0 ± 0.5 | 10.0 | 8.4 | 247 | 990 | -36 ± 5 | 1.47 | 400 | 82.5 | 0 | 29 | +6 ± 2 |
| surge_both | 89.0 | +3.6 ± 0.7 | 5.7 | 5.6 | 222 | 1069 | +43 ± 8 | 1.25 | 443 | 68.6 | 63 | 29 | +85 ± 6 |
| surge_strong | 89.5 | +4.1 ± 0.6 | 5.3 | 5.5 | 220 | 1075 | +49 ± 7 | 1.24 | 446 | 68.0 | 68 | 49 | +91 ± 7 |
| surge_forecast_both | 89.1 | +3.6 ± 0.7 | 5.5 | 5.7 | 220 | 1070 | +44 ± 8 | 1.25 | 443 | 68.7 | 63 | 30 | +85 ± 5 |

## 500 drivers

| arm | served % | Δ served pp | priced out % | cancel % | wait_all s | trips/h | Δ trips/h | mean mult | online | earnings/h | logons | chase moves/h | Δ trips/h vs surge_fixed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_surge | 93.8 |  | 0.0 | 6.2 | 220 | 1127 |  | 1.00 | 500 | 51.3 | 0 | 0 |  |
| reposition | 95.4 | +1.5 ± 0.3 | 0.0 | 4.6 | 190 | 1145 | +19 ± 4 | 1.00 | 500 | 52.1 | 0 | 0 | +43 ± 5 |
| surge_fixed | 91.8 | -2.1 ± 0.2 | 3.6 | 4.8 | 203 | 1102 | -25 ± 2 | 1.15 | 500 | 57.6 | 0 | 0 |  |
| surge_logon | 94.6 | +0.7 ± 0.4 | 1.9 | 3.6 | 190 | 1136 | +9 ± 5 | 1.08 | 528 | 53.0 | 49 | 0 | +33 ± 6 |
| surge_chase | 92.1 | -1.7 ± 0.1 | 3.4 | 4.6 | 201 | 1106 | -20 ± 1 | 1.14 | 500 | 57.4 | 0 | 22 | +4 ± 2 |
| surge_both | 94.9 | +1.1 ± 0.4 | 1.8 | 3.4 | 190 | 1140 | +13 ± 5 | 1.08 | 529 | 52.9 | 50 | 20 | +38 ± 5 |
| surge_strong | 95.2 | +1.4 ± 0.4 | 1.5 | 3.3 | 185 | 1144 | +17 ± 5 | 1.06 | 533 | 52.0 | 53 | 32 | +41 ± 6 |
| surge_forecast_both | 94.9 | +1.0 ± 0.4 | 1.7 | 3.5 | 191 | 1139 | +13 ± 4 | 1.08 | 528 | 52.8 | 49 | 18 | +37 ± 4 |

