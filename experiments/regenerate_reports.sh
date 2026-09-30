#!/bin/bash
# Rebuild every summary and report from the saved runs (experiments/results/*_runs.csv). Never simulates:
# RIDESYNC_NO_SIM makes run_grid fail if a run is missing. Also the record of the arguments behind each result.
# The March 2024 reports print the environment of their day in a note line (calibration, fares); rerunning
# them today prints the July 2026 one there, so check `git diff` before committing.
cd "$(dirname "$0")/.."
export RIDESYNC_NO_SIM=1
P=data/processed
MAR13=$P/trips_2024-03-13_1700_3h_manhattan_f0.1.parquet; MAR27=$P/trips_2024-03-27_1700_3h_manhattan_f0.1.parquet
PM=$P/trips_2026-07-15_1700_3h_manhattan_f0.1.parquet; AM=$P/trips_2026-07-15_0700_3h_manhattan_f0.1.parquet
SAT=$P/trips_2026-07-18_2000_3h_manhattan_f0.1.parquet; FULL=$P/trips_2026-07-15_1700_3h_manhattan_f1.parquet
OSRM_ARMS="--arms batched_greedy@30s+aware optimal@30s+aware"
run() { echo "== $*"; python "$@" --resume > /dev/null || { echo "FAILED: $*"; exit 1; }; }
run experiments/m1_batching.py
run experiments/m1b_cancel_aware.py
run experiments/m2_real_demand.py --travel straight --slice $MAR13
run experiments/m2_real_demand.py --travel osrm --slice $MAR13
run experiments/m6_surge.py --slice $MAR13
run experiments/m6_eta_sim.py --base straight --slice $MAR13 --noise 0.267
run experiments/m6_eta_sim.py --base straight --slice $MAR13 --noise 0.267 --late-tolerance 120 180 300
run experiments/m7_reposition.py --slice $MAR27
for d in "wed_pm $PM" "wed_am $AM" "sat_night $SAT"; do set -- $d
  run experiments/m2_real_demand.py --slice $2 --tag m8b_m2_$1
  run experiments/m6_surge.py --slice $2 --tag m8b_surge_$1
  run experiments/m7_reposition.py --slice $2 --tag m8b_m7_$1
  run experiments/m2_real_demand.py --travel osrm --slice $2 --fleets 300 400 500 --seeds 4 $OSRM_ARMS --tag m8b_m2_osrm_$1
done
run experiments/m2_real_demand.py --slice $FULL --fleets 3000 3500 4000 4500 5000 --seeds 3 --tag m8b_m2_full
run experiments/m2_real_demand.py --travel osrm --slice $FULL --fleets 3000 4000 5000 --seeds 2 $OSRM_ARMS --tag m8b_m2_osrm_full
run experiments/m6_eta_sim.py --base straight --tag m8b_eta_sim --noise 0.275
run experiments/m6_eta_sim.py --base straight --tag m8b_eta_sim --noise 0.275 --late-tolerance 120 180 300
run experiments/m6_eta_sim.py --base osrm --tag m8b_eta_sim --noise 0.268
run experiments/m6_eta_sim.py --base osrm --tag m8b_eta_sim --noise 0.268 --late-tolerance 120 180 300
echo "== m8b_summary"; unset RIDESYNC_NO_SIM; python experiments/m8b_summary.py > /dev/null && echo "all regenerated"
