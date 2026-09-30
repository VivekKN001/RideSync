# M8C_2026-04: fare fit (TLC, Manhattan)

Median regression of `base_passenger_fare` on trip miles and minutes, fitted on weekday 10:00-15:59 (when Uber's and Lyft's own surge is rarest) of 2026-01-01 to 2026-03-31 and tested on 2026-04-01 to 2026-04-30. APE = |error| / fare.

Simulator fare: **$4.14 + $1.62/mile + $0.80/minute**, minimum $7.55; straight-line to road miles x1.35.

- Uber: $3.96 + $1.46/mile + $0.89/minute, minimum $7.91
- Lyft: $3.91 + $2.08/mile + $0.64/minute, minimum $6.94

## Test days

| model | test | mae | median_ape | p90_ape | bias | n |
|---|---|---|---|---|---|---|
| one median fare for every trip | calm hours | $10.42 | 36.5% | 99.6% | -3.89 | 11,571 |
| fitted fare, Uber + Lyft (simulator) | calm hours | $6.04 | 18.5% | 50.1% | -1.74 | 11,571 |
| fitted fare, Uber + Lyft (simulator) | all hours (incl. their surge) | $5.83 | 19.8% | 52.5% | -1.60 | 30,000 |
| Uber trips, Uber + Lyft fit | calm hours | $6.75 | 20.0% | 51.8% | -2.61 | 8,712 |
| Uber trips, own Uber fit | calm hours | $6.75 | 20.8% | 54.9% | -1.53 | 8,712 |
| Lyft trips, Uber + Lyft fit | calm hours | $3.89 | 14.6% | 42.8% | +0.93 | 2,859 |
| Lyft trips, own Lyft fit | calm hours | $3.60 | 12.0% | 35.5% | -1.13 | 2,859 |

## On top of the fare (2026-04-01 to 2026-04-30, all hours, mean per trip)

Tolls $0.03, Black Car Fund $0.55, sales tax $2.02, congestion surcharge $2.48, congestion pricing (CBD) fee $1.19 (charged on 79% of trips): 27.2% on top of the fare. Median rider total $25.91. Taxes and fees are not platform revenue, so the simulator's revenue is fare x multiplier.
