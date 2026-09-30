# M8B — real Manhattan demand, osrm travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2026-07-18_2000_3h_manhattan_f0.1.parquet`. Travel: osrm (TravelConfig(model='osrm', speed_mps=7.0, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=2.260516365000587, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 202s, p50 155s, p90 420s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 38.4 |  | 282 |  | 448 | 443 | 727 |  | 5.3 | 4.2 |
| batched_greedy@30s+aware | 34.0 | -4.4 ± 1.0 | 353 | +71 ± 7 | 421 | 335 | 779 | +52 ± 12 | 7.2 | 42.5 |
| optimal@30s+aware | 34.2 | -4.2 ± 0.9 | 354 | +72 ± 5 | 423 | 336 | 777 | +50 ± 11 | 7.1 | 42.8 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 20.6 |  | 271 |  | 338 | 337 | 937 |  | 13.9 | 2.2 |
| batched_greedy@30s+aware | 18.5 | -2.1 ± 1.1 | 315 | +45 ± 6 | 352 | 308 | 962 | +24 ± 13 | 15.0 | 23.7 |
| optimal@30s+aware | 18.6 | -1.9 ± 0.5 | 315 | +44 ± 7 | 353 | 311 | 960 | +23 ± 6 | 14.9 | 23.1 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 10.2 |  | 239 |  | 264 | 264 | 1060 |  | 26.2 | 1.8 |
| batched_greedy@30s+aware | 10.1 | -0.1 ± 0.4 | 263 | +24 ± 4 | 280 | 257 | 1061 | +1 ± 5 | 26.9 | 14.9 |
| optimal@30s+aware | 9.7 | -0.4 ± 0.2 | 264 | +25 ± 4 | 281 | 258 | 1065 | +5 ± 3 | 26.5 | 14.7 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@30s+aware | 29.4 | 26.8% | 42.8 |
| 400 | optimal@30s+aware | 35.1 | 32.2% | 23.1 |
| 500 | optimal@30s+aware | 31.3 | 30.6% | 14.7 |
