#!/bin/bash
while pgrep -f batch2.sh >/dev/null; do sleep 10; done
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 TLIM=240
PY=python3
run(){ echo "== $@" >> batch3.out; $PY g8run.py "$@" >> batch3.out 2>&1; }
N=100000
CCAP=60 KK=12 run HS64 frame 81 $N 4.0 3.0 0 0
CCAP=60 KK=12 run HS64 frame 82 $N 6.0 2.0 0 0
CCAP=56 KK=12 run E7s e7:../mergerows/m3_E7s_3_9.pkl 83 $N 4.0 3.0 0 0
CCAP=56 KK=12 run E7s e7:../mergerows/m3_E7s_3_25.pkl 84 $N 6.0 2.0 0 0
echo ALLDONE >> batch3.out
