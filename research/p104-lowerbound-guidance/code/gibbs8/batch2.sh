#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 TLIM=240
PY=python3
run(){ echo "== $@" >> batch2.out; $PY g8run.py "$@" >> batch2.out 2>&1; }
N=100000
CCAP=64 KK=8  run HS64 frame 41 $N 1.5 1.0 0 0
CCAP=66 KK=12 run HS64 frame 42 $N 2.0 2.0 2 12
CCAP=70 KK=12 run HS64 frame 43 $N 2.0 2.0 4 20
CCAP=56 KK=24 run HS64 frame 44 $N 1.0 5.0 0 0
CCAP=64 KK=16 run HS64 frame 45 $N 1.5 3.0 0 60
CCAP=72 KK=16 run HS64 frame 46 $N 1.5 3.0 3 60
for f in 3_1 3_13 3_21; do
 CCAP=58 KK=12 run E7s e7:../mergerows/m3_E7s_$f.pkl 5$f $N 1.5 2.0 0 0
 CCAP=64 KK=12 run E7s e7:../mergerows/m3_E7s_$f.pkl 6$f $N 2.0 2.0 2 12
done
CCAP=64 KK=16 run E7s e7:../mergerows/m3_E7s_3_1.pkl 71 $N 1.5 3.0 0 60
CCAP=70 KK=16 run E7s e7:../mergerows/m3_E7s_3_9.pkl 72 $N 1.5 3.0 3 60
echo ALLDONE >> batch2.out
