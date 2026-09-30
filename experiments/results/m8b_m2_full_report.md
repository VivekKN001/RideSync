# M8B — real Manhattan demand, straight travel times

Deltas are paired against `immediate_greedy` for the same seed (mean ± 95% CI, Student t over seeds).
`wait_all` counts cancelled riders up to their cancellation time; `wait` is completed riders only.
Demand: `data/processed/trips_2026-07-15_1700_3h_manhattan_f1.parquet`. Travel: straight (TravelConfig(model='straight', speed_mps=3.4608154282234755, detour=1.35, osrm_url='http://localhost:5000', time_multiplier=1.0, eta_model=None, noise_sigma=0.0)).
Real-world benchmark (Uber, request → driver on scene): mean 319s, p50 241s, p90 692s.

## 3000 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 29.7 |  | 255 |  | 361 | 360 | 7936 |  | 5.0 | 8.6 |
| batched_greedy@10s | 20.2 | -9.5 ± 0.2 | 261 | +6 ± 6 | 276 | 212 | 9005 | +1069 ± 22 | 5.1 | 255.7 |
| optimal@10s | 20.0 | -9.7 ± 0.6 | 264 | +8 ± 4 | 276 | 209 | 9029 | +1093 ± 72 | 5.0 | 266.0 |
| batched_greedy@10s+aware | 19.4 | -10.2 ± 0.5 | 264 | +9 ± 2 | 271 | 201 | 9089 | +1153 ± 55 | 5.1 | 280.2 |
| optimal@10s+aware | 19.3 | -10.3 ± 0.6 | 265 | +10 ± 4 | 272 | 202 | 9102 | +1166 ± 72 | 5.0 | 281.7 |
| batched_greedy@30s+aware | 19.1 | -10.5 ± 0.2 | 254 | -2 ± 3 | 256 | 184 | 9125 | +1189 ± 20 | 5.3 | 319.0 |
| optimal@30s+aware | 18.9 | -10.7 ± 0.4 | 257 | +2 ± 1 | 259 | 185 | 9147 | +1211 ± 49 | 5.1 | 324.5 |

## 3500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 14.8 |  | 236 |  | 277 | 277 | 9615 |  | 7.1 | 4.3 |
| batched_greedy@10s | 12.9 | -1.9 ± 0.4 | 229 | -8 ± 4 | 258 | 247 | 9824 | +209 ± 46 | 7.3 | 55.2 |
| optimal@10s | 12.7 | -2.0 ± 0.5 | 246 | +9 ± 2 | 275 | 257 | 9845 | +231 ± 56 | 6.9 | 75.6 |
| batched_greedy@10s+aware | 10.4 | -4.3 ± 0.5 | 241 | +5 ± 5 | 251 | 217 | 10103 | +488 ± 52 | 7.5 | 140.3 |
| optimal@10s+aware | 10.4 | -4.4 ± 0.5 | 251 | +15 ± 8 | 262 | 227 | 10113 | +498 ± 56 | 7.1 | 143.0 |
| batched_greedy@30s+aware | 10.1 | -4.7 ± 0.4 | 224 | -12 ± 6 | 227 | 185 | 10141 | +526 ± 43 | 8.3 | 203.5 |
| optimal@30s+aware | 9.4 | -5.3 ± 0.4 | 242 | +6 ± 4 | 247 | 204 | 10216 | +601 ± 47 | 7.2 | 201.6 |

## 4000 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 6.3 |  | 190 |  | 202 | 202 | 10573 |  | 13.8 | 3.5 |
| batched_greedy@10s | 6.4 | +0.1 ± 0.2 | 186 | -3 ± 3 | 199 | 193 | 10561 | -12 ± 21 | 14.4 | 33.5 |
| optimal@10s | 5.7 | -0.6 ± 0.2 | 191 | +1 ± 3 | 202 | 196 | 10642 | +70 ± 20 | 13.6 | 33.2 |
| batched_greedy@10s+aware | 5.2 | -1.1 ± 0.1 | 198 | +8 ± 6 | 205 | 192 | 10691 | +119 ± 12 | 13.8 | 59.3 |
| optimal@10s+aware | 4.7 | -1.6 ± 0.1 | 201 | +11 ± 3 | 208 | 199 | 10753 | +180 ± 15 | 12.8 | 48.4 |
| batched_greedy@30s+aware | 6.1 | -0.2 ± 0.3 | 194 | +5 ± 1 | 197 | 168 | 10595 | +22 ± 29 | 15.9 | 148.1 |
| optimal@30s+aware | 3.9 | -2.4 ± 0.0 | 202 | +13 ± 2 | 207 | 184 | 10844 | +272 ± 6 | 13.0 | 121.8 |

