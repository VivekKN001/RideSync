# RideSync

Real-time ride-hailing dispatch: batched optimal bipartite matching (Hungarian) vs greedy,
evaluated on a measurable cost function (wait time, cancellations, driver idle time).

## Status

| Milestone | Scope | State |
|---|---|---|
| M0 | Hungarian from scratch, greedy baselines, deterministic offline simulator, metrics | done |
| M1 | Experiment: gain vs fleet density and batch window; cancellation-aware cost | done — `experiments/FINDINGS.md` |
| M2 | OSRM + NYC (Manhattan) road network + TLC demand replay | done — `experiments/FINDINGS.md` |
| M3 | Kafka + live simulator + matcher service | done — live mode below; results in `experiments/FINDINGS.md` |
| M4 | PyFlink job: driver state, windowed zone features, late events | done — stream features below; lateness experiment in `experiments/FINDINGS.md` |
| M5 | Postgres sink, ClickHouse, Grafana, deck.gl live map | done — screens below |
| M6 | ML: OSRM ETA correction feeding edge costs, demand forecast, surge policy + elasticity | code done — models and results: `python -m ridesync.ml.train`, then the M6 experiments |
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

## Stream features and screens (M4, M5)

```
 Kafka world topics ──► Flink (ridesync.stream) ──► zone-features  (per zone, per simulated minute)
                    │                           └─► late-events    (after the watermark; never silently dropped)
                    ├─► ClickHouse (Kafka engine, no code) ── event history + time series ──┐
                    ├─► ridesync.sinks.postgres ── Postgres trip ledger (one row per trip) ──┴─► Grafana :3000
                    └─► ridesync.web ── WebSocket ──► live map :8000 (deck.gl)
```

- **Flink is only the runner.** The feature logic is plain Python (`ridesync/stream/features.py`) with a reference
  runner that the tests and the lateness experiment use; the Flink job produces the same rows. Driver state is Flink
  keyed state, checkpointed every 10 s. Watermarks are per partition with a bounded lateness (`--lateness-ms`,
  default 2 s).
- **Trip ledger.** A consumer group with committed offsets; offsets are committed after the database transaction,
  every write is an idempotent upsert, and a trip never moves back to an earlier status, so redelivered or
  out-of-order events leave it right.
- **Dashboards are code.** `docker/grafana/make_dashboard.py` writes `docker/grafana/dashboards/ridesync.json`,
  which Grafana loads on start: waiting riders, matches per minute, cancel rate, pickup ETA, solve time, offer
  round trip, a zone table and a run picker.

## Demand forecast, surge pricing, ETA correction (M6)

```
 TLC March 2024 ──► ridesync.ml.train ──► demand.joblib   zone x 15 min, gradient-boosted trees (Poisson), 15/30/60 min ahead
                                     ├──► fare.json       median regression of TLC fares on miles and minutes
                                     └──► eta_<base>.joblib  learned log(observed / base) on top of any travel model

 app open ──► price for the rider's zone ──► requests with probability m^-elasticity, else leaves or retries once
              ▲ every 5 min: pressure = (expected demand + waiting) / free supply ──► multiplier, steps of 0.25, capped
              └ expected demand: reactive (last 15 min of opens) or forecast (the demand model)
```

- **Train on days 1–21, test on 22–31.** Every model is compared with simple baselines on the held-out days
  (reports in `experiments/results/m6_*_report.md`). Demand features only read buckets before the forecast time;
  a test blanks the future to prove it.
- **Surge with a fixed fleet only rations.** No drivers come when prices rise (that would be M7), so surge trades
  trips for fewer cancellations and more revenue per trip. The question it can answer: do forecast-driven prices beat
  prices from current counts? Elasticity has no public data, so it's an assumption and the experiment varies it.
  All riders' price draws are seeded per rider, so arms stay paired. With surge off the simulator is unchanged (tested).
- **The ETA model learns from trips and is applied to every drive.** TLC records pickup-to-dropoff times, not the
  driver's drive to the rider, so the correction assumes both slow down the same way. Trip ends are placed on random
  points in their zones, which puts a floor under the accuracy; the report measures it.
- **World vs belief.** `SimConfig.belief` is what the matcher assumes, `travel` is what drives really take
  (optionally with per-trip noise, `travel.noise_sigma`). With the two equal the simulator is unchanged (tested).
- **Live.** The simulator prices zones itself (identical to offline, tested in lockstep), or with `--price-service`
  takes prices from `ridesync.live.pricing`, which reads Flink's zone features (app opens, free drivers, waiting)
  and publishes `zone-prices`. Grafana shows the multiplier, expected vs actual demand and the surging zones.

