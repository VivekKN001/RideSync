# M8B — real Manhattan demand, straight travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2026-07-15_1700_3h_manhattan_f0.1.parquet`. Travel: straight (TravelConfig(model='straight', speed_mps=3.4608154282234755, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=1.0, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 309s, p50 231s, p90 678s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 33.5 |  | 267 |  | 389 | 380 | 751 |  | 6.7 | 5.2 |
| batched_greedy@10s | 31.2 | -2.4 ± 0.6 | 286 | +19 ± 6 | 381 | 350 | 778 | +27 ± 6 | 6.5 | 14.4 |
| optimal@10s | 31.0 | -2.6 ± 0.5 | 291 | +24 ± 5 | 385 | 352 | 780 | +29 ± 6 | 6.3 | 15.2 |
| batched_greedy@10s+aware | 26.6 | -6.9 ± 0.5 | 322 | +55 ± 4 | 364 | 292 | 829 | +78 ± 6 | 6.7 | 30.9 |
| optimal@10s+aware | 26.7 | -6.8 ± 0.3 | 322 | +55 ± 5 | 365 | 294 | 828 | +77 ± 4 | 6.6 | 30.2 |
| batched_greedy@30s+aware | 26.3 | -7.2 ± 0.5 | 316 | +49 ± 4 | 350 | 272 | 833 | +82 ± 6 | 6.9 | 35.2 |
| optimal@30s+aware | 26.3 | -7.3 ± 0.6 | 320 | +53 ± 5 | 355 | 275 | 833 | +82 ± 6 | 6.7 | 35.6 |

## 350 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 21.0 |  | 248 |  | 310 | 309 | 892 |  | 9.2 | 2.5 |
| batched_greedy@10s | 20.4 | -0.6 ± 0.5 | 254 | +6 ± 3 | 313 | 305 | 899 | +7 ± 5 | 9.2 | 5.4 |
| optimal@10s | 20.7 | -0.4 ± 0.6 | 259 | +11 ± 5 | 320 | 311 | 896 | +4 ± 6 | 9.0 | 5.5 |
| batched_greedy@10s+aware | 17.2 | -3.9 ± 0.4 | 290 | +42 ± 3 | 320 | 284 | 936 | +44 ± 4 | 9.0 | 16.7 |
| optimal@10s+aware | 17.4 | -3.6 ± 0.5 | 295 | +47 ± 6 | 326 | 288 | 933 | +41 ± 6 | 8.9 | 17.3 |
| batched_greedy@30s+aware | 16.7 | -4.3 ± 0.3 | 289 | +41 ± 5 | 313 | 265 | 941 | +49 ± 4 | 9.5 | 23.1 |
| optimal@30s+aware | 16.8 | -4.2 ± 0.4 | 296 | +48 ± 2 | 322 | 273 | 939 | +47 ± 5 | 9.1 | 23.5 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 11.3 |  | 218 |  | 245 | 244 | 1002 |  | 14.3 | 1.9 |
| batched_greedy@10s | 11.5 | +0.2 ± 0.2 | 221 | +3 ± 2 | 247 | 242 | 1000 | -2 ± 2 | 14.5 | 4.2 |
| optimal@10s | 11.2 | -0.1 ± 0.2 | 226 | +7 ± 3 | 252 | 246 | 1003 | +1 ± 2 | 14.0 | 4.2 |
| batched_greedy@10s+aware | 9.8 | -1.5 ± 0.2 | 240 | +21 ± 4 | 254 | 238 | 1018 | +17 ± 2 | 14.2 | 8.9 |
| optimal@10s+aware | 9.8 | -1.5 ± 0.2 | 244 | +26 ± 3 | 259 | 243 | 1019 | +17 ± 2 | 13.8 | 9.0 |
| batched_greedy@30s+aware | 9.8 | -1.5 ± 0.3 | 244 | +25 ± 3 | 256 | 227 | 1019 | +17 ± 3 | 14.9 | 15.7 |
| optimal@30s+aware | 9.5 | -1.8 ± 0.3 | 249 | +31 ± 5 | 262 | 234 | 1022 | +21 ± 3 | 14.1 | 15.4 |

