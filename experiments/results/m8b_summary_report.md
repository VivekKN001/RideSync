# M8b: the experiments on more days and at full scale

Same code and settings as M2, M6 (surge) and M7, with the M8 models (trained 2025-01..2026-06) and straight-line travel calibrated on 15 July 2026 unless marked road times (OSRM × 2.26). Every day is in the models' test month. 10% of Manhattan trips unless marked full scale (fleets 10x). Paired deltas, mean ± 95% CI (Student t over seeds).

## Batching with the cancellation-aware cost (`optimal@30s+aware`) against instant nearest-driver (M2)

| day | drivers | cancel % (instant) | Δ cancel | Δ trips/h | Δ wait_all s |
|---|---|---|---|---|---|
| Wed 13 Mar 2024, 17-20 (M2) | 300 | 28.3% | -6.5 ± 1.1 pp | +74 ± 12.5 (+9.1%) | +54 ± 6.7 |
| Wed 13 Mar 2024, 17-20 (M2) | 350 | 14.6% | -2.5 ± 0.4 pp | +28 ± 4.2 (+2.9%) | +43 ± 6.6 |
| Wed 13 Mar 2024, 17-20 (M2) | 400 | 7.9% | -1.3 ± 0.6 pp | +15 ± 6.6 (+1.5%) | +27 ± 7.9 |
| Wed 13 Mar 2024, 17-20 (M2) | 450 | 5.4% | -0.7 ± 0.3 pp | +8 ± 3.8 (+0.8%) | +19 ± 1.8 |
| Wed 13 Mar 2024, 17-20 (M2) | 500 | 4.1% | -0.5 ± 0.2 pp | +6 ± 2.5 (+0.6%) | +17 ± 1.5 |
| Wed 15 Jul 2026, 17-20 | 300 | 33.5% | -7.3 ± 0.7 pp | +82 ± 8.3 (+10.9%) | +53 ± 6.8 |
| Wed 15 Jul 2026, 17-20 | 350 | 21.0% | -4.2 ± 0.5 pp | +47 ± 6.0 (+5.3%) | +48 ± 2.5 |
| Wed 15 Jul 2026, 17-20 | 400 | 11.3% | -1.8 ± 0.4 pp | +21 ± 4.5 (+2.1%) | +31 ± 7.1 |
| Wed 15 Jul 2026, 17-20 | 450 | 7.0% | -0.8 ± 0.3 pp | +9 ± 3.5 (+0.9%) | +24 ± 3.1 |
| Wed 15 Jul 2026, 17-20 | 500 | 4.8% | -0.6 ± 0.5 pp | +6 ± 5.6 (+0.6%) | +21 ± 4.0 |
| Wed 15 Jul 2026, 07-10 | 300 | 31.0% | -1.6 ± 0.8 pp | +17 ± 7.9 (+2.4%) | +35 ± 2.4 |
| Wed 15 Jul 2026, 07-10 | 350 | 24.7% | +0.9 ± 0.4 pp | -9 ± 4.4 (-1.2%) | +34 ± 6.3 |
| Wed 15 Jul 2026, 07-10 | 400 | 22.7% | +0.8 ± 0.6 pp | -9 ± 5.9 (-1.1%) | +33 ± 5.5 |
| Wed 15 Jul 2026, 07-10 | 450 | 21.0% | +1.0 ± 0.5 pp | -11 ± 5.3 (-1.3%) | +31 ± 6.5 |
| Wed 15 Jul 2026, 07-10 | 500 | 19.8% | +0.5 ± 0.4 pp | -5 ± 4.4 (-0.6%) | +34 ± 5.7 |
| Sat 18 Jul 2026, 20-23 | 300 | 36.3% | -7.3 ± 0.8 pp | +86 ± 9.4 (+11.4%) | +50 ± 6.7 |
| Sat 18 Jul 2026, 20-23 | 350 | 24.3% | -4.9 ± 0.8 pp | +58 ± 10.0 (+6.5%) | +47 ± 3.3 |
| Sat 18 Jul 2026, 20-23 | 400 | 15.8% | -2.8 ± 0.4 pp | +34 ± 5.2 (+3.4%) | +39 ± 3.9 |
| Sat 18 Jul 2026, 20-23 | 450 | 9.9% | -1.8 ± 0.6 pp | +21 ± 7.6 (+2.0%) | +29 ± 3.4 |
| Sat 18 Jul 2026, 20-23 | 500 | 6.5% | -1.0 ± 0.6 pp | +11 ± 6.9 (+1.0%) | +27 ± 4.1 |
| Wed 15 Jul 2026, 17-20, full scale | 3000 | 29.7% | -10.7 ± 0.4 pp | +1211 ± 49.3 (+15.3%) | +2 ± 1.4 |
| Wed 15 Jul 2026, 17-20, full scale | 3500 | 14.8% | -5.3 ± 0.4 pp | +601 ± 47.1 (+6.2%) | +6 ± 4.2 |
| Wed 15 Jul 2026, 17-20, full scale | 4000 | 6.3% | -2.4 ± 0.0 pp | +272 ± 5.5 (+2.6%) | +13 ± 1.6 |
| Wed 15 Jul 2026, 17-20, full scale | 4500 | 4.4% | -2.0 ± 0.4 pp | +220 ± 40.4 (+2.0%) | +10 ± 1.8 |
| Wed 15 Jul 2026, 17-20, full scale | 5000 | 2.9% | -1.3 ± 0.2 pp | +141 ± 19.9 (+1.3%) | +12 ± 4.8 |
| Wed 13 Mar 2024, 17-20, road times (M2) | 300 | 28.8% | -3.8 ± 0.5 pp | +43 ± 6.1 (+5.4%) | +59 ± 7.7 |
| Wed 13 Mar 2024, 17-20, road times (M2) | 350 | 17.8% | -2.0 ± 0.4 pp | +22 ± 4.0 (+2.4%) | +39 ± 3.3 |
| Wed 13 Mar 2024, 17-20, road times (M2) | 400 | 11.7% | -0.6 ± 0.3 pp | +6 ± 3.5 (+0.6%) | +26 ± 4.1 |
| Wed 13 Mar 2024, 17-20, road times (M2) | 450 | 8.5% | -0.2 ± 0.4 pp | +2 ± 4.4 (+0.2%) | +20 ± 2.0 |
| Wed 13 Mar 2024, 17-20, road times (M2) | 500 | 6.9% | -0.2 ± 0.4 pp | +2 ± 4.9 (+0.2%) | +19 ± 2.5 |
| Wed 15 Jul 2026, 17-20, road times | 300 | 34.3% | -4.0 ± 0.9 pp | +45 ± 10.7 (+6.1%) | +61 ± 6.3 |
| Wed 15 Jul 2026, 17-20, road times | 400 | 15.6% | -0.9 ± 0.6 pp | +10 ± 6.4 (+1.1%) | +30 ± 4.5 |
| Wed 15 Jul 2026, 17-20, road times | 500 | 8.7% | -0.1 ± 0.3 pp | +1 ± 3.8 (+0.1%) | +23 ± 2.3 |
| Wed 15 Jul 2026, 07-10, road times | 300 | 34.4% | -0.6 ± 1.1 pp | +7 ± 11.9 (+1.0%) | +46 ± 7.8 |
| Wed 15 Jul 2026, 07-10, road times | 400 | 25.3% | +2.3 ± 1.1 pp | -24 ± 11.5 (-3.0%) | +38 ± 12.5 |
| Wed 15 Jul 2026, 07-10, road times | 500 | 22.0% | +2.1 ± 1.0 pp | -22 ± 10.7 (-2.7%) | +35 ± 6.7 |
| Sat 18 Jul 2026, 20-23, road times | 300 | 38.4% | -4.2 ± 1.5 pp | +50 ± 17.5 (+6.9%) | +72 ± 7.8 |
| Sat 18 Jul 2026, 20-23, road times | 400 | 20.6% | -1.9 ± 0.8 pp | +23 ± 9.7 (+2.4%) | +44 ± 11.6 |
| Sat 18 Jul 2026, 20-23, road times | 500 | 10.2% | -0.4 ± 0.4 pp | +5 ± 4.4 (+0.5%) | +25 ± 5.8 |
| Wed 15 Jul 2026, 17-20, full scale, road times | 3000 | 27.3% | -7.3 / -7.4 pp (per seed) | +822 / +834 (+10.1%) | +20 / +21 |
| Wed 15 Jul 2026, 17-20, full scale, road times | 4000 | 8.9% | -1.8 / -1.4 pp (per seed) | +202 / +161 (+1.8%) | +17 / +17 |
| Wed 15 Jul 2026, 17-20, full scale, road times | 5000 | 5.6% | -0.8 / -1.1 pp (per seed) | +92 / +125 (+1.0%) | +15 / +18 |

