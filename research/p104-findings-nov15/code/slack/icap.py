"""SLACK icap.py [C-param]: reprice layouts with INTERVAL line caps.  A line covering stages a..b is one idle op scaling one register by
D_a...D_b; by SL its end-referred vectors lie in R^{Z_a cap ... cap Z_b} and are orthogonal to Y_a..Y_b (rows) / X_a..X_b (cols), and
lines sharing a stage are independent.  Hence N[a,b] := #lines covering [a,b] <= |Z_[a,b]| - rank(Y_a..Y_b | Z_[a,b]).
layout_price / step1 impose this ONLY for b = a+1 (per-boundary 'cap |S|-4'); here every interval is imposed with rank r (r=4 = Crossing
rank; r=3 = worst case if the Crossing Lemma fails on the restricted set).  Greedy: at each boundary keep the OLDEST lines subject to all
interval caps (same rule that reproduces built B)."""
import sys; sys.path.insert(0, '.')
from layout_price import price, two_arm
from collections import Counter
L = 17; nl = 8
def lines_iv(masks, r_of):
    Z = [frozenset(i for i, ms in enumerate(masks) if k in ms) for k in range(L)]
    m = [len(z) - 2 for z in Z]
    alive = []; out = Counter()
    for k in range(L):
        if k > 0:
            if k - 1 == nl - 1: keep_list = []
            else:
                keep_list = []
                for s in alive:       # oldest first
                    trial = keep_list + [s]
                    ok = len(trial) <= m[k]
                    for a in range(min(trial), k):     # interval [a, k]
                        Za = frozenset.intersection(*Z[a:k + 1]); cnt = sum(1 for t in trial if t <= a)
                        if cnt > max(len(Za) - r_of(a, k), 0): ok = False; break
                    if ok: keep_list.append(s)
            kept = Counter(keep_list); rem = Counter(alive) - kept
            for s, v in rem.items(): out[k - s] += v
            alive = sorted(keep_list)
        alive += [k] * (m[k] - len(alive))
    for s in alive: out[L - s] += 1
    return out, [len(z) for z in Z]
def invoice_iv(masks, r_of):
    T = Counter(8 * len(ms) + 1 for ms in masks)
    lc, Z = lines_iv(masks, r_of)
    P = Counter({8 * l: v for l, v in lc.items()})
    thin = len(masks) + 2 - 2 * L; assert thin >= 0
    for _ in range(thin):
        rr = min((x for x in P if x % 8 == 0 and P[x] > 0), default=None)
        if rr is None: P[1] += 1; continue
        P[rr] -= 1; P[rr + 1] += 1
    return T, +P, Z
