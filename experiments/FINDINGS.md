# Findings so far (synthetic city, straight-line travel times)

Setup: Manhattan-shaped synthetic city, 1,200 requests/h, fleets of 250–450 drivers, 8 paired seeds per arm.
Full tables: `results/m1_report.md`, `results/m1b_report.md`, `results/m1c_report.md`.

## 1. Batching is the big lever, and only under scarcity (M1)

| Fleet | Batching vs immediate nearest-driver |
|---|---|
| 250 (undersupplied) | cancellations 41% → ~29%, +18–21% trips/h |
| 300 (tight) | 30 s window: −6.5 pp cancellations, +77 trips/h, but +33 s wait |
| 400+ (oversupplied) | no benefit; each extra second of window becomes extra wait |

Immediate greedy fails under scarcity because a freed driver goes to the *oldest* waiting rider no matter how far
away they are. Long pickups follow, and then cancellations on the quoted ETA.

## 2. The objective matters more than the solver (M1b)

A cancellation-aware edge cost (`e + V·P(cancel | e)`, and only match when that beats waiting) gives e.g. at
300 drivers, 10 s window: cancellations 21.3% → 17.5%, trips/h 931 → 976. **Greedy with the same cost gets
the same gain.** The optimal solver and cheapest-edge-first greedy stay within noise of each other in every
setting.

Belief sensitivity: overestimating cancellation (pessimistic belief) did as well or slightly better than the true
belief; underestimating it (optimistic) lost most of the gain. When the model is uncertain, lean pessimistic.

## 3. Why optimal ≈ greedy here (M1c)

Solving each batch with both, the optimal assignment beats cheapest-edge-first greedy by only 4–14 s of total
pickup time per batch, and it's strictly better in only 5–16% of batches. By contrast it beats FIFO
nearest-driver greedy by 350–700 s per batch under scarcity. The loss comes from greedy *by arrival order*, not
from greedy itself.

Likely cause: straight-line distance with a uniform speed is a nearly Euclidean metric, and cheapest-edge-first
greedy is known to be near-optimal on such instances.
**Hypothesis for M2:** a real road network (one-way streets, bridges, the river edges, park transverses) breaks
that geometry and creates more conflicts inside a batch. That is where the optimal solver should start to pay off.
We'll rerun M1b/M1c on OSRM times with real TLC demand to test it.

## Honest framing for the project

"Batched, cancellation-aware dispatch beats immediate nearest-driver dispatch by X% on trips/hour under scarcity;
the optimal assignment adds Y% over a well-designed greedy on real road networks." Y needs to be measured, not
assumed.

---

# M2 — real Manhattan demand (TLC replay), calibrated straight-line times

Demand: Uber/Lyft requests from Manhattan to Manhattan, Wed 2024-03-13 17:00–20:00, 10% sample
(~1,110 requests/h in the slice, ~11,100/h real). Travel: straight-line fitted to observed trip times
(3.75 m/s with detour 1.35, i.e. 13.5 km/h, which matches the real median). Full tables: `results/m2_straight_report.md`.

**Calibration anchor.** Real Uber wait (request → driver on scene) is mean 164 s, p50 140 s. The simulator's
immediate-greedy baseline hits that at ~500 drivers for the 10% slice. Caveat: sampling demand *and* fleet at
10% lowers spatial density, which lengthens pickups and shrinks batches compared with full scale. So "500" is not
an estimate of the real fleet, and full-scale effects need a run at a higher sample fraction.

**Real demand is clustered, and that gives the optimal solver work to do.** Paired optimal − greedy, same cost,
6 seeds (95% CI):

| arm | 400 drivers | 450 drivers | 500 drivers |
|---|---|---|---|
| @10s, plain | +2.1 ± 3.1 trips/h | +1.9 ± 1.0 trips/h, −0.17 ± 0.09 pp cancel | +1.9 ± 1.2 trips/h, −0.17 ± 0.11 pp |
| @30s, cancellation-aware | **+6.7 ± 3.5 trips/h, −0.59 ± 0.31 pp** | **+4.7 ± 2.5, −0.42 ± 0.22 pp** | **+3.3 ± 2.1, −0.30 ± 0.18 pp** |