## 450 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 7.0 |  | 190 |  | 203 | 203 | 1051 |  | 21.9 | 1.6 |
| batched_greedy@10s | 6.9 | -0.1 ± 0.2 | 193 | +4 ± 2 | 206 | 201 | 1052 | +1 ± 2 | 22.0 | 3.9 |
| optimal@10s | 6.6 | -0.3 ± 0.1 | 194 | +5 ± 2 | 207 | 201 | 1055 | +4 ± 2 | 21.8 | 3.9 |
| batched_greedy@10s+aware | 6.4 | -0.6 ± 0.3 | 204 | +15 ± 3 | 212 | 202 | 1058 | +7 ± 3 | 22.0 | 6.3 |
| optimal@10s+aware | 6.3 | -0.7 ± 0.3 | 204 | +14 ± 3 | 211 | 201 | 1058 | +7 ± 3 | 21.9 | 6.2 |
| batched_greedy@30s+aware | 6.5 | -0.4 ± 0.2 | 213 | +24 ± 3 | 220 | 198 | 1056 | +5 ± 2 | 22.5 | 13.0 |
| optimal@30s+aware | 6.1 | -0.8 ± 0.2 | 214 | +24 ± 2 | 221 | 199 | 1060 | +9 ± 3 | 21.9 | 12.7 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 4.8 |  | 171 |  | 179 | 179 | 1075 |  | 29.2 | 1.5 |
| batched_greedy@10s | 4.9 | +0.0 ± 0.3 | 176 | +4 ± 2 | 184 | 178 | 1074 | -0 ± 3 | 29.2 | 3.8 |
| optimal@10s | 4.7 | -0.2 ± 0.3 | 178 | +7 ± 3 | 186 | 181 | 1077 | +2 ± 3 | 29.0 | 3.8 |
| batched_greedy@10s+aware | 4.6 | -0.3 ± 0.2 | 184 | +12 ± 3 | 188 | 180 | 1078 | +3 ± 3 | 29.1 | 5.2 |
| optimal@10s+aware | 4.5 | -0.4 ± 0.2 | 183 | +12 ± 2 | 188 | 180 | 1079 | +4 ± 3 | 29.0 | 5.1 |
| batched_greedy@30s+aware | 4.7 | -0.2 ± 0.1 | 191 | +20 ± 3 | 196 | 176 | 1077 | +2 ± 1 | 29.5 | 11.7 |
| optimal@30s+aware | 4.3 | -0.6 ± 0.4 | 192 | +21 ± 3 | 196 | 177 | 1081 | +6 ± 4 | 29.1 | 11.5 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@10s | 10.2 | 10.9% | 15.2 |
| 350 | optimal@10s | 10.2 | 11.8% | 5.5 |
| 400 | optimal@10s | 5.1 | 7.4% | 4.2 |
| 450 | optimal@10s | 3.1 | 4.4% | 3.9 |
| 500 | optimal@10s | 2.2 | 3.9% | 3.8 |
| 300 | optimal@10s+aware | 7.0 | 5.2% | 30.2 |
| 350 | optimal@10s+aware | 8.1 | 6.5% | 17.3 |
| 400 | optimal@10s+aware | 7.3 | 6.2% | 9.0 |
| 450 | optimal@10s+aware | 5.2 | 5.0% | 6.2 |
| 500 | optimal@10s+aware | 4.4 | 4.3% | 5.1 |
| 300 | optimal@30s+aware | 49.1 | 30.2% | 35.6 |
| 350 | optimal@30s+aware | 68.0 | 39.4% | 23.5 |
| 400 | optimal@30s+aware | 62.2 | 37.7% | 15.4 |
| 450 | optimal@30s+aware | 47.4 | 32.8% | 12.7 |
| 500 | optimal@30s+aware | 33.4 | 27.9% | 11.5 |
