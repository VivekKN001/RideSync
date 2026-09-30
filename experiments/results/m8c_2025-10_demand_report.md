# M8C_2025-10: demand forecast (TLC, Manhattan)

Requests per taxi zone per 15 minutes, full scale. Train: 2024-10-01 to 2025-09-30, test: 2025-10-01 to 2025-10-31 (history for the lag features from 2024-01-01). 66 zones, 62,841,241 requests; a zone-bucket averages 24.9 requests (26.3 in the test period).
WAPE = sum |error| / sum actual. Lower is better.

## 15 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 16.4% | 4.30 |
| last value | 21.5% | 5.65 |
| same time last week | 24.0% | 6.32 |
| same time last year (52 weeks) | 23.7% | 6.22 |
| zone x weekday x time mean | 18.2% | 4.79 |

## 30 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 17.0% | 4.48 |
| last value | 23.7% | 6.23 |
| same time last week | 24.0% | 6.32 |
| same time last year (52 weeks) | 23.7% | 6.22 |
| zone x weekday x time mean | 18.2% | 4.79 |

## 60 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 18.1% | 4.77 |
| last value | 29.0% | 7.63 |
| same time last week | 24.0% | 6.32 |
| same time last year (52 weeks) | 23.7% | 6.22 |
| zone x weekday x time mean | 18.2% | 4.79 |

