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