With 30 s batches, greedy's batch solution is strictly worse in 27–44% of batches, by 32–73 s of total pickup time
each. That's a real edge, but small (≈0.3–0.6% more trips). The large effects still come from batching and the
cancellation-aware objective (e.g. 300 drivers: −6 pp cancellations, +69 trips/h vs immediate greedy).

## M2 on OSRM road times

Same demand, seeds and arms, with travel times from OSRM on the NYC road network × 2.09 (fitted so OSRM matches
observed TLC trip times). Full tables: `results/m2_osrm_report.md`.

**Road times did not widen the optimal-vs-greedy gap. They erased it at the trip level.** Paired optimal − greedy,
@30s cancellation-aware, 6 seeds (t-interval over paired seeds):

| | 300 drivers | 350 | 400 | 450 | 500 |
|---|---|---|---|---|---|
| trips/h | +0.7 ± 6.2 | +2.1 ± 2.5 | +2.3 ± 6.7 | +0.2 ± 5.1 | +3.3 ± 2.2 |
| cancel pp | −0.1 ± 0.5 | −0.2 ± 0.2 | −0.2 ± 0.6 | −0.0 ± 0.5 | −0.3 ± 0.2 |

Batch by batch, greedy is still worse in 30–41% of 30 s batches, by 24–46 s of pickup time: about the same share
as with straight-line times. The saving is real per batch, but it doesn't turn into trips: a few seconds of pickup
disappear against 4–6.5 minute pickups on real roads.

**Batching and the cancellation-aware objective still matter, but less.** At 300 drivers, @30s aware vs immediate
greedy: −3.8 pp cancellations and +43 trips/h (straight-line: −6.5 pp, +74). The gain shrinks as the fleet grows and
is gone by 450 drivers. Road pickups are slower than the straight-line model predicts (immediate greedy, 500 drivers:
231 s vs 164 s for Uber), so the same fleet is scarcer, and a longer pickup leaves less for a batch to save.

**Updated framing:** "Batched, cancellation-aware dispatch gives −4 pp cancellations and +5% trips/h over
immediate nearest-driver under scarcity on real Manhattan roads. The optimal assignment beats greedy in a third of
batches, but on trips/h it's within noise (≤ 0.3%)." The case for the Hungarian solver is correctness and
predictability per batch, not throughput.

---

# M3: live over Kafka vs offline

`experiments/m3_live_vs_offline.py`, `results/m3_straight_report.md`. Same config as M2 (3 h Manhattan slice, 500
drivers, optimal every 30 s, cancellation-aware cost, straight-line travel), 2 seeds, deltas paired per seed.
The simulator and a separate matcher process talk over Kafka, paced at N simulated seconds per wall second, so a
wall-clock delay of d costs d × N simulated seconds. Higher speeds magnify latency. A real deployment runs at 1×.

**Lockstep == offline.** The live code over a zero-latency in-memory bus is identical to the offline simulator
for both seeds, so any difference below comes only from latency.

| mode | cancel % | Δ cancel pp | wait_all s | Δ wait_all s | time to match s | Δ trips/h |
|---|---|---|---|---|---|---|
| offline | 3.92 | — | 181.3 | — | 17.9 | — |
| live 10× | 3.77 | −0.14 | 182.7 | +1.4 | 18.6 | +1.6 |
| live 30× | 3.88 | −0.04 | 183.1 | +1.9 | 19.9 | +0.4 |
| live 60× | 3.81 | −0.11 | 185.5 | +4.2 | 21.4 | +1.2 |

**Going live costs a few seconds of wait and nothing else.** The wait grows with speed (+1.4 → +4.2 s), and it
tracks the offer delay (0.6 / 2.0 / 4.4 sim s at 10× / 30× / 60×). Cancel rate and trips/h move within noise, the
number of batches is identical, and almost no offers are rejected for stale state (≤ 0.03%).

**The pipeline itself is fast and constant in wall time.** From tick to solved batch takes 15–22 ms p50 (≤ 53 ms
p99), and an offer takes 27–38 ms p50 (≤ 52 ms p99) to reach the simulator, at every speed. Only the conversion
to simulated seconds changes. At 1× that is well under 0.1 s of delay against a 30 s batch window, so a real-time
deployment should match the offline numbers.

---

