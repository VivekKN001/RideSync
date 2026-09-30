# M8C — real Manhattan demand, straight travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2025-10-15_1700_3h_manhattan_f0.1.parquet`. Travel: straight (TravelConfig(model='straight', speed_mps=3.4383094245627905, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=1.0, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 176s, p50 149s, p90 347s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 39.1 |  | 275 |  | 431 | 417 | 732 |  | 1.2 | 7.1 |
| batched_greedy@10s | 35.0 | -4.0 ± 0.7 | 316 | +40 ± 9 | 419 | 356 | 780 | +48 ± 8 | 0.9 | 25.5 |
| optimal@10s | 35.8 | -3.3 ± 0.7 | 308 | +33 ± 9 | 423 | 372 | 771 | +40 ± 9 | 0.8 | 21.3 |
| batched_greedy@10s+aware | 32.2 | -6.9 ± 0.9 | 338 | +63 ± 8 | 391 | 297 | 815 | +83 ± 10 | 1.4 | 40.1 |
| optimal@10s+aware | 32.0 | -7.1 ± 0.8 | 340 | +65 ± 7 | 394 | 300 | 817 | +85 ± 9 | 1.3 | 39.9 |
| batched_greedy@30s+aware | 31.7 | -7.4 ± 0.9 | 333 | +57 ± 6 | 377 | 279 | 820 | +88 ± 11 | 1.5 | 44.5 |
| optimal@30s+aware | 31.6 | -7.5 ± 1.0 | 334 | +59 ± 7 | 380 | 280 | 821 | +89 ± 12 | 1.3 | 44.7 |

## 350 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 27.5 |  | 264 |  | 357 | 352 | 870 |  | 2.8 | 3.6 |
| batched_greedy@10s | 27.0 | -0.6 ± 0.6 | 275 | +11 ± 4 | 362 | 347 | 877 | +7 ± 7 | 2.7 | 8.1 |
| optimal@10s | 27.1 | -0.5 ± 0.6 | 280 | +16 ± 6 | 370 | 356 | 876 | +5 ± 7 | 2.5 | 7.9 |
| batched_greedy@10s+aware | 22.8 | -4.7 ± 0.3 | 321 | +57 ± 6 | 364 | 304 | 927 | +57 ± 4 | 2.6 | 26.0 |
| optimal@10s+aware | 22.8 | -4.7 ± 0.5 | 325 | +60 ± 5 | 368 | 308 | 926 | +56 ± 6 | 2.5 | 26.2 |
| batched_greedy@30s+aware | 22.5 | -5.1 ± 0.4 | 316 | +52 ± 6 | 350 | 280 | 931 | +61 ± 4 | 3.2 | 32.6 |
| optimal@30s+aware | 22.5 | -5.0 ± 0.4 | 320 | +56 ± 5 | 356 | 287 | 930 | +60 ± 5 | 2.8 | 32.5 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 17.3 |  | 242 |  | 290 | 288 | 993 |  | 6.8 | 2.3 |
| batched_greedy@10s | 16.8 | -0.5 ± 0.3 | 246 | +5 ± 6 | 292 | 285 | 999 | +6 ± 4 | 6.8 | 4.7 |
| optimal@10s | 17.0 | -0.3 ± 0.3 | 250 | +8 ± 2 | 296 | 289 | 997 | +4 ± 4 | 6.5 | 4.9 |
| batched_greedy@10s+aware | 15.2 | -2.2 ± 0.3 | 287 | +45 ± 4 | 316 | 283 | 1019 | +26 ± 4 | 6.4 | 15.3 |
| optimal@10s+aware | 15.1 | -2.2 ± 0.6 | 285 | +43 ± 5 | 315 | 283 | 1019 | +26 ± 8 | 6.2 | 14.5 |
| batched_greedy@30s+aware | 14.8 | -2.5 ± 0.8 | 285 | +43 ± 5 | 308 | 263 | 1023 | +30 ± 10 | 6.9 | 22.5 |
| optimal@30s+aware | 14.6 | -2.8 ± 0.7 | 288 | +46 ± 6 | 312 | 269 | 1026 | +33 ± 8 | 6.3 | 21.9 |

