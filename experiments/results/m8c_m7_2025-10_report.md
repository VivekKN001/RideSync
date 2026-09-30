# M7: repositioning idle drivers (Manhattan TLC replay, 2025-10-15 17:00, 3 h)

Optimal @30 s, cancellation-aware, straight-line travel with per-trip noise (sigma 0.27); riders give up on late drivers (median tolerance 180 s). Every 300 s the policy may move drivers idle >= 120 s, at most 50% of the idle fleet, on drives <= 600 s. 6 seeds, mean ± 95% CI of paired differences (Student t).
`empty driving` = share of driver time driving without a rider (to pickups + repositioning).

## 300 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 33.5 |  | 2.2 | 335 |  | 276 |  | 798 |  | 15.0 |  | 0.00 | 0 |  |
| drift | 34.0 | +0.5 ± 0.7 | 2.1 | 335 | -1 ± 4 | 275 | -1 ± 2 | 792 | -6.0 ± 8.4 | 15.0 | -0.1 ± 0.3 | 0.01 | 1 | 93 |
| planned_reactive | 33.9 | +0.3 ± 0.9 | 2.2 | 334 | -1 ± 5 | 275 | -1 ± 4 | 794 | -4.1 ± 10.6 | 15.0 | +0.0 ± 0.4 | 0.00 | 1 | 100 |
| planned_forecast | 33.7 | +0.1 ± 0.5 | 2.1 | 336 | +0 ± 3 | 276 | -0 ± 4 | 797 | -1.8 ± 6.5 | 15.0 | -0.0 ± 0.3 | 0.01 | 1 | 100 |

### 300 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 34.0 |  | 2.1 | 335 |  | 275 |  | 792 |  | 15.0 |  | 0.01 | 1 | 93 |
| planned_reactive | 33.9 | -0.2 ± 0.9 | 2.2 | 334 | -1 ± 4 | 275 | -0 ± 3 | 794 | +1.9 ± 10.6 | 15.0 | +0.1 ± 0.4 | 0.00 | 1 | 100 |
| planned_forecast | 33.7 | -0.3 ± 0.6 | 2.1 | 336 | +1 ± 3 | 276 | +1 ± 4 | 797 | +4.2 ± 7.5 | 15.0 | +0.1 ± 0.3 | 0.01 | 1 | 100 |

## 400 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 17.3 |  | 3.3 | 288 |  | 262 |  | 994 |  | 15.4 |  | 0.00 | 0 |  |
| drift | 16.8 | -0.5 ± 0.3 | 3.0 | 288 | +0 ± 6 | 262 | +0 ± 4 | 999 | +5.6 ± 4.0 | 15.7 | +0.3 ± 0.4 | 0.07 | 17 | 77 |
| planned_reactive | 16.6 | -0.7 ± 0.2 | 3.0 | 286 | -3 ± 7 | 261 | -1 ± 5 | 1002 | +8.5 ± 2.9 | 15.8 | +0.4 ± 0.2 | 0.08 | 21 | 84 |
| planned_forecast | 16.7 | -0.6 ± 0.4 | 3.2 | 293 | +4 ± 6 | 265 | +3 ± 4 | 1000 | +6.7 ± 5.4 | 15.9 | +0.5 ± 0.2 | 0.07 | 19 | 86 |

### 400 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 16.8 |  | 3.0 | 288 |  | 262 |  | 999 |  | 15.7 |  | 0.07 | 17 | 77 |
| planned_reactive | 16.6 | -0.2 ± 0.4 | 3.0 | 286 | -3 ± 7 | 261 | -1 ± 5 | 1002 | +2.9 ± 5.3 | 15.8 | +0.1 ± 0.3 | 0.08 | 21 | 84 |
| planned_forecast | 16.7 | -0.1 ± 0.4 | 3.2 | 293 | +4 ± 3 | 265 | +3 ± 4 | 1000 | +1.1 ± 4.5 | 15.9 | +0.2 ± 0.3 | 0.07 | 19 | 86 |

## 500 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 8.4 |  | 2.3 | 217 |  | 197 |  | 1099 |  | 11.0 |  | 0.00 | 0 |  |
| drift | 7.6 | -0.8 ± 0.3 | 2.2 | 211 | -6 ± 2 | 191 | -6 ± 4 | 1109 | +9.6 ± 4.0 | 12.6 | +1.6 ± 0.2 | 0.27 | 107 | 53 |
| planned_reactive | 6.2 | -2.3 ± 0.5 | 1.9 | 189 | -28 ± 4 | 168 | -29 ± 4 | 1127 | +27.2 ± 5.7 | 12.3 | +1.3 ± 0.2 | 0.36 | 149 | 66 |
| planned_forecast | 6.5 | -1.9 ± 0.4 | 2.0 | 193 | -24 ± 1 | 172 | -25 ± 3 | 1123 | +23.2 ± 4.4 | 11.8 | +0.8 ± 0.2 | 0.28 | 113 | 69 |

### 500 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 7.6 |  | 2.2 | 211 |  | 191 |  | 1109 |  | 12.6 |  | 0.27 | 107 | 53 |
| planned_reactive | 6.2 | -1.5 ± 0.5 | 1.9 | 189 | -22 ± 4 | 168 | -23 ± 5 | 1127 | +17.6 ± 5.9 | 12.3 | -0.3 ± 0.2 | 0.36 | 149 | 66 |
| planned_forecast | 6.5 | -1.1 ± 0.5 | 2.0 | 193 | -19 ± 2 | 172 | -19 ± 2 | 1123 | +13.6 ± 6.2 | 11.8 | -0.7 ± 0.1 | 0.28 | 113 | 69 |

## Move cap: 5 vs 10 minutes, 400 drivers (against `planned_forecast`, 10 min)

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 17.3 | +0.6 ± 0.4 | 3.3 | 288 | -4 ± 6 | 262 | -3 ± 4 | 994 | -6.7 ± 5.4 | 15.4 | -0.5 ± 0.2 | 0.00 | 0 |  |
| planned_forecast | 16.7 |  | 3.2 | 293 |  | 265 |  | 1000 |  | 15.9 |  | 0.07 | 19 | 86 |
| planned_forecast_5min | 16.8 | +0.1 ± 0.8 | 3.1 | 291 | -2 ± 3 | 263 | -2 ± 4 | 999 | -1.6 ± 9.2 | 15.4 | -0.5 ± 0.2 | 0.02 | 3 | 75 |

