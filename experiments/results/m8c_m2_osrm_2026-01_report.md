# M8C — real Manhattan demand, osrm travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2026-01-14_1700_3h_manhattan_f0.1.parquet`. Travel: osrm (TravelConfig(model='osrm', speed_mps=7.0, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=2.009750812567714, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 176s, p50 145s, p90 364s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 17.4 |  | 267 |  | 320 | 320 | 817 |  | 12.4 | 1.9 |
| batched_greedy@30s+aware | 16.5 | -0.9 ± 0.9 | 306 | +40 ± 10 | 340 | 306 | 826 | +9 ± 9 | 13.4 | 16.7 |
| optimal@30s+aware | 16.3 | -1.0 ± 0.5 | 309 | +42 ± 4 | 344 | 310 | 828 | +10 ± 5 | 13.1 | 16.4 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 7.8 |  | 225 |  | 242 | 242 | 912 |  | 30.2 | 1.7 |
| batched_greedy@30s+aware | 8.0 | +0.2 ± 0.7 | 247 | +21 ± 8 | 258 | 238 | 910 | -2 ± 7 | 31.0 | 11.4 |
| optimal@30s+aware | 8.0 | +0.2 ± 0.5 | 246 | +21 ± 8 | 257 | 238 | 910 | -2 ± 5 | 30.9 | 11.2 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 5.4 |  | 196 |  | 205 | 205 | 935 |  | 44.4 | 1.6 |
| batched_greedy@30s+aware | 5.8 | +0.3 ± 0.4 | 215 | +19 ± 2 | 220 | 202 | 932 | -3 ± 4 | 44.8 | 10.5 |
| optimal@30s+aware | 5.5 | +0.0 ± 0.5 | 215 | +20 ± 3 | 220 | 202 | 935 | -0 ± 5 | 44.6 | 10.5 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@30s+aware | 36.2 | 34.8% | 16.4 |
| 400 | optimal@30s+aware | 22.8 | 25.6% | 11.2 |
| 500 | optimal@30s+aware | 14.9 | 20.8% | 10.5 |
