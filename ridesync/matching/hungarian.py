"""Hungarian algorithm (Kuhn-Munkres) for the rectangular assignment problem.

Written from scratch using the shortest-augmenting-path form with dual
potentials (u for rows, v for columns). Rows are added one at a time; for each
new row we grow a Dijkstra-like alternating tree over columns using reduced
costs ``c[i, j] - u[i] - v[j]`` until we reach a free column, then flip the
augmenting path. Potentials are updated so reduced costs on the tree stay zero
and all reduced costs stay non-negative, which is what certifies optimality.

Complexity is O(n^2 * m) for an n x m matrix with n <= m. The inner loop over
columns is vectorized with numpy, so the Python-level loop is O(n^2) in the
worst case and far less in practice.

Reference for this formulation: the "e-maxx" O(n^2 m) Hungarian algorithm.
"""
from __future__ import annotations

import numpy as np


def hungarian(cost: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Minimum-cost assignment for a (possibly rectangular) cost matrix.

    Returns ``(rows, cols)`` index arrays like
    ``scipy.optimize.linear_sum_assignment``: ``min(n, m)`` pairs, sorted by row.
    All entries must be finite; encode forbidden pairs with a large cost.
    """
    cost = np.asarray(cost, dtype=float)
    if cost.ndim != 2:
        raise ValueError("cost must be a 2-D matrix")
    if not np.all(np.isfinite(cost)):
        raise ValueError("cost must be finite; use a large value for forbidden pairs")

    n, m = cost.shape
    if n == 0 or m == 0:
        empty = np.empty(0, dtype=int)
        return empty, empty
    if n > m:
        cols, rows = hungarian(cost.T)
        order = np.argsort(rows)
        return rows[order], cols[order]

    # 1-indexed internally; column 0 is a virtual root holding the row being added.
    a = np.zeros((n + 1, m + 1))
    a[1:, 1:] = cost
    u = np.zeros(n + 1)
    v = np.zeros(m + 1)
    p = np.zeros(m + 1, dtype=int)    # p[j] = row matched to column j (0 = free)
    way = np.zeros(m + 1, dtype=int)  # way[j] = previous column on the alternating path

    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = np.full(m + 1, np.inf)  # best reduced cost reaching each column so far
        used = np.zeros(m + 1, dtype=bool)

        # Grow the alternating tree until it reaches a free column.
        while True:
            used[j0] = True
            i0 = p[j0]
            free = ~used[1:]
            cur = a[i0, 1:] - u[i0] - v[1:]
            better = free & (cur < minv[1:])
            minv[1:][better] = cur[better]
            way[1:][better] = j0

            masked = np.where(free, minv[1:], np.inf)
            j1 = int(np.argmin(masked)) + 1
            delta = masked[j1 - 1]

            # Shift potentials: tree columns keep zero reduced cost, others get closer.
            u[p[used]] += delta
            v[used] -= delta
            minv[~used] -= delta

            j0 = j1
            if p[j0] == 0:
                break

        # Flip the augmenting path back to the root.
        while j0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1

    cols = np.nonzero(p[1:])[0]
    rows = p[1:][cols] - 1
    order = np.argsort(rows)
    return rows[order], cols[order]