## Optimal against greedy on the same 30 s batches and cost, full scale

Paired `optimal@30s+aware` − `batched_greedy@30s+aware`. With 2 seeds each seed's delta is shown, not an interval.

| travel | drivers | seeds | Δ trips/h | Δ cancel | Δ wait_all s | batches where greedy is worse |
|---|---|---|---|---|---|---|
| straight-line | 3000 | 3 | +22 ± 31.6 | -0.2 ± 0.3 pp | +4 ± 2.6 | 91% |
| straight-line | 3500 | 3 | +75 ± 42.4 | -0.7 ± 0.4 pp | +17 ± 1.9 | 89% |
| straight-line | 4000 | 3 | +249 ± 27.8 | -2.2 ± 0.2 pp | +8 ± 2.1 | 88% |
| straight-line | 4500 | 3 | +187 ± 25.8 | -1.7 ± 0.2 pp | +4 ± 2.7 | 86% |
| straight-line | 5000 | 3 | +133 ± 21.2 | -1.2 ± 0.2 pp | +4 ± 2.7 | 86% |
| road times (OSRM) | 3000 | 2 | +28 / +22 (per seed) | -0.3 / -0.2 pp | +5 / +5 | 93% |
| road times (OSRM) | 4000 | 2 | +191 / +148 (per seed) | -1.7 / -1.3 pp | +7 / +7 | 88% |
| road times (OSRM) | 5000 | 2 | +91 / +112 (per seed) | -0.8 / -1.0 pp | +4 / +4 | 87% |

