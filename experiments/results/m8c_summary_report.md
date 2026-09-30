# M8c: four test months

Each test month's models train on the 12 months before it (October 2025, January 2026, April 2026; ``RIDESYNC_MODELS=data/models_<month>``); July 2026 is M8's (trained on 2025-01..2026-06). Every test day is a mid-month Wednesday, 17:00-20:00, 10% of Manhattan trips, with travel calibrated on that day.

Paired deltas, mean ± 95% CI (Student t over seeds).

## The models on each test month

| test month | demand WAPE, 15 min: model / best baseline | 60 min | ETA MAPE: learned / distance x hour table / base alone | ETA range coverage (target 80%) |
|---|---|---|---|---|
| Oct 2025 (Wed 15th) | 16.4% / 18.2% | 18.1% / 18.2% | 24.8% / 32.0% / 53.1% | 79.3% |
| Jan 2026 (Wed 14th) | 17.3% / 22.2% | 19.4% / 26.9% | 24.7% / 34.0% / 47.2% | 79.4% |
| Apr 2026 (Wed 15th) | 16.6% / 18.5% | 17.6% / 18.5% | 24.3% / 32.7% / 54.8% | 79.8% |
| Jul 2026 (Wed 15th) | 17.8% / 22.4% | 19.0% / 22.4% | 24.8% / 33.4% / 55.6% | 79.5% |

## Batching with the cancellation-aware cost (`optimal@30s+aware`) against instant nearest-driver

| test month | travel | drivers | cancel % (instant) | Δ cancel | Δ trips/h |
|---|---|---|---|---|---|
| Oct 2025 (Wed 15th) | straight-line | 300 | 39.1% | -7.5 ± 1.0 pp | +89 ± 12.0 (+12.2%) |
| Oct 2025 (Wed 15th) | straight-line | 400 | 17.3% | -2.8 ± 0.7 pp | +33 ± 8.1 (+3.4%) |
| Oct 2025 (Wed 15th) | straight-line | 500 | 7.3% | -1.1 ± 0.3 pp | +13 ± 3.5 (+1.2%) |
| Oct 2025 (Wed 15th) | road times | 300 | 40.3% | -4.0 ± 1.5 pp | +48 ± 17.8 (+6.7%) |
| Oct 2025 (Wed 15th) | road times | 400 | 21.5% | -1.7 ± 0.7 pp | +20 ± 8.4 (+2.1%) |
| Oct 2025 (Wed 15th) | road times | 500 | 10.8% | -0.1 ± 0.4 pp | +2 ± 4.6 (+0.2%) |
| Jan 2026 (Wed 14th) | straight-line | 300 | 14.2% | -2.5 ± 0.4 pp | +25 ± 4.4 (+2.9%) |
| Jan 2026 (Wed 14th) | straight-line | 400 | 5.1% | -0.7 ± 0.3 pp | +7 ± 2.9 (+0.7%) |
| Jan 2026 (Wed 14th) | straight-line | 500 | 3.0% | -0.3 ± 0.2 pp | +3 ± 1.9 (+0.3%) |
| Jan 2026 (Wed 14th) | road times | 300 | 17.4% | -1.0 ± 0.5 pp | +10 ± 5.0 (+1.3%) |
| Jan 2026 (Wed 14th) | road times | 400 | 7.8% | +0.2 ± 0.5 pp | -2 ± 5.2 (-0.2%) |
| Jan 2026 (Wed 14th) | road times | 500 | 5.4% | +0.0 ± 0.5 pp | -0 ± 4.5 (-0.0%) |
| Apr 2026 (Wed 15th) | straight-line | 300 | 29.5% | -5.9 ± 0.6 pp | +61 ± 6.2 (+8.4%) |
| Apr 2026 (Wed 15th) | straight-line | 400 | 10.5% | -1.4 ± 0.5 pp | +14 ± 5.0 (+1.5%) |
| Apr 2026 (Wed 15th) | straight-line | 500 | 5.4% | -0.6 ± 0.4 pp | +6 ± 4.2 (+0.6%) |
| Apr 2026 (Wed 15th) | road times | 300 | 30.4% | -3.4 ± 1.0 pp | +35 ± 10.8 (+4.8%) |
| Apr 2026 (Wed 15th) | road times | 400 | 14.5% | -0.8 ± 0.3 pp | +8 ± 2.6 (+0.9%) |
| Apr 2026 (Wed 15th) | road times | 500 | 9.0% | -0.3 ± 0.4 pp | +3 ± 4.6 (+0.4%) |
| Jul 2026 (Wed 15th) | straight-line | 300 | 33.5% | -7.3 ± 0.7 pp | +82 ± 8.3 (+10.9%) |
| Jul 2026 (Wed 15th) | straight-line | 400 | 11.3% | -1.8 ± 0.4 pp | +21 ± 4.5 (+2.1%) |
| Jul 2026 (Wed 15th) | straight-line | 500 | 4.8% | -0.6 ± 0.5 pp | +6 ± 5.6 (+0.6%) |
| Jul 2026 (Wed 15th) | road times | 300 | 34.3% | -4.0 ± 0.9 pp | +45 ± 10.7 (+6.1%) |
| Jul 2026 (Wed 15th) | road times | 400 | 15.6% | -0.9 ± 0.6 pp | +10 ± 6.4 (+1.1%) |
| Jul 2026 (Wed 15th) | road times | 500 | 8.7% | -0.1 ± 0.3 pp | +1 ± 3.8 (+0.1%) |

