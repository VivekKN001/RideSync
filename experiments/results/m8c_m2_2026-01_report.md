# M8C — real Manhattan demand, straight travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2026-01-14_1700_3h_manhattan_f0.1.parquet`. Travel: straight (TravelConfig(model='straight', speed_mps=3.9571235871174046, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=1.0, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 176s, p50 145s, p90 364s.

## 300 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 14.2 |  | 233 |  | 271 | 270 | 849 |  | 9.2 | 1.7 |
| batched_greedy@10s | 13.7 | -0.5 ± 0.4 | 235 | +2 ± 4 | 270 | 264 | 854 | +5 ± 4 | 9.2 | 3.6 |
| optimal@10s | 13.8 | -0.4 ± 0.2 | 238 | +5 ± 6 | 274 | 268 | 852 | +4 ± 2 | 9.1 | 3.6 |
| batched_greedy@10s+aware | 12.2 | -2.0 ± 0.2 | 263 | +30 ± 8 | 285 | 265 | 868 | +20 ± 2 | 8.7 | 9.0 |
| optimal@10s+aware | 12.0 | -2.2 ± 0.2 | 264 | +31 ± 8 | 286 | 265 | 870 | +22 ± 2 | 8.5 | 9.0 |
| batched_greedy@30s+aware | 11.9 | -2.4 ± 0.4 | 264 | +30 ± 6 | 281 | 248 | 872 | +23 ± 4 | 9.4 | 15.2 |
| optimal@30s+aware | 11.7 | -2.5 ± 0.4 | 270 | +37 ± 3 | 289 | 256 | 873 | +25 ± 4 | 8.5 | 15.0 |

## 350 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 7.6 |  | 195 |  | 211 | 210 | 914 |  | 19.2 | 1.5 |
| batched_greedy@10s | 7.5 | -0.1 ± 0.2 | 198 | +3 ± 5 | 213 | 208 | 915 | +1 ± 2 | 19.3 | 3.3 |
| optimal@10s | 7.3 | -0.3 ± 0.2 | 199 | +3 ± 3 | 213 | 208 | 917 | +3 ± 2 | 19.2 | 3.3 |
| batched_greedy@10s+aware | 7.1 | -0.5 ± 0.4 | 208 | +13 ± 8 | 217 | 207 | 919 | +5 ± 4 | 19.4 | 5.6 |
| optimal@10s+aware | 7.0 | -0.6 ± 0.5 | 209 | +13 ± 5 | 218 | 208 | 920 | +6 ± 5 | 19.2 | 5.5 |
| batched_greedy@30s+aware | 7.3 | -0.3 ± 0.3 | 218 | +22 ± 7 | 226 | 203 | 917 | +3 ± 3 | 19.4 | 11.7 |
| optimal@30s+aware | 6.6 | -1.0 ± 0.2 | 222 | +26 ± 4 | 229 | 207 | 924 | +10 ± 2 | 18.7 | 11.3 |

## 400 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 5.1 |  | 167 |  | 176 | 175 | 938 |  | 28.9 | 1.4 |
| batched_greedy@10s | 4.9 | -0.2 ± 0.2 | 172 | +5 ± 3 | 180 | 175 | 940 | +2 ± 2 | 28.8 | 3.2 |
| optimal@10s | 5.0 | -0.1 ± 0.1 | 172 | +5 ± 3 | 180 | 175 | 940 | +1 ± 1 | 28.8 | 3.2 |
| batched_greedy@10s+aware | 4.7 | -0.4 ± 0.3 | 179 | +12 ± 3 | 184 | 176 | 943 | +4 ± 3 | 28.5 | 4.7 |
| optimal@10s+aware | 4.6 | -0.5 ± 0.2 | 179 | +12 ± 3 | 183 | 175 | 944 | +5 ± 2 | 28.6 | 4.7 |
| batched_greedy@30s+aware | 5.0 | -0.2 ± 0.2 | 189 | +22 ± 2 | 193 | 173 | 940 | +2 ± 2 | 28.8 | 10.6 |
| optimal@30s+aware | 4.4 | -0.7 ± 0.3 | 189 | +22 ± 3 | 193 | 173 | 945 | +7 ± 3 | 28.4 | 10.4 |