## Learned ETA against a distance × hour table, riders cancelling on late drivers (M6)

400 drivers. Lateness tolerance = median time past the quote a rider waits before cancelling.

| day | tolerance | cancel % (table) | Δ cancel | Δ trips/h | abs ETA error s (table → learned) |
|---|---|---|---|---|---|
| Wed 13 Mar 2024 (M6) | 120 s | 35.7% | -7.7 ± 0.4 pp | +87 ± 5.0 (+12.0%) | 55 → 55 |
| Wed 13 Mar 2024 (M6) | 180 s | 31.3% | -6.7 ± 1.4 pp | +75 ± 16.1 (+9.7%) | 67 → 61 |
| Wed 13 Mar 2024 (M6) | 300 s | 25.5% | -3.9 ± 1.2 pp | +44 ± 13.1 (+5.3%) | 87 → 68 |
| Wed 15 Jul 2026, 17-20 | 120 s | 41.6% | -8.1 ± 0.7 pp | +92 ± 7.6 (+13.9%) | 57 → 57 |
| Wed 15 Jul 2026, 17-20 | 180 s | 36.3% | -5.7 ± 0.8 pp | +65 ± 9.6 (+9.0%) | 72 → 62 |
| Wed 15 Jul 2026, 17-20 | 300 s | 31.1% | -3.3 ± 0.7 pp | +37 ± 7.6 (+4.8%) | 94 → 70 |
| Wed 15 Jul 2026, 17-20, road times | 120 s | 64.1% | -20.4 ± 0.9 pp | +231 ± 10.4 (+56.9%) | 81 → 64 |
| Wed 15 Jul 2026, 17-20, road times | 180 s | 54.5% | -14.1 ± 1.0 pp | +159 ± 11.5 (+31.0%) | 107 → 70 |
| Wed 15 Jul 2026, 17-20, road times | 300 s | 42.5% | -4.9 ± 1.1 pp | +55 ± 12.2 (+8.5%) | 145 → 78 |

## Surge pricing against none, elasticity 0.5 (M6)

