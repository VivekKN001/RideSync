# M7: repositioning idle drivers (Manhattan TLC replay, 2026-07-15 07:00, 3 h)

Optimal @30 s, cancellation-aware, straight-line travel with per-trip noise (sigma 0.27); riders give up on late drivers (median tolerance 180 s). Every 300 s the policy may move drivers idle >= 120 s, at most 50% of the idle fleet, on drives <= 600 s. 6 seeds, mean ± 95% CI of paired differences (Student t).
`empty driving` = share of driver time driving without a rider (to pickups + repositioning).

## 300 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 32.1 |  | 2.7 | 299 |  | 264 |  | 711 |  | 15.4 |  | 0.00 | 0 |  |
| drift | 31.8 | -0.3 ± 0.5 | 2.9 | 299 | +0 ± 3 | 266 | +2 ± 3 | 713 | +2.7 ± 4.9 | 16.3 | +0.9 ± 0.3 | 0.12 | 26 | 63 |
| planned_reactive | 30.2 | -1.9 ± 0.6 | 2.6 | 293 | -6 ± 5 | 258 | -6 ± 3 | 731 | +19.8 ± 6.7 | 16.7 | +1.3 ± 0.4 | 0.21 | 48 | 75 |
| planned_forecast | 30.4 | -1.6 ± 0.6 | 2.6 | 295 | -3 ± 5 | 259 | -5 ± 5 | 728 | +17.1 ± 6.3 | 16.4 | +1.0 ± 0.3 | 0.19 | 43 | 79 |

### 300 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 31.8 |  | 2.9 | 299 |  | 266 |  | 713 |  | 16.3 |  | 0.12 | 26 | 63 |
| planned_reactive | 30.2 | -1.6 ± 0.6 | 2.6 | 293 | -6 ± 4 | 258 | -8 ± 3 | 731 | +17.1 ± 6.3 | 16.7 | +0.5 ± 0.2 | 0.21 | 48 | 75 |
| planned_forecast | 30.4 | -1.4 ± 0.9 | 2.6 | 295 | -4 ± 3 | 259 | -7 ± 4 | 728 | +14.4 ± 9.5 | 16.4 | +0.1 ± 0.2 | 0.19 | 43 | 79 |

## 400 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 25.4 |  | 2.6 | 263 |  | 224 |  | 781 |  | 11.3 |  | 0.00 | 0 |  |
| drift | 25.3 | -0.1 ± 0.6 | 2.6 | 267 | +5 ± 5 | 229 | +6 ± 4 | 782 | +0.9 ± 6.8 | 13.5 | +2.2 ± 0.2 | 0.28 | 94 | 42 |
| planned_reactive | 19.5 | -5.9 ± 0.5 | 2.1 | 230 | -33 ± 5 | 190 | -33 ± 4 | 843 | +61.9 ± 5.2 | 14.4 | +3.1 ± 0.3 | 0.53 | 188 | 61 |
| planned_forecast | 19.7 | -5.6 ± 0.5 | 2.2 | 232 | -30 ± 5 | 194 | -30 ± 5 | 840 | +59.0 ± 4.7 | 14.0 | +2.7 ± 0.4 | 0.47 | 160 | 69 |

### 400 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 25.3 |  | 2.6 | 267 |  | 229 |  | 782 |  | 13.5 |  | 0.28 | 94 | 42 |
| planned_reactive | 19.5 | -5.8 ± 0.5 | 2.1 | 230 | -37 ± 6 | 190 | -39 ± 5 | 843 | +61.0 ± 4.8 | 14.4 | +0.9 ± 0.2 | 0.53 | 188 | 61 |
| planned_forecast | 19.7 | -5.6 ± 0.3 | 2.2 | 232 | -35 ± 6 | 194 | -36 ± 4 | 840 | +58.1 ± 3.4 | 14.0 | +0.5 ± 0.2 | 0.47 | 160 | 69 |

## 500 drivers: against `none`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 22.2 |  | 2.7 | 247 |  | 207 |  | 814 |  | 8.9 |  | 0.00 | 0 |  |
| drift | 22.3 | +0.1 ± 1.2 | 2.7 | 255 | +7 ± 3 | 218 | +10 ± 4 | 813 | -1.1 ± 12.8 | 12.1 | +3.1 ± 0.3 | 0.36 | 166 | 32 |
| planned_reactive | 13.7 | -8.5 ± 1.4 | 1.6 | 195 | -53 ± 7 | 158 | -49 ± 7 | 903 | +89.5 ± 14.8 | 13.3 | +4.3 ± 0.3 | 0.67 | 337 | 46 |
| planned_forecast | 15.0 | -7.2 ± 1.3 | 1.8 | 199 | -48 ± 7 | 162 | -45 ± 6 | 890 | +75.8 ± 13.1 | 12.1 | +3.2 ± 0.3 | 0.52 | 263 | 51 |

### 500 drivers: against `drift`

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drift | 22.3 |  | 2.7 | 255 |  | 218 |  | 813 |  | 12.1 |  | 0.36 | 166 | 32 |
| planned_reactive | 13.7 | -8.7 ± 0.7 | 1.6 | 195 | -60 ± 9 | 158 | -59 ± 9 | 903 | +90.6 ± 7.0 | 13.3 | +1.2 ± 0.6 | 0.67 | 337 | 46 |
| planned_forecast | 15.0 | -7.4 ± 0.5 | 1.8 | 199 | -55 ± 9 | 162 | -56 ± 9 | 890 | +76.9 ± 5.6 | 12.1 | +0.0 ± 0.5 | 0.52 | 263 | 51 |

## Move cap: 5 vs 10 minutes, 400 drivers (against `planned_forecast`, 10 min)

| arm | cancel % | Δ cancel pp | late cancel % | wait_all s | Δ wait_all s | pickup s | Δ pickup s | trips/h | Δ trips/h | empty driving % | Δ empty pp | moves/driver-h | reposition km/h | moves cut by a dispatch % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 25.4 | +5.6 ± 0.5 | 2.6 | 263 | +30 ± 5 | 224 | +30 ± 5 | 781 | -59.0 ± 4.7 | 11.3 | -2.7 ± 0.4 | 0.00 | 0 |  |
| planned_forecast | 19.7 |  | 2.2 | 232 |  | 194 |  | 840 |  | 14.0 |  | 0.47 | 160 | 69 |
| planned_forecast_5min | 24.6 | +4.9 ± 0.4 | 2.7 | 258 | +26 ± 5 | 217 | +23 ± 5 | 789 | -51.5 ± 4.1 | 11.8 | -2.2 ± 0.4 | 0.12 | 29 | 50 |

