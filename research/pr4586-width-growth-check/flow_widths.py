"""Separately written default-height flow (#4436) and chronological width recurrence (#4507) used by verify.py.

The flow was written for my #4456 checks of #4436; the width recurrence for my check of #4507. Neither imports
#4436's, #4507's or #4586's code. Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from math import factorial
import itertools, json, sys
def multis(n_types, size):
    if n_types == 0:
        if size == 0: yield ()
        return
    for x in range(size + 1):
        for rest in multis(n_types - 1, size - x): yield (x,) + rest
def flow(N, W, P):
    ks = sorted(W); m = ks[-1]; kmin = ks[0]
    def c(a):
        v = 1
        for k, x in zip(ks, a): v *= k ** x
        return v
    def u(a):
        v = factorial(sum(a))
        for k, x in zip(ks, a): v = v // factorial(x) * W[k] ** x
        return v
    G = 0
    while kmin ** (G + 1) <= N // m: G += 1
    F = [{1: 1}]
    for d in range(1, G + 1):
        nxt = {}
        for rho, cnt in F[d - 1].items():
            for r, pr in P.items():
                if m * rho * r <= N: nxt[rho * r] = nxt.get(rho * r, 0) + cnt * pr
        F.append(nxt)
    S, X, BX = {}, {}, {}
    col = units = matched = 0
    add = lambda D, k, v: D.__setitem__(k, D.get(k, 0) + v)
    present = lambda rho, a: m * rho * c(a) <= N
    for d in range(G + 1):
        for rho, cnt in F[d].items():
            for b in multis(len(ks), G - d):
                if not present(rho, b): continue
                units += cnt * u(b); col += cnt * u(b) * rho * c(b)
                for r, pr in P.items():
                    issued = cnt * pr * u(b); rank = r * rho * c(b)
                    if d == G:
                        add(X, rank, issued); continue
                    D = sum(W[k] * u(tuple(x - (i == j) for j, x in enumerate(b)))
                            for i, k in enumerate(ks) if b[i] > 0 and present(rho * r, tuple(x - (i == j) for j, x in enumerate(b))))
                    matched += cnt * pr * D
                    if issued - cnt * pr * D:
                        add(X, rank, issued - cnt * pr * D); add(BX, rank, issued - cnt * pr * D)
    for a in multis(len(ks), G):
        if present(1, a):
            for k in ks: add(S, k * c(a), W[k] * u(a))
    for d in range(1, G + 1):
        for rho, cnt in F[d - 1].items():
            for r, pr in P.items():
                for a in multis(len(ks), G - d):
                    if not present(rho * r, a): continue
                    for i, k in enumerate(ks):
                        b = list(a); b[i] += 1
                        if not present(rho, tuple(b)):
                            add(S, rho * r * c(tuple(b)), cnt * pr * u(a) * W[k])
    return dict(G=G, S=S, X=X, BX=BX, col=col, units=units, matched=matched)


import math, sys, time
from math import gcd


def lcm(a, b):
    return a // gcd(a, b) * b


def cuts(N, W, P):
    """per-cut exit batches (e, q, copies) under the chronological policy, plus aggregate exits"""
    ks = sorted(W); m = ks[-1]; kmin = ks[0]
    G = 0
    while kmin ** (G + 1) <= N // m:
        G += 1
    cap = N // m
    Fh = [{1: 1}]
    for h in range(1, G + 1):
        nxt = {}
        for c, v in Fh[-1].items():
            for k, w in W.items():
                if c * k <= cap:
                    nxt[c * k] = nxt.get(c * k, 0) + w * v
        Fh.append(nxt)
    paths = [{1: 1}]  # depth -> rho -> multiplicity
    for d in range(1, G + 1):
        nxt = {}
        for rho, mult in paths[-1].items():
            for r, pr in P.items():
                if m * rho * r <= N:
                    nxt[rho * r] = nxt.get(rho * r, 0) + mult * pr
        paths.append(nxt)
    out, agg = [], {}
    for d in range(G + 1):
        h = G - d
        for rho, mult in paths[d].items():
            for c, units in Fh[h].items():
                if m * rho * c > N:
                    continue
                for r, pr in P.items():
                    if h == 0:
                        q = units  # = 1: every paid job of the leaf class exits
                    else:
                        q = sum(w * Fh[h - 1].get(c // k, 0) for k, w in W.items()
                                if c % k == 0 and m * rho * r * (c // k) > N)
                    if q:
                        e = rho * r * c
                        out.append((e, q, mult * pr))
                        agg[e] = agg.get(e, 0) + q * mult * pr
    return G, out, agg


def widths(W, P, Nmax, check_every=0):
    m = max(W)
    B = [1] * m  # base widths below m (B_0 = 1)
    nested = [1] * m
    for N in range(m, Nmax + 1):
        R = flow(N, W, P)
        G, cs, agg = cuts(N, W, P)
        assert agg == {e: v for e, v in R['X'].items() if v}, (N, 'aggregate exits match the flow')
        S = sum(R['S'].values())
        a = 1
        for s, cnt in R['S'].items():
            e = N - s
            a = lcm(a, B[e] // gcd(B[e], cnt))
        for e, q, _ in cs:
            a = lcm(a, B[e] // gcd(B[e], q))
        B.append(S * a)
        nested.append(nested[-1] * S)
        assert nested[-1] % B[-1] == 0, (N, 'new width divides nested width')
    return B, nested


