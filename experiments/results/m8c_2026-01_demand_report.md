# M8C_2026-01: demand forecast (TLC, Manhattan)

Requests per taxi zone per 15 minutes, full scale. Train: 2025-01-01 to 2025-12-31, test: 2026-01-01 to 2026-01-31 (history for the lag features from 2024-01-01). 66 zones, 62,230,356 requests; a zone-bucket averages 24.8 requests (24.4 in the test period).
WAPE = sum |error| / sum actual. Lower is better.

## 15 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 17.3% | 4.22 |
| last value | 22.2% | 5.41 |
| same time last week | 34.3% | 8.35 |
| same time last year (52 weeks) | 28.7% | 7.00 |
| zone x weekday x time mean | 26.9% | 6.55 |

## 30 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 18.2% | 4.43 |
| last value | 24.4% | 5.95 |
| same time last week | 34.3% | 8.35 |
| same time last year (52 weeks) | 28.7% | 7.00 |
| zone x weekday x time mean | 26.9% | 6.55 |

## 60 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 19.4% | 4.72 |
| last value | 29.8% | 7.26 |
| same time last week | 34.3% | 8.35 |
| same time last year (52 weeks) | 28.7% | 7.00 |
| zone x weekday x time mean | 26.9% | 6.55 |