# M4: stream features (PyFlink) and late events

The Flink job (`ridesync/stream/job.py`) turns `rider-events` + `driver-events` into per-zone, per-minute features
(requests, matches, cancellations, completed trips, free drivers, average wait and pickup ETA) on
`zone-features`. Events that arrive after the watermark go to `late-events`. The logic is plain Python in
`ridesync/stream/features.py`, and Flink only runs it.

**Flink == reference.** On a live run, every row Flink produced that has counts is identical to the reference
runner's. Flink adds ~48 empty rows: single minutes with no events, between two active minutes of the same zone
(it fills gaps, the reference skips them). This quirk is harmless.

**How long to wait for late events** (`experiments/m4_lateness.py`, `results/m4_lateness_report.md`). A 3 h run
with 20% of events delayed like a phone network (lognormal, p50 0.3 s, p99 3 s, max 12 s):

| allowance | late events | requests missing from counts | row delay after minute ends |
|---|---|---|---|
| 0 s | 0.10% | 0.12% | 0 s |
| 0.25–1 s | 0.01% | 0.03% | 1 s |
| 2 s | 0.01% | 0.03% | 2 s |
| 5 s | 0.00% | 0.00% | 5 s |

Delays are quantised to the simulator's 1 s tick. Even zero allowance loses only 0.1% of events, because only the
tail of a 20% slice arrives after the next tick. A 1 s allowance cuts the loss 10×, at a cost of 1 s. Going past
that buys almost nothing until 5 s. The job defaults to 2 s (`--lateness-ms`) as a margin for real networks that
are worse than this model. Nothing is silently dropped either way: the rest lands on `late-events`.

---

# M6: demand forecast, surge pricing, ETA correction

Models are trained on TLC March 2024 (Manhattan): days 1–21 for training, days 22–31 for testing. Reports:
`results/m6_demand_report.md`, `m6_fare_report.md`, `m6_eta_straight_report.md`, `m6_surge_report.md`,
`m6_eta_sim_straight_report.md`.

## Demand forecast (6a)

Requests per taxi zone per 15 minutes at full scale (66 zones, 5.36 M requests), predicted by a Poisson GBT
(scikit-learn HistGradientBoosting). WAPE on the test days (lower is better):

| horizon | GBT | last value | same time last week | zone × weekday × time mean |
|---|---|---|---|---|
| 15 min | **16.9%** | 21.4% | 27.0% | 22.4% |
| 30 min | **17.7%** | 23.6% | 27.0% | 22.4% |
| 60 min | **18.8%** | 28.2% | 27.0% | 22.4% |

The model beats the best baseline by 4.5–5.5 pp, and the gap grows with the horizon: "last value" decays fast
while the GBT loses only 1.9 pp from 15 to 60 minutes.

## Fares

The fare is a median regression of the TLC base fare on miles and minutes, fitted on weekday 10:00–15:59
(when Uber's and Lyft's own surge is rarest) on days 1–21 and tested on days 22–31: **$4.09 + $1.96/mile +
$0.69/minute**, minimum $8.23. These fares drive the revenue columns below. `results/m6_fare_report.md`:

| fare model (test days) | MAE | median APE | p90 APE |
|---|---|---|---|
| one median fare for every trip | $9.12 | 35.1% | 96.1% |
| **fitted formula, Uber + Lyft (simulator)** | **$4.97** | **15.5%** | 47.5% |
| formula fitted per company: Uber / Lyft | $5.63 / $3.40 | 17.6% / 11.9% | 52.0% / 31.0% |
| GBT with zones and company, calm hours (scratch check) | $4.60 | 13.4% | 44.7% |
| GBT with time of day as well, all hours (learns their surge) | $4.23 | 14.1% | 47.4% |

**The formula is close to what TLC data can predict.** On unseen days it errs by $4.97 (the $4.87 measured on
its own training trips was not overfit). A flexible model that also knows both zones and the company gains only
$0.37. Adding time of day gets to $4.23, but only by learning Uber's and Lyft's own surge, which the simulator
must not copy because it prices surge itself. Per-company fits don't help. Lyft tracks a rate card closely (12%
median error); Uber doesn't (17–18%, even fitted on its own), consistent with Uber's upfront, route-based
pricing. The remaining ~$4.50 comes from things TLC doesn't record: the quoted route, promotions and
per-rider pricing. Riders also pay 23.8% on top of the fare (sales tax, congestion surcharge, Black Car Fund,
tolls; median total $22.98). That isn't platform revenue, so simulated revenue stays fare × multiplier.

