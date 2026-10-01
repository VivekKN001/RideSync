#!/bin/bash
# M8d: more days per test month, as run on 2026-10-01. Every Wednesday evening (17-20) of the four test months,
# and a Wednesday morning (07-10) and Saturday night (20-23) in October, January and April as July has. Each day
# runs the straight-line experiments of M8c (M2 batching, M7 repositioning, the ETA experiment with late cancels,
# M6b surge with driver response) with its month's models and calibration. The ETA experiment runs only its
# baselines and the learned ETA at a 180 s tolerance: its world model makes a run take ~2.5 min, too slow for the
# full grid on every day. Needs the raw TLC month files (RIDESYNC_TLC_DIR) for the slices. Every experiment resumes from its runs CSV, so the script can be stopped and
# started again. Days that M8/M8c already ran keep their old tags (experiments/m8d_summary.py maps them).
set -u
cd "$(dirname "$0")/.."
P=data/processed
W=${WORKERS:-8}
run() { echo "[$(date +%H:%M)] $*"; "$@" > /dev/null || echo "FAILED: $*"; }

# month:day:start  (one 3 h window, 10% of Manhattan trips)
DAYS="
2025-10:2025-10-01:1700 2025-10:2025-10-08:1700 2025-10:2025-10-22:1700 2025-10:2025-10-29:1700
2025-10:2025-10-15:0700 2025-10:2025-10-18:2000
2026-01:2026-01-07:1700 2026-01:2026-01-21:1700 2026-01:2026-01-28:1700
2026-01:2026-01-14:0700 2026-01:2026-01-17:2000
2026-04:2026-04-01:1700 2026-04:2026-04-08:1700 2026-04:2026-04-22:1700 2026-04:2026-04-29:1700
2026-04:2026-04-15:0700 2026-04:2026-04-18:2000
2026-07:2026-07-01:1700 2026-07:2026-07-08:1700 2026-07:2026-07-22:1700 2026-07:2026-07-29:1700
"
# July's morning and Saturday night have every experiment but the ETA one (M8b tags)
ETA_ONLY="2026-07:2026-07-15:0700 2026-07:2026-07-18:2000"

setup() {  # month day start -> SL, models and calibration of the month (July: the defaults)
  SL=$P/trips_${2}_${3}_3h_manhattan_f0.1.parquet
  [ -f "$SL" ] || run python -m ridesync.data.tlc --date "$2" --start "${3:0:2}:${3:2:2}" --hours 3 --boroughs Manhattan --sample-frac 0.1
  if [ "$1" = 2026-07 ]; then unset RIDESYNC_MODELS RIDESYNC_CALIBRATION
  else export RIDESYNC_MODELS=data/models_$1 RIDESYNC_CALIBRATION=$P/calibration_$1.json; fi
  T=${2}_${3}
}

for d in $DAYS; do IFS=: read -r M D S <<< "$d"; setup "$M" "$D" "$S"
  run python experiments/m2_real_demand.py --slice "$SL" --workers "$W" --tag "m8d_m2_$T" --resume
  run python experiments/m7_reposition.py --slice "$SL" --workers "$W" --tag "m8d_m7_$T" --resume
  run python experiments/m6_eta_sim.py --base straight --slice "$SL" --workers "$W" --tag "m8d_eta_sim_$T" --late-tolerance 180 --arms learned_eta --resume
  run python experiments/m6b_supply.py --slice "$SL" --workers "$W" --tag "m8d_m6b_$T" --resume
done
for d in $ETA_ONLY; do IFS=: read -r M D S <<< "$d"; setup "$M" "$D" "$S"
  run python experiments/m6_eta_sim.py --base straight --slice "$SL" --workers "$W" --tag "m8d_eta_sim_$T" --late-tolerance 180 --arms learned_eta --resume
done
unset RIDESYNC_MODELS RIDESYNC_CALIBRATION
run python experiments/m8d_summary.py
echo "[$(date +%H:%M)] done"
