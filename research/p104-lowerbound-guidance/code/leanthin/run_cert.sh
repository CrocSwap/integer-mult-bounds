#!/bin/bash
cd code/leanthin
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
PY=python3
for k in 76 77 78 79 80 90 100 110 120 81 82 83 84 85 86 87 88 89 91 92 93 94 95 96 97 98 99; do
  $PY lt2.py $k && $PY lt3.py $k >> cert_all.log
done
