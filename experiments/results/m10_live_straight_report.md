# M10: live over Kafka vs offline, with repositioning and late cancels

Demand `data/processed/trips_2026-07-15_1700_3h_manhattan_f0.1.parquet`, 3 h, 500 drivers, optimal (lsa) every 30 s, cancellation-aware cost, straight travel with noise sigma 0.27; the matcher's repositioning plan (forecast demand) every 5 min, riders who give up on a late driver. 2 seed(s); deltas are paired with offline for the same seed.

Lockstep (live code, zero latency) identical to offline for every seed: **True**

| mode | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | time to match s | Δ trips/h | batches | late cancel % | moves / driver-h |
|---|---|---|---|---|---|---|---|---|---|
| offline | 3.40 | +0.00 | 158.1 | +0.0 | 17.2 | +0.0 | 360 | 1.08 | 0.42 |
| live 10x | 3.42 | +0.02 | 160.0 | +1.9 | 17.4 | -0.2 | 358 | 1.03 | 0.41 |
| live 30x | 3.63 | +0.23 | 160.0 | +1.9 | 17.6 | -2.6 | 358 | 1.22 | 0.41 |

## Where the latency goes (live runs, mean over seeds)

| speed | offer delay, sim s (mean / p99) | tick → batch solved, ms (p50 / p99) | offer → simulator, ms (p50 / p99) | rejected offers % | max lag, sim s | wall s |
|---|---|---|---|---|---|---|
| 10x | 0.23 / 0.42 | 6.0 / 10.2 | 11.5 / 25.5 | 0.00 | 0.6 | 1863 |
| 30x | 0.99 / 18.93 | 6.2 / 17.3 | 11.1 / 28.4 | 1.13 | 3.0 | 620 |

Repositioning moves the simulator received from the matcher (live runs, total): started 2723.
