# M8B — real Manhattan demand, straight travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2026-07-18_2000_3h_manhattan_f0.1.parquet`. Travel: straight (TravelConfig(model='straight', speed_mps=3.4608154282234755, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=1.0, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 202s, p50 155s, p90 420s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 36.3 |  | 276 |  | 417 | 405 | 751 |  | 1.6 | 6.6 |
| batched_greedy@10s | 32.7 | -3.6 ± 0.5 | 300 | +24 ± 4 | 395 | 346 | 794 | +43 ± 6 | 1.4 | 20.9 |
| optimal@10s | 32.6 | -3.7 ± 0.9 | 303 | +27 ± 9 | 401 | 352 | 795 | +44 ± 10 | 1.4 | 20.6 |
| batched_greedy@10s+aware | 29.3 | -7.0 ± 0.6 | 328 | +53 ± 7 | 374 | 291 | 834 | +82 ± 7 | 1.7 | 36.7 |
| optimal@10s+aware | 29.0 | -7.3 ± 0.7 | 331 | +56 ± 6 | 378 | 294 | 837 | +86 ± 8 | 1.6 | 36.5 |
| batched_greedy@30s+aware | 29.2 | -7.2 ± 0.9 | 323 | +47 ± 6 | 361 | 272 | 836 | +84 ± 11 | 1.9 | 42.1 |
| optimal@30s+aware | 29.0 | -7.3 ± 0.8 | 326 | +50 ± 7 | 365 | 275 | 837 | +86 ± 9 | 1.8 | 42.1 |

## 350 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 24.3 |  | 255 |  | 332 | 329 | 893 |  | 4.2 | 3.4 |
| batched_greedy@10s | 23.4 | -0.9 ± 0.5 | 260 | +4 ± 4 | 329 | 318 | 904 | +11 ± 6 | 4.3 | 7.2 |
| optimal@10s | 23.8 | -0.6 ± 0.6 | 265 | +10 ± 4 | 337 | 324 | 900 | +7 ± 7 | 4.2 | 7.5 |
| batched_greedy@10s+aware | 19.6 | -4.8 ± 0.7 | 300 | +44 ± 5 | 332 | 282 | 949 | +56 ± 8 | 4.3 | 22.6 |
| optimal@10s+aware | 19.9 | -4.5 ± 0.9 | 302 | +46 ± 6 | 335 | 283 | 946 | +53 ± 10 | 4.3 | 23.2 |
| batched_greedy@30s+aware | 19.7 | -4.6 ± 1.0 | 299 | +43 ± 6 | 325 | 262 | 947 | +54 ± 12 | 4.8 | 30.4 |
| optimal@30s+aware | 19.4 | -4.9 ± 0.8 | 302 | +47 ± 3 | 329 | 267 | 951 | +58 ± 10 | 4.4 | 29.7 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 15.8 |  | 233 |  | 273 | 272 | 994 |  | 9.8 | 2.4 |
| batched_greedy@10s | 15.4 | -0.4 ± 0.4 | 234 | +2 ± 5 | 273 | 266 | 998 | +4 ± 5 | 10.1 | 5.1 |
| optimal@10s | 15.2 | -0.5 ± 0.3 | 238 | +5 ± 4 | 276 | 270 | 1001 | +6 ± 3 | 9.8 | 5.0 |
| batched_greedy@10s+aware | 13.1 | -2.7 ± 0.3 | 265 | +33 ± 6 | 288 | 260 | 1026 | +32 ± 3 | 9.7 | 13.2 |
| optimal@10s+aware | 12.9 | -2.8 ± 0.5 | 266 | +34 ± 8 | 289 | 262 | 1027 | +33 ± 6 | 9.4 | 13.2 |
| batched_greedy@30s+aware | 12.9 | -2.8 ± 0.2 | 265 | +32 ± 6 | 282 | 242 | 1027 | +33 ± 3 | 10.6 | 21.1 |
| optimal@30s+aware | 12.9 | -2.8 ± 0.4 | 272 | +39 ± 4 | 290 | 249 | 1028 | +34 ± 5 | 10.0 | 21.2 |