## Surge pricing (6b): with a fixed fleet, surge rations demand

Same 3 h slice, optimal @30 s, cancellation-aware. Every 5 minutes, each zone gets a multiplier from
pressure = (expected demand over 15 min + waiting riders) / free drivers, pooled over zones within 2 km. Riders
accept a price with probability m^−ε. Half of those who decline leave; the other half retry once. 6 seeds,
paired against no surge. Rows are forecast-driven surge vs no surge (reactive is the same within noise):

| drivers | ε | no-surge cancel | Δ cancel pp | Δ wait_all s | Δ trips/h | Δ revenue/h | surged trips |
|---|---|---|---|---|---|---|---|
| 300 | 0.3 | 21.8% | −7.4 | −22 | −28 ± 5 (−3.2%) | +102% | 87% |
| 300 | 0.8 | 21.8% | −13.8 | −74 | −56 ± 6 (−6.4%) | +48% | 67% |
| 400 | 0.5 | 6.5% | −1.6 | −23 | −32 ± 4 (−3.0%) | +18% | 29% |
| 500 | 0.5 | 3.5% | −0.5 | −4 | −7 ± 3 (−0.7%) | +5% | 8% |

**Calibrating the trigger.** The first version priced each zone alone, with the surge starting at pressure 1.
It surged 43–91% of trips in every cell, including 51% at 500 drivers, where cancellations are only 3.5% and a
third of the fleet sits idle. The diagnostic (`pricing.elasticity = 0`, so prices change nothing) showed why.
Per zone, a 10% slice has 2–3 riders per 15 minutes and 0–1 free drivers, so a third of demand at 500 drivers
came from zones with *no* free driver at that moment, while idle drivers waited one zone over. Pooling over
2 km turns this into a signal that tracks scarcity: median pressure is about 2 at 500 drivers and about 20 at
300, compared with 2 vs 4 per zone. The threshold (4) and slope (0.2) put the first 0.25 step at pressure 5.25
and the 2.5× cap at 11.5. The first version's full results are in the git history (`fbd7962`).

**Surge now scales with scarcity.** At 500 drivers it barely fires (8% of trips, −0.7% trips/h). At 300 drivers
it surges most trips and cuts cancellations from 21.8% to 8–14%.

**It still never adds trips.** The fleet is fixed, so higher prices cannot attract more drivers. Trips/h falls
0.6–6.4% and the gain is queue quality: fewer cancellations and shorter waits, plus the multiplier's revenue.
Showing surge increasing throughput would need a driver-supply response, which this simulator does not model.

**The forecast still doesn't beat reacting to current demand.** Forecast − reactive stays within noise in
every cell (≤ 0.4 pp cancel, ≤ 4 trips/h). Reprices happen every 5 minutes, so reactive demand is at most
about 5 minutes stale, and a 16.9% vs 21.4% WAPE difference changes few 0.25-step decisions. The forecast would
matter for a slower lever, such as moving drivers ahead of demand (M7).

## ETA correction (6c)

Offline accuracy on 200 k test trips (pickup-to-dropoff time), `results/m6_eta_{straight,osrm}_report.md`:

| method | straight-line base MAPE | OSRM base MAPE | OSRM median APE | OSRM p90 APE |
|---|---|---|---|---|
| base alone (global calibration) | 51.8% | 40.8% | 30.6% | 84.3% |
| base × pickup zone × hour table | 39.9% | 34.2% | 26.0% | 68.8% |
| base × learned correction (GBT), no live traffic | 24.8% | 24.6% | 18.1% | 50.5% |
| **base × learned correction + live traffic** | **24.2%** | **24.0%** | **17.7%** | **49.3%** |

**The learned correction halves the error**, and it clearly beats a lookup table.

**Road times help the raw base, but not the corrected model.** OSRM is 11 pp better before correction. After
the correction the two bases end up within 0.2 pp of each other: from a zone and an hour, the model already
learns what the road network adds at this level.

