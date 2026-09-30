# M8B — real Manhattan demand, straight travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2026-07-15_0700_3h_manhattan_f0.1.parquet`. Travel: straight (TravelConfig(model='straight', speed_mps=3.4608154282234755, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=1.0, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 224s, p50 191s, p90 461s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 31.0 |  | 259 |  | 338 | 326 | 722 |  | 10.2 | 9.8 |
| batched_greedy@10s | 30.7 | -0.3 ± 0.6 | 263 | +4 ± 7 | 331 | 312 | 725 | +3 ± 6 | 10.7 | 12.9 |
| optimal@10s | 30.6 | -0.4 ± 0.4 | 265 | +6 ± 7 | 336 | 318 | 726 | +4 ± 4 | 10.2 | 12.5 |
| batched_greedy@10s+aware | 29.7 | -1.3 ± 0.8 | 289 | +30 ± 4 | 312 | 275 | 736 | +14 ± 8 | 12.5 | 24.6 |
| optimal@10s+aware | 29.6 | -1.5 ± 0.8 | 292 | +33 ± 4 | 317 | 280 | 737 | +15 ± 8 | 12.1 | 24.4 |
| batched_greedy@30s+aware | 30.0 | -1.0 ± 0.8 | 292 | +33 ± 3 | 312 | 265 | 732 | +11 ± 9 | 13.2 | 29.3 |
| optimal@30s+aware | 29.4 | -1.6 ± 0.8 | 294 | +35 ± 2 | 315 | 268 | 739 | +17 ± 8 | 12.4 | 28.7 |

## 350 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 24.7 |  | 236 |  | 287 | 279 | 788 |  | 17.8 | 7.8 |
| batched_greedy@10s | 24.8 | +0.1 ± 0.6 | 244 | +8 ± 3 | 288 | 273 | 787 | -1 ± 6 | 18.1 | 11.0 |
| optimal@10s | 24.7 | +0.0 ± 0.5 | 244 | +8 ± 2 | 289 | 275 | 788 | -0 ± 5 | 17.9 | 10.6 |
| batched_greedy@10s+aware | 25.7 | +1.0 ± 0.7 | 265 | +29 ± 8 | 277 | 246 | 778 | -10 ± 8 | 20.9 | 21.2 |
| optimal@10s+aware | 25.5 | +0.8 ± 0.6 | 265 | +29 ± 5 | 277 | 247 | 780 | -9 ± 7 | 20.8 | 21.1 |
| batched_greedy@30s+aware | 25.9 | +1.3 ± 0.8 | 272 | +36 ± 5 | 283 | 241 | 775 | -13 ± 9 | 21.4 | 26.0 |
| optimal@30s+aware | 25.6 | +0.9 ± 0.4 | 270 | +34 ± 6 | 281 | 240 | 779 | -9 ± 4 | 21.1 | 25.4 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 22.7 |  | 225 |  | 268 | 260 | 809 |  | 26.6 | 7.3 |
| batched_greedy@10s | 22.9 | +0.2 ± 0.2 | 228 | +3 ± 3 | 266 | 253 | 807 | -2 ± 2 | 27.1 | 9.8 |
| optimal@10s | 22.4 | -0.3 ± 0.3 | 230 | +5 ± 3 | 268 | 256 | 812 | +3 ± 3 | 26.6 | 9.4 |
| batched_greedy@10s+aware | 23.6 | +0.9 ± 0.5 | 253 | +28 ± 6 | 261 | 232 | 799 | -10 ± 6 | 29.2 | 19.8 |
| optimal@10s+aware | 23.4 | +0.7 ± 0.7 | 254 | +29 ± 5 | 262 | 233 | 802 | -7 ± 8 | 28.9 | 19.6 |
| batched_greedy@30s+aware | 23.9 | +1.2 ± 0.8 | 259 | +34 ± 6 | 265 | 226 | 797 | -12 ± 8 | 29.6 | 24.6 |
| optimal@30s+aware | 23.5 | +0.8 ± 0.6 | 258 | +33 ± 6 | 265 | 227 | 800 | -9 ± 6 | 29.3 | 24.0 |

