# M8C — real Manhattan demand, straight travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2026-04-15_1700_3h_manhattan_f0.1.parquet`. Travel: straight (TravelConfig(model='straight', speed_mps=3.4324343591702036, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=1.0, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 213s, p50 171s, p90 431s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 29.5 |  | 266 |  | 369 | 364 | 728 |  | 3.5 | 3.5 |
| batched_greedy@10s | 28.3 | -1.2 ± 0.4 | 278 | +12 ± 6 | 369 | 352 | 740 | +12 ± 4 | 3.1 | 8.1 |
| optimal@10s | 28.5 | -1.0 ± 0.4 | 278 | +12 ± 7 | 372 | 357 | 738 | +10 ± 4 | 3.2 | 7.4 |
| batched_greedy@10s+aware | 24.2 | -5.3 ± 0.5 | 326 | +60 ± 4 | 371 | 309 | 783 | +55 ± 6 | 3.0 | 23.5 |
| optimal@10s+aware | 24.1 | -5.4 ± 0.6 | 324 | +58 ± 3 | 369 | 308 | 784 | +56 ± 7 | 3.0 | 23.2 |
| batched_greedy@30s+aware | 23.8 | -5.8 ± 0.9 | 321 | +55 ± 4 | 357 | 288 | 787 | +59 ± 9 | 3.5 | 28.8 |
| optimal@30s+aware | 23.6 | -5.9 ± 0.6 | 321 | +55 ± 4 | 359 | 290 | 789 | +61 ± 6 | 3.2 | 28.2 |

## 350 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 17.8 |  | 246 |  | 295 | 294 | 849 |  | 7.6 | 2.2 |
| batched_greedy@10s | 17.5 | -0.3 ± 0.4 | 247 | +2 ± 7 | 295 | 288 | 852 | +3 ± 4 | 7.7 | 4.3 |
| optimal@10s | 17.3 | -0.5 ± 0.7 | 248 | +3 ± 4 | 296 | 289 | 854 | +6 ± 7 | 7.5 | 4.2 |
| batched_greedy@10s+aware | 15.6 | -2.2 ± 0.4 | 284 | +39 ± 5 | 314 | 285 | 871 | +23 ± 4 | 7.3 | 12.1 |
| optimal@10s+aware | 15.6 | -2.2 ± 0.4 | 285 | +39 ± 7 | 315 | 285 | 871 | +23 ± 4 | 7.3 | 12.4 |
| batched_greedy@30s+aware | 15.2 | -2.7 ± 0.3 | 290 | +44 ± 5 | 313 | 270 | 876 | +28 ± 3 | 7.7 | 19.3 |
| optimal@30s+aware | 15.0 | -2.9 ± 0.3 | 291 | +45 ± 6 | 316 | 274 | 878 | +30 ± 3 | 7.2 | 18.6 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 10.5 |  | 218 |  | 241 | 240 | 924 |  | 14.9 | 1.8 |
| batched_greedy@10s | 10.5 | -0.1 ± 0.6 | 218 | +0 ± 2 | 241 | 235 | 925 | +1 ± 6 | 15.1 | 3.8 |
| optimal@10s | 10.4 | -0.1 ± 0.3 | 220 | +3 ± 2 | 243 | 238 | 925 | +1 ± 3 | 15.1 | 3.7 |
| batched_greedy@10s+aware | 9.5 | -1.1 ± 0.6 | 238 | +20 ± 4 | 253 | 240 | 935 | +11 ± 6 | 14.7 | 7.0 |
| optimal@10s+aware | 9.3 | -1.2 ± 0.5 | 238 | +21 ± 4 | 253 | 240 | 936 | +12 ± 5 | 14.4 | 6.9 |
| batched_greedy@30s+aware | 9.6 | -0.9 ± 0.5 | 245 | +28 ± 3 | 259 | 232 | 933 | +9 ± 5 | 15.2 | 13.4 |
| optimal@30s+aware | 9.1 | -1.4 ± 0.5 | 247 | +29 ± 4 | 260 | 235 | 938 | +14 ± 5 | 14.3 | 13.1 |

