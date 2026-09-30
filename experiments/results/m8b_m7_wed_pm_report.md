# M7: repositioning idle drivers (Manhattan TLC replay, 2026-07-15 17:00, 3 h)

Optimal @30 s, cancellation-aware, straight-line travel with per-trip noise (sigma 0.27); riders give up on late drivers (median tolerance 180 s). Every 300 s the policy may move drivers idle >= 120 s, at most 50% of the idle fleet, on drives <= 600 s. 6 seeds, mean ± 95% CI of paired differences (Student t).
`empty driving` = share of driver time driving without a rider (to pickups + repositioning).

## 300 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 29.1 |  | 2.4 | 323 |  | 271 |  | 800 |  | 15.2 |  | 0.00 | 0 |  |
| drift | 28.7 | -0.5 ± 0.6 | 2.1 | 320 | -3 ± 3 | 268 | -3 ± 3 | 806 | +5.3 ± 6.5 | 15.7 | +0.5 ± 0.4 | 0.10 | 27 | 39 |
| planned_reactive | 29.3 | +0.2 ± 0.8 | 2.5 | 319 | -4 ± 3 | 268 | -2 ± 4 | 798 | -2.2 ± 8.8 | 15.8 | +0.6 ± 0.2 | 0.12 | 28 | 58 |
| planned_forecast | 29.1 | -0.1 ± 0.8 | 2.4 | 319 | -3 ± 4 | 269 | -2 ± 3 | 801 | +1.0 ± 9.4 | 15.6 | +0.4 ± 0.2 | 0.08 | 18 | 58 |

### 300 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 28.7 |  | 2.1 | 320 |  | 268 |  | 806 |  | 15.7 |  | 0.10 | 27 | 39 |
| planned_reactive | 29.3 | +0.7 ± 0.7 | 2.5 | 319 | -1 ± 3 | 268 | +0 ± 5 | 798 | -7.5 ± 7.4 | 15.8 | +0.1 ± 0.5 | 0.12 | 28 | 58 |
| planned_forecast | 29.1 | +0.4 ± 0.6 | 2.4 | 319 | -1 ± 5 | 269 | +1 ± 5 | 801 | -4.3 ± 6.2 | 15.6 | -0.1 ± 0.5 | 0.08 | 18 | 58 |

## 400 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 12.4 |  | 2.9 | 257 |  | 232 |  | 989 |  | 14.0 |  | 0.00 | 0 |  |
| drift | 12.8 | +0.4 ± 0.6 | 2.9 | 251 | -6 ± 5 | 228 | -5 ± 4 | 985 | -4.1 ± 7.2 | 15.0 | +1.0 ± 0.4 | 0.18 | 58 | 50 |
| planned_reactive | 11.8 | -0.6 ± 0.7 | 2.9 | 251 | -6 ± 7 | 227 | -5 ± 7 | 996 | +7.2 ± 7.9 | 15.5 | +1.4 ± 0.4 | 0.25 | 77 | 63 |
| planned_forecast | 11.6 | -0.9 ± 0.7 | 2.6 | 249 | -8 ± 5 | 226 | -6 ± 6 | 999 | +9.8 ± 8.3 | 14.8 | +0.8 ± 0.3 | 0.17 | 49 | 71 |

### 400 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 12.8 |  | 2.9 | 251 |  | 228 |  | 985 |  | 15.0 |  | 0.18 | 58 | 50 |
| planned_reactive | 11.8 | -1.0 ± 0.9 | 2.9 | 251 | +0 ± 10 | 227 | -0 ± 8 | 996 | +11.3 ± 10.3 | 15.5 | +0.4 ± 0.5 | 0.25 | 77 | 63 |
| planned_forecast | 11.6 | -1.2 ± 0.7 | 2.6 | 249 | -2 ± 2 | 226 | -2 ± 4 | 999 | +13.9 ± 7.7 | 14.8 | -0.2 ± 0.2 | 0.17 | 49 | 71 |

## 500 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 6.6 |  | 2.2 | 195 |  | 174 |  | 1055 |  | 9.6 |  | 0.00 | 0 |  |
| drift | 6.2 | -0.4 ± 0.4 | 2.1 | 194 | -1 ± 4 | 173 | -1 ± 3 | 1059 | +4.7 ± 4.6 | 11.7 | +2.2 ± 0.2 | 0.32 | 133 | 43 |
| planned_reactive | 4.1 | -2.5 ± 0.3 | 1.6 | 167 | -28 ± 4 | 146 | -28 ± 3 | 1083 | +28.3 ± 3.1 | 12.9 | +3.4 ± 0.2 | 0.60 | 273 | 53 |
| planned_forecast | 3.9 | -2.7 ± 0.3 | 1.4 | 160 | -34 ± 4 | 140 | -34 ± 4 | 1085 | +30.5 ± 3.6 | 11.3 | +1.7 ± 0.2 | 0.41 | 192 | 58 |

### 500 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 6.2 |  | 2.1 | 194 |  | 173 |  | 1059 |  | 11.7 |  | 0.32 | 133 | 43 |
| planned_reactive | 4.1 | -2.1 ± 0.3 | 1.6 | 167 | -27 ± 3 | 146 | -27 ± 3 | 1083 | +23.6 ± 3.5 | 12.9 | +1.2 ± 0.2 | 0.60 | 273 | 53 |
| planned_forecast | 3.9 | -2.3 ± 0.5 | 1.4 | 160 | -34 ± 3 | 140 | -33 ± 3 | 1085 | +25.8 ± 5.7 | 11.3 | -0.5 ± 0.2 | 0.41 | 192 | 58 |

## Move cap: 5 vs 10 minutes, 400 drivers (against `planned_forecast`, 10 min)

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 12.4 | +0.9 ± 0.7 | 2.9 | 257 | +8 ± 5 | 232 | +6 ± 6 | 989 | -9.8 ± 8.3 | 14.0 | -0.8 ± 0.3 | 0.00 | 0 |  |
| planned_forecast | 11.6 |  | 2.6 | 249 |  | 226 |  | 999 |  | 14.8 |  | 0.17 | 49 | 71 |
| planned_forecast_5min | 12.6 | +1.0 ± 0.5 | 2.9 | 255 | +6 ± 7 | 232 | +6 ± 9 | 987 | -11.6 ± 5.8 | 14.3 | -0.5 ± 0.3 | 0.06 | 12 | 54 |

