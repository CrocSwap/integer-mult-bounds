"""Exact DP over every merge of a cyclic point sequence p_i = mp*i and a cyclic line sequence x_l = ml*l + c (mod 273),
for all unit pairs (mp, ml) and all offsets c. Point 0 starts the point sequence WLOG (the graph is shift invariant).
Writes the value histogram and, for the best (mp, ml, c), random optimal tracebacks checked with the exact cost.
usage: python merge_dp.py OUT.json"""
import json, sys, time
from math import gcd
import numpy as np
from multiprocessing import Pool
from numba import njit
from core import load, order_cost

G = "graph16_59.txt"
N = 273
K = 8


@njit(cache=True)
def tables(Dp, mp, ml, c):
    inv = 0
    for t in range(1, N):
        if (ml * t) % N == 1:
            inv = t
    cP = np.zeros((N, N + 1), np.int64)  # cP[i, l] = # neighbours of point p_i among first l lines
    cL = np.zeros((N, N + 1), np.int64)  # cL[l, i] = # neighbours of line x_l among first i points
    invp = 0
    for t in range(1, N):
        if (mp * t) % N == 1:
            invp = t
    for i in range(N):
        p = (mp * i) % N
        for d in Dp:
            x = (p + d) % N
            l = (inv * (x - c)) % N
            cP[i, l + 1] += 1
            cL[l, i + 1] += 1
    for i in range(N):
        for l in range(1, N + 1):
            cP[i, l] += cP[i, l - 1]
    for l in range(N):
        for i in range(1, N + 1):
            cL[l, i] += cL[l, i - 1]
    return cP, cL


@njit(cache=True)
def dp(cP, cL):
    f = np.full((N + 1, N + 1), 1 << 40, np.int64)
    f[0, 0] = 0
    for i in range(N + 1):
        for l in range(N + 1):
            if i < N:
                v = f[i, l] + max(0, K - cP[i, l])
                if v < f[i + 1, l]:
                    f[i + 1, l] = v
            if l < N:
                v = f[i, l] + max(0, K - cL[l, i])
                if v < f[i, l + 1]:
                    f[i, l + 1] = v
    return f


@njit(cache=True)
def sweep(Dp, mp, units):
    out = np.empty((len(units), N), np.int64)
    for a in range(len(units)):
        for c in range(N):
            cP, cL = tables(Dp, mp, units[a], c)
            out[a, c] = dp(cP, cL)[N, N]
    return out


def job(a):
    mp, Dp, units = a
    return mp, sweep(np.array(Dp, np.int64), mp, np.array(units, np.int64))


def traceback(Dp, mp, ml, c, rng):
    cP, cL = tables(np.array(Dp, np.int64), mp, ml, c)
    f = dp(cP, cL)
    i = l = N; seq = []
    while i or l:
        opts = []
        if i and f[i - 1, l] + max(0, K - cP[i - 1, l]) == f[i, l]:
            opts.append("P")
        if l and f[i, l - 1] + max(0, K - cL[l - 1, i]) == f[i, l]:
            opts.append("L")
        s = opts[rng.integers(len(opts))]
        if s == "P":
            i -= 1; seq.append((mp * i) % N)
        else:
            l -= 1; seq.append(N + (ml * l + c) % N)
    return int(f[N, N]), seq[::-1]


if __name__ == "__main__":
    nbr = load(G)
    Dp = sorted(int(x) - N for x in nbr[0])
    units = [u for u in range(1, N) if gcd(u, N) == 1]
    t = time.time()
    with Pool(8) as p:
        res = dict(p.map(job, [(mp, Dp, units) for mp in units]))
    hist = {}
    best = None
    for mp in units:
        arr = res[mp]
        for a, ml in enumerate(units):
            for c in range(N):
                v = int(arr[a, c]); hist[v] = hist.get(v, 0) + 1
                if best is None or v < best[0]:
                    best = (v, [])
                if v == best[0]:
                    best[1].append((mp, ml, c))
    print("DPs", len(units) ** 2 * N, "sec", round(time.time() - t, 1))
    print("lowest values:", sorted(hist.items())[:8])
    print("best", best[0], "attained by", len(best[1]), "triples; first", best[1][:6])
    rng = np.random.default_rng(7)
    tb = []
    for (mp, ml, c) in best[1][:40]:
        for _ in range(3):
            v, seq = traceback(Dp, mp, ml, c, rng)
            assert order_cost(nbr, np.array(seq, np.int64)) == v
            tb.append(dict(mp=mp, ml=ml, c=c, value=v, order=seq))
    json.dump(dict(hist=sorted(hist.items()), best=best[0], best_triples=best[1], tracebacks=tb), open(sys.argv[1], "w"))
