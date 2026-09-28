# M6: fare fit (TLC 2024-03, Manhattan)

Median regression of `base_passenger_fare` on trip miles and minutes, fitted on weekday 10:00-15:59 (when Uber's and Lyft's own surge is rarest) of days 1-21 and tested on days 22-31. APE = |error| / fare.

Simulator fare: **$4.09 + $1.96/mile + $0.69/minute**, minimum $8.23; straight-line to road miles x1.34.

- Uber: $3.63 + $2.22/mile + $0.73/minute, minimum $8.30
- Lyft: $4.74 + $1.87/mile + $0.54/minute, minimum $7.39

## Test days

| model | test | mae | median_ape | p90_ape | bias | n |
|---|---|---|---|---|---|---|
| one median fare for every trip | calm hours | $9.12 | 35.1% | 96.1% | -2.98 | 30,000 |
| fitted fare, Uber + Lyft (simulator) | calm hours | $4.97 | 15.5% | 47.5% | -0.78 | 30,000 |
| fitted fare, Uber + Lyft (simulator) | all hours (incl. their surge) | $4.57 | 16.3% | 48.7% | -0.27 | 30,000 |
| Uber trips, Uber + Lyft fit | calm hours | $5.53 | 16.9% | 49.7% | -1.40 | 30,000 |
| Uber trips, own Uber fit | calm hours | $5.63 | 17.6% | 52.0% | -0.41 | 30,000 |
| Lyft trips, Uber + Lyft fit | calm hours | $3.49 | 12.4% | 34.4% | +0.72 | 30,000 |
| Lyft trips, own Lyft fit | calm hours | $3.40 | 11.9% | 31.0% | -1.65 | 30,000 |

## On top of the fare (all hours, mean per trip)

Tolls $0.02, Black Car Fund $0.58, sales tax $1.87, congestion surcharge $2.52: 23.8% on top of the fare. Median rider total $22.98. Taxes and fees are not platform revenue, so the simulator's revenue is fare x multiplier.