## 450 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 10.9 |  | 218 |  | 243 | 242 | 1070 |  | 13.1 | 1.8 |
| batched_greedy@10s | 10.8 | -0.0 ± 0.5 | 220 | +3 ± 4 | 244 | 238 | 1071 | +1 ± 6 | 13.2 | 4.2 |
| optimal@10s | 11.0 | +0.1 ± 0.3 | 223 | +5 ± 2 | 248 | 242 | 1069 | -1 ± 4 | 13.3 | 4.2 |
| batched_greedy@10s+aware | 9.8 | -1.1 ± 0.2 | 243 | +25 ± 4 | 259 | 242 | 1084 | +13 ± 3 | 12.8 | 9.0 |
| optimal@10s+aware | 10.0 | -0.9 ± 0.3 | 242 | +25 ± 5 | 259 | 242 | 1081 | +11 ± 3 | 12.9 | 8.9 |
| batched_greedy@30s+aware | 9.9 | -0.9 ± 0.5 | 248 | +30 ± 4 | 261 | 231 | 1082 | +11 ± 6 | 13.5 | 16.8 |
| optimal@30s+aware | 9.5 | -1.4 ± 0.5 | 251 | +34 ± 4 | 265 | 236 | 1087 | +17 ± 5 | 12.7 | 16.3 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 7.3 |  | 193 |  | 207 | 206 | 1113 |  | 20.1 | 1.6 |
| batched_greedy@10s | 7.3 | +0.0 ± 0.2 | 197 | +4 ± 3 | 211 | 205 | 1113 | -0 ± 3 | 20.3 | 4.0 |
| optimal@10s | 7.2 | -0.1 ± 0.2 | 197 | +4 ± 1 | 210 | 205 | 1115 | +1 ± 3 | 20.2 | 4.0 |
| batched_greedy@10s+aware | 6.6 | -0.7 ± 0.3 | 209 | +16 ± 3 | 218 | 207 | 1122 | +8 ± 3 | 20.0 | 6.4 |
| optimal@10s+aware | 6.6 | -0.7 ± 0.3 | 208 | +16 ± 4 | 217 | 207 | 1122 | +8 ± 4 | 20.0 | 6.3 |
| batched_greedy@30s+aware | 6.8 | -0.4 ± 0.2 | 217 | +24 ± 3 | 224 | 202 | 1119 | +5 ± 3 | 20.4 | 13.8 |
| optimal@30s+aware | 6.2 | -1.1 ± 0.3 | 220 | +27 ± 2 | 228 | 205 | 1127 | +13 ± 3 | 19.7 | 13.6 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@10s | 9.6 | 11.0% | 21.3 |
| 350 | optimal@10s | 11.2 | 12.5% | 7.9 |
| 400 | optimal@10s | 6.4 | 8.6% | 4.9 |
| 450 | optimal@10s | 4.0 | 6.0% | 4.2 |
| 500 | optimal@10s | 2.6 | 4.3% | 4.0 |
| 300 | optimal@10s+aware | 4.1 | 3.8% | 39.9 |
| 350 | optimal@10s+aware | 7.3 | 5.7% | 26.2 |
| 400 | optimal@10s+aware | 7.8 | 6.9% | 14.5 |
| 450 | optimal@10s+aware | 6.2 | 5.8% | 8.9 |
| 500 | optimal@10s+aware | 4.3 | 4.7% | 6.3 |
| 300 | optimal@30s+aware | 38.3 | 27.9% | 44.7 |
| 350 | optimal@30s+aware | 58.0 | 36.2% | 32.5 |
| 400 | optimal@30s+aware | 68.2 | 41.6% | 21.9 |
| 450 | optimal@30s+aware | 61.7 | 41.7% | 16.3 |
| 500 | optimal@30s+aware | 47.6 | 34.9% | 13.6 |