## 450 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 7.2 |  | 197 |  | 210 | 209 | 959 |  | 22.8 | 1.7 |
| batched_greedy@10s | 7.2 | +0.0 ± 0.4 | 198 | +2 ± 3 | 212 | 207 | 958 | -0 ± 4 | 23.0 | 3.7 |
| optimal@10s | 7.1 | -0.1 ± 0.4 | 198 | +1 ± 2 | 211 | 206 | 960 | +1 ± 4 | 23.0 | 3.6 |
| batched_greedy@10s+aware | 6.6 | -0.6 ± 0.5 | 208 | +12 ± 1 | 217 | 207 | 965 | +7 ± 5 | 22.6 | 5.4 |
| optimal@10s+aware | 6.4 | -0.8 ± 0.5 | 209 | +12 ± 3 | 217 | 208 | 967 | +8 ± 5 | 22.5 | 5.4 |
| batched_greedy@30s+aware | 6.5 | -0.7 ± 0.6 | 216 | +20 ± 4 | 223 | 203 | 965 | +7 ± 6 | 23.0 | 11.5 |
| optimal@30s+aware | 6.2 | -1.0 ± 0.4 | 219 | +22 ± 5 | 226 | 205 | 969 | +11 ± 4 | 22.5 | 11.4 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 5.4 |  | 178 |  | 186 | 186 | 977 |  | 30.2 | 1.6 |
| batched_greedy@10s | 5.4 | -0.0 ± 0.1 | 182 | +4 ± 3 | 191 | 186 | 978 | +0 ± 1 | 30.2 | 3.6 |
| optimal@10s | 5.3 | -0.1 ± 0.3 | 181 | +3 ± 3 | 189 | 184 | 978 | +1 ± 3 | 30.2 | 3.6 |
| batched_greedy@10s+aware | 5.0 | -0.4 ± 0.3 | 189 | +11 ± 3 | 194 | 186 | 981 | +4 ± 3 | 30.2 | 4.8 |
| optimal@10s+aware | 5.0 | -0.4 ± 0.4 | 188 | +10 ± 2 | 193 | 185 | 982 | +4 ± 4 | 30.1 | 4.8 |
| batched_greedy@30s+aware | 5.1 | -0.3 ± 0.3 | 197 | +19 ± 4 | 201 | 182 | 980 | +3 ± 3 | 30.3 | 10.9 |
| optimal@30s+aware | 4.8 | -0.6 ± 0.4 | 197 | +19 ± 2 | 201 | 182 | 984 | +6 ± 4 | 30.2 | 10.7 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@10s | 6.6 | 8.5% | 7.4 |
| 350 | optimal@10s | 5.2 | 6.7% | 4.2 |
| 400 | optimal@10s | 3.2 | 4.8% | 3.7 |
| 450 | optimal@10s | 2.3 | 4.1% | 3.6 |
| 500 | optimal@10s | 1.7 | 3.2% | 3.6 |
| 300 | optimal@10s+aware | 4.8 | 4.0% | 23.2 |
| 350 | optimal@10s+aware | 5.8 | 5.0% | 12.4 |
| 400 | optimal@10s+aware | 5.0 | 4.6% | 6.9 |
| 450 | optimal@10s+aware | 4.1 | 4.1% | 5.4 |
| 500 | optimal@10s+aware | 2.8 | 3.6% | 4.8 |
| 300 | optimal@30s+aware | 42.6 | 29.0% | 28.2 |
| 350 | optimal@30s+aware | 51.2 | 33.7% | 18.6 |
| 400 | optimal@30s+aware | 46.6 | 32.3% | 13.1 |
| 450 | optimal@30s+aware | 35.3 | 26.7% | 11.4 |
| 500 | optimal@30s+aware | 25.5 | 23.3% | 10.7 |
