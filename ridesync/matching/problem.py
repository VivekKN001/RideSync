"""The matching problem handed to every strategy, and its cost model.

One dispatch batch is a set of waiting riders and available drivers with a
pickup-ETA matrix ``eta[r, d]`` in seconds (``inf`` = infeasible).

Cost model
----------
Think of it as maximizing expected value. A completed trip is worth ``V``
seconds of pickup time (``trip_value_s``). If a quoted ETA ``e`` makes the
rider cancel with probability ``p(e)``, then matching r to d has expected
benefit ``V * (1 - p(e)) - e``, and leaving r unmatched this batch has benefit 0
(the rider stays in the pool for the next batch). Minimizing negated benefit,
shifted by the constant V, gives:

    edge cost       c[r, d] = e + V * p(e)
    unmatched cost  U_r     = V + wait_weight * waited_s(r)

An edge is only *allowed* if ``e <= max_pickup_eta_s`` and ``c[r, d] < U_r``,
meaning it beats waiting for the next batch.

- Without a cancellation model (``p = 0``) and with ``V = max_pickup_eta_s``,
  every feasible edge beats waiting, so the solver maximizes the number of
  matches and then minimizes total ETA (the original M0 model).
- With a cancellation model, the solver declines matches the rider would
  probably cancel. That's where optimal matching can beat "match everyone now".

``p(e)`` is the matcher's *belief* about rider ETA tolerance, a lognormal
CDF. Offline it is set to the population-level truth; in M6 it becomes a
learned model. ``wait_weight > 0`` favours long-waiting riders (fairness).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.special import ndtr


@dataclass(frozen=True)
class CancelBelief:
    """Belief that a rider cancels on seeing pickup ETA e: P(tolerance < e), tolerance ~ lognormal."""

    median_s: float = 600.0
    sigma: float = 0.4

    def prob(self, eta_s: np.ndarray) -> np.ndarray:
        with np.errstate(divide="ignore"):
            z = (np.log(np.maximum(eta_s, 1e-9)) - np.log(self.median_s)) / self.sigma
        return ndtr(z)


@dataclass(frozen=True)
class CostParams:
    max_pickup_eta_s: float = 900.0
    wait_weight: float = 0.0  # >0 favours long-waiting riders (fairness); M1 shows it raises mean wait
    trip_value_s: Optional[float] = None  # V; defaults to max_pickup_eta_s
    cancel: Optional[CancelBelief] = None  # None = ignore quote cancellations (M0 model)

    @property
    def value_s(self) -> float:
        return self.max_pickup_eta_s if self.trip_value_s is None else self.trip_value_s


@dataclass
class MatchingProblem:
    eta: np.ndarray            # (R, D) pickup ETA seconds, inf where infeasible
    waited_s: np.ndarray       # (R,) seconds each rider has already waited
    request_order: np.ndarray  # (R,) rank by request time, 0 = oldest
    params: CostParams
    cost: np.ndarray           # (R, D) edge cost, inf where not allowed

    @property
    def shape(self) -> tuple[int, int]:
        return self.eta.shape

    def unmatched_cost(self) -> np.ndarray:
        return self.params.value_s + self.params.wait_weight * self.waited_s

    def allowed(self) -> np.ndarray:
        return np.isfinite(self.cost)

    def total_cost(self, pairs: list[tuple[int, int]]) -> float:
        """Objective value of a solution, used to compare strategies on one batch."""
        matched = np.zeros(self.shape[0], dtype=bool)
        total = 0.0
        for r, d in pairs:
            total += self.cost[r, d]
            matched[r] = True
        return float(total + self.unmatched_cost()[~matched].sum())


def make_problem(
    eta: np.ndarray,
    waited_s: np.ndarray,
    request_times: np.ndarray,
    params: CostParams,
) -> MatchingProblem:
    eta = np.asarray(eta, dtype=float)
    eta = np.where(eta <= params.max_pickup_eta_s, eta, np.inf)
    waited_s = np.asarray(waited_s, dtype=float)
    order = np.empty(len(request_times), dtype=int)
    order[np.argsort(request_times, kind="stable")] = np.arange(len(request_times))

    cost = eta.copy()
    if params.cancel is not None:
        finite = np.isfinite(eta)
        cost[finite] += params.value_s * params.cancel.prob(eta[finite])
    unmatched = params.value_s + params.wait_weight * waited_s
    cost[~(cost < unmatched[:, None])] = np.inf
    return MatchingProblem(eta, waited_s, order, params, cost)
