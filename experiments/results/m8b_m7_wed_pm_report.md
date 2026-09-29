# M7: repositioning idle drivers (Manhattan TLC replay, 2026-07-15 17:00, 3 h)

Optimal @30 s, cancellation-aware, straight-line travel with per-trip noise (sigma 0.27); riders give up on late drivers (median tolerance 180 s). Every 300 s the policy may move drivers idle >= 120 s, at most 50% of the idle fleet, on drives <= 600 s. 6 seeds, mean ± 95% CI of paired differences.
`empty driving` = share of driver time driving without a rider (to pickups + repositioning).

## 300 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 29.1 |  | 2.4 | 323 |  | 271 |  | 800 |  | 15.2 |  | 0.00 | 0 |  |
| drift | 28.7 | -0.5 ± 0.4 | 2.1 | 320 | -3 ± 2 | 268 | -3 ± 2 | 806 | +5.3 ± 5.0 | 15.7 | +0.5 ± 0.3 | 0.10 | 27 | 39 |
| planned_reactive | 29.3 | +0.2 ± 0.6 | 2.5 | 319 | -4 ± 2 | 268 | -2 ± 3 | 798 | -2.2 ± 6.7 | 15.8 | +0.6 ± 0.2 | 0.12 | 28 | 58 |
| planned_forecast | 29.1 | -0.1 ± 0.6 | 2.4 | 319 | -3 ± 3 | 269 | -2 ± 2 | 801 | +1.0 ± 7.2 | 15.6 | +0.4 ± 0.1 | 0.08 | 18 | 58 |

### 300 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 28.7 |  | 2.1 | 320 |  | 268 |  | 806 |  | 15.7 |  | 0.10 | 27 | 39 |
| planned_reactive | 29.3 | +0.7 ± 0.5 | 2.5 | 319 | -1 ± 2 | 268 | +0 ± 4 | 798 | -7.5 ± 5.7 | 15.8 | +0.1 ± 0.4 | 0.12 | 28 | 58 |
| planned_forecast | 29.1 | +0.4 ± 0.4 | 2.4 | 319 | -1 ± 4 | 269 | +1 ± 4 | 801 | -4.3 ± 4.7 | 15.6 | -0.1 ± 0.4 | 0.08 | 18 | 58 |

## 400 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 12.4 |  | 2.9 | 257 |  | 232 |  | 989 |  | 14.0 |  | 0.00 | 0 |  |
| drift | 12.8 | +0.4 ± 0.5 | 2.9 | 251 | -6 ± 4 | 228 | -5 ± 3 | 985 | -4.1 ± 5.5 | 15.0 | +1.0 ± 0.3 | 0.18 | 58 | 50 |
| planned_reactive | 11.8 | -0.6 ± 0.5 | 2.9 | 251 | -6 ± 5 | 227 | -5 ± 6 | 996 | +7.2 ± 6.0 | 15.5 | +1.4 ± 0.3 | 0.25 | 77 | 63 |
| planned_forecast | 11.6 | -0.9 ± 0.6 | 2.6 | 249 | -8 ± 4 | 226 | -6 ± 5 | 999 | +9.8 ± 6.4 | 14.8 | +0.8 ± 0.2 | 0.17 | 49 | 71 |

### 400 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 12.8 |  | 2.9 | 251 |  | 228 |  | 985 |  | 15.0 |  | 0.18 | 58 | 50 |
| planned_reactive | 11.8 | -1.0 ± 0.7 | 2.9 | 251 | +0 ± 8 | 227 | -0 ± 6 | 996 | +11.3 ± 7.8 | 15.5 | +0.4 ± 0.4 | 0.25 | 77 | 63 |
| planned_forecast | 11.6 | -1.2 ± 0.5 | 2.6 | 249 | -2 ± 2 | 226 | -2 ± 3 | 999 | +13.9 ± 5.8 | 14.8 | -0.2 ± 0.2 | 0.17 | 49 | 71 |

## 500 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 6.6 |  | 2.2 | 195 |  | 174 |  | 1055 |  | 9.6 |  | 0.00 | 0 |  |
| drift | 6.2 | -0.4 ± 0.3 | 2.1 | 194 | -1 ± 3 | 173 | -1 ± 3 | 1059 | +4.7 ± 3.5 | 11.7 | +2.2 ± 0.2 | 0.32 | 133 | 43 |
| planned_reactive | 4.1 | -2.5 ± 0.2 | 1.6 | 167 | -28 ± 3 | 146 | -28 ± 2 | 1083 | +28.3 ± 2.4 | 12.9 | +3.4 ± 0.1 | 0.60 | 273 | 53 |
| planned_forecast | 3.9 | -2.7 ± 0.2 | 1.4 | 160 | -34 ± 3 | 140 | -34 ± 3 | 1085 | +30.5 ± 2.7 | 11.3 | +1.7 ± 0.2 | 0.41 | 192 | 58 |

### 500 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 6.2 |  | 2.1 | 194 |  | 173 |  | 1059 |  | 11.7 |  | 0.32 | 133 | 43 |
| planned_reactive | 4.1 | -2.1 ± 0.2 | 1.6 | 167 | -27 ± 2 | 146 | -27 ± 2 | 1083 | +23.6 ± 2.7 | 12.9 | +1.2 ± 0.2 | 0.60 | 273 | 53 |
| planned_forecast | 3.9 | -2.3 ± 0.4 | 1.4 | 160 | -34 ± 3 | 140 | -33 ± 2 | 1085 | +25.8 ± 4.4 | 11.3 | -0.5 ± 0.1 | 0.41 | 192 | 58 |

## Move cap: 5 vs 10 minutes, 400 drivers (against `planned_forecast`, 10 min)

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 12.4 | +0.9 ± 0.6 | 2.9 | 257 | +8 ± 4 | 232 | +6 ± 5 | 989 | -9.8 ± 6.4 | 14.0 | -0.8 ± 0.2 | 0.00 | 0 |  |
| planned_forecast | 11.6 |  | 2.6 | 249 |  | 226 |  | 999 |  | 14.8 |  | 0.17 | 49 | 71 |
| planned_forecast_5min | 12.6 | +1.0 ± 0.4 | 2.9 | 255 | +6 ± 6 | 232 | +6 ± 7 | 987 | -11.6 ± 4.4 | 14.3 | -0.5 ± 0.2 | 0.06 | 12 | 54 |

