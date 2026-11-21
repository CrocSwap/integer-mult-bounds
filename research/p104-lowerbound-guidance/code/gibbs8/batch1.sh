#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
PY=python3
N=1500
run(){ $PY g8run.py "$@" >> batch1.out 2>&1; }
run HS64 frame 11 $N 2.0 2.0 0 0
run HS64 frame 12 $N 1.0 1.0 0 0
run HS64 frame 13 $N 3.0 0.5 0 0
run HS64 frame 14 $N 2.0 2.0 2 12
run HS64 frame 15 $N 1.0 1.0 4 20
run HS64 frame 16 $N 2.0 3.0 2 30
for f in 3_1 3_13 3_21; do
 run E7s e7:../mergerows/m3_E7s_$f.pkl 21 $N 2.0 2.0 0 0
 run E7s e7:../mergerows/m3_E7s_$f.pkl 22 $N 1.0 1.0 2 12
 run E7s e7:../mergerows/m3_E7s_$f.pkl 23 $N 3.0 0.5 0 0
done
echo ALLDONE >> batch1.out