## Layout

```
ridesync/matching/   hungarian.py (Kuhn-Munkres, from scratch), problem.py (cost model), strategies.py
ridesync/dispatch/   one batch: available drivers, ETA matrix, problem, solve (shared by offline and live)
ridesync/sim/        discrete-event simulator: config, demand, engine, metrics
ridesync/live/       schema (topics, messages), bus (in-memory) + kafka_bus, world (live simulator),
                     matcher (service), lockstep, sim (CLI), topics
ridesync/stream/     zones (point -> taxi zone, dependency-free), features (zone features + reference runner),
                     job (PyFlink wiring)
ridesync/sinks/      postgres (trip ledger)
ridesync/ml/         M6 models: demand (forecast), fare (fit), eta (correction + noisy world), train (CLI)
ridesync/pricing.py  surge policy, rider conversion, demand estimates (shared by the simulator and live pricing)
ridesync/live/pricing.py  live pricing service: zone-features -> zone-prices
ridesync/web/        live map server (FastAPI + WebSocket) and page
ridesync/viz/        replay page for offline runs
docker/              Flink image, ClickHouse schema, Postgres schema, Grafana provisioning + dashboard generator
ridesync/geo.py      Route + travel-time interface, straight-line model
ridesync/routing/    OSRM client (table/route, chunking, cache, fallback), calibration, model factory
ridesync/data/       downloads; TLC high-volume FHV trips -> demand slices with in-zone coordinates
ridesync/experiments.py   parallel grid runner + paired comparisons
experiments/         experiment scripts and results
tests/               Hungarian vs brute force / scipy, strategy validity, simulator invariants,
                     live == offline in lockstep, matcher restart, Kafka end to end (when a broker is up),
                     zone features vs simulator totals, trip ledger against real Postgres (when it is up)
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
pip install -e ".[dev,live,web]" pandas pyarrow geopandas requests
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
docker compose --profile routing up -d osrm
python -m ridesync.routing.calibrate --slice data/processed/trips_2024-03-13_1700_3h_manhattan_f0.1.parquet --osrm http://localhost:5000
python experiments/m2_real_demand.py --travel osrm

# M3: live mode over Kafka
docker compose up -d kafka
python -m ridesync.live.matcher                              # terminal 1: runs until Ctrl+C
python -m ridesync.live.sim --speed 10 --compare-offline     # terminal 2: 3 h of demand in ~18 min
python experiments/m3_live_vs_offline.py                     # offline vs lockstep vs live at 10x/30x/60x

# M4: stream features (Flink UI on http://localhost:8081)
docker build -t ridesync-flink:1.20 docker/flink             # once
python -m ridesync.stream.zones                              # once: data/processed/taxi_zones.json
docker compose --profile stream up -d                        # Flink jobmanager + taskmanager
docker compose --profile stream run --rm flink-submit         # add --lateness-ms 5000 etc. to change the job
python experiments/m4_lateness.py                            # watermark allowance vs late events

# M6: models (TLC March 2024 in data/raw), then experiments
pip install -e ".[ml]"
python -m ridesync.ml.train demand                           # ~1-2 min
python -m ridesync.ml.train fare                             # ~1 min
python -m ridesync.ml.train eta --base straight              # ~3 min
python experiments/m6_surge.py                               # no surge vs reactive vs forecast, 3 fleets x 3 elasticities
python experiments/m6_eta_sim.py                             # matcher belief: global multiplier vs learned ETA
docker compose --profile routing up -d osrm                  # optional: the same on road times
python -m ridesync.ml.train eta --base osrm
python experiments/m6_eta_sim.py --base osrm

# M6 live: surge on the live map and dashboards
python -m ridesync.live.sim --speed 20 --surge forecast                  # the simulator prices zones itself
python -m ridesync.live.pricing                                          # or: a separate pricing service (needs Flink)
python -m ridesync.live.sim --speed 20 --surge forecast --price-service

# M5: storage and screens
docker compose --profile storage up -d                       # Grafana on http://localhost:3000
# existing ClickHouse volume from before M6 (init scripts run only once):
docker compose exec -T clickhouse clickhouse-client --multiquery < docker/clickhouse/init/02_m6.sql
python -m ridesync.sinks.postgres                            # terminal: trip ledger
python -m ridesync.web                                       # terminal: live map on http://localhost:8000
python -m ridesync.live.matcher                              # terminal
python -m ridesync.live.sim --speed 20                       # then watch the map and dashboards

# Done for the day: stop everything (a plain `docker compose stop` only stops Kafka)
docker compose --profile "*" stop
```
