# M4: watermark allowance vs late events

3 h Manhattan run, 500 drivers, optimal every 30 s. 20% of rider and driver events delayed (lognormal, median 300 ms, sigma 1.0): observed p50 307 ms, p95 1580 ms, p99 3089 ms, max 12.3 s. Ticks are never delayed.

Row readiness is measured over the demand window (17:00-20:00), while the simulator ticks every second.

| allowance | late events | requests missing from counts | row ready after minute ends (p50 / p95) |
|---|---|---|---|
| 0 s | 0.10% | 0.12% | 0.00 s / 0.00 s |
| 0.25 s | 0.01% | 0.03% | 1.00 s / 1.00 s |
| 0.5 s | 0.01% | 0.03% | 1.00 s / 1.00 s |
| 1 s | 0.01% | 0.03% | 1.00 s / 1.00 s |
| 2 s | 0.01% | 0.03% | 2.00 s / 2.00 s |
| 5 s | 0.00% | 0.00% | 5.00 s / 5.00 s |
