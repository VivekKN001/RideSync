import itertools

import numpy as np
import pytest
from scipy.optimize import linear_sum_assignment

from ridesync.matching import hungarian


def brute_force(cost):
    n, m = cost.shape
    if n <= m:
        return min(sum(cost[i, c] for i, c in enumerate(p)) for p in itertools.permutations(range(m), n))
    return brute_force(cost.T)


def check(cost):
    rows, cols = hungarian(cost)
    k = min(cost.shape)
    assert len(rows) == len(cols) == k
    assert len(set(rows)) == k and len(set(cols)) == k
    assert np.all(np.diff(rows) > 0)
    r2, c2 = linear_sum_assignment(cost)
    assert cost[rows, cols].sum() == pytest.approx(cost[r2, c2].sum(), rel=1e-9, abs=1e-9)


@pytest.mark.parametrize("seed", range(40))
def test_matches_brute_force_small(seed):
    rng = np.random.default_rng(seed)
    n, m = rng.integers(1, 6, size=2)
    cost = rng.integers(0, 20, size=(n, m)).astype(float)
    rows, cols = hungarian(cost)
    assert cost[rows, cols].sum() == pytest.approx(brute_force(cost))


@pytest.mark.parametrize("seed", range(30))
@pytest.mark.parametrize("shape", [(30, 30), (20, 45), (45, 20), (1, 50), (50, 1)])
def test_matches_scipy(seed, shape):
    rng = np.random.default_rng(seed)
    check(rng.random(shape) * 1000)


def test_ties_and_integers():
    rng = np.random.default_rng(7)
    check(rng.integers(0, 3, size=(40, 40)).astype(float))
    check(np.zeros((5, 8)))


def test_negative_costs():
    rng = np.random.default_rng(3)
    check(rng.normal(size=(25, 30)) * 100)


def test_large_forbidden_values():
    rng = np.random.default_rng(11)
    cost = rng.random((30, 40)) * 900
    cost[rng.random(cost.shape) < 0.7] = 1e7
    check(cost)


def test_empty():
    rows, cols = hungarian(np.zeros((0, 4)))
    assert rows.size == cols.size == 0


def test_rejects_non_finite():
    with pytest.raises(ValueError):
        hungarian(np.array([[1.0, np.inf]]))
