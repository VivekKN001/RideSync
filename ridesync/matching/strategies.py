"""Pluggable matching strategies. Each maps a MatchingProblem to (rider, driver) pairs.

- ``fifo_greedy``: riders in request order each take their cheapest free driver.
  With a zero dispatch interval this is the classic "immediate nearest driver" dispatch.
- ``global_greedy``: repeatedly take the cheapest remaining (rider, driver) edge in the batch.
- ``hungarian``: optimal batch assignment with our own Kuhn-Munkres implementation.
- ``lsa``: the same optimum via scipy's Jonker-Volgenant solver (faster on large batches).
"""
from __future__ import annotations

from typing import Callable, Dict, List, Tuple

import numpy as np
from scipy.optimize import linear_sum_assignment

from .hungarian import hungarian
from .problem import MatchingProblem

Pairs = List[Tuple[int, int]]
Strategy = Callable[[MatchingProblem], Pairs]


def fifo_greedy(problem: MatchingProblem) -> Pairs:
    if problem.shape[1] == 0:
        return []
    taken = np.zeros(problem.shape[1], dtype=bool)
    pairs: Pairs = []
    for r in np.argsort(problem.request_order):
        options = np.where(taken, np.inf, problem.cost[r])
        d = int(np.argmin(options))
        if np.isfinite(options[d]):
            taken[d] = True
            pairs.append((int(r), d))
    return pairs


def global_greedy(problem: MatchingProblem) -> Pairs:
    rs, ds = np.nonzero(problem.allowed())
    # Cheapest edge first; ties broken toward the longer-waiting rider.
    order = np.lexsort((problem.request_order[rs], problem.cost[rs, ds]))
    rider_done = np.zeros(problem.shape[0], dtype=bool)
    driver_done = np.zeros(problem.shape[1], dtype=bool)
    pairs: Pairs = []
    for k in order:
        r, d = rs[k], ds[k]
        if not rider_done[r] and not driver_done[d]:
            rider_done[r] = driver_done[d] = True
            pairs.append((int(r), int(d)))
    return pairs


def _augmented_matrix(problem: MatchingProblem, rows: np.ndarray, cols: np.ndarray) -> np.ndarray:
    """R x (D + R) matrix: real drivers, then one dummy "stay unmatched" column per rider.

    Disallowed edges get a cost above any dummy, so they are never chosen over
    staying unmatched. The dummy columns also make the matrix wide, so every
    rider is always assigned to something.
    """
    cost = problem.cost[np.ix_(rows, cols)]
    unmatched = problem.unmatched_cost()[rows]
    forbidden = float(unmatched.max()) * 2 + 1.0
    real = np.where(np.isfinite(cost), cost, forbidden)
    dummy = np.full((len(rows), len(rows)), forbidden)
    np.fill_diagonal(dummy, unmatched)
    return np.hstack([real, dummy])


def _optimal(solver: Callable[[np.ndarray], Tuple[np.ndarray, np.ndarray]]) -> Strategy:
    def solve(problem: MatchingProblem) -> Pairs:
        allowed = problem.allowed()
        # Riders with no allowed driver (and drivers nobody can use) can't change the optimum.
        rows = np.nonzero(allowed.any(axis=1))[0]
        cols = np.nonzero(allowed.any(axis=0))[0]
        if rows.size == 0 or cols.size == 0:
            return []
        r_idx, c_idx = solver(_augmented_matrix(problem, rows, cols))
        real = c_idx < cols.size
        return [(int(rows[r]), int(cols[c])) for r, c in zip(r_idx[real], c_idx[real])]

    return solve


STRATEGIES: Dict[str, Strategy] = {
    "fifo_greedy": fifo_greedy,
    "global_greedy": global_greedy,
    "hungarian": _optimal(hungarian),
    "lsa": _optimal(linear_sum_assignment),
}


def get_strategy(name: str) -> Strategy:
    try:
        return STRATEGIES[name]
    except KeyError:
        raise ValueError(f"unknown strategy {name!r}; choose from {sorted(STRATEGIES)}") from None
