"""The cost function the project is judged on, computed from a finished simulation.

Only riders who open the app inside the measurement window [warmup, duration] count,
and driver time is clipped to the same window. Without surge pricing every rider who opens the app
requests, so "requests" and "app opens" are the same; with it (M6), rates such as ``cancel_rate``
are per request, and ``served_rate`` / ``priced_out_rate`` are per app open.
"""
from __future__ import annotations

from typing import Dict

import numpy as np

from ..geo import haversine_pairs_m
from ..pricing import fares
from .engine import DriverState, RiderState, Simulation


def _pct(x: np.ndarray, q: float) -> float:
    return float(np.percentile(x, q)) if x.size else float("nan")


def _mean(x: np.ndarray) -> float:
    return float(x.mean()) if x.size else float("nan")


def summarize(sim: Simulation) -> Dict[str, float]:
    lo, hi = sim.window
    opened = [r for r in sim.riders if lo <= r.open_t < hi]
    riders = [r for r in opened if r.state is not RiderState.PRICED_OUT]
    n = len(riders)
    done = [r for r in riders if r.state is RiderState.DONE]
    cancelled = [r for r in riders if r.state is RiderState.CANCELLED]

    wait = np.array([r.pickup_t - r.spec.request_t for r in done])
    to_match = np.array([r.matched_t - r.spec.request_t for r in done])
    pickup = np.array([r.pickup_t - r.matched_t for r in done])
    # Wait of completed riders alone is survivorship-biased: a policy that lets long
    # waiters cancel looks faster. This version counts cancelled riders up to their cancel time.
    wait_all = np.concatenate([wait, [r.cancel_t - r.spec.request_t for r in cancelled]])

    hours = (hi - lo) / 3600.0
    # Quote accuracy: actual time from match to pickup minus the quoted ETA (0 when belief == world).
    eta_err = np.array([(r.pickup_t - r.matched_t) - r.quoted_eta_s for r in done])
    if done:
        o = np.array([r.spec.origin for r in done])
        dst = np.array([r.spec.dest for r in done])
        fare = fares(sim.cfg.fare, haversine_pairs_m(o, dst), np.array([r.dropoff_t - r.pickup_t for r in done]))
        price = np.array([r.price for r in done])
    else:
        fare = price = np.array([])
    n_open = len(opened)

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
        "completed_per_hour": len(done) / hours,
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
        # M6: pricing and revenue (fares from cfg.fare; surge multiplier as quoted at request).
        "app_opens": n_open,
        "priced_out_rate": (n_open - n) / n_open if n_open else float("nan"),
        "served_rate": len(done) / n_open if n_open else float("nan"),
        "retried_rate": sum(r.attempt > 0 for r in opened) / n_open if n_open else float("nan"),
        "surged_trip_frac": _mean(price > 1.0),
        "mean_multiplier_paid": _mean(price),
        "revenue_per_hour": float((fare * price).sum()) / hours,
        "surge_revenue_per_hour": float((fare * (price - 1.0)).sum()) / hours,
        # M6: how far the quoted pickup ETA was from the drive that followed.
        "eta_error_mean_s": _mean(eta_err),
        "eta_abs_error_mean_s": _mean(np.abs(eta_err)),
        "eta_late_2min_frac": _mean(eta_err > 120.0),
    }
