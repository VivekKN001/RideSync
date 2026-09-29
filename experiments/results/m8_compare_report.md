# M8: which training data predicts July 2026 best?

Same models, features and settings in every arm; only the training period differs. All tested on July 2026 (Manhattan, TLC high-volume FHV). `18mo_1mo_rows` is the 18 months cut down to June 2026's number of rows: the span without the volume.

## Demand, 15 minutes ahead (requests per zone per 15 min)

| arm | training rows | WAPE | MAE |
|---|---|---|---|
| mar2024 | 196,416 | 18.19% | 4.41 |
| jun2026 | 190,080 | 17.88% | 4.33 |
| 18mo | 3,459,456 | 17.78% | 4.30 |
| baseline: last value |  | 23.11% | 5.60 |
| baseline: same time last week |  | 28.48% | 6.89 |
| baseline: same time last year (52 weeks) |  | 26.29% | 6.37 |
| baseline: zone x weekday x time mean |  | 22.43% | 5.43 |
| 18mo_1mo_rows | 190,080 | 17.95% | 4.35 |
| 30mo | 5,778,432 | 17.71% | 4.29 |

## Demand, 60 minutes ahead (requests per zone per 15 min)

| arm | training rows | WAPE | MAE |
|---|---|---|---|
| mar2024 | 196,416 | 19.91% | 4.82 |
| jun2026 | 190,080 | 19.18% | 4.64 |
| 18mo | 3,459,456 | 18.99% | 4.60 |
| baseline: last value |  | 30.17% | 7.31 |
| baseline: same time last week |  | 28.48% | 6.89 |
| baseline: same time last year (52 weeks) |  | 26.29% | 6.37 |
| baseline: zone x weekday x time mean |  | 22.43% | 5.43 |
| 18mo_1mo_rows | 190,080 | 19.22% | 4.65 |
| 30mo | 5,778,432 | 18.92% | 4.58 |

## ETA correction (straight-line base, live traffic), trip time pickup to dropoff

| arm | training trips | MAE s | median APE | p90 APE | bias s |
|---|---|---|---|---|---|
| baseline: base model alone |  | 506 | 38.8% | 126.7% | +257 |
| mar2024 | 92,989 | 220 | 19.1% | 52.2% | -44 |
| jun2026 | 89,991 | 217 | 18.9% | 52.8% | -26 |
| 18mo | 1,637,811 | 212 | 18.4% | 51.1% | -32 |
| 18mo_1mo_rows | 89,991 | 218 | 18.9% | 52.5% | -36 |
| 30mo | 2,735,702 | 212 | 18.3% | 51.2% | -33 |
