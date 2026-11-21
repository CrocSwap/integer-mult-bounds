# EIGENCAP ec2: reduced type LP (KASYM rows: n, MAINS=2k, SEP, RC2_l l=3..k; parts<=k-2) with MIXED main/idle singletons,
# plus the IDLE row  #idle singletons >= 2(k-2)  (IDLE LAW + [CONJ] non-invariant events are singletons). Float LP (HiGHS), exhaustive types.
import os, sys
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'): os.environ[v]='1'
import numpy as np
from scipy.optimize import linprog
s = .99
def parts(D, mx):
    if D == 0: yield (); return
    for L in range(min(D, mx), 0, -1):
        for p in parts(D-L, L): yield (L,)+p
def HP(k): return 208/k*((k-2)*(17**s-16**s)+(8*k+1)**s-8**s*k)
def lp(k, idle_min):
    n = 2*k-2; ls = list(range(3, k+1)); cols = []; A = []; c = []
    for D in range(2, k+1):
        for P in parts(D, k-2):
            ones = P.count(1); Pa = np.array(P)
            row = [(D*D-(Pa*Pa).sum())/2]
            for l in ls: row.append((Pa[Pa<l]*(k-Pa[Pa<l])).sum()/(k-1) if D>=l else (D*D-(Pa*Pa).sum())/(k-1))
            v = (8*D+1)**s - sum((8*L)**s for L in P)
            for m in range(ones+1):
                cols.append((D, P, m)); c.append(-v); A.append(row + [m, ones-m])
    A = np.array(A).T; b = np.array([k*(k-1)] + [2*k]*len(ls))
    Aub = -A[:1+len(ls)]; bub = -b
    Aub = np.vstack([Aub, -A[-1:]]); bub = np.append(bub, -idle_min)
    r = linprog(np.array(c), A_ub=Aub, b_ub=bub, A_eq=np.vstack([np.ones((1, len(cols))), A[-2:-1]]), b_eq=[n, 2*k], bounds=(0, None), method='highs')
    sup = [(round(x, 3), cols[i]) for i, x in enumerate(r.x) if x > 1e-7]
    return 104*(-r.fun)/k, sup
if __name__ == '__main__':
    for k in [int(a) for a in sys.argv[1:]]:
        v0, _ = lp(k, 0); v1, sup = lp(k, 2*(k-2))
        print('k %d HP %.4f LP %.4f LP+IDLE %.4f  (bar 128.891) %s' % (k, HP(k), v0, v1, 'ABOVE' if v1 > 128.891 else 'below'), flush=True)
        if os.environ.get('V'): print('   ', sup)