## 450 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 9.9 |  | 205 |  | 227 | 226 | 1063 |  | 16.9 | 1.9 |
| batched_greedy@10s | 10.0 | +0.1 ± 0.7 | 205 | -0 ± 4 | 225 | 220 | 1062 | -1 ± 8 | 17.3 | 4.4 |
| optimal@10s | 9.8 | -0.1 ± 0.4 | 209 | +3 ± 3 | 229 | 223 | 1065 | +2 ± 5 | 16.9 | 4.4 |
| batched_greedy@10s+aware | 8.7 | -1.2 ± 0.7 | 223 | +18 ± 1 | 236 | 221 | 1077 | +14 ± 8 | 17.1 | 8.5 |
| optimal@10s+aware | 8.5 | -1.4 ± 0.5 | 226 | +20 ± 6 | 239 | 224 | 1080 | +17 ± 6 | 16.7 | 8.4 |
| batched_greedy@30s+aware | 8.4 | -1.5 ± 0.7 | 230 | +24 ± 4 | 240 | 213 | 1081 | +17 ± 8 | 17.2 | 16.0 |
| optimal@30s+aware | 8.1 | -1.8 ± 0.6 | 234 | +29 ± 3 | 245 | 218 | 1084 | +21 ± 8 | 16.7 | 15.6 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 6.5 |  | 176 |  | 187 | 187 | 1104 |  | 24.0 | 1.7 |
| batched_greedy@10s | 6.5 | +0.1 ± 0.5 | 180 | +4 ± 4 | 191 | 185 | 1103 | -1 ± 6 | 24.0 | 4.0 |
| optimal@10s | 6.4 | -0.0 ± 0.4 | 181 | +5 ± 3 | 192 | 187 | 1104 | +0 ± 5 | 24.0 | 4.0 |
| batched_greedy@10s+aware | 5.9 | -0.5 ± 0.4 | 192 | +16 ± 4 | 199 | 188 | 1110 | +6 ± 5 | 24.0 | 6.5 |
| optimal@10s+aware | 5.8 | -0.6 ± 0.5 | 193 | +17 ± 6 | 200 | 190 | 1111 | +7 ± 6 | 23.9 | 6.5 |
| batched_greedy@30s+aware | 5.8 | -0.6 ± 0.5 | 200 | +24 ± 4 | 206 | 183 | 1111 | +7 ± 6 | 24.2 | 14.0 |
| optimal@30s+aware | 5.5 | -1.0 ± 0.6 | 203 | +27 ± 4 | 208 | 186 | 1115 | +11 ± 7 | 23.8 | 13.5 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@10s | 8.7 | 10.1% | 20.6 |
| 350 | optimal@10s | 9.8 | 11.5% | 7.5 |
| 400 | optimal@10s | 6.1 | 8.7% | 5.0 |
| 450 | optimal@10s | 3.8 | 6.0% | 4.4 |
| 500 | optimal@10s | 2.4 | 3.9% | 4.0 |
| 300 | optimal@10s+aware | 5.4 | 4.4% | 36.5 |
| 350 | optimal@10s+aware | 6.6 | 5.7% | 23.2 |
| 400 | optimal@10s+aware | 7.8 | 6.8% | 13.2 |
| 450 | optimal@10s+aware | 6.1 | 5.9% | 8.4 |
| 500 | optimal@10s+aware | 4.6 | 4.5% | 6.5 |
| 300 | optimal@30s+aware | 40.1 | 28.8% | 42.1 |
| 350 | optimal@30s+aware | 51.8 | 36.9% | 29.7 |
| 400 | optimal@30s+aware | 59.9 | 41.7% | 21.2 |
| 450 | optimal@30s+aware | 52.6 | 36.2% | 15.6 |
| 500 | optimal@30s+aware | 37.0 | 31.0% | 13.5 |
