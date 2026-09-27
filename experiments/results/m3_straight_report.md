# M3: live over Kafka vs offline, same config and seeds

Demand `data/processed/trips_2024-03-13_1700_3h_manhattan_f0.1.parquet`, 3 h, 500 drivers, optimal (lsa) every 30 s, cancellation-aware cost, straight travel. 2 seed(s); deltas are paired with offline for the same seed.

Lockstep (live code, zero latency) identical to offline for every seed: **True**

| mode | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | time to match s | Δ trips/h | batches |
|---|---|---|---|---|---|---|---|
| offline | 3.92 | +0.00 | 181.3 | +0.0 | 17.9 | +0.0 | 362 |
| live 10x | 3.77 | -0.14 | 182.7 | +1.4 | 18.6 | +1.6 | 362 |
| live 30x | 3.88 | -0.04 | 183.1 | +1.9 | 19.9 | +0.4 | 362 |
| live 60x | 3.81 | -0.11 | 185.5 | +4.2 | 21.4 | +1.2 | 362 |

## Where the latency goes (live runs, mean over seeds)

| speed | offer delay, sim s (mean / p99) | tick → batch solved, ms (p50 / p99) | offer → simulator, ms (p50 / p99) | rejected offers % | max lag, sim s | wall s |
|---|---|---|---|---|---|---|
| 10x | 0.60 / 0.92 | 19.9 / 53.4 | 27.2 / 35.4 | 0.00 | 0.5 | 1537 |
| 30x | 1.96 / 2.83 | 22.3 / 52.5 | 26.6 / 31.9 | 0.00 | 4.1 | 513 |
| 60x | 4.37 / 6.50 | 15.4 / 38.2 | 37.8 / 51.7 | 0.03 | 1.9 | 258 |
