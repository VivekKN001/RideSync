# M8C — real Manhattan demand, osrm travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2026-04-15_1700_3h_manhattan_f0.1.parquet`. Travel: osrm (TravelConfig(model='osrm', speed_mps=7.0, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=2.3130357806891215, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 213s, p50 171s, p90 431s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 30.4 |  | 286 |  | 403 | 401 | 719 |  | 7.1 | 2.9 |
| batched_greedy@30s+aware | 27.1 | -3.3 ± 1.0 | 338 | +52 ± 8 | 398 | 340 | 752 | +34 ± 10 | 8.2 | 26.7 |
| optimal@30s+aware | 27.1 | -3.4 ± 1.0 | 338 | +52 ± 4 | 397 | 341 | 753 | +35 ± 11 | 8.0 | 26.2 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 14.5 |  | 262 |  | 303 | 302 | 883 |  | 19.5 | 2.0 |
| batched_greedy@30s+aware | 13.7 | -0.8 ± 0.7 | 288 | +26 ± 4 | 313 | 287 | 891 | +8 ± 8 | 20.3 | 14.8 |
| optimal@30s+aware | 13.7 | -0.8 ± 0.3 | 288 | +26 ± 6 | 314 | 289 | 891 | +8 ± 3 | 20.2 | 14.6 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 9.0 |  | 231 |  | 251 | 251 | 940 |  | 33.8 | 1.8 |
| batched_greedy@30s+aware | 8.8 | -0.2 ± 0.6 | 251 | +20 ± 3 | 262 | 242 | 942 | +2 ± 6 | 34.3 | 12.3 |
| optimal@30s+aware | 8.7 | -0.3 ± 0.4 | 251 | +20 ± 4 | 263 | 243 | 943 | +3 ± 5 | 34.2 | 12.2 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@30s+aware | 27.0 | 25.0% | 26.2 |
| 400 | optimal@30s+aware | 30.4 | 29.0% | 14.6 |
| 500 | optimal@30s+aware | 17.5 | 22.2% | 12.2 |
