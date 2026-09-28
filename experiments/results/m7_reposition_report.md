# M7: repositioning idle drivers (Manhattan TLC replay, 2024-03-27 17:00-20:00)

Optimal @30 s, cancellation-aware, straight-line travel with per-trip noise (sigma 0.27); riders give up on late drivers (median tolerance 180 s). Every 300 s the policy may move drivers idle >= 120 s, at most 50% of the idle fleet, on drives <= 600 s. 6 seeds, mean ± 95% CI of paired differences.
`empty driving` = share of driver time driving without a rider (to pickups + repositioning).

## 300 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 28.5 |  | 2.4 | 328 |  | 275 |  | 853 |  | 16.3 |  | 0.00 | 0 |  |
| drift | 28.0 | -0.5 ± 0.4 | 2.2 | 328 | +0 ± 3 | 275 | +1 ± 4 | 859 | +5.9 ± 5.2 | 16.4 | +0.1 ± 0.4 | 0.00 | 0 | 100 |
| planned_reactive | 28.1 | -0.4 ± 0.4 | 2.2 | 327 | -1 ± 3 | 273 | -2 ± 4 | 858 | +4.7 ± 5.1 | 16.1 | -0.2 ± 0.3 | 0.00 | 1 | 97 |
| planned_forecast | 27.8 | -0.7 ± 0.8 | 2.1 | 327 | -1 ± 2 | 275 | +0 ± 4 | 861 | +8.5 ± 9.5 | 16.2 | -0.0 ± 0.4 | 0.00 | 1 | 90 |

### 300 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 28.0 |  | 2.2 | 328 |  | 275 |  | 859 |  | 16.4 |  | 0.00 | 0 | 100 |
| planned_reactive | 28.1 | +0.1 ± 0.4 | 2.2 | 327 | -2 ± 2 | 273 | -3 ± 3 | 858 | -1.3 ± 5.3 | 16.1 | -0.3 ± 0.4 | 0.00 | 1 | 97 |
| planned_forecast | 27.8 | -0.2 ± 0.7 | 2.1 | 327 | -1 ± 2 | 275 | -1 ± 4 | 861 | +2.6 ± 7.8 | 16.2 | -0.1 ± 0.4 | 0.00 | 1 | 90 |

## 400 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 12.0 |  | 2.8 | 259 |  | 236 |  | 1050 |  | 15.0 |  | 0.00 | 0 |  |
| drift | 12.5 | +0.5 ± 0.4 | 2.8 | 262 | +3 ± 3 | 239 | +2 ± 3 | 1044 | -5.5 ± 4.8 | 15.5 | +0.5 ± 0.3 | 0.10 | 26 | 62 |
| planned_reactive | 10.9 | -1.1 ± 0.5 | 3.0 | 253 | -6 ± 2 | 230 | -7 ± 3 | 1063 | +13.1 ± 5.6 | 15.9 | +0.8 ± 0.3 | 0.17 | 50 | 79 |
| planned_forecast | 11.2 | -0.9 ± 0.2 | 2.7 | 250 | -9 ± 2 | 228 | -8 ± 2 | 1060 | +10.2 ± 2.4 | 15.6 | +0.6 ± 0.2 | 0.15 | 44 | 82 |

### 400 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 12.5 |  | 2.8 | 262 |  | 239 |  | 1044 |  | 15.5 |  | 0.10 | 26 | 62 |
| planned_reactive | 10.9 | -1.6 ± 0.8 | 3.0 | 253 | -9 ± 4 | 230 | -9 ± 4 | 1063 | +18.6 ± 9.4 | 15.9 | +0.3 ± 0.1 | 0.17 | 50 | 79 |
| planned_forecast | 11.2 | -1.3 ± 0.5 | 2.7 | 250 | -12 ± 3 | 228 | -10 ± 3 | 1060 | +15.7 ± 5.9 | 15.6 | +0.1 ± 0.2 | 0.15 | 44 | 82 |

## 500 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 6.9 |  | 2.4 | 204 |  | 185 |  | 1110 |  | 10.5 |  | 0.00 | 0 |  |
| drift | 7.4 | +0.4 ± 0.5 | 2.5 | 215 | +11 ± 4 | 196 | +11 ± 4 | 1105 | -5.2 ± 5.9 | 12.2 | +1.7 ± 0.1 | 0.19 | 75 | 45 |
| planned_reactive | 3.2 | -3.7 ± 0.3 | 1.5 | 162 | -42 ± 6 | 142 | -43 ± 7 | 1155 | +44.7 ± 3.5 | 12.4 | +1.9 ± 0.2 | 0.50 | 246 | 57 |
| planned_forecast | 3.5 | -3.5 ± 0.3 | 1.5 | 166 | -37 ± 2 | 148 | -37 ± 3 | 1151 | +41.2 ± 3.3 | 11.8 | +1.3 ± 0.1 | 0.40 | 197 | 62 |

### 500 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 7.4 |  | 2.5 | 215 |  | 196 |  | 1105 |  | 12.2 |  | 0.19 | 75 | 45 |
| planned_reactive | 3.2 | -4.2 ± 0.6 | 1.5 | 162 | -53 ± 9 | 142 | -54 ± 8 | 1155 | +49.9 ± 7.0 | 12.4 | +0.2 ± 0.3 | 0.50 | 246 | 57 |
| planned_forecast | 3.5 | -3.9 ± 0.3 | 1.5 | 166 | -49 ± 5 | 148 | -48 ± 4 | 1151 | +46.4 ± 3.4 | 11.8 | -0.3 ± 0.3 | 0.40 | 197 | 62 |

## Move cap: 5 vs 10 minutes, 400 drivers (against `planned_forecast`, 10 min)

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 12.0 | +0.9 ± 0.2 | 2.8 | 259 | +9 ± 2 | 236 | +8 ± 2 | 1050 | -10.2 ± 2.4 | 15.0 | -0.6 ± 0.2 | 0.00 | 0 |  |
| planned_forecast | 11.2 |  | 2.7 | 250 |  | 228 |  | 1060 |  | 15.6 |  | 0.15 | 44 | 82 |
| planned_forecast_5min | 11.9 | +0.7 ± 0.4 | 2.8 | 256 | +6 ± 4 | 234 | +6 ± 3 | 1051 | -8.5 ± 4.9 | 15.2 | -0.4 ± 0.2 | 0.05 | 10 | 66 |

