# M8B — real Manhattan demand, osrm travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2026-07-15_1700_3h_manhattan_f0.1.parquet`. Travel: osrm (TravelConfig(model='osrm', speed_mps=7.0, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=2.260516365000587, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 309s, p50 231s, p90 678s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 34.3 |  | 280 |  | 417 | 412 | 742 |  | 10.7 | 4.0 |
| batched_greedy@30s+aware | 30.3 | -4.0 ± 0.8 | 339 | +58 ± 4 | 399 | 331 | 787 | +46 ± 9 | 12.0 | 34.1 |
| optimal@30s+aware | 30.3 | -4.0 ± 0.9 | 341 | +61 ± 6 | 402 | 332 | 787 | +45 ± 11 | 12.1 | 34.3 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 15.6 |  | 263 |  | 309 | 309 | 953 |  | 19.0 | 1.9 |
| batched_greedy@30s+aware | 15.5 | -0.1 ± 0.8 | 293 | +29 ± 6 | 322 | 290 | 954 | +1 ± 9 | 20.5 | 18.2 |
| optimal@30s+aware | 14.7 | -0.9 ± 0.6 | 294 | +30 ± 4 | 322 | 291 | 964 | +10 ± 6 | 20.0 | 17.6 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 8.7 |  | 228 |  | 248 | 248 | 1031 |  | 32.5 | 1.7 |
| batched_greedy@30s+aware | 8.8 | +0.0 ± 0.5 | 249 | +21 ± 5 | 262 | 242 | 1030 | -0 ± 5 | 33.1 | 13.0 |
| optimal@30s+aware | 8.6 | -0.1 ± 0.3 | 252 | +23 ± 2 | 265 | 245 | 1032 | +1 ± 4 | 32.9 | 13.0 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@30s+aware | 32.2 | 26.8% | 34.3 |
| 400 | optimal@30s+aware | 38.7 | 33.2% | 17.6 |
| 500 | optimal@30s+aware | 29.2 | 29.5% | 13.0 |
