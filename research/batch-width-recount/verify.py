#!/usr/bin/env python3
"""Independent recomputation of #4507: least chronological batch widths for #4436's direct mixed flow.

Separately written code: #4436's flow (as in research/pr4436-direct-flow-check) for sources and aggregate exits, and a
new per-cut enumerator. Target words are aggregated by product, F_0(1) = 1, F_h(c) = sum_k W_k F_(h-1)(c/k); at depth
d, path multiplier rho and present class c (m rho c <= n) a rank-r paid position leaves the per-cut batch
q = sum_k W_k F_(G-d-1)(c/k) over k with m rho r (c/k) > n (q = F_0 = 1 at depth G), at rank rho r c. Path
multiplicities scale totals but never a per-cut batch. Widths: B_e = 1 below m, and
    a_n = lcm over complements (n - s, S_s) and per-cut exits (e, q) of B_e / gcd(B_e, q),   B_n = S a_n.
Checks: aggregate per-cut exits equal the flow's exits at every rank; the toy {2:4,3:1} <- {1:6,2:2} widths through
rank 12 and #4507's counterexample (pooled multiplier 175, chronological 700, B_12 = 110600); the fixture bit lengths
433 -> 42 and 1,002 -> 88 at rank 100; raw p7 at rank 1,000: 17,504 nested bits -> 2,524 bits, factor in
[2^14980, 2^14981), strict reduction at 879 of 880 ranks; every new width divides the nested width.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from math import gcd
import json
import sys

from math import factorial
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




def need(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    toy_W, toy_P = {2: 4, 3: 1}, {1: 6, 2: 2}
    B, nested = widths(toy_W, toy_P, 12)
    need(B == [1, 1, 1, 5, 5, 25, 140, 140, 700, 625, 875, 4375, 110600], "toy widths through rank 12")
    R = flow(12, toy_W, toy_P)
    G, cs, agg = cuts(12, toy_W, toy_P)
    need(R["S"] == {6: 60, 8: 64, 9: 6, 12: 28} and agg == {1: 216, 2: 216, 4: 72, 8: 8}, "toy sources and exits")
    pooled = 1
    for s, cnt in R["S"].items():
        pooled = lcm(pooled, B[12 - s] // gcd(B[12 - s], cnt))
    for e, tot in agg.items():
        pooled = lcm(pooled, B[e] // gcd(B[e], tot))
    need(pooled == 175 and B[12] // sum(R["S"].values()) == 700, "pooled 175 versus chronological 700")
    need(sorted({(e, q) for e, q, _ in cs if e == 8}) == [(8, 1)], "the rank-8 leaf cuts each hold one job")
    fixtures = {}
    for W, P, n, bits in (({2: 1, 5: 1}, {1: 2, 4: 1}, 100, (433, 42, 95, 96)),
                          ({2: 4, 3: 1}, {1: 6, 2: 2}, 100, (1002, 88, 97, 98))):
        B, nested = widths(W, P, n)
        m = max(W)
        got = (nested[n].bit_length(), B[n].bit_length(), sum(1 for e in range(m, n + 1) if B[e] < nested[e]), n - m + 1)
        need(got == bits, f"fixture {W} <- {P}: {got}")
        fixtures[str(W)] = got
    W = {5: 420, 6: 270, 7: 840, 8: 1395, 9: 3195, 25: 448, 41: 448, 57: 448, 121: 224}
    P = {1: 37305, 2: 10695, 3: 3360, 4: 1530, 5: 300, 8: 1464, 16: 448, 32: 448, 48: 448}
    B, nested = widths(W, P, 1000)
    factor = nested[1000] // B[1000]
    need(nested[1000].bit_length() == 17504 and B[1000].bit_length() == 2524, "p7 rank 1000 bit lengths")
    need(2 ** 14980 <= factor < 2 ** 14981, "p7 reduction factor")
    need(sum(1 for e in range(121, 1001) if B[e] < nested[e]) == 879, "strict reduction at 879 of 880 ranks")
    print(json.dumps({"status": "PASS_BATCH_WIDTH_RECOUNT", "toy_B12": 110600, "pooled_vs_chronological": [175, 700],
                      "fixtures_bits": fixtures, "p7_bits": [17504, 2524], "p7_factor_bits": factor.bit_length(),
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
