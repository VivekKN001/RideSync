# M8C_2025-10: fare fit (TLC, Manhattan)

Median regression of `base_passenger_fare` on trip miles and minutes, fitted on weekday 10:00-15:59 (when Uber's and Lyft's own surge is rarest) of 2025-07-01 to 2025-09-30 and tested on 2025-10-01 to 2025-10-31. APE = |error| / fare.

Simulator fare: **$4.05 + $1.64/mile + $0.78/minute**, minimum $7.86; straight-line to road miles x1.35.

- Uber: $4.07 + $1.63/mile + $0.85/minute, minimum $8.29
- Lyft: $3.42 + $2.16/mile + $0.61/minute, minimum $7.30

## Test days

| model | test | mae | median_ape | p90_ape | bias | n |
|---|---|---|---|---|---|---|
| one median fare for every trip | calm hours | $11.09 | 36.5% | 93.2% | -4.95 | 12,249 |
| fitted fare, Uber + Lyft (simulator) | calm hours | $6.73 | 18.6% | 50.6% | -2.48 | 12,249 |
| fitted fare, Uber + Lyft (simulator) | all hours (incl. their surge) | $6.35 | 19.8% | 52.9% | -1.86 | 30,000 |
| Uber trips, Uber + Lyft fit | calm hours | $7.61 | 20.0% | 52.9% | -4.00 | 8,962 |
| Uber trips, own Uber fit | calm hours | $7.51 | 20.7% | 54.3% | -2.57 | 8,962 |
| Lyft trips, Uber + Lyft fit | calm hours | $4.32 | 15.8% | 42.5% | +1.69 | 3,287 |
| Lyft trips, own Lyft fit | calm hours | $3.72 | 12.6% | 34.3% | -0.90 | 3,287 |

## On top of the fare (2025-10-01 to 2025-10-31, all hours, mean per trip)

Tolls $0.03, Black Car Fund $0.57, sales tax $2.11, congestion surcharge $2.50, congestion pricing (CBD) fee $1.21 (charged on 81% of trips): 27.3% on top of the fare. Median rider total $26.18. Taxes and fees are not platform revenue, so the simulator's revenue is fare x multiplier.
