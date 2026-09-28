# M6: demand forecast (TLC 2024-03, Manhattan)

Requests per taxi zone per 15 minutes, full scale. Train: days 1-21, test: days 22-31. 66 zones, 5,356,107 requests; a zone-bucket averages 27.3 requests (26.9 on test days).
WAPE = sum |error| / sum actual. Lower is better.

## 15 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 16.9% | 4.56 |
| last value | 21.4% | 5.77 |
| same time last week | 27.0% | 7.26 |
| zone x weekday x time mean | 22.4% | 6.03 |

## 30 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 17.7% | 4.77 |
| last value | 23.6% | 6.36 |
| same time last week | 27.0% | 7.26 |
| zone x weekday x time mean | 22.4% | 6.03 |

## 60 minutes ahead

| method | wape | mae |
|---|---|---|
| model (GBT, Poisson) | 18.8% | 5.06 |
| last value | 28.2% | 7.61 |
| same time last week | 27.0% | 7.26 |
| zone x weekday x time mean | 22.4% | 6.03 |

