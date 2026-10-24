#!/usr/bin/env python3
"""Evaluate saved JCR states: kappa at p16 a7 for the found per-call profile, and what changed vs the word.
Usage: py -3.12 eval_state.py jcr_state_seed2.json [more...]"""
import json, sys, math, collections, gzip
from decimal import Decimal as D, getcontext
getcontext().prec = 40
W3 = 'D:/Math/imb-docking/research/kappa-round3-warp-20261022/'
A = json.load(open(W3 + 'ARITHMETIC.json'))
H = {int(k): n for k, n in A['local_helpers'].items()}; N0 = {int(k): n for k, n in A['local_paid'].items()}
v, d = 112, 8
def pw(x, t): x = D(x); return D(0) if x == 0 else (t * x.ln()).exp()
def mom(P, t): return sum(D(n) * pw(r, t) for r, n in P.items())
def inv(p, a):
    T = collections.Counter({r: (p + 2) * n for r, n in H.items()}); P = collections.Counter()
    P[1] += v * (p - 1); T[1 + d * (p + 2)] += 2 * v
    for L in (a, p - 1 - a):
        for j in range(1, L + 1): T[1 + d * (j + 1)] += 2 * v; P[d * (j + 1)] += 2 * v
    return T, P
def kappa(Nloc, p=16, a=7):
    T, P = inv(p, a)
    for r, n in Nloc.items(): P[r] += (p + 2) * n
    lo, hi = D('1e-6'), D('0.05')
    for _ in range(120):
        m = (lo + hi) / 2
        if mom(T, 1 - m) - mom(P, 1 - m) > 0: lo = m
        else: hi = m
    return lo
k0 = kappa(N0)
print(f'word #4610: local_paid {N0}  kappa = {k0:.10f}')
for path in sys.argv[1:]:
    st = json.load(open(path))
    prof = {int(k): n for k, n in st['profile'].items()} if 'profile' in st else None
    if prof is None: print(path, 'no profile (checkpoint only), best Lambda', st['best']); continue
    Nloc = collections.Counter(prof)
    if not st.get('centre_included'): Nloc[8] += 8          # centre jobs
    k = kappa(Nloc)
    print(f'{path}: Lambda {st["best"]:.4f}; profile {dict(sorted(prof.items()))}; mass {sum(r*n for r,n in prof.items())}; '
          f'kappa = {k:.10f} ({(k/k0-1)*100:+.3f}% vs word); best p,a: ', end='')
    best = max((kappa(Nloc, p, a), p, a) for p in range(8, 25) for a in range(0, (p - 1) // 2 + 1))
    print(f'{best[0]:.10f} at p={best[1]} a={best[2]}')