## Coordinated repositioning (`planned_forecast`, the month's own demand model) against staying put

| test month | drivers | cancel % (none) | Δ cancel | Δ trips/h | Δ empty driving |
|---|---|---|---|---|---|
| Oct 2025 (Wed 15th) | 400 | 17.3% | -0.6 ± 0.4 pp | +7 ± 5.4 | +0.5 ± 0.2 pp |
| Oct 2025 (Wed 15th) | 500 | 8.4% | -1.9 ± 0.4 pp | +23 ± 4.4 | +0.8 ± 0.2 pp |
| Jan 2026 (Wed 14th) | 400 | 6.1% | -2.6 ± 0.7 pp | +26 ± 7.2 | +2.4 ± 0.3 pp |
| Jan 2026 (Wed 14th) | 500 | 4.0% | -2.4 ± 0.3 pp | +23 ± 3.1 | +3.3 ± 0.2 pp |
| Apr 2026 (Wed 15th) | 400 | 11.7% | -1.3 ± 0.4 pp | +14 ± 3.7 | +1.3 ± 0.1 pp |
| Apr 2026 (Wed 15th) | 500 | 6.5% | -2.5 ± 0.6 pp | +25 ± 5.9 | +2.0 ± 0.2 pp |
| Jul 2026 (Wed 15th) | 400 | 12.4% | -0.9 ± 0.7 pp | +10 ± 8.3 | +0.8 ± 0.3 pp |
| Jul 2026 (Wed 15th) | 500 | 6.6% | -2.7 ± 0.3 pp | +30 ± 3.6 | +1.7 ± 0.2 pp |

## Learned ETA (the month's own model) against the distance x hour table, riders cancelling on late drivers, 400 drivers

| test month | tolerance | Δ cancel | Δ trips/h |
|---|---|---|---|
| Oct 2025 (Wed 15th) | 120 s | -8.4 ± 0.4 pp | +100 ± 5.0 (+14.6%) |
| Oct 2025 (Wed 15th) | 180 s | -6.1 ± 0.5 pp | +73 ± 5.4 (+9.8%) |
| Oct 2025 (Wed 15th) | 300 s | -3.4 ± 0.8 pp | +41 ± 9.4 (+5.1%) |
| Jan 2026 (Wed 14th) | 120 s | -6.9 ± 1.2 pp | +68 ± 11.5 (+10.0%) |
| Jan 2026 (Wed 14th) | 180 s | -5.5 ± 0.5 pp | +54 ± 5.1 (+7.4%) |
| Jan 2026 (Wed 14th) | 300 s | -4.1 ± 0.6 pp | +41 ± 6.2 (+5.3%) |
| Apr 2026 (Wed 15th) | 120 s | -8.1 ± 0.6 pp | +83 ± 6.2 (+14.0%) |
| Apr 2026 (Wed 15th) | 180 s | -4.8 ± 0.9 pp | +49 ± 9.1 (+7.4%) |
| Apr 2026 (Wed 15th) | 300 s | -1.1 ± 0.6 pp | +11 ± 6.6 (+1.5%) |
| Jul 2026 (Wed 15th) | 120 s | -8.1 ± 0.7 pp | +92 ± 7.6 (+13.9%) |
| Jul 2026 (Wed 15th) | 180 s | -5.7 ± 0.8 pp | +65 ± 9.6 (+9.0%) |
| Jul 2026 (Wed 15th) | 300 s | -3.3 ± 0.7 pp | +37 ± 7.6 (+4.8%) |
