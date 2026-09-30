# M2 — real Manhattan demand, straight travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2024-03-13_1700_3h_manhattan_f0.1.parquet`. Travel: straight (TravelConfig(model='straight', speed_mps=3.7530456331156192, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=1.0)).
Real-world benchmark (Uber, request → driver on scene): mean 164s, p50 140s, p90 321s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 28.3 |  | 266 |  | 365 | 361 | 805 |  | 2.1 | 3.2 |
| batched_greedy@10s | 26.4 | -2.0 ± 0.6 | 283 | +17 ± 6 | 369 | 348 | 827 | +22 ± 7 | 2.0 | 9.0 |
| optimal@10s | 26.6 | -1.8 ± 0.4 | 280 | +14 ± 9 | 366 | 348 | 825 | +20 ± 5 | 1.9 | 8.6 |
| batched_greedy@10s+aware | 22.3 | -6.0 ± 0.6 | 323 | +57 ± 9 | 365 | 301 | 873 | +68 ± 7 | 1.8 | 25.3 |
| optimal@10s+aware | 22.2 | -6.1 ± 0.9 | 323 | +57 ± 6 | 365 | 302 | 874 | +69 ± 10 | 1.8 | 24.8 |
| batched_greedy@30s+aware | 22.0 | -6.3 ± 0.9 | 316 | +50 ± 6 | 350 | 279 | 876 | +71 ± 10 | 2.1 | 30.6 |
| optimal@30s+aware | 21.8 | -6.5 ± 1.1 | 320 | +54 ± 7 | 355 | 284 | 879 | +74 ± 12 | 1.8 | 30.5 |

## 350 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 14.6 |  | 237 |  | 276 | 276 | 959 |  | 6.1 | 1.8 |
| batched_greedy@10s | 14.6 | -0.1 ± 0.5 | 239 | +2 ± 4 | 276 | 271 | 960 | +1 ± 6 | 6.2 | 4.2 |
| optimal@10s | 14.6 | -0.1 ± 0.4 | 243 | +6 ± 7 | 281 | 275 | 960 | +1 ± 5 | 6.0 | 4.2 |
| batched_greedy@10s+aware | 12.5 | -2.2 ± 0.5 | 275 | +37 ± 6 | 300 | 277 | 983 | +24 ± 5 | 5.3 | 10.7 |
| optimal@10s+aware | 12.5 | -2.1 ± 0.4 | 278 | +41 ± 6 | 304 | 280 | 983 | +24 ± 4 | 5.1 | 10.9 |
| batched_greedy@30s+aware | 12.4 | -2.3 ± 0.3 | 272 | +35 ± 6 | 293 | 256 | 985 | +26 ± 4 | 6.1 | 17.9 |
| optimal@30s+aware | 12.2 | -2.5 ± 0.4 | 280 | +43 ± 7 | 302 | 266 | 987 | +28 ± 4 | 5.4 | 17.7 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 7.9 |  | 200 |  | 216 | 216 | 1035 |  | 14.4 | 1.6 |
| batched_greedy@10s | 7.8 | -0.0 ± 0.5 | 204 | +4 ± 4 | 220 | 215 | 1036 | +0 ± 5 | 14.6 | 3.8 |
| optimal@10s | 7.6 | -0.2 ± 0.4 | 204 | +4 ± 1 | 219 | 214 | 1038 | +2 ± 4 | 14.3 | 3.8 |
| batched_greedy@10s+aware | 7.3 | -0.6 ± 0.4 | 215 | +15 ± 3 | 225 | 215 | 1042 | +6 ± 5 | 14.6 | 6.2 |
| optimal@10s+aware | 7.0 | -0.9 ± 0.5 | 216 | +16 ± 4 | 227 | 217 | 1045 | +10 ± 5 | 14.2 | 5.9 |
| batched_greedy@30s+aware | 7.1 | -0.8 ± 0.3 | 225 | +25 ± 4 | 235 | 212 | 1044 | +8 ± 4 | 14.6 | 13.0 |
| optimal@30s+aware | 6.5 | -1.3 ± 0.6 | 227 | +27 ± 8 | 236 | 214 | 1050 | +15 ± 7 | 14.1 | 12.6 |

