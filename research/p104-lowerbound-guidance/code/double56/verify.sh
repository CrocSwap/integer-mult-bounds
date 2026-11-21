#!/bin/sh
# DOUBLE56 verify.sh: re-runs every [C] claim in D56.md (single thread, < 5 min).
set -e
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
P=python3
$P e8rho.py            # E8-56: rho_B = rho_A = 28, Rado certificates 28
$P e8xy.py             # J=J'=all, dim Xs = dim Ys = 76, rank tau-form 48, (I+X) vanishes on Xs x Ys
$P e8schur.py          # a_k, b_k in label code C; dim C*C = 36
$P clique_chk.py       # tau-triviality of J5, I5, J3+J2; star defect; random J8 decoders >= 8
$P lemmaA_chk.py 0     # isotropic-pair lemma on E8-56 and 4 completed decoders
$P kerM.py             # linear decoders: Z4 kernel of valid M is {0, 2v}
$P linchk.py           # E8-56 is linear: X Y^T = Gb
$P nbr.py              # 168 transvection neighbours: 58; splits >= 57
$P lin.py 0 5          # random factorizations: 72
$P e120.py             # E8-120 linear decoder: C = 72, rho 36+36
