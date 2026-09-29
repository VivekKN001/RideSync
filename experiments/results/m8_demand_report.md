# M8: demand forecast (TLC, Manhattan)

Requests per taxi zone per 15 minutes, full scale. Train: 2025-01-01 to 2026-06-30, test: 2026-07-01 to 2026-07-31 (history for the lag features from 2024-01-01). 66 zones, 90,722,546 requests; a zone-bucket averages 24.8 requests (24.2 in the test period).
WAPE = sum |error| / sum actual. Lower is better.

## 15 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 17.8% | 4.30 |
| last value | 23.1% | 5.60 |
| same time last week | 28.5% | 6.89 |
| same time last year (52 weeks) | 26.3% | 6.37 |
| zone x weekday x time mean | 22.4% | 5.43 |

## 30 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 18.3% | 4.44 |
| last value | 25.4% | 6.15 |
| same time last week | 28.5% | 6.89 |
| same time last year (52 weeks) | 26.3% | 6.37 |
| zone x weekday x time mean | 22.4% | 5.43 |

## 60 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 19.0% | 4.60 |
| last value | 30.2% | 7.31 |
| same time last week | 28.5% | 6.89 |
| same time last year (52 weeks) | 26.3% | 6.37 |
| zone x weekday x time mean | 22.4% | 5.43 |

