# M7: repositioning idle drivers (Manhattan TLC replay, 2026-04-15 17:00, 3 h)

Optimal @30 s, cancellation-aware, straight-line travel with per-trip noise (sigma 0.27); riders give up on late drivers (median tolerance 180 s). Every 300 s the policy may move drivers idle >= 120 s, at most 50% of the idle fleet, on drives <= 600 s. 6 seeds, mean ± 95% CI of paired differences (Student t).
`empty driving` = share of driver time driving without a rider (to pickups + repositioning).

## 300 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 27.2 |  | 2.9 | 324 |  | 284 |  | 752 |  | 16.1 |  | 0.00 | 0 |  |
| drift | 26.6 | -0.6 ± 0.6 | 2.7 | 324 | -0 ± 4 | 286 | +2 ± 3 | 758 | +5.9 ± 6.2 | 16.3 | +0.2 ± 0.4 | 0.02 | 3 | 86 |
| planned_reactive | 26.3 | -0.9 ± 0.5 | 2.9 | 324 | +0 ± 5 | 286 | +2 ± 6 | 761 | +9.7 ± 4.8 | 16.5 | +0.4 ± 0.3 | 0.02 | 4 | 85 |
| planned_forecast | 26.7 | -0.5 ± 0.3 | 2.7 | 324 | +1 ± 3 | 287 | +2 ± 4 | 757 | +5.3 ± 3.5 | 16.3 | +0.2 ± 0.2 | 0.03 | 5 | 88 |

### 300 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 26.6 |  | 2.7 | 324 |  | 286 |  | 758 |  | 16.3 |  | 0.02 | 3 | 86 |
| planned_reactive | 26.3 | -0.4 ± 0.6 | 2.9 | 324 | +0 ± 4 | 286 | +0 ± 5 | 761 | +3.9 ± 6.4 | 16.5 | +0.1 ± 0.5 | 0.02 | 4 | 85 |
| planned_forecast | 26.7 | +0.1 ± 0.8 | 2.7 | 324 | +1 ± 4 | 287 | +1 ± 3 | 757 | -0.6 ± 8.5 | 16.3 | -0.0 ± 0.4 | 0.03 | 5 | 88 |

## 400 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 11.7 |  | 3.0 | 249 |  | 229 |  | 912 |  | 13.2 |  | 0.00 | 0 |  |
| drift | 11.4 | -0.3 ± 0.3 | 2.9 | 251 | +2 ± 5 | 231 | +1 ± 5 | 915 | +3.5 ± 3.3 | 14.6 | +1.4 ± 0.2 | 0.19 | 57 | 61 |
| planned_reactive | 10.1 | -1.6 ± 0.3 | 2.7 | 238 | -10 ± 6 | 219 | -10 ± 4 | 928 | +16.6 ± 3.4 | 14.9 | +1.7 ± 0.1 | 0.28 | 92 | 74 |
| planned_forecast | 10.4 | -1.3 ± 0.4 | 2.8 | 235 | -14 ± 3 | 216 | -13 ± 4 | 925 | +13.6 ± 3.7 | 14.5 | +1.3 ± 0.1 | 0.26 | 81 | 75 |

### 400 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 11.4 |  | 2.9 | 251 |  | 231 |  | 915 |  | 14.6 |  | 0.19 | 57 | 61 |
| planned_reactive | 10.1 | -1.3 ± 0.6 | 2.7 | 238 | -12 ± 4 | 219 | -11 ± 4 | 928 | +13.1 ± 5.9 | 14.9 | +0.3 ± 0.2 | 0.28 | 92 | 74 |
| planned_forecast | 10.4 | -1.0 ± 0.3 | 2.8 | 235 | -16 ± 3 | 216 | -15 ± 3 | 925 | +10.1 ± 3.3 | 14.5 | -0.1 ± 0.1 | 0.26 | 81 | 75 |

## 500 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 6.5 |  | 2.0 | 199 |  | 180 |  | 966 |  | 9.0 |  | 0.00 | 0 |  |
| drift | 6.7 | +0.2 ± 0.7 | 2.2 | 203 | +4 ± 6 | 183 | +4 ± 7 | 963 | -2.3 ± 7.2 | 11.5 | +2.5 ± 0.2 | 0.32 | 138 | 41 |
| planned_reactive | 3.9 | -2.6 ± 0.5 | 1.5 | 157 | -43 ± 5 | 137 | -43 ± 6 | 993 | +27.1 ± 4.9 | 12.2 | +3.2 ± 0.2 | 0.59 | 292 | 51 |
| planned_forecast | 4.0 | -2.5 ± 0.6 | 1.6 | 159 | -41 ± 5 | 138 | -42 ± 5 | 991 | +25.4 ± 5.9 | 11.1 | +2.0 ± 0.2 | 0.45 | 220 | 53 |

### 500 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 6.7 |  | 2.2 | 203 |  | 183 |  | 963 |  | 11.5 |  | 0.32 | 138 | 41 |
| planned_reactive | 3.9 | -2.8 ± 0.6 | 1.5 | 157 | -47 ± 3 | 137 | -46 ± 3 | 993 | +29.3 ± 5.9 | 12.2 | +0.6 ± 0.2 | 0.59 | 292 | 51 |
| planned_forecast | 4.0 | -2.7 ± 0.4 | 1.6 | 159 | -45 ± 3 | 138 | -45 ± 3 | 991 | +27.7 ± 4.0 | 11.1 | -0.5 ± 0.2 | 0.45 | 220 | 53 |

## Move cap: 5 vs 10 minutes, 400 drivers (against `planned_forecast`, 10 min)

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 11.7 | +1.3 ± 0.4 | 3.0 | 249 | +14 ± 3 | 229 | +13 ± 4 | 912 | -13.6 ± 3.7 | 13.2 | -1.3 ± 0.1 | 0.00 | 0 |  |
| planned_forecast | 10.4 |  | 2.8 | 235 |  | 216 |  | 925 |  | 14.5 |  | 0.26 | 81 | 75 |
| planned_forecast_5min | 11.3 | +0.9 ± 0.4 | 2.9 | 249 | +14 ± 4 | 229 | +13 ± 3 | 916 | -9.5 ± 4.1 | 13.5 | -0.9 ± 0.1 | 0.07 | 15 | 52 |

