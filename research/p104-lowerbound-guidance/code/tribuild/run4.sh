#!/bin/bash
cd code/tribuild
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
PY=python3
for k in $(seq 5 120); do timeout 900 $PY tb4.py one 3 0 1 1 1 $k | grep chat; done > tb4_one.log 2>&1
for g in $(seq 2 40); do timeout 1800 $PY tb4.py tri 2 1 1 1 1 $g | grep chat; done > tb4_tri.log 2>&1
for g in $(seq 3 60); do timeout 1800 $PY tb4.py two 2 1 1 1 1 $g | grep chat; done > tb4_two.log 2>&1