**Live traffic helps a little.** `TrafficFeed` gives the model recent speeds, measured from trips that have
already finished (strictly before the request's 5-minute bucket, so no future trips leak in):
- city-wide speed and trip count over the last 30 minutes;
- speed over the last 60 minutes of trips that started in the pickup zone;
- speed over the last 60 minutes of trips that ended in the dropoff zone.

These features cut the error by 0.6 pp and the p90 error by 1.2 pp. In the simulator the same table acts as
the live feed. A deployment would compute it in Flink from `driver-events`.

**The model is at the limit of zone-level data.** As a ceiling, we measured an oracle that predicts each test
trip's time from other *actual* trips between the same two zones, in the same half hour of the same day. It
knows the future, and it only covers the busiest 35% of zone pairs, which are the easiest. It reaches 22.4%
MAPE when its median includes the trip's own time, and 28.6% with a leave-one-out mean. The model's 24.0% on
*all* trips sits between the two. Trips between the same zones in the same half hour really do vary this much,
and placing a trip at random points in its zones already moves the base time by ~14%. Doing better needs
exact coordinates, which public TLC data doesn't have. More features or tuning won't get there.

**In the simulator** (`m6_eta_sim.py`, straight base, 400 drivers, 6 seeds, paired): the world drives on the
corrected model plus noise, and the matcher believes either the global base or the learned model.

| matcher belief | \|ETA error\| s | mean error s | late > 2 min | cancel % | wait_all s | trips/h |
|---|---|---|---|---|---|---|
| global multiplier | 266 | +260 | 78.9% | 12.8 | 512 | 979 |
| learned ETA | 74 (−191 ± 2) | +12 | 12.7% | 19.9 (+7.0 ± 0.4) | 332 (−179 ± 4) | 900 (−79 ± 5) |

Honest quotes cut the ETA error by 72%. The share of pickups more than 2 minutes late drops from 79% to 13%,
and the average rider waits 179 s less. The cancellation and trips/h columns look worse, but that's a known
simulator artifact: riders cancel on a long *quote* but never while the driver is on the way. The global
matcher quotes 4.3 minutes too optimistically, so riders accept and then wait 512 s on average. The learned
matcher quotes truthfully, and some riders decline up front. In reality, many of the misled riders would cancel
mid-pickup. The fair comparison is quote accuracy and wait, and there the learned ETA clearly wins.

**With riders who give up on late drivers, the learned ETA wins on every measure** (`riders.enroute_cancel`,
`results/m6_eta_sim_straight_late_report.md`). A matched rider whose driver hasn't arrived by the quote plus a
lateness tolerance cancels, and the driver stops where it is. No public data exists for that tolerance, so it
runs at three medians (lognormal, σ 0.5). Paired, 6 seeds, 400 drivers:

| lateness tolerance (median) | global multiplier: cancel / trips/h | learned ETA: cancel / trips/h | Δ trips/h |
|---|---|---|---|
| 2 min | 69.0% / 348 | 28.0% / 809 | **+461 ± 6** |
| 3 min | 55.4% / 501 | 24.6% / 847 | **+346 ± 14** |
| 5 min | 37.2% / 705 | 21.6% / 881 | **+176 ± 8** |

The earlier cancellation result really was the artifact. Once an optimistic quote costs something, a matcher
that believes one city-wide speed at rush hour loses a third to two thirds of its riders to late drivers:
late cancellations are 35–69% of requests, against 2–11% with the learned ETA. How large the effect is depends
on the tolerance. That the learned ETA wins does not. The global arm is an extreme case: calibrated over all
hours, it is 4.3 minutes optimistic at 17:00–20:00. A real platform would at least use per-hour
calibration. (`wait_all` looks better for the global arm at short tolerances only because riders who cancel
stop waiting.)

**Framing:** "A GBT demand forecast beats the best baseline by ~5 pp WAPE. A learned ETA correction with
live traffic halves travel-time error (24% MAPE, at the limit of zone-level data). In simulation it cuts
late pickups from 79% to 13%, and when riders give up on late drivers it adds 25–130% trips/h. Surge with a fixed fleet trades
throughput for shorter queues and fewer cancellations, mostly where drivers are scarce. Its real benefit
depends on a driver-supply response, which is out of scope."
