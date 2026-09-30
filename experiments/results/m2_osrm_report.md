# M2 — real Manhattan demand, osrm travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2024-03-13_1700_3h_manhattan_f0.1.parquet`. Travel: osrm (TravelConfig(model='osrm', speed_mps=7.0, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=2.087996675020272)).
Real-world benchmark (Uber, request → driver on scene): mean 164s, p50 140s, p90 321s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 28.8 |  | 285 |  | 394 | 393 | 800 |  | 6.5 | 2.6 |
| batched_greedy@10s | 28.5 | -0.3 ± 0.7 | 288 | +3 ± 4 | 394 | 386 | 804 | +4 ± 8 | 6.6 | 5.3 |
| optimal@10s | 28.4 | -0.4 ± 0.5 | 289 | +5 ± 3 | 396 | 389 | 804 | +4 ± 6 | 6.3 | 5.1 |
| batched_greedy@10s+aware | 25.6 | -3.2 ± 0.5 | 341 | +56 ± 7 | 405 | 354 | 836 | +36 ± 5 | 7.6 | 22.8 |
| optimal@10s+aware | 25.9 | -2.9 ± 0.1 | 341 | +56 ± 7 | 406 | 357 | 833 | +33 ± 2 | 7.6 | 22.3 |
| batched_greedy@30s+aware | 25.0 | -3.8 ± 0.5 | 341 | +57 ± 6 | 395 | 333 | 842 | +42 ± 6 | 7.6 | 29.4 |
| optimal@30s+aware | 25.0 | -3.8 ± 0.5 | 344 | +59 ± 8 | 399 | 336 | 843 | +43 ± 6 | 7.4 | 29.2 |

## 350 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 17.8 |  | 271 |  | 327 | 326 | 923 |  | 11.4 | 2.0 |
| batched_greedy@10s | 17.7 | -0.2 ± 0.1 | 273 | +3 ± 3 | 328 | 323 | 925 | +2 ± 2 | 11.6 | 4.3 |
| optimal@10s | 17.6 | -0.3 ± 0.3 | 276 | +6 ± 3 | 331 | 326 | 926 | +3 ± 4 | 11.3 | 4.3 |
| batched_greedy@10s+aware | 16.5 | -1.3 ± 0.4 | 304 | +33 ± 5 | 345 | 322 | 938 | +15 ± 4 | 11.8 | 11.8 |
| optimal@10s+aware | 16.5 | -1.3 ± 0.3 | 303 | +32 ± 3 | 343 | 322 | 938 | +15 ± 4 | 11.7 | 11.4 |
| batched_greedy@30s+aware | 16.0 | -1.8 ± 0.1 | 307 | +37 ± 7 | 342 | 307 | 944 | +20 ± 2 | 12.2 | 18.9 |
| optimal@30s+aware | 15.8 | -2.0 ± 0.4 | 310 | +39 ± 3 | 346 | 312 | 946 | +22 ± 4 | 11.7 | 18.3 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 11.7 |  | 251 |  | 282 | 281 | 992 |  | 19.1 | 1.8 |
| batched_greedy@10s | 11.7 | -0.0 ± 0.5 | 254 | +3 ± 4 | 285 | 280 | 993 | +0 ± 6 | 19.2 | 4.1 |
| optimal@10s | 11.6 | -0.0 ± 0.6 | 254 | +3 ± 5 | 285 | 280 | 993 | +1 ± 7 | 19.3 | 4.1 |
| batched_greedy@10s+aware | 11.5 | -0.2 ± 0.5 | 266 | +16 ± 4 | 290 | 280 | 995 | +2 ± 6 | 19.8 | 7.6 |
| optimal@10s+aware | 11.5 | -0.2 ± 0.4 | 269 | +18 ± 6 | 294 | 282 | 994 | +2 ± 5 | 19.7 | 7.6 |
| batched_greedy@30s+aware | 11.3 | -0.4 ± 0.7 | 275 | +24 ± 5 | 297 | 273 | 996 | +4 ± 8 | 20.2 | 14.6 |
| optimal@30s+aware | 11.1 | -0.6 ± 0.3 | 277 | +26 ± 4 | 299 | 275 | 999 | +6 ± 4 | 19.8 | 14.5 |