## 450 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 3.8 |  | 151 |  | 157 | 157 | 952 |  | 36.6 | 1.3 |
| batched_greedy@10s | 3.8 | +0.0 ± 0.2 | 155 | +4 ± 2 | 160 | 155 | 952 | -0 ± 2 | 36.6 | 3.1 |
| optimal@10s | 3.7 | -0.1 ± 0.2 | 155 | +4 ± 1 | 161 | 156 | 953 | +1 ± 2 | 36.5 | 3.1 |
| batched_greedy@10s+aware | 3.6 | -0.2 ± 0.2 | 161 | +10 ± 2 | 164 | 156 | 953 | +2 ± 2 | 36.6 | 4.3 |
| optimal@10s+aware | 3.5 | -0.3 ± 0.2 | 160 | +9 ± 2 | 163 | 155 | 955 | +3 ± 2 | 36.5 | 4.3 |
| batched_greedy@30s+aware | 3.6 | -0.2 ± 0.4 | 172 | +21 ± 1 | 174 | 155 | 954 | +2 ± 4 | 36.5 | 10.1 |
| optimal@30s+aware | 3.4 | -0.4 ± 0.2 | 170 | +19 ± 2 | 172 | 154 | 956 | +4 ± 2 | 36.5 | 9.9 |

## 500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 3.0 |  | 140 |  | 144 | 144 | 960 |  | 43.0 | 1.3 |
| batched_greedy@10s | 3.0 | -0.0 ± 0.1 | 144 | +4 ± 1 | 148 | 143 | 960 | +0 ± 1 | 43.0 | 3.1 |
| optimal@10s | 3.0 | -0.0 ± 0.1 | 145 | +5 ± 1 | 149 | 144 | 960 | +0 ± 1 | 42.9 | 3.1 |
| batched_greedy@10s+aware | 2.8 | -0.2 ± 0.3 | 148 | +8 ± 2 | 150 | 143 | 961 | +2 ± 3 | 42.9 | 4.0 |
| optimal@10s+aware | 2.8 | -0.2 ± 0.3 | 148 | +9 ± 3 | 150 | 143 | 961 | +2 ± 3 | 42.9 | 4.0 |
| batched_greedy@30s+aware | 3.1 | +0.1 ± 0.4 | 158 | +19 ± 2 | 160 | 142 | 959 | -1 ± 4 | 43.1 | 9.7 |
| optimal@30s+aware | 2.7 | -0.3 ± 0.2 | 159 | +19 ± 2 | 161 | 142 | 962 | +3 ± 2 | 42.8 | 9.6 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 300 | optimal@10s | 4.9 | 7.5% | 3.6 |
| 350 | optimal@10s | 2.2 | 4.6% | 3.3 |
| 400 | optimal@10s | 1.6 | 3.3% | 3.2 |
| 450 | optimal@10s | 1.4 | 2.9% | 3.1 |
| 500 | optimal@10s | 1.0 | 2.6% | 3.1 |
| 300 | optimal@10s+aware | 7.6 | 6.2% | 9.0 |
| 350 | optimal@10s+aware | 4.7 | 5.0% | 5.5 |
| 400 | optimal@10s+aware | 3.4 | 4.1% | 4.7 |
| 450 | optimal@10s+aware | 2.9 | 3.4% | 4.3 |
| 500 | optimal@10s+aware | 1.9 | 2.7% | 4.0 |
| 300 | optimal@30s+aware | 58.4 | 38.9% | 15.0 |
| 350 | optimal@30s+aware | 47.4 | 34.4% | 11.3 |
| 400 | optimal@30s+aware | 30.9 | 27.0% | 10.4 |
| 450 | optimal@30s+aware | 23.4 | 22.6% | 9.9 |
| 500 | optimal@30s+aware | 17.7 | 19.8% | 9.6 |
