#!/bin/bash
cd code/tribuild
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
PY=python3
for g in 3 4 5; do timeout 1200 $PY tb1.py tri 3 1 1 0 $g; timeout 1200 $PY tb1.py tri 3 1 1 1 $g; done
for g in 12 13; do timeout 1200 $PY tb1.py one 3 0 1 1 $g; done
for g in 6 7; do timeout 2400 $PY tb1.py tri 3 1 1 1 $g; done
for g in 9 10; do timeout 1200 $PY tb1.py two 3 1 1 1 $g; done
