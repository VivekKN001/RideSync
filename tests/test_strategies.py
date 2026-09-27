import numpy as np
import pytest

from ridesync.matching import CostParams, get_strategy, make_problem
from ridesync.matching.problem import CancelBelief

PARAMS = CostParams(max_pickup_eta_s=900, wait_weight=1.0)


def random_problem(seed, n_riders, n_drivers, infeasible_frac=0.5):
    rng = np.random.default_rng(seed)
    eta = rng.uniform(30, 1200, size=(n_riders, n_drivers))
    eta[rng.random(eta.shape) < infeasible_frac] = np.inf
    request_t = rng.uniform(0, 300, n_riders)
    return make_problem(eta, 300 - request_t, request_t, PARAMS)


def assert_valid(problem, pairs):
    rs = [r for r, _ in pairs]
    ds = [d for _, d in pairs]
    assert len(set(rs)) == len(rs) and len(set(ds)) == len(ds)
    assert all(problem.allowed()[r, d] for r, d in pairs)


@pytest.mark.parametrize("name", ["fifo_greedy", "global_greedy", "hungarian", "lsa"])
@pytest.mark.parametrize("seed", range(20))
@pytest.mark.parametrize("shape", [(10, 10), (5, 30), (30, 5), (0, 5), (5, 0)])
def test_valid_assignments(name, seed, shape):
    p = random_problem(seed, *shape)
    assert_valid(p, get_strategy(name)(p))


@pytest.mark.parametrize("seed", range(30))
@pytest.mark.parametrize("shape", [(15, 15), (8, 25), (25, 8)])
def test_optimal_never_worse_than_greedy(seed, shape):
    p = random_problem(seed, *shape)
    opt = p.total_cost(get_strategy("hungarian")(p))
    assert opt == pytest.approx(p.total_cost(get_strategy("lsa")(p)))
    for greedy in ("fifo_greedy", "global_greedy"):
        assert opt <= p.total_cost(get_strategy(greedy)(p)) + 1e-6


def test_classic_greedy_trap():
    # Driver 0 is slightly closer to rider 0, but it's rider 1's only option.
    eta = np.array([[60.0, 120.0], [100.0, np.inf]])
    p = make_problem(eta, np.zeros(2), np.array([0.0, 1.0]), PARAMS)
    assert sorted(get_strategy("fifo_greedy")(p)) == [(0, 0)]
    assert sorted(get_strategy("hungarian")(p)) == [(0, 1), (1, 0)]


def test_long_waiting_rider_wins_scarce_driver():
    eta = np.array([[100.0], [150.0]])
    p = make_problem(eta, np.array([0.0, 400.0]), np.array([400.0, 0.0]), PARAMS)
    assert get_strategy("hungarian")(p) == [(1, 0)]


AWARE = CostParams(max_pickup_eta_s=900, trip_value_s=1200, cancel=CancelBelief(600, 0.4))


def test_default_cost_is_plain_eta():
    p = random_problem(0, 12, 9)
    finite = np.isfinite(p.eta)
    assert np.array_equal(np.isfinite(p.cost), finite)
    assert np.allclose(p.cost[finite], p.eta[finite])


@pytest.mark.parametrize("seed", range(30))
def test_optimal_never_worse_than_greedy_cancel_aware(seed):
    rng = np.random.default_rng(seed)
    eta = rng.uniform(30, 1200, size=(20, 14))
    eta[rng.random(eta.shape) < 0.4] = np.inf
    request_t = rng.uniform(0, 300, 20)
    p = make_problem(eta, 300 - request_t, request_t, AWARE)
    opt_pairs = get_strategy("hungarian")(p)
    assert_valid(p, opt_pairs)
    opt = p.total_cost(opt_pairs)
    assert opt == pytest.approx(p.total_cost(get_strategy("lsa")(p)))
    for greedy in ("fifo_greedy", "global_greedy"):
        assert opt <= p.total_cost(get_strategy(greedy)(p)) + 1e-6


def test_cancel_aware_skips_likely_cancellation():
    # 850 s ETA: feasible, but P(cancel) ~ 0.8, so expected value is below waiting.
    eta = np.array([[850.0]])
    plain = make_problem(eta, np.zeros(1), np.zeros(1), PARAMS)
    aware = make_problem(eta, np.zeros(1), np.zeros(1), AWARE)
    assert get_strategy("hungarian")(plain) == [(0, 0)]
    assert get_strategy("hungarian")(aware) == []
    assert get_strategy("fifo_greedy")(aware) == []


def test_cancel_probability_monotone():
    b = CancelBelief(600, 0.4)
    probs = b.prob(np.array([60.0, 300.0, 600.0, 900.0, 1800.0]))
    assert np.all(np.diff(probs) > 0)
    assert probs[2] == pytest.approx(0.5)
