#!/bin/bash
# independent checker (aud_cert.py) on the frozen multipliers; about 45 s per config
cd "$(dirname "$0")"; mkdir -p logs
for i in 0 1 2 3 4 5 6 7; do ${PYTHON:-python3} -I aud_cert.py $i multipliers/lam_cfg${i}_fin.pkl > logs/aud_cfg$i.log 2>&1; tail -1 logs/aud_cfg$i.log | sed -e 's#EXACT LB .* = #EXACT LB = #'; done
