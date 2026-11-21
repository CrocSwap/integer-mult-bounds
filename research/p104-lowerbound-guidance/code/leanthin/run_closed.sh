#!/bin/bash
cd code/leanthin
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
PY=python3
: > closed_all.log
for k in $(seq 76 140) 160 200; do
  $PY lt5.py $k > /dev/null 2>>closed_err.log && $PY - <<PYEOF >> closed_all.log
import lt3
from fractions import Fraction
k=$k
c,eps,arg,fl,mode=lt3.verify(k,f'certs/closed_k{k}.json')
print(f'k{k} [{mode}] closed-form dual: EXACT chat <= {float(c):.6f}  (HQ2 {fl:.6f}; {"< bar" if c<Fraction(128891,1000) else ">= bar"})',flush=True)
PYEOF
done