| day | drivers | arm | Δ trips/h | Δ cancel | Δ wait_all s | Δ revenue/h |
|---|---|---|---|---|---|---|
| Wed 13 Mar 2024 (M6) | 300 | surge_forecast | -43 ± 5.7 | -11.0 ± 0.7 pp | -46 ± 4.8 | +13902 ± 504.8 |
| Wed 13 Mar 2024 (M6) | 300 | surge_reactive | -43 ± 3.6 | -11.0 ± 0.4 pp | -46 ± 6.0 | +14219 ± 261.2 |
| Wed 13 Mar 2024 (M6) | 400 | surge_forecast | -32 ± 5.5 | -1.6 ± 0.6 pp | -23 ± 6.6 | +3842 ± 529.6 |
| Wed 13 Mar 2024 (M6) | 400 | surge_reactive | -31 ± 5.5 | -2.0 ± 0.4 pp | -23 ± 5.5 | +4041 ± 432.4 |
| Wed 13 Mar 2024 (M6) | 500 | surge_forecast | -7 ± 4.0 | -0.5 ± 0.2 pp | -4 ± 2.6 | +1195 ± 208.9 |
| Wed 13 Mar 2024 (M6) | 500 | surge_reactive | -11 ± 4.3 | -0.4 ± 0.3 pp | -5 ± 2.5 | +1192 ± 199.6 |
| Wed 15 Jul 2026, 17-20 | 300 | surge_forecast | -34 ± 2.2 | -11.5 ± 0.4 pp | -34 ± 4.2 | +15195 ± 555.9 |
| Wed 15 Jul 2026, 17-20 | 300 | surge_reactive | -37 ± 2.1 | -11.6 ± 0.4 pp | -35 ± 7.0 | +15542 ± 432.0 |
| Wed 15 Jul 2026, 17-20 | 400 | surge_forecast | -25 ± 5.7 | -3.0 ± 0.3 pp | -26 ± 3.0 | +5079 ± 428.2 |
| Wed 15 Jul 2026, 17-20 | 400 | surge_reactive | -28 ± 5.4 | -3.3 ± 0.3 pp | -30 ± 2.2 | +5620 ± 364.8 |
| Wed 15 Jul 2026, 17-20 | 500 | surge_forecast | -9 ± 1.5 | -0.6 ± 0.2 pp | -5 ± 1.2 | +1260 ± 187.4 |
| Wed 15 Jul 2026, 17-20 | 500 | surge_reactive | -14 ± 3.2 | -0.6 ± 0.2 pp | -7 ± 1.5 | +1478 ± 233.0 |
| Wed 15 Jul 2026, 07-10 | 300 | surge_forecast | -24 ± 4.8 | -6.8 ± 0.5 pp | -19 ± 5.0 | +7484 ± 449.0 |
| Wed 15 Jul 2026, 07-10 | 300 | surge_reactive | -26 ± 4.7 | -6.6 ± 0.5 pp | -20 ± 5.0 | +7581 ± 506.4 |
| Wed 15 Jul 2026, 07-10 | 400 | surge_forecast | -14 ± 6.4 | -5.2 ± 0.5 pp | -10 ± 3.2 | +5459 ± 511.4 |
| Wed 15 Jul 2026, 07-10 | 400 | surge_reactive | -15 ± 4.3 | -5.1 ± 0.5 pp | -9 ± 2.4 | +5552 ± 308.1 |
| Wed 15 Jul 2026, 07-10 | 500 | surge_forecast | -13 ± 3.7 | -4.2 ± 0.4 pp | -13 ± 1.4 | +4545 ± 325.9 |
| Wed 15 Jul 2026, 07-10 | 500 | surge_reactive | -15 ± 2.9 | -4.1 ± 0.4 pp | -12 ± 2.3 | +4654 ± 370.7 |
| Sat 18 Jul 2026, 20-23 | 300 | surge_forecast | -41 ± 8.7 | -12.6 ± 0.7 pp | -26 ± 4.2 | +18009 ± 423.4 |
| Sat 18 Jul 2026, 20-23 | 300 | surge_reactive | -41 ± 6.6 | -12.5 ± 0.8 pp | -28 ± 4.1 | +18069 ± 245.6 |
| Sat 18 Jul 2026, 20-23 | 400 | surge_forecast | -37 ± 4.7 | -5.4 ± 0.7 pp | -37 ± 4.6 | +9103 ± 763.8 |
| Sat 18 Jul 2026, 20-23 | 400 | surge_reactive | -39 ± 5.3 | -5.9 ± 0.6 pp | -41 ± 5.5 | +9373 ± 844.7 |
| Sat 18 Jul 2026, 20-23 | 500 | surge_forecast | -18 ± 5.9 | -1.4 ± 0.5 pp | -15 ± 4.1 | +3018 ± 582.2 |
| Sat 18 Jul 2026, 20-23 | 500 | surge_reactive | -20 ± 4.0 | -1.5 ± 0.5 pp | -18 ± 3.7 | +3272 ± 568.3 |

## Repositioning idle drivers against staying put (M7)

