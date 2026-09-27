# RideSync

Real-time ride-hailing dispatch: batched optimal bipartite matching (Hungarian) vs greedy,
evaluated on a measurable cost function (wait time, cancellations, driver idle time).

## Status

| Milestone | Scope | State |
|---|---|---|
| M0 | Hungarian from scratch, greedy baselines, deterministic offline simulator, metrics | done |
| M1 | Experiment: gain vs fleet density and batch window; cancellation-aware cost | done — `experiments/FINDINGS.md` |
| M2 | OSRM + NYC (Manhattan) road network + TLC demand replay | real demand + calibration done; OSRM runs pending Docker |
| M3 | Kafka + live simulator + matcher service | done — live mode below; results in `experiments/FINDINGS.md` |
| M4 | PyFlink job: driver state, windowed zone features, late events, matching snapshots | |
| M5 | Postgres sink, ClickHouse, Grafana, deck.gl live map | |
| M6 | ML: OSRM ETA correction feeding edge costs, demand forecast, surge policy + elasticity | |
| M7 | (optional) Idle-driver repositioning | |

## Decisions

- **City:** NYC (Manhattan + nearby), because TLC trip data exists. Mysore has good OSM coverage but no public
  trip-level demand data, so its ML would be trained on our own simulator's output. The city stays pluggable
  (road extract + zones + demand source).
- **Stream processing:** PyFlink. The shared `ridesync` package must stay compatible with Python 3.10.
- **Commitment:** no reassignment after dispatch. On-trip drivers finishing within 120 s count as supply
  ("chaining"): their ETA = time left on the trip + drive from the dropoff.
- **Surge:** demand forecast + pricing policy + simulated price elasticity (no public surge data exists to train on).
- **Two modes, one matcher:** offline (seeded, faster than real time) for experiments; live
  (Kafka/Flink) for the demo. Both build and solve batches with `ridesync.dispatch`.

## Live mode (M3)

```
 live simulator (world, authoritative)                 matcher service (proposes)
 same engine as offline, paced at N× wall clock ──► rider-events   ──► rebuilds drivers + waiting riders
                                                ──► driver-events  ──► from events; every interval_s of
 applies or rejects each offer ◄── dispatch-offers ◄──────────────     event time: ETA matrix → strategy
                               ──► offer-responses ─────────────────►  → offers
                                                    dispatch-batches ◄ (batch stats, for M5)
```

- **Event time, per-partition watermarks.** The simulator writes a `tick` to every partition of the world topics
  after all events up to that time. The matcher's watermark is the minimum over partitions (Kafka only orders
  within a partition), and a batch fires once the watermark passes its boundary. Results don't depend on the
  speed factor, only on how long offers take to come back.
- **The simulator decides, the matcher proposes.** Offers for a rider who already cancelled or a driver who is no
  longer free are rejected with a reason. Offers have ids, so a redelivered offer is a no-op. While an offer is
  unanswered its rider and driver are left out of later batches (15 s timeout on both sides).
- **Restarts.** The matcher reads all topics from the beginning without dispatching ("catch-up"), which restores
  the current run's state, including offers in flight, and then resumes at the next batch boundary.
- **Proof that live loses nothing:** `ridesync.live.lockstep` runs both over an in-memory bus with zero latency.
  Its results are bit-identical to the offline simulator (tested with 1 and 3 partitions and with reordered
  delivery), so any live-vs-offline difference is latency alone.

## Layout

```
ridesync/matching/   hungarian.py (Kuhn-Munkres, from scratch), problem.py (cost model), strategies.py
ridesync/dispatch/   one batch: available drivers, ETA matrix, problem, solve (shared by offline and live)
ridesync/sim/        discrete-event simulator: config, demand, engine, metrics
ridesync/live/       schema (topics, messages), bus (in-memory) + kafka_bus, world (live simulator),
                     matcher (service), lockstep, sim (CLI), topics
ridesync/geo.py      Route + travel-time interface, straight-line model
ridesync/routing/    OSRM client (table/route, chunking, cache, fallback), calibration, model factory
ridesync/data/       downloads; TLC high-volume FHV trips -> demand slices with in-zone coordinates
ridesync/experiments.py   parallel grid runner + paired comparisons
experiments/         experiment scripts and results
tests/               Hungarian vs brute force / scipy, strategy validity, simulator invariants,
                     live == offline in lockstep, matcher restart, Kafka end to end (when a broker is up)
```

## Cost model

Matching rider *r* to driver *d* costs the pickup ETA. Leaving *r* unmatched costs
`max_pickup_eta + λ·waited(r)`. That forces the maximum number of matches, and λ > 0 favours long-waiting
riders (fairness). The optimal solve pads the matrix with one "stay unmatched" column per rider.

## Assumptions the metrics depend on (see `ridesync/sim/config.py`)

- Riders cancel if unmatched after a lognormal patience (median 5 min), or right away if the quoted ETA
  exceeds a lognormal tolerance (median 10 min). No cancellation while the driver is en route.
- Drivers accept 95% of offers; a declined (rider, driver) pair is never offered again.
- Travel time: synthetic runs use great-circle × 1.35 at 25 km/h; real-demand runs use a speed fitted to TLC trip
  times (13.5 km/h), or OSRM × a fitted multiplier. Vehicles move along the route geometry over time.
- TLC gives zones, not coordinates, so trip endpoints are sampled uniformly inside their zone polygons.
- Accept/decline and demand draws are seeded per run, so every strategy faces identical riders and
  decisions (common random numbers) and comparisons are paired.

## Run

```
python -m venv .venv && .venv\Scripts\activate
pip install -e ".[dev,live]" pandas pyarrow geopandas requests
pytest

# M0/M1: synthetic city, no external data
python experiments/m1_batching.py
python experiments/m1b_cancel_aware.py
python experiments/m1c_batch_gap.py

# M2: real Manhattan demand
python -m ridesync.data.fetch --tlc 2024-03 --osm            # TLC trips + zones, NYC OSM extract
python -m ridesync.data.tlc --date 2024-03-13 --start 17:00 --hours 3 --boroughs Manhattan --sample-frac 0.1
python -m ridesync.routing.calibrate --slice data/processed/trips_2024-03-13_1700_3h_manhattan_f0.1.parquet
python experiments/m2_real_demand.py --travel straight

# M2 with the road network (Docker)
docker compose --profile prep run --rm osrm-prep             # one-off, ~5 min
docker compose up -d osrm
python -m ridesync.routing.calibrate --slice data/processed/trips_2024-03-13_1700_3h_manhattan_f0.1.parquet --osrm http://localhost:5000
python experiments/m2_real_demand.py --travel osrm

# M3: live mode over Kafka
docker compose up -d kafka
python -m ridesync.live.matcher                              # terminal 1: runs until Ctrl+C
python -m ridesync.live.sim --speed 10 --compare-offline     # terminal 2: 3 h of demand in ~18 min
python experiments/m3_live_vs_offline.py                     # offline vs lockstep vs live at 10x/30x/60x
```
