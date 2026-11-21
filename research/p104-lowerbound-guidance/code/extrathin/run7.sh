#!/bin/bash
# EXTRATHIN batch: one process at a time
cd code/extrathin
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
PY=python3
timeout 3000 $PY et6.py tri 3 1 1 8 9 10
timeout 1500 $PY et6.py tri 3 1 -1 6 8
timeout 1500 $PY et6.py one 3 0 1 12 13 14 18
timeout 1500 $PY et6.py one 3 0 0 13
timeout 1500 $PY et6.py two 3 1 -1 9 10
timeout 1500 $PY et6.py path3 3 1 1 6
