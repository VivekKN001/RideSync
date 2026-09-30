# M8B — real Manhattan demand, osrm travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2026-07-15_0700_3h_manhattan_f0.1.parquet`. Travel: osrm (TravelConfig(model='osrm', speed_mps=7.0, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=2.260516365000587, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 224s, p50 191s, p90 461s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 34.4 |  | 277 |  | 393 | 385 | 686 |  | 16.1 | 7.2 |
| batched_greedy@30s+aware | 34.1 | -0.4 ± 1.6 | 320 | +43 ± 10 | 364 | 318 | 690 | +4 ± 17 | 20.1 | 29.8 |
| optimal@30s+aware | 33.8 | -0.6 ± 1.1 | 323 | +46 ± 8 | 368 | 320 | 693 | +7 ± 12 | 19.8 | 29.8 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 25.3 |  | 255 |  | 325 | 321 | 782 |  | 30.6 | 5.0 |
| batched_greedy@30s+aware | 27.7 | +2.5 ± 1.3 | 293 | +38 ± 14 | 319 | 282 | 756 | -26 ± 14 | 35.2 | 24.9 |
| optimal@30s+aware | 27.5 | +2.3 ± 1.1 | 293 | +38 ± 12 | 320 | 283 | 758 | -24 ± 11 | 34.9 | 24.4 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 22.0 |  | 245 |  | 302 | 299 | 816 |  | 42.8 | 4.2 |
| batched_greedy@30s+aware | 24.5 | +2.5 ± 1.3 | 280 | +35 ± 8 | 300 | 266 | 790 | -26 ± 14 | 46.0 | 22.4 |
| optimal@30s+aware | 24.1 | +2.1 ± 1.0 | 280 | +35 ± 7 | 300 | 265 | 794 | -22 ± 11 | 45.8 | 22.1 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@30s+aware | 23.0 | 23.9% | 29.8 |
| 400 | optimal@30s+aware | 19.4 | 22.0% | 24.4 |
| 500 | optimal@30s+aware | 14.5 | 19.3% | 22.1 |
