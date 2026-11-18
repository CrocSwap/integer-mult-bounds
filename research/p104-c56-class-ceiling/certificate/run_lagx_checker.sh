#!/bin/bash
# first checker (jr_lagx.py: jr_lag flag DP with Fraction weights); about 4 min per config; usage: run_lagx_checker.sh [cfg ...]
cd "$(dirname "$0")"; mkdir -p logs
for i in ${@:-0 1 2 3 4 5 6 7}; do
  ${PYTHON:-python3} -I jr_lagx.py $i multipliers/lam_cfg${i}_fin.pkl > logs/lagx_cfg$i.log 2>&1
  tail -1 logs/lagx_cfg$i.log | awk '{print $1, $2, $NF}'
done
