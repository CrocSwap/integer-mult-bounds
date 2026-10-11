"""Per-register DP ceiling for frame retiming (ignores partner coupling and nondegeneracy)."""
import pickle, math, time
from collections import Counter
from search import *

def w(r): return r*math.log(120/r) if r > 0 else 0.0

def intervals():
    d, L, ev, frame, ops, fixed, need = setup(); rec = d['rec']; n = d['n']; chi = d['chi']
    def join(f, g):
        if L.sub(f, g): return g
        if L.sub(g, f): return f
        return L.register(list(L.B[f]) + list(L.B[g]))
    spanf = {}
    def spanframe(nd):
        r = spanf.get(nd)
        if r is None: r = spanf[nd] = L.register([chi[s] for s in nd]) if nd else d['ZERO']
        return r
    st = dict(d['initial']); lo = {}
    for k in range(0, len(rec), 6):
        op, a, b, c, f, z = rec[k:k+6]; i = k//6
        if op == 1:
            g = f if i in fixed else join(join(st[a], st[b]), spanframe(need[i]))
            st[a] = g
            if b != n: st[b] = g
            lo[i] = g
        elif op == 2: st[a] = c; lo[i] = c
    U = dict(d['final']); hi = {}
    for k in range(len(rec)-6, -1, -6):
        op, a, b, c, f, z = rec[k:k+6]; i = k//6
        if op == 1:
            g = f if i in fixed else L.meet(U[a], U[b])
            U[a] = g
            if b != n: U[b] = g
            hi[i] = g
        elif op == 2: U[a] = c; hi[i] = c
    return d, L, ev, frame, ops, fixed, need, lo, hi, join, spanframe

def register_dp(L, s, lst, lo, hi, init, fin):
    """Optimal concave chain cost and histogram for one register (relaxed)."""
    seq_lo = [lo[i] for i in lst]; seq_hi = [hi[i] for i in lst]; k = len(lst)
    dl = [L.dimf[x] for x in seq_lo]; dh = [L.dimf[x] for x in seq_hi]
    D0, DF = L.dimf[init], L.dimf[fin]
    # umax[p]: last u with lo_u inside hi_p (monotone)
    umax = [0]*k; u = 0
    for p in range(k):
        u = max(u, p)
        while u+1 < k and L.sub(seq_lo[u+1], seq_hi[p]): u += 1
        umax[p] = u
    # initial frame serves a prefix
    p0 = 0
    while p0 < k and L.sub(seq_lo[p0], init): p0 += 1
    # dp[p] = {D: (cost, hist)} : gates < p served, current level dim D
    INF = float('inf'); dp = [dict() for _ in range(k+1)]; dp[p0][D0] = (0.0, ())
    for p in range(p0, k):
        if not dp[p]: continue
        for D, (c0, h0) in dp[p].items():
            if D > dh[p]: continue
            for u in range(p, umax[p]+1):
                lowD = max(D, dl[u]); hiD = dh[p]
                if lowD > hiD: break
                for X in {lowD, hiD}:
                    gp = X - D; c = c0 + w(gp); h = h0 + ((gp,) if gp else ())
                    cur = dp[u+1].get(X)
                    if cur is None or c < cur[0]: dp[u+1][X] = (c, h)
    best = None
    for D, (c, h) in dp[k].items():
        gp = DF - D; c2 = c + w(gp); h2 = h + ((gp,) if gp else ())
        if best is None or c2 < best[0]: best = (c2, h2)
    return best

if __name__ == '__main__':
    t = time.time()
    d, L, ev, frame, ops, fixed, need, lo, hi, join, spanframe = intervals()
    print('intervals', time.time()-t, flush=True)
    tot = Counter([22]*24); obj = 0.0
    for s, lst in ev.items():
        c, h = register_dp(L, s, lst, lo, hi, d['initial'][s], d['final'][s])
        obj += c; tot.update(h)
    base = cost(d, L, {}); desc = Counter({1: -1760, 2: 880, 20: -880, 21: 1760, 22: -880}); cur = Counter(base); cur.update(desc)
    print('ceiling calls', sum(tot.values()), 'mass', sum(r*c for r, c in tot.items()))
    print(sorted(tot.items()))
    print('ceiling saving', saving_from_local(tot, cur), 'current', saving(BASEH), time.time()-t)
    pickle.dump(dict(lo=lo, hi=hi), open('intervals.pkl', 'wb'))
