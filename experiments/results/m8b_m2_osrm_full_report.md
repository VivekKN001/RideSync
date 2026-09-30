# M8B — real Manhattan demand, osrm travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2026-07-15_1700_3h_manhattan_f1.parquet`. Travel: osrm (TravelConfig(model='osrm', speed_mps=7.0, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=2.260516365000587, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 319s, p50 241s, p90 692s.

## 3000 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 27.3 |  | 273 |  | 373 | 372 | 8203 |  | 6.5 | 7.9 |
| batched_greedy@30s+aware | 20.2 | -7.1 ± 1.1 | 289 | +16 ± 7 | 305 | 242 | 9006 | +803 ± 122 | 7.3 | 298.4 |
| optimal@30s+aware | 19.9 | -7.3 ± 0.7 | 293 | +21 ± 9 | 311 | 247 | 9031 | +828 ± 79 | 7.1 | 298.4 |

## 4000 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 8.9 |  | 220 |  | 240 | 240 | 10275 |  | 18.5 | 5.9 |
| batched_greedy@30s+aware | 8.8 | -0.1 ± 0.1 | 230 | +10 ± 3 | 238 | 209 | 10288 | +12 ± 15 | 20.7 | 155.2 |
| optimal@30s+aware | 7.3 | -1.6 ± 2.3 | 237 | +17 ± 4 | 246 | 221 | 10457 | +182 ± 259 | 18.7 | 137.0 |

## 5000 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 5.6 |  | 182 |  | 192 | 192 | 10644 |  | 34.5 | 5.6 |
| batched_greedy@30s+aware | 5.6 | -0.1 ± 0.7 | 194 | +12 ± 13 | 198 | 176 | 10651 | +7 ± 79 | 35.4 | 127.2 |
| optimal@30s+aware | 4.7 | -1.0 ± 1.9 | 199 | +17 ± 14 | 203 | 183 | 10753 | +108 ± 213 | 34.4 | 117.1 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 3000 | optimal@30s+aware | 773.5 | 92.9% | 298.4 |
| 4000 | optimal@30s+aware | 1028.4 | 88.1% | 137.0 |
| 5000 | optimal@30s+aware | 841.3 | 86.8% | 117.1 |