## 450 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 5.4 |  | 180 |  | 189 | 189 | 1063 |  | 23.0 | 1.5 |
| batched_greedy@10s | 5.3 | -0.0 ± 0.3 | 183 | +3 ± 4 | 192 | 187 | 1064 | +0 ± 3 | 23.2 | 3.7 |
| optimal@10s | 5.2 | -0.2 ± 0.3 | 183 | +3 ± 3 | 192 | 187 | 1065 | +2 ± 3 | 23.1 | 3.7 |
| batched_greedy@10s+aware | 5.0 | -0.3 ± 0.2 | 189 | +9 ± 2 | 195 | 188 | 1067 | +4 ± 2 | 23.2 | 5.0 |
| optimal@10s+aware | 4.8 | -0.5 ± 0.2 | 190 | +10 ± 4 | 196 | 188 | 1069 | +6 ± 2 | 23.0 | 4.9 |
| batched_greedy@30s+aware | 5.0 | -0.3 ± 0.2 | 199 | +19 ± 3 | 204 | 184 | 1067 | +4 ± 2 | 23.4 | 11.8 |
| optimal@30s+aware | 4.6 | -0.7 ± 0.3 | 199 | +19 ± 2 | 205 | 186 | 1072 | +8 ± 4 | 23.0 | 11.5 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 4.1 |  | 162 |  | 168 | 168 | 1078 |  | 30.6 | 1.4 |
| batched_greedy@10s | 4.1 | +0.0 ± 0.1 | 165 | +3 ± 3 | 171 | 166 | 1078 | -0 ± 1 | 30.8 | 3.6 |
| optimal@10s | 3.9 | -0.2 ± 0.1 | 165 | +3 ± 2 | 171 | 166 | 1080 | +2 ± 1 | 30.7 | 3.6 |
| batched_greedy@10s+aware | 3.9 | -0.1 ± 0.2 | 172 | +10 ± 3 | 176 | 169 | 1079 | +1 ± 2 | 30.7 | 4.5 |
| optimal@10s+aware | 3.7 | -0.3 ± 0.2 | 171 | +10 ± 2 | 175 | 169 | 1081 | +3 ± 3 | 30.6 | 4.5 |
| batched_greedy@30s+aware | 3.8 | -0.2 ± 0.3 | 180 | +19 ± 3 | 184 | 165 | 1081 | +3 ± 3 | 30.9 | 11.1 |
| optimal@30s+aware | 3.5 | -0.5 ± 0.2 | 179 | +17 ± 1 | 183 | 165 | 1084 | +6 ± 3 | 30.7 | 10.9 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@10s | 9.9 | 11.8% | 8.6 |
| 350 | optimal@10s | 6.9 | 9.0% | 4.2 |
| 400 | optimal@10s | 3.4 | 5.7% | 3.8 |
| 450 | optimal@10s | 2.0 | 4.1% | 3.7 |
| 500 | optimal@10s | 1.6 | 3.6% | 3.6 |
| 300 | optimal@10s+aware | 6.9 | 6.0% | 24.8 |
| 350 | optimal@10s+aware | 7.9 | 6.8% | 10.9 |
| 400 | optimal@10s+aware | 7.0 | 6.4% | 5.9 |
| 450 | optimal@10s+aware | 5.6 | 5.1% | 4.9 |
| 500 | optimal@10s+aware | 4.2 | 4.4% | 4.5 |
| 300 | optimal@30s+aware | 53.7 | 35.5% | 30.5 |
| 350 | optimal@30s+aware | 72.6 | 44.1% | 17.7 |
| 400 | optimal@30s+aware | 59.1 | 37.8% | 12.6 |
| 450 | optimal@30s+aware | 40.2 | 30.6% | 11.5 |
| 500 | optimal@30s+aware | 32.3 | 26.5% | 10.9 |