## 450 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 21.0 |  | 221 |  | 258 | 250 | 827 |  | 33.4 | 7.2 |
| batched_greedy@10s | 21.0 | +0.1 ± 0.3 | 224 | +3 ± 3 | 257 | 245 | 826 | -1 ± 3 | 33.7 | 9.2 |
| optimal@10s | 20.9 | -0.1 ± 0.2 | 225 | +4 ± 3 | 258 | 246 | 828 | +1 ± 2 | 33.4 | 9.0 |
| batched_greedy@10s+aware | 21.9 | +1.0 ± 0.7 | 245 | +25 ± 6 | 251 | 224 | 817 | -10 ± 7 | 35.6 | 18.4 |
| optimal@10s+aware | 21.8 | +0.8 ± 0.6 | 246 | +26 ± 7 | 253 | 226 | 819 | -8 ± 7 | 35.3 | 18.3 |
| batched_greedy@30s+aware | 22.1 | +1.1 ± 0.6 | 251 | +31 ± 6 | 256 | 218 | 816 | -11 ± 6 | 36.0 | 23.2 |
| optimal@30s+aware | 22.0 | +1.0 ± 0.5 | 252 | +31 ± 6 | 257 | 220 | 816 | -11 ± 5 | 35.8 | 22.9 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 19.8 |  | 212 |  | 247 | 241 | 839 |  | 39.4 | 6.2 |
| batched_greedy@10s | 19.7 | -0.1 ± 0.4 | 218 | +6 ± 4 | 249 | 237 | 840 | +1 ± 4 | 39.5 | 8.6 |
| optimal@10s | 19.5 | -0.3 ± 0.3 | 219 | +7 ± 3 | 249 | 237 | 842 | +3 ± 4 | 39.3 | 8.5 |
| batched_greedy@10s+aware | 20.5 | +0.7 ± 0.8 | 239 | +27 ± 8 | 244 | 218 | 832 | -7 ± 8 | 41.1 | 17.4 |
| optimal@10s+aware | 20.4 | +0.6 ± 0.6 | 240 | +28 ± 7 | 244 | 219 | 833 | -6 ± 6 | 41.0 | 17.3 |
| batched_greedy@30s+aware | 20.6 | +0.8 ± 0.6 | 246 | +34 ± 7 | 250 | 213 | 831 | -8 ± 6 | 41.4 | 22.2 |
| optimal@30s+aware | 20.3 | +0.5 ± 0.4 | 246 | +34 ± 6 | 250 | 214 | 834 | -5 ± 4 | 41.0 | 21.7 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@10s | 5.0 | 7.0% | 12.5 |
| 350 | optimal@10s | 3.6 | 5.1% | 10.6 |
| 400 | optimal@10s | 2.9 | 4.8% | 9.4 |
| 450 | optimal@10s | 2.7 | 4.6% | 9.0 |
| 500 | optimal@10s | 2.2 | 4.4% | 8.5 |
| 300 | optimal@10s+aware | 5.3 | 4.5% | 24.4 |
| 350 | optimal@10s+aware | 2.9 | 3.2% | 21.1 |
| 400 | optimal@10s+aware | 3.0 | 3.1% | 19.6 |
| 450 | optimal@10s+aware | 2.6 | 3.1% | 18.3 |
| 500 | optimal@10s+aware | 2.7 | 3.1% | 17.3 |
| 300 | optimal@30s+aware | 38.0 | 26.8% | 28.7 |
| 350 | optimal@30s+aware | 28.2 | 25.2% | 25.4 |
| 400 | optimal@30s+aware | 27.3 | 23.5% | 24.0 |
| 450 | optimal@30s+aware | 24.0 | 22.3% | 22.9 |
| 500 | optimal@30s+aware | 25.9 | 22.1% | 21.7 |
