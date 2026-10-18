"""Asymmetric sinks on the complex P112 unit (frame decoder: 8 coordinate totals, cost 64).
A relaxed target t takes a sink w != u_t (w.u_t = 1); its decoder row is n_t = L c + alpha * beta with an extra total
beta_S = <L_S, g> on sources Q.  Feasible iff (L_t, beta_t) is not in span{(L_S, beta_S) : S in Z(w) \\ {t}}, Z(w) the
live lines with <w, u_S> = 1.  Cost of the extra total = rank_F2 of the readers' rows (<w_t, u_S>)_{S in Q}."""
import numpy as np, itertools, sys
from collections import defaultdict
from geo import *
LIVE = list(range(8, 120))
Lf = L.astype(float)
W_ALL = list(range(1, 512))
def Zset(w, t):
    return [S for S in LIVE if S != t and lab_dot(w, uint[S])]
def free_relax():
    out = []
    for t in LIVE:
        for w in W_ALL:
            if w == uint[t] or not lab_dot(w, uint[t]): continue
            Z = Zset(w, t)
            r1 = np.linalg.matrix_rank(Lf[Z]); r2 = np.linalg.matrix_rank(np.vstack([Lf[Z], Lf[t]]))
            if r2 > r1: out.append((t, w))
    return out
def feasible_pairs(Q, g):
    Qs = set(Q)
    beta = {S: float(L[S] @ g) if S in Qs else 0.0 for S in LIVE}
    ext = {S: np.append(Lf[S], beta[S]) for S in LIVE}
    res = []
    for t in LIVE:
        for w in W_ALL:
            if w == uint[t] or not lab_dot(w, uint[t]): continue
            Z = Zset(w, t)
            M = np.array([ext[S] for S in Z])
            r1 = np.linalg.matrix_rank(M); r2 = np.linalg.matrix_rank(np.vstack([M, ext[t]]))
            if r2 > r1:
                row = tuple(lab_dot(w, uint[S]) for S in Q)
                res.append((t, w, row))
    return res
def best_rank1(res):
    groups = defaultdict(set)
    for t, w, row in res:
        if any(row): groups[row].add(t)
    if not groups: return 0, None
    row, ts = max(groups.items(), key=lambda kv: len(kv[1]))
    return len(ts), sorted(ts)
if __name__ == '__main__':
    fr = free_relax()
    print('free relaxations (no extra total):', len(fr), flush=True)