## 450 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 8.5 |  | 232 |  | 252 | 251 | 1029 |  | 27.1 | 1.8 |
| batched_greedy@10s | 8.3 | -0.1 ± 0.3 | 236 | +4 ± 4 | 255 | 250 | 1030 | +1 ± 3 | 27.0 | 4.0 |
| optimal@10s | 8.1 | -0.3 ± 0.4 | 236 | +4 ± 3 | 255 | 250 | 1032 | +3 ± 4 | 26.9 | 4.0 |
| batched_greedy@10s+aware | 8.6 | +0.1 ± 0.5 | 243 | +11 ± 2 | 258 | 250 | 1027 | -2 ± 5 | 27.7 | 6.4 |
| optimal@10s+aware | 8.3 | -0.1 ± 0.6 | 243 | +11 ± 2 | 257 | 249 | 1030 | +2 ± 7 | 27.5 | 6.3 |
| batched_greedy@30s+aware | 8.3 | -0.1 ± 0.5 | 251 | +19 ± 2 | 265 | 245 | 1030 | +2 ± 6 | 27.7 | 12.9 |
| optimal@30s+aware | 8.3 | -0.2 ± 0.4 | 252 | +20 ± 2 | 266 | 246 | 1030 | +2 ± 4 | 27.7 | 12.9 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 6.9 |  | 217 |  | 232 | 231 | 1046 |  | 34.2 | 1.8 |
| batched_greedy@10s | 7.0 | +0.1 ± 0.4 | 221 | +4 ± 1 | 235 | 230 | 1045 | -1 ± 4 | 34.3 | 4.0 |
| optimal@10s | 7.0 | +0.0 ± 0.2 | 220 | +3 ± 2 | 235 | 230 | 1045 | -0 ± 3 | 34.3 | 3.9 |
| batched_greedy@10s+aware | 7.1 | +0.1 ± 0.5 | 225 | +8 ± 4 | 235 | 228 | 1044 | -1 ± 6 | 34.7 | 5.8 |
| optimal@10s+aware | 7.2 | +0.2 ± 0.6 | 226 | +9 ± 2 | 237 | 230 | 1043 | -3 ± 7 | 34.7 | 5.9 |
| batched_greedy@30s+aware | 7.1 | +0.1 ± 0.4 | 235 | +17 ± 2 | 245 | 226 | 1044 | -1 ± 5 | 34.8 | 12.4 |
| optimal@30s+aware | 6.8 | -0.2 ± 0.4 | 236 | +19 ± 2 | 245 | 227 | 1048 | +2 ± 5 | 34.6 | 12.3 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@10s | 8.2 | 9.9% | 5.1 |
| 350 | optimal@10s | 4.0 | 6.3% | 4.3 |
| 400 | optimal@10s | 2.5 | 4.2% | 4.1 |
| 450 | optimal@10s | 1.4 | 3.0% | 4.0 |
| 500 | optimal@10s | 1.1 | 2.4% | 3.9 |
| 300 | optimal@10s+aware | 3.9 | 4.6% | 22.3 |
| 350 | optimal@10s+aware | 5.6 | 6.3% | 11.4 |
| 400 | optimal@10s+aware | 4.7 | 5.4% | 7.6 |
| 450 | optimal@10s+aware | 3.4 | 4.9% | 6.3 |
| 500 | optimal@10s+aware | 2.4 | 4.4% | 5.9 |
| 300 | optimal@30s+aware | 37.3 | 32.3% | 29.2 |
| 350 | optimal@30s+aware | 46.0 | 41.0% | 18.3 |
| 400 | optimal@30s+aware | 36.2 | 36.4% | 14.5 |
| 450 | optimal@30s+aware | 32.0 | 34.9% | 12.9 |
| 500 | optimal@30s+aware | 24.4 | 29.6% | 12.3 |
