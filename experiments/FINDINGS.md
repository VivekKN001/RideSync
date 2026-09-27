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

**Next:** the same experiment on OSRM road times (`--travel osrm`), to test whether one-way streets, bridges and
the river edges widen the optimal-vs-greedy gap further.
