# ADDITIVE ad1: (a) ls5 in-tree DP with the HOSTED free edge (Y2_t also ends at P_t for the 96 D ports), (b) t-dependence of S,
# (c) rung ceilings with the corrected S at t_lo (S(t) nondecreasing in t: p_R/p_8 increasing, see AD.md), exact Fraction certs.
# ls5/rg1 are our own lane code, imported read-only.
import os, sys, io, contextlib, signal
signal.alarm(1100)
from fractions import Fraction as Fr
from decimal import Decimal as D, getcontext, ROUND_FLOOR, ROUND_CEILING
LS = '<research-tree>/cards/WILD/UNIMODEL/claspec/landspan'
os.chdir(LS); sys.path.insert(0, LS)
with contextlib.redirect_stdout(io.StringIO()):
    import ls5
n, M, UU, NT = ls5.n, ls5.M, ls5.UU, ls5.NT
def vin(cw, nfree, Z=0.0, conv=lambda a, b: a / b):
    best = {1: {1: Z}}
    for d in range(2, n):
        items = [(e, m, v) for e in best for m, v in best[e].items()]
        if d < n - 1:
            res = {}
            for mt in range(1, M + 1):
                uu = UU[(d, mt)]
                if uu == 0: continue
                K = {0: Z}
                for mm in range(1, mt + 1):
                    bv = None
                    for (e, m, v) in items:
                        if m <= mm and (mm - m) in K:
                            c = K[mm - m] + v + conv(cw(d, e), uu)
                            if bv is None or c < bv: bv = c
                    if bv is not None: K[mm] = bv
                if mt in K: res[mt] = K[mt]
            best[d] = res
        else:   # top P_t: knapsack over children, up to nfree edges free (finals of Y_t, Y2_t)
            K = [{0: Z}] + [dict() for _ in range(nfree)]
            for mm in range(1, M + 1):
                for f in range(nfree + 1):
                    bv = None
                    for (e, m, v) in items:
                        if m > mm: continue
                        r = mm - m
                        if r in K[f]:
                            c = K[f][r] + v + cw(d, e)
                            if bv is None or c < bv: bv = c
                        if f >= 1 and r in K[f - 1]:
                            c = K[f - 1][r] + v
                            if bv is None or c < bv: bv = c
                    if bv is not None: K[f][mm] = bv
            return K[nfree][M]
def pq(t, R, mode):
    getcontext().prec = 50; sD = 1 - D(str(t)); v = (D(R) - D(R) ** sD) / (R - 1)
    return Fr(v.quantize(D(10) ** -40, rounding=mode))
def S_of(t, exact=False):
    s = 1 - t; pR = lambda R: (R - R ** s) / (R - 1)
    if exact:
        w = lambda d, e: pq(t, min(8, 9 - e), ROUND_FLOOR); conv = lambda x, y: Fr(x) / y
        v1 = vin(w, 1, Fr(0), conv); v2 = vin(w, 2, Fr(0), conv); p8 = pq(t, 8, ROUND_CEILING)
    else:
        w = lambda d, e: pR(min(8, 9 - e)); v1 = vin(w, 1); v2 = vin(w, 2); p8 = pR(8)
    return NT * v1 / p8, (8 * v1 + 96 * v2) / p8
if __name__ == '__main__':
    for t in (0.0075, 0.0078, 0.01, 0.02, 0.05):
        a, b = S_of(t); print(f't={t}: S (1 free edge, ls5) {a:.4f} | S_fix (Y2 free at 96 ports) {b:.4f}', flush=True)
    for t in ('0.0075', '0.01'):
        a, b = S_of(float(t), exact=True)
        print(f'EXACT t={t}: ls5 {float(a):.6f}  S_fix >= {float(b):.6f}  (Fraction, weights floor, p8 ceil)', flush=True)
