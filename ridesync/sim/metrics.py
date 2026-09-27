"""The cost function the project is judged on, computed from a finished simulation.

Only riders who request inside the measurement window [warmup, duration] count,
and driver time is clipped to the same window.
"""
from __future__ import annotations

from typing import Dict

import numpy as np

from .engine import DriverState, RiderState, Simulation


def _pct(x: np.ndarray, q: float) -> float:
    return float(np.percentile(x, q)) if x.size else float("nan")


def _mean(x: np.ndarray) -> float:
    return float(x.mean()) if x.size else float("nan")


def summarize(sim: Simulation) -> Dict[str, float]:
    lo, hi = sim.window
    riders = [r for r in sim.riders if lo <= r.spec.request_t < hi]
    n = len(riders)
    done = [r for r in riders if r.state is RiderState.DONE]
    cancelled = [r for r in riders if r.state is RiderState.CANCELLED]

    wait = np.array([r.pickup_t - r.spec.request_t for r in done])
    to_match = np.array([r.matched_t - r.spec.request_t for r in done])
    pickup = np.array([r.pickup_t - r.matched_t for r in done])
    # Wait of completed riders alone is survivorship-biased: a policy that lets long
    # waiters cancel looks faster. This version counts cancelled riders up to their cancel time.
    wait_all = np.concatenate([wait, [r.cancel_t - r.spec.request_t for r in cancelled]])

    total = {s: sum(d.time_in[s] for d in sim.drivers) for s in DriverState}
    driver_time = sum(total.values()) or 1.0
    st = sim.stats

    return {
        "requests": n,
        "completed": len(done),
        "completion_rate": len(done) / n if n else float("nan"),
        "cancel_rate": len(cancelled) / n if n else float("nan"),
        "cancel_no_match_rate": sum(r.cancel_reason == "no_match" for r in cancelled) / n if n else float("nan"),
        "cancel_eta_rate": sum(r.cancel_reason == "eta_quote" for r in cancelled) / n if n else float("nan"),
        "wait_mean_s": _mean(wait),
        "wait_p50_s": _pct(wait, 50),
        "wait_p90_s": _pct(wait, 90),
        "wait_all_mean_s": _mean(wait_all),
        "completed_per_hour": len(done) / ((hi - lo) / 3600.0),
        "time_to_match_mean_s": _mean(to_match),
        "pickup_mean_s": _mean(pickup),
        "driver_idle_frac": total[DriverState.IDLE] / driver_time,
        "driver_enroute_frac": total[DriverState.EN_ROUTE] / driver_time,
        "driver_ontrip_frac": total[DriverState.ON_TRIP] / driver_time,
        "batches": st.batches,
        "batch_riders_mean": _mean(np.array(st.batch_riders)),
        "solve_ms_mean": _mean(np.array(st.solve_ms)),
        "solve_ms_p99": _pct(np.array(st.solve_ms), 99),
        "decline_rate": st.declines / st.offers if st.offers else 0.0,
        # Shadow cost minus chosen cost, per batch and as a share of the chosen objective.
        "shadow_gap_s_per_batch": _mean(np.subtract(st.shadow_batch_cost, st.batch_cost)),
        "shadow_gap_frac": (
            (sum(st.shadow_batch_cost) - sum(st.batch_cost)) / sum(st.batch_cost) if st.batch_cost else float("nan")
        ),
        "shadow_worse_batches_frac": _mean(np.subtract(st.shadow_batch_cost, st.batch_cost) > 1e-6),
    }
