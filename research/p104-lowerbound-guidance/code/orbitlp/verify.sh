#!/bin/sh
# ORBITLP verify.sh: re-checks every [C] claim in OL.md (single thread). prof.npy is rebuilt if missing (~2 min C + loadtxt).
set -e
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
P=python3
$P geo.py
$P e8.py | tail -2
if [ ! -f prof.npy ]; then cc -O2 -o lcs lcs.c && ./lcs && $P dump.py && cc -O2 -o rect rect.c && ./rect && $P lp1.py; fi
$P verify_dual.py dual_F.json
$P verify_dual.py dual_FD.json
$P dbl.py e8W.npy e8V.npy E8-56
$P carry3.py 2>/dev/null | grep -E "OK|FAIL"
