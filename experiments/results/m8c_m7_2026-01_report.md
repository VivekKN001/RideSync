# M7: repositioning idle drivers (Manhattan TLC replay, 2026-01-14 17:00, 3 h)

Optimal @30 s, cancellation-aware, straight-line travel with per-trip noise (sigma 0.27); riders give up on late drivers (median tolerance 180 s). Every 300 s the policy may move drivers idle >= 120 s, at most 50% of the idle fleet, on drives <= 600 s. 6 seeds, mean ± 95% CI of paired differences (Student t).
`empty driving` = share of driver time driving without a rider (to pickups + repositioning).

## 300 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 14.7 |  | 3.1 | 277 |  | 255 |  | 844 |  | 17.2 |  | 0.00 | 0 |  |
| drift | 14.2 | -0.4 ± 0.3 | 3.0 | 267 | -10 ± 8 | 246 | -8 ± 8 | 848 | +4.3 ± 3.0 | 17.6 | +0.4 ± 0.3 | 0.14 | 31 | 70 |
| planned_reactive | 13.6 | -1.1 ± 0.7 | 2.9 | 269 | -8 ± 3 | 247 | -8 ± 3 | 855 | +10.8 ± 6.9 | 17.7 | +0.5 ± 0.2 | 0.15 | 34 | 84 |
| planned_forecast | 13.5 | -1.1 ± 0.5 | 3.0 | 268 | -9 ± 4 | 247 | -8 ± 4 | 855 | +11.2 ± 4.5 | 17.7 | +0.5 ± 0.4 | 0.14 | 32 | 84 |

### 300 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 14.2 |  | 3.0 | 267 |  | 246 |  | 848 |  | 17.6 |  | 0.14 | 31 | 70 |
| planned_reactive | 13.6 | -0.7 ± 0.7 | 2.9 | 269 | +1 ± 8 | 247 | +1 ± 6 | 855 | +6.5 ± 6.8 | 17.7 | +0.1 ± 0.3 | 0.15 | 34 | 84 |
| planned_forecast | 13.5 | -0.7 ± 0.4 | 3.0 | 268 | +1 ± 9 | 247 | +1 ± 9 | 855 | +6.9 ± 3.9 | 17.7 | +0.1 ± 0.4 | 0.14 | 32 | 84 |

## 400 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 6.1 |  | 1.9 | 193 |  | 173 |  | 929 |  | 10.3 |  | 0.00 | 0 |  |
| drift | 6.2 | +0.1 ± 0.4 | 2.0 | 194 | +1 ± 5 | 174 | +0 ± 4 | 928 | -0.6 ± 4.4 | 12.6 | +2.2 ± 0.2 | 0.33 | 118 | 47 |
| planned_reactive | 3.3 | -2.9 ± 0.6 | 1.1 | 152 | -42 ± 4 | 132 | -42 ± 5 | 957 | +28.3 ± 6.0 | 13.8 | +3.4 ± 0.3 | 0.71 | 302 | 54 |
| planned_forecast | 3.5 | -2.6 ± 0.7 | 1.3 | 153 | -41 ± 5 | 133 | -41 ± 4 | 954 | +25.6 ± 7.2 | 12.7 | +2.4 ± 0.3 | 0.55 | 242 | 56 |

### 400 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 6.2 |  | 2.0 | 194 |  | 174 |  | 928 |  | 12.6 |  | 0.33 | 118 | 47 |
| planned_reactive | 3.3 | -2.9 ± 0.2 | 1.1 | 152 | -43 ± 4 | 132 | -42 ± 4 | 957 | +28.9 ± 2.1 | 13.8 | +1.2 ± 0.2 | 0.71 | 302 | 54 |
| planned_forecast | 3.5 | -2.6 ± 0.4 | 1.3 | 153 | -42 ± 6 | 133 | -41 ± 6 | 954 | +26.2 ± 3.9 | 12.7 | +0.1 ± 0.3 | 0.55 | 242 | 56 |

## 500 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 4.0 |  | 1.5 | 161 |  | 141 |  | 950 |  | 7.0 |  | 0.00 | 0 |  |
| drift | 4.0 | -0.0 ± 0.2 | 1.4 | 169 | +9 ± 2 | 150 | +9 ± 1 | 950 | +0.1 ± 2.5 | 9.8 | +2.8 ± 0.1 | 0.35 | 165 | 37 |
| planned_reactive | 1.7 | -2.3 ± 0.3 | 0.7 | 117 | -44 ± 2 | 98 | -42 ± 2 | 972 | +22.8 ± 2.6 | 12.5 | +5.5 ± 0.2 | 0.88 | 512 | 34 |
| planned_forecast | 1.7 | -2.4 ± 0.3 | 0.6 | 116 | -45 ± 2 | 97 | -43 ± 3 | 973 | +23.3 ± 3.1 | 10.4 | +3.3 ± 0.2 | 0.60 | 363 | 36 |

### 500 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 4.0 |  | 1.4 | 169 |  | 150 |  | 950 |  | 9.8 |  | 0.35 | 165 | 37 |
| planned_reactive | 1.7 | -2.3 ± 0.2 | 0.7 | 117 | -53 ± 3 | 98 | -51 ± 2 | 972 | +22.7 ± 2.4 | 12.5 | +2.7 ± 0.2 | 0.88 | 512 | 34 |
| planned_forecast | 1.7 | -2.4 ± 0.4 | 0.6 | 116 | -54 ± 3 | 97 | -52 ± 3 | 973 | +23.3 ± 3.6 | 10.4 | +0.5 ± 0.2 | 0.60 | 363 | 36 |

## Move cap: 5 vs 10 minutes, 400 drivers (against `planned_forecast`, 10 min)

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 6.1 | +2.6 ± 0.7 | 1.9 | 193 | +41 ± 5 | 173 | +41 ± 4 | 929 | -25.6 ± 7.2 | 10.3 | -2.4 ± 0.3 | 0.00 | 0 |  |
| planned_forecast | 3.5 |  | 1.3 | 153 |  | 133 |  | 954 |  | 12.7 |  | 0.55 | 242 | 56 |
| planned_forecast_5min | 5.6 | +2.1 ± 0.3 | 1.7 | 186 | +34 ± 6 | 166 | +33 ± 6 | 933 | -20.7 ± 2.9 | 10.8 | -1.9 ± 0.2 | 0.18 | 48 | 47 |

