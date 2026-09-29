# M7: repositioning idle drivers (Manhattan TLC replay, 2026-07-18 20:00, 3 h)

Optimal @30 s, cancellation-aware, straight-line travel with per-trip noise (sigma 0.27); riders give up on late drivers (median tolerance 180 s). Every 300 s the policy may move drivers idle >= 120 s, at most 50% of the idle fleet, on drives <= 600 s. 6 seeds, mean ± 95% CI of paired differences.
`empty driving` = share of driver time driving without a rider (to pickups + repositioning).

## 300 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 32.0 |  | 2.2 | 330 |  | 269 |  | 802 |  | 14.9 |  | 0.00 | 0 |  |
| drift | 32.2 | +0.1 ± 0.6 | 2.0 | 330 | +0 ± 2 | 269 | -0 ± 4 | 801 | -1.3 ± 6.6 | 14.9 | -0.0 ± 0.3 | 0.01 | 3 | 89 |
| planned_reactive | 32.0 | -0.0 ± 0.1 | 2.2 | 329 | -0 ± 2 | 270 | +1 ± 4 | 802 | +0.1 ± 1.4 | 15.0 | +0.1 ± 0.4 | 0.01 | 1 | 95 |
| planned_forecast | 31.9 | -0.1 ± 0.5 | 2.1 | 329 | -1 ± 3 | 270 | +0 ± 3 | 803 | +1.2 ± 5.5 | 14.9 | +0.0 ± 0.2 | 0.01 | 1 | 96 |

### 300 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 32.2 |  | 2.0 | 330 |  | 269 |  | 801 |  | 14.9 |  | 0.01 | 3 | 89 |
| planned_reactive | 32.0 | -0.1 ± 0.5 | 2.2 | 329 | -0 ± 2 | 270 | +1 ± 5 | 802 | +1.4 ± 6.2 | 15.0 | +0.1 ± 0.4 | 0.01 | 1 | 95 |
| planned_forecast | 31.9 | -0.2 ± 0.4 | 2.1 | 329 | -1 ± 3 | 270 | +0 ± 4 | 803 | +2.5 ± 4.2 | 14.9 | +0.0 ± 0.4 | 0.01 | 1 | 96 |

## 400 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 15.5 |  | 2.8 | 276 |  | 246 |  | 997 |  | 14.4 |  | 0.00 | 0 |  |
| drift | 15.0 | -0.5 ± 0.2 | 2.8 | 278 | +1 ± 7 | 247 | +0 ± 4 | 1002 | +5.3 ± 2.7 | 15.0 | +0.6 ± 0.3 | 0.09 | 29 | 61 |
| planned_reactive | 14.6 | -0.9 ± 0.2 | 2.7 | 271 | -5 ± 4 | 242 | -5 ± 4 | 1007 | +10.2 ± 2.3 | 15.1 | +0.7 ± 0.2 | 0.14 | 39 | 78 |
| planned_forecast | 14.8 | -0.7 ± 0.1 | 2.8 | 272 | -4 ± 5 | 242 | -5 ± 5 | 1006 | +8.5 ± 1.7 | 14.9 | +0.6 ± 0.3 | 0.12 | 34 | 80 |

### 400 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 15.0 |  | 2.8 | 278 |  | 247 |  | 1002 |  | 15.0 |  | 0.09 | 29 | 61 |
| planned_reactive | 14.6 | -0.4 ± 0.4 | 2.7 | 271 | -6 ± 5 | 242 | -5 ± 2 | 1007 | +4.9 ± 4.4 | 15.1 | +0.1 ± 0.3 | 0.14 | 39 | 78 |
| planned_forecast | 14.8 | -0.3 ± 0.3 | 2.8 | 272 | -5 ± 3 | 242 | -5 ± 2 | 1006 | +3.1 ± 3.9 | 14.9 | -0.1 ± 0.2 | 0.12 | 34 | 80 |

## 500 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 7.7 |  | 2.2 | 209 |  | 187 |  | 1089 |  | 10.2 |  | 0.00 | 0 |  |
| drift | 7.8 | +0.1 ± 0.2 | 2.2 | 211 | +1 ± 2 | 187 | +0 ± 3 | 1088 | -1.0 ± 2.3 | 11.3 | +1.1 ± 0.2 | 0.14 | 58 | 53 |
| planned_reactive | 5.6 | -2.1 ± 0.2 | 1.9 | 183 | -27 ± 5 | 161 | -25 ± 5 | 1114 | +25.3 ± 2.4 | 11.9 | +1.7 ± 0.3 | 0.36 | 156 | 57 |
| planned_forecast | 5.8 | -1.9 ± 0.2 | 1.9 | 185 | -24 ± 4 | 164 | -23 ± 4 | 1111 | +22.4 ± 2.8 | 11.4 | +1.1 ± 0.2 | 0.28 | 119 | 62 |

### 500 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 7.8 |  | 2.2 | 211 |  | 187 |  | 1088 |  | 11.3 |  | 0.14 | 58 | 53 |
| planned_reactive | 5.6 | -2.2 ± 0.2 | 1.9 | 183 | -28 ± 5 | 161 | -26 ± 5 | 1114 | +26.3 ± 2.7 | 11.9 | +0.6 ± 0.2 | 0.36 | 156 | 57 |
| planned_forecast | 5.8 | -2.0 ± 0.3 | 1.9 | 185 | -26 ± 3 | 164 | -23 ± 3 | 1111 | +23.4 ± 3.6 | 11.4 | +0.0 ± 0.2 | 0.28 | 119 | 62 |

## Move cap: 5 vs 10 minutes, 400 drivers (against `planned_forecast`, 10 min)

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 15.5 | +0.7 ± 0.1 | 2.8 | 276 | +4 ± 5 | 246 | +5 ± 5 | 997 | -8.5 ± 1.7 | 14.4 | -0.6 ± 0.3 | 0.00 | 0 |  |
| planned_forecast | 14.8 |  | 2.8 | 272 |  | 242 |  | 1006 |  | 14.9 |  | 0.12 | 34 | 80 |
| planned_forecast_5min | 15.7 | +0.9 ± 0.3 | 2.8 | 277 | +5 ± 3 | 247 | +5 ± 5 | 995 | -10.7 ± 3.0 | 14.4 | -0.5 ± 0.3 | 0.03 | 6 | 64 |

