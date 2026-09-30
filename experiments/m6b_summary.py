"""M6b across every test day: what surge does once drivers respond, next to free repositioning.

    python experiments/m6b_summary.py      # -> experiments/results/m6b_summary_report.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RESULTS = Path(__file__).parent / "results"
DAYS = {
    "wed_pm": "Wed 15 Jul 2026, 17-20", "wed_am": "Wed 15 Jul 2026, 07-10", "sat_night": "Sat 18 Jul 2026, 20-23",
    "2025-10": "Wed 15 Oct 2025, 17-20", "2026-01": "Wed 14 Jan 2026, 17-20", "2026-04": "Wed 15 Apr 2026, 17-20",
}
FLEET = "drivers.num_drivers"
ARMS = [("surge_fixed", "surge, fixed fleet"), ("surge_chase", "surge, drivers chase"),
        ("surge_logon", "surge, drivers log on"), ("surge_both", "surge, both"), ("reposition", "repositioning, no surge")]


def _pm(r, col: str, scale: float = 1.0, fmt: str = "{:+.0f}") -> str:
    return f"{fmt.format(r['d_' + col] * scale)} ± {r['ci_' + col] * scale:.0f}"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    lines = ["# M6b: surge when drivers respond, on every test day", "",
             "Δ trips/h against `no_surge` at the same fleet and seed, 6 seeds, mean ± 95% CI (Student t). Rider "
             "elasticity 0.5; medium response: 20% reserve, ε = 1, chase strength 0.5 (`experiments/m6b_supply.py`).",
             "", "| day | drivers | cancel % (no surge) | " + " | ".join(label for _, label in ARMS)
             + " | online (both) | earnings/online h: no surge → both |",
             "|---|---|---|" + "---|" * len(ARMS) + "---|---|"]
    for key, label in DAYS.items():
        p = RESULTS / f"m6b_supply_{key}_summary.csv"
        if not p.exists():
            continue
        s = pd.read_csv(p)
        for n in sorted(s[FLEET].unique()):
            g = s[s[FLEET] == n].set_index("arm")
            base, both = g.loc["no_surge"], g.loc["surge_both"]
            cells = [_pm(g.loc[a], "completed_per_hour") for a, _ in ARMS]
            lines.append(f"| {label} | {n} | {base['cancel_rate']:.1%} | " + " | ".join(cells)
                         + f" | {both['drivers_online_mean']:.0f} | ${base['earnings_per_online_hour']:.0f} → "
                           f"${both['earnings_per_online_hour']:.0f} |")
    text = "\n".join(lines) + "\n"
    (RESULTS / "m6b_summary_report.md").write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
