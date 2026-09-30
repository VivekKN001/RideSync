# M8C — real Manhattan demand, osrm travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2025-10-15_1700_3h_manhattan_f0.1.parquet`. Travel: osrm (TravelConfig(model='osrm', speed_mps=7.0, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=2.30560767146133, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 176s, p50 149s, p90 347s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 40.3 |  | 285 |  | 464 | 457 | 717 |  | 4.4 | 4.7 |
| batched_greedy@30s+aware | 36.3 | -4.0 ± 1.2 | 357 | +71 ± 11 | 433 | 346 | 764 | +48 ± 14 | 6.5 | 43.0 |
| optimal@30s+aware | 36.3 | -4.0 ± 1.5 | 358 | +72 ± 8 | 434 | 346 | 765 | +48 ± 18 | 6.4 | 43.7 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 21.5 |  | 277 |  | 350 | 349 | 943 |  | 10.9 | 1.9 |
| batched_greedy@30s+aware | 19.9 | -1.6 ± 1.0 | 326 | +49 ± 5 | 370 | 327 | 962 | +19 ± 13 | 12.0 | 23.3 |
| optimal@30s+aware | 19.8 | -1.7 ± 0.7 | 324 | +47 ± 4 | 370 | 328 | 963 | +20 ± 8 | 11.8 | 22.7 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 10.8 |  | 247 |  | 275 | 275 | 1071 |  | 22.9 | 1.6 |
| batched_greedy@30s+aware | 11.1 | +0.3 ± 0.3 | 271 | +23 ± 7 | 292 | 269 | 1068 | -4 ± 3 | 23.9 | 14.7 |
| optimal@30s+aware | 10.6 | -0.1 ± 0.4 | 274 | +27 ± 5 | 294 | 272 | 1073 | +2 ± 5 | 23.4 | 14.4 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@30s+aware | 25.5 | 24.4% | 43.7 |
| 400 | optimal@30s+aware | 44.0 | 37.1% | 22.7 |
| 500 | optimal@30s+aware | 41.0 | 35.0% | 14.4 |