| day | drivers | arm | cancel % (none) | Δ cancel | Δ trips/h | Δ pickup s | Δ empty driving |
|---|---|---|---|---|---|---|---|
| Wed 27 Mar 2024 (M7) | 300 | drift | 28.5% | -0.5 ± 0.6 pp | +6 ± 6.8 | +1 ± 5.1 | +0.1 ± 0.6 pp |
| Wed 27 Mar 2024 (M7) | 300 | planned_forecast | 28.5% | -0.7 ± 1.0 pp | +9 ± 12.5 | +0 ± 5.7 | -0.0 ± 0.5 pp |
| Wed 27 Mar 2024 (M7) | 400 | drift | 12.0% | +0.5 ± 0.5 pp | -5 ± 6.3 | +2 ± 4.2 | +0.5 ± 0.3 pp |
| Wed 27 Mar 2024 (M7) | 400 | planned_forecast | 12.0% | -0.9 ± 0.3 pp | +10 ± 3.2 | -8 ± 3.1 | +0.6 ± 0.3 pp |
| Wed 27 Mar 2024 (M7) | 500 | drift | 6.9% | +0.4 ± 0.6 pp | -5 ± 7.7 | +11 ± 4.6 | +1.7 ± 0.2 pp |
| Wed 27 Mar 2024 (M7) | 500 | planned_forecast | 6.9% | -3.5 ± 0.4 pp | +41 ± 4.3 | -37 ± 3.3 | +1.3 ± 0.2 pp |
| Wed 15 Jul 2026, 17-20 | 300 | drift | 29.1% | -0.5 ± 0.6 pp | +5 ± 6.5 | -3 ± 3.0 | +0.5 ± 0.4 pp |
| Wed 15 Jul 2026, 17-20 | 300 | planned_forecast | 29.1% | -0.1 ± 0.8 pp | +1 ± 9.4 | -2 ± 2.8 | +0.4 ± 0.2 pp |
| Wed 15 Jul 2026, 17-20 | 400 | drift | 12.4% | +0.4 ± 0.6 pp | -4 ± 7.2 | -5 ± 4.3 | +1.0 ± 0.4 pp |
| Wed 15 Jul 2026, 17-20 | 400 | planned_forecast | 12.4% | -0.9 ± 0.7 pp | +10 ± 8.3 | -6 ± 6.3 | +0.8 ± 0.3 pp |
| Wed 15 Jul 2026, 17-20 | 500 | drift | 6.6% | -0.4 ± 0.4 pp | +5 ± 4.6 | -1 ± 3.4 | +2.2 ± 0.2 pp |
| Wed 15 Jul 2026, 17-20 | 500 | planned_forecast | 6.6% | -2.7 ± 0.3 pp | +30 ± 3.6 | -34 ± 3.5 | +1.7 ± 0.2 pp |
| Wed 15 Jul 2026, 07-10 | 300 | drift | 32.1% | -0.3 ± 0.5 pp | +3 ± 4.9 | +2 ± 2.9 | +0.9 ± 0.3 pp |
| Wed 15 Jul 2026, 07-10 | 300 | planned_forecast | 32.1% | -1.6 ± 0.6 pp | +17 ± 6.3 | -5 ± 5.2 | +1.0 ± 0.3 pp |
| Wed 15 Jul 2026, 07-10 | 400 | drift | 25.4% | -0.1 ± 0.6 pp | +1 ± 6.8 | +6 ± 4.4 | +2.2 ± 0.2 pp |
| Wed 15 Jul 2026, 07-10 | 400 | planned_forecast | 25.4% | -5.6 ± 0.5 pp | +59 ± 4.7 | -30 ± 4.7 | +2.7 ± 0.4 pp |
| Wed 15 Jul 2026, 07-10 | 500 | drift | 22.2% | +0.1 ± 1.2 pp | -1 ± 12.8 | +10 ± 4.4 | +3.1 ± 0.3 pp |
| Wed 15 Jul 2026, 07-10 | 500 | planned_forecast | 22.2% | -7.2 ± 1.3 pp | +76 ± 13.1 | -45 ± 6.5 | +3.2 ± 0.3 pp |
| Sat 18 Jul 2026, 20-23 | 300 | drift | 32.0% | +0.1 ± 0.7 pp | -1 ± 8.7 | -0 ± 5.7 | -0.0 ± 0.3 pp |
| Sat 18 Jul 2026, 20-23 | 300 | planned_forecast | 32.0% | -0.1 ± 0.6 pp | +1 ± 7.2 | +0 ± 3.7 | +0.0 ± 0.3 pp |
| Sat 18 Jul 2026, 20-23 | 400 | drift | 15.5% | -0.5 ± 0.3 pp | +5 ± 3.5 | +0 ± 5.3 | +0.6 ± 0.4 pp |
| Sat 18 Jul 2026, 20-23 | 400 | planned_forecast | 15.5% | -0.7 ± 0.2 pp | +8 ± 2.2 | -5 ± 6.6 | +0.6 ± 0.4 pp |
| Sat 18 Jul 2026, 20-23 | 500 | drift | 7.7% | +0.1 ± 0.3 pp | -1 ± 3.0 | +0 ± 3.4 | +1.1 ± 0.3 pp |
| Sat 18 Jul 2026, 20-23 | 500 | planned_forecast | 7.7% | -1.9 ± 0.3 pp | +22 ± 3.7 | -23 ± 5.7 | +1.1 ± 0.3 pp |
