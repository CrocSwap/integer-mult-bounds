# ADDITIVE ad3: shape of the ls5 optimum at the top P_t (number of paid / free children, child dims), t=.0075.
import ad1
from ad1 import n, M, UU, NT
t = 0.0075; s = 1 - t; pR = lambda R: (R - R ** s) / (R - 1)
cw = lambda d, e: pR(min(8, 9 - e))
best = {1: {1: 0.0}}
for d in range(2, n - 1):
    items = [(e, m, v) for e in best for m, v in best[e].items()]; res = {}
    for mt in range(1, M + 1):
        uu = UU[(d, mt)]
        if uu == 0: continue
        K = {0: 0.0}
        for mm in range(1, mt + 1):
            bv = min((K[mm - m] + v + cw(d, e) / uu for (e, m, v) in items if m <= mm and (mm - m) in K), default=None)
            if bv is not None: K[mm] = bv
        if mt in K: res[mt] = K[mt]
    best[d] = res
items = [(e, m, v) for e in best for m, v in best[e].items()]
for nfree in (1, 2):
    K = [{0: (0.0, [])}] + [dict() for _ in range(nfree)]
    for mm in range(1, M + 1):
        for f in range(nfree + 1):
            bv = None
            for (e, m, v) in items:
                if m > mm: continue
                r = mm - m
                if r in K[f]:
                    c = (K[f][r][0] + v + cw(8, e), K[f][r][1] + [(e, m, 'paid')])
                    if bv is None or c[0] < bv[0]: bv = c
                if f >= 1 and r in K[f - 1]:
                    c = (K[f - 1][r][0] + v, K[f - 1][r][1] + [(e, m, 'free')])
                    if bv is None or c[0] < bv[0]: bv = c
            if bv is not None: K[f][mm] = bv
    val, ch = K[nfree][M]
    print(f'nfree={nfree}: top children (dim, content, paid/free) = {ch}; paid top edges/tree = {sum(1 for x in ch if x[2]=="paid")}')
