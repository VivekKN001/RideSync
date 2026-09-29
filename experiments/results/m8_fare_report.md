# M8: fare fit (TLC, Manhattan)

Median regression of `base_passenger_fare` on trip miles and minutes, fitted on weekday 10:00-15:59 (when Uber's and Lyft's own surge is rarest) of 2026-04-01 to 2026-06-30 and tested on 2026-07-01 to 2026-07-31. APE = |error| / fare.

Simulator fare: **$3.89 + $1.46/mile + $0.85/minute**, minimum $7.71; straight-line to road miles x1.35.

- Uber: $3.80 + $1.23/mile + $0.94/minute, minimum $7.85
- Lyft: $3.71 + $2.05/mile + $0.67/minute, minimum $7.30

## Test days

| model | test | mae | median_ape | p90_ape | bias | n |
|---|---|---|---|---|---|---|
| one median fare for every trip | calm hours | $10.59 | 37.9% | 117.2% | -2.24 | 12,652 |
| fitted fare, Uber + Lyft (simulator) | calm hours | $6.39 | 20.1% | 52.5% | -1.69 | 12,652 |
| fitted fare, Uber + Lyft (simulator) | all hours (incl. their surge) | $6.02 | 20.3% | 53.8% | -1.44 | 30,000 |
| Uber trips, Uber + Lyft fit | calm hours | $7.14 | 21.8% | 54.8% | -2.55 | 9,599 |
| Uber trips, own Uber fit | calm hours | $7.14 | 22.3% | 58.1% | -1.47 | 9,599 |
| Lyft trips, Uber + Lyft fit | calm hours | $4.00 | 15.6% | 43.7% | +1.00 | 3,053 |
| Lyft trips, own Lyft fit | calm hours | $3.67 | 13.5% | 35.4% | -0.89 | 3,053 |

## On top of the fare (2026-07-01 to 2026-07-31, all hours, mean per trip)

Tolls $0.03, Black Car Fund $0.54, sales tax $1.99, congestion surcharge $2.48, congestion pricing (CBD) fee $1.21 (charged on 81% of trips): 27.4% on top of the fare. Median rider total $25.45. Taxes and fees are not platform revenue, so the simulator's revenue is fare x multiplier.