## 4500 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 4.4 |  | 168 |  | 176 | 176 | 10785 |  | 22.8 | 3.3 |
| batched_greedy@10s | 4.4 | -0.0 ± 0.2 | 167 | -2 ± 2 | 174 | 169 | 10786 | +1 ± 21 | 23.2 | 32.7 |
| optimal@10s | 3.8 | -0.6 ± 0.2 | 169 | +1 ± 1 | 176 | 171 | 10856 | +71 ± 17 | 22.6 | 32.6 |
| batched_greedy@10s+aware | 3.7 | -0.7 ± 0.3 | 173 | +5 ± 1 | 178 | 170 | 10865 | +80 ± 38 | 22.8 | 43.8 |
| optimal@10s+aware | 3.3 | -1.1 ± 0.1 | 174 | +6 ± 2 | 179 | 172 | 10913 | +128 ± 13 | 22.2 | 39.3 |
| batched_greedy@30s+aware | 4.1 | -0.3 ± 0.3 | 175 | +6 ± 2 | 176 | 153 | 10818 | +33 ± 30 | 23.9 | 126.6 |
| optimal@30s+aware | 2.5 | -2.0 ± 0.4 | 178 | +10 ± 2 | 181 | 162 | 11005 | +220 ± 40 | 22.1 | 107.6 |

## 5000 drivers

| arm | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | wait s | pickup s | trips/h | Δ trips/h | idle % | batch riders |
|---|---|---|---|---|---|---|---|---|---|---|
| immediate_greedy | 2.9 |  | 146 |  | 150 | 150 | 10949 |  | 30.4 | 3.2 |
| batched_greedy@10s | 3.0 | +0.1 ± 0.2 | 147 | +1 ± 3 | 151 | 146 | 10943 | -6 ± 22 | 30.6 | 32.5 |
| optimal@10s | 2.6 | -0.4 ± 0.3 | 149 | +3 ± 5 | 153 | 148 | 10989 | +41 ± 29 | 30.3 | 32.5 |
| batched_greedy@10s+aware | 2.6 | -0.4 ± 0.2 | 151 | +5 ± 4 | 154 | 147 | 10992 | +43 ± 21 | 30.4 | 38.3 |
| optimal@10s+aware | 2.2 | -0.7 ± 0.1 | 152 | +6 ± 3 | 155 | 149 | 11031 | +82 ± 14 | 30.0 | 36.3 |
| batched_greedy@30s+aware | 2.9 | -0.1 ± 0.1 | 154 | +8 ± 2 | 155 | 135 | 10957 | +8 ± 8 | 31.2 | 115.0 |
| optimal@30s+aware | 1.7 | -1.3 ± 0.2 | 158 | +12 ± 5 | 159 | 142 | 11090 | +141 ± 20 | 30.0 | 103.0 |

## Per-batch optimality gap (cheapest-edge greedy − optimal, same batch)

| drivers | arm | gap s / batch | batches where greedy is worse | riders / batch |
|---|---|---|---|---|
| 3000 | optimal@10s | 77.0 | 60.6% | 266.0 |
| 3500 | optimal@10s | 257.8 | 78.1% | 75.6 |
| 4000 | optimal@10s | 147.3 | 74.4% | 33.2 |
| 4500 | optimal@10s | 102.0 | 69.9% | 32.6 |
| 5000 | optimal@10s | 75.9 | 66.4% | 32.5 |
| 3000 | optimal@10s+aware | 121.0 | 61.3% | 281.7 |
| 3500 | optimal@10s+aware | 263.5 | 76.9% | 143.0 |
| 4000 | optimal@10s+aware | 294.7 | 76.7% | 48.4 |
| 4500 | optimal@10s+aware | 228.8 | 72.9% | 39.3 |
| 5000 | optimal@10s+aware | 176.8 | 69.8% | 36.3 |
| 3000 | optimal@30s+aware | 854.5 | 91.4% | 324.5 |
| 3500 | optimal@30s+aware | 1532.8 | 89.0% | 201.6 |
| 4000 | optimal@30s+aware | 1695.6 | 87.8% | 121.8 |
| 4500 | optimal@30s+aware | 1449.3 | 86.4% | 107.6 |
| 5000 | optimal@30s+aware | 1193.9 | 85.9% | 103.0 |
