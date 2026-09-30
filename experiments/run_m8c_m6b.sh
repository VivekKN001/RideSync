#!/bin/bash
# M8c (three more test months) and M6b (surge with driver response on all six test days), as run on 2026-09-30.
# Each month's models train on the 12 months before it and live in data/models_<month>; its travel calibration
# (straight + OSRM, fitted on the test day) in data/processed/calibration_<month>.json. Needs OSRM up
# (OSRM_THREADS=14 docker compose --profile routing up -d osrm) and the monthly reductions of 2024-10..2026-04.
# Every experiment resumes from its runs CSV, so the script can be stopped and started again.
set -u
cd "$(dirname "$0")/.."
P=data/processed
MONTHS="2025-10:2024-10:2025-09:2025-10-15 2026-01:2025-01:2025-12:2026-01-14 2026-04:2025-04:2026-03:2026-04-15"
OSRM_ARMS="--arms batched_greedy@30s+aware optimal@30s+aware"
run() { echo "[$(date +%H:%M)] $*"; "$@" > /dev/null || echo "FAILED: $*"; }

for m in $MONTHS; do IFS=: read -r M TR0 TR1 DAY <<< "$m"
  SL=$P/trips_${DAY}_1700_3h_manhattan_f0.1.parquet
  [ -f "$SL" ] || run python -m ridesync.data.tlc --date "$DAY" --start 17:00 --hours 3 --boroughs Manhattan --sample-frac 0.1
  export RIDESYNC_MODELS=data/models_$M RIDESYNC_CALIBRATION=$P/calibration_$M.json
  mkdir -p "$RIDESYNC_MODELS"
  [ -f "$RIDESYNC_CALIBRATION" ] || run python -m ridesync.routing.calibrate --slice "$SL" --osrm http://localhost:5000
  [ -f "$RIDESYNC_MODELS/eta_straight.joblib" ] || run python -m ridesync.ml.train all --train "$TR0:$TR1" --test "$M" --report "m8c_$M"
  run python experiments/m2_real_demand.py --slice "$SL" --workers 8 --tag "m8c_m2_$M" --resume
  run python experiments/m7_reposition.py --slice "$SL" --workers 8 --tag "m8c_m7_$M" --resume
  run python experiments/m6_eta_sim.py --base straight --slice "$SL" --workers 8 --tag "m8c_eta_sim_$M" --late-tolerance 120 180 300 --resume
  run python experiments/m2_real_demand.py --travel osrm --slice "$SL" --fleets 300 400 500 --seeds 4 --workers 8 $OSRM_ARMS --tag "m8c_m2_osrm_$M" --resume
  run python experiments/m6b_supply.py --slice "$SL" --workers 8 --tag "m6b_supply_$M" --resume
done
unset RIDESYNC_MODELS RIDESYNC_CALIBRATION
for d in "wed_pm 2026-07-15_1700" "wed_am 2026-07-15_0700" "sat_night 2026-07-18_2000"; do set -- $d
  run python experiments/m6b_supply.py --slice "$P/trips_$2_3h_manhattan_f0.1.parquet" --workers 8 --tag "m6b_supply_$1" --resume
done
run python experiments/m8c_summary.py
run python experiments/m6b_summary.py
