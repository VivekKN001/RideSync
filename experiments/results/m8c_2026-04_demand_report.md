# M8C_2026-04: demand forecast (TLC, Manhattan)

Requests per taxi zone per 15 minutes, full scale. Train: 2025-04-01 to 2026-03-31, test: 2026-04-01 to 2026-04-30 (history for the lag features from 2024-04-01). 66 zones, 61,696,196 requests; a zone-bucket averages 24.6 requests (25.8 in the test period).
WAPE = sum |error| / sum actual. Lower is better.

## 15 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 16.6% | 4.28 |
| last value | 22.0% | 5.66 |
| same time last week | 23.9% | 6.17 |
| same time last year (52 weeks) | 25.2% | 6.48 |
| zone x weekday x time mean | 18.5% | 4.77 |

## 30 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 17.0% | 4.39 |
| last value | 24.1% | 6.21 |
| same time last week | 23.9% | 6.17 |
| same time last year (52 weeks) | 25.2% | 6.48 |
| zone x weekday x time mean | 18.5% | 4.77 |

## 60 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 17.6% | 4.54 |
| last value | 29.3% | 7.54 |
| same time last week | 23.9% | 6.17 |
| same time last year (52 weeks) | 25.2% | 6.48 |
| zone x weekday x time mean | 18.5% | 4.77 |

