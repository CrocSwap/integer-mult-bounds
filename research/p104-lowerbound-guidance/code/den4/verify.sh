#!/bin/sh
# DEN4 verify: exact checks (asserts inside). ~3 min, 1 proc.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
cd "$(dirname "$0")"
python quarter.py && python run1.py && python run3.py && python run4.py && python run6.py && python run2.py 0 3
