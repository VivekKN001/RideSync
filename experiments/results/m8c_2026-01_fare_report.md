# M8C_2026-01: fare fit (TLC, Manhattan)

Median regression of `base_passenger_fare` on trip miles and minutes, fitted on weekday 10:00-15:59 (when Uber's and Lyft's own surge is rarest) of 2025-10-01 to 2025-12-31 and tested on 2026-01-01 to 2026-01-31. APE = |error| / fare.

Simulator fare: **$3.97 + $1.27/mile + $0.84/minute**, minimum $7.79; straight-line to road miles x1.36.

- Uber: $3.54 + $1.25/mile + $0.95/minute, minimum $8.03
- Lyft: $4.46 + $1.75/mile + $0.62/minute, minimum $7.14

## Test days

| model | test | mae | median_ape | p90_ape | bias | n |
|---|---|---|---|---|---|---|
| one median fare for every trip | calm hours | $10.33 | 38.0% | 112.1% | -2.20 | 11,853 |
| fitted fare, Uber + Lyft (simulator) | calm hours | $6.19 | 18.6% | 50.9% | -2.48 | 11,853 |
| fitted fare, Uber + Lyft (simulator) | all hours (incl. their surge) | $6.30 | 19.6% | 53.1% | -2.92 | 30,000 |
| Uber trips, Uber + Lyft fit | calm hours | $6.96 | 19.5% | 52.0% | -3.82 | 8,583 |
| Uber trips, own Uber fit | calm hours | $6.82 | 19.7% | 53.7% | -2.42 | 8,583 |
| Lyft trips, Uber + Lyft fit | calm hours | $4.15 | 16.2% | 46.4% | +1.03 | 3,270 |
| Lyft trips, own Lyft fit | calm hours | $3.82 | 14.6% | 38.1% | -1.20 | 3,270 |

## On top of the fare (2026-01-01 to 2026-01-31, all hours, mean per trip)

Tolls $0.02, Black Car Fund $0.54, sales tax $2.00, congestion surcharge $2.48, congestion pricing (CBD) fee $1.19 (charged on 79% of trips): 27.3% on top of the fare. Median rider total $25.09. Taxes and fees are not platform revenue, so the simulator's revenue is fare x multiplier.
