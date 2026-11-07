#!/usr/bin/env python3
"""Exact checks for the E8 subspace invariants of the P104 ports.  Python 3.12, standard library only.

Run:  python3 -I -B research/p104-e8-subspace-invariants/check.py
Marker: PASS_P104_E8_SUBSPACE_INVARIANTS

Input: the 104 ports of research/p104-designer-toolkit-v2/words/5561.json.gz (9-bit integers).
P120 is rebuilt from coordinates (all 9-bit vectors of weight 3 or 7).  Both sets are checked in one
pass over every subspace X of F2^9 with dim X <= 4 (4,108,728 subspaces, in reduced echelon form).
Duality V = X^perp covers dimensions 5..8, and the pair (X, X^perp) covers both ends of every
'star' product, so no subspace of dimension > 4 is enumerated.
"""
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORTS_FILE = HERE.parent / "p104-designer-toolkit-v2" / "words" / "5561.json.gz"


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


pc = lambda x: bin(x).count("1")
dot = lambda a, b: pc(a & b) & 1

P104 = json.load(gzip.open(PORTS_FILE))["ports"]
P120 = [x for x in range(512) if pc(x) in (3, 7)]
require(len(P104) == 104 and len(set(P104)) == 104 and set(P104) <= set(P120) and len(P120) == 120, "port sets")
require(all(pc(x) & 1 for x in P120), "every port has odd weight")

# ---- the quadratic form: q(x) = C(wt x, 2) mod 2 on F2^9, polar form B(x,y) = wt(x)wt(y) + wt(x&y) mod 2.
q = lambda x: (pc(x) * (pc(x) - 1) // 2) & 1
B = lambda x, y: (pc(x) * pc(y) + pc(x & y)) & 1
require(all(q(x ^ y) == q(x) ^ q(y) ^ B(x, y) for x in range(512) for y in range(0, 512, 7)), "q polarises to B")
require([x for x in range(512) if all(B(x, y) == 0 for y in range(512))] == [0, 511], "radical of B is <all-ones>")
require(q(511) == 0, "q(1) = 0, so q descends to F2^9/<1> = F2^8")
require(sorted(x for x in range(512) if q(x) and pc(x) & 1) == P120, "P120 = odd vectors with q = 1 = the 120 nonsingular points of O8+(2)")
require(sum(1 for x in range(512) if q(x) == 1 and pc(x) % 2 == 0) == 120, "even nonsingular vectors are the complements: 120 classes")
require(all(B(x, y) == 1 ^ dot(x, y) for x in P120 for y in P120), "for odd vectors B(x,y) = 1 + x.y: E8-orthogonal <=> port dot 1")
# 120 = 2^7 - 2^3 nonsingular points: hyperbolic (plus) type, Witt index 4
require(120 == 2 ** 7 - 2 ** 3, "plus type")

bit = [0] * 512
for i, x in enumerate(P120):
    bit[x] = 1 << i
M = {120: (1 << 120) - 1, 104: sum(bit[x] for x in P104)}
perp1 = [0] * 512  # mask of P120 ports orthogonal (dot 0) to y
for y in range(512):
    m = 0
    for x in P120:
        if not dot(x, y):
            m |= bit[x]
    perp1[y] = m
SETS = (104, 120)
Ne = {s: [0] * 10 for s in SETS}      # max ports in a dim-e subspace
star = {s: [0] * 10 for s in SETS}    # max N(V) N(V^perp) over dim V = e
sat = {s: [0] * 10 for s in SETS}     # saturated subspaces of dim e
beta = {s: [0] * 10 for s in SETS}    # max N(g) N(A^perp), g < A hyperplane, dim A = d
fac = {s: [None] * 10 for s in SETS}
nodes = [0] * 5


def combos(units):
    out = [0]
    for u in units:
        out += [v | (1 << u) for v in out]
    return out[1:]


YPIV, YFREE = {}, {}


def yreps(pivmask, dual):
    key = pivmask
    if key not in YPIV:
        YPIV[key] = combos([b for b in range(9) if pivmask >> b & 1])
        YFREE[key] = combos([b for b in range(9) if not pivmask >> b & 1])
    return YFREE[key] if dual else YPIV[key]


def evalA(s, d, Aports, cones, ys):
    best = 0
    for y in ys:
        c = (Aports & perp1[y]).bit_count()
        if c > best:
            best = c
    if best * cones > beta[s][d]:
        beta[s][d] = best * cones
        fac[s][d] = (best, cones)


def visit(k, rows, span, pm, per, pivmask):
    nodes[k] += 1
    odd = any(pc(r) & 1 for r in rows)
    for s in SETS:
        Ms = M[s]
        nX = (pm & Ms).bit_count()
        nXp = (per & Ms).bit_count()
        if nX > Ne[s][k]:
            Ne[s][k] = nX
        if nXp > Ne[s][9 - k]:
            Ne[s][9 - k] = nXp
        pr = nX * nXp
        if pr > star[s][k]:
            star[s][k] = pr
        if pr > star[s][9 - k]:
            star[s][9 - k] = pr
        if nX == 1 << (k - 1) and odd:
            sat[s][k] += 1
        if nXp == 1 << (8 - k) and 511 not in span:   # V = X^perp has an odd vector iff 1 is not in X
            sat[s][9 - k] += 1
        d = k   # A = X, hyperplanes g of X, cones = ports of X^perp
        if d >= 2 and pr > beta[s][d] and nXp * min(nX, 1 << (d - 2) if d <= 5 else nX) > beta[s][d]:
            evalA(s, d, pm & Ms, nXp, yreps(pivmask, False))
        d = 9 - k   # A = X^perp, hyperplanes of X^perp, cones = ports of X
        if d <= 8 and pr > beta[s][d] and nX * min(nXp, 1 << (d - 2) if d <= 5 else nXp) > beta[s][d]:
            evalA(s, d, per & Ms, nX, yreps(pivmask, True))


CAND = {}


def cand(pivmask, p):
    key = (pivmask, p)
    if key not in CAND:
        free = [b for b in range(p) if not pivmask >> b & 1]
        out = []
        for sub in range(1 << len(free)):
            r = 1 << p
            for j, b in enumerate(free):
                if sub >> j & 1:
                    r |= 1 << b
            out.append(r)
        CAND[key] = out
    return CAND[key]


def dfs(k, rows, span, pm, per, pivmask, last):
    if k:
        visit(k, rows, span, pm, per, pivmask)
    if k == 3:
        leaves(rows, span, pm, per, pivmask, last)
        return
    for p in range(last + 1, 9):
        for r in cand(pivmask, p):
            new = [x ^ r for x in span]
            m = pm
            for x in new:
                m |= bit[x]
            dfs(k + 1, rows + [r], span + new, m, per & perp1[r], pivmask | 1 << p, p)


def leaves(rows, span, pm, per, pivmask, last):
    """Dimension-4 subspaces extending a dimension-3 one; the cheap path skips nodes that cannot change any record."""
    a0, a1, a2, a3, a4, a5, a6, a7 = span
    M104 = M[104]
    ne5_104, ne5_120 = Ne[104][5], Ne[120][5]
    thr = {s: min(star[s][4], beta[s][4], beta[s][5]) for s in SETS}
    for p in range(last + 1, 9):
        pm2 = pivmask | 1 << p
        for r in cand(pivmask, p):
            per4 = per & perp1[r]
            c120 = per4.bit_count()
            c104 = (per4 & M104).bit_count()
            pm4 = pm | bit[a0 ^ r] | bit[a1 ^ r] | bit[a2 ^ r] | bit[a3 ^ r] | bit[a4 ^ r] | bit[a5 ^ r] | bit[a6 ^ r] | bit[a7 ^ r]
            n120 = pm4.bit_count()
            n104 = (pm4 & M104).bit_count()
            if (c120 > ne5_120 or c104 > ne5_104 or n120 * c120 > thr[120] or n104 * c104 > thr[104]
                    or n120 == 8 or n104 == 8 or c120 == 16):
                visit(4, rows + [r], span + [x ^ r for x in span], pm4, per4, pm2)
                ne5_104, ne5_120 = Ne[104][5], Ne[120][5]
                thr = {s: min(star[s][4], beta[s][4], beta[s][5]) for s in SETS}
            else:
                nodes[4] += 1


dfs(0, [], [0], 0, (1 << 120) - 1, 0, -1)
require(nodes[1:] == [511, 43435, 788035, 3309747], "subspace counts [9 choose k]_2")

ne = {s: Ne[s][1:9] for s in SETS}
# (a) saturation: odd elements of V all ports.  Counts by dimension 1..6 (dims 7, 8 also zero).
print("saturated subspaces, dim 1..8:  P104", sat[104][1:9], " P120", sat[120][1:9])
require(sat[104][1:9] == [104, 5356, 17958, 3441, 0, 0, 0, 0], "P104 saturated counts")
require(sat[120][1:9] == [120, 7140, 32130, 11475, 0, 0, 0, 0], "P120 saturated counts")
# (b) ports per dimension
print("N_e, e=1..8:  P104", ne[104], " P120", ne[120])
require(ne[104][:7] == ne[120][:7] == [1, 2, 4, 8, 12, 20, 36], "N_e e=1..7 identical for P104 and P120")
require(ne[104][7] == 60 and ne[120][7] == 64, "N_8 differs: 60 vs 64")
# (c) star law
deg = {s: {sum(1 for y in P if y != x and not dot(x, y)) for x in P} for s, P in ((104, P104), (120, P120))}
require(deg == {104: {48}, 120: {56}}, "port graph (dot = 0) is regular of degree 48 (P104) and 56 (P120)")
print("graph with edge = dot 0: P104 regular degree 48, 2496 edges; P120 regular degree 56, 3360 edges")
print("max N(V)N(V^perp), e=1..8:  P104", star[104][1:9], " P120", star[120][1:9])
require(star[104][1:9] == [48] * 8, "P104 star law")
require(star[120][1:9] == [56, 56, 48, 48, 48, 48, 56, 56], "P120 star law")
print("covering lower bound for the edges by subspace bicliques: P104 >= 2496/48 = 52, P120 >= 3360/56 = 60")
# (d) flag rectangles
print("max flag rectangle mass, level d=2..8:  P104", beta[104][2:9], " P120", beta[120][2:9])
print("  maximiser found (ports(g), cones(A)) at d=5:  P104", fac[104][5], " P120", fac[120][5])
require(beta[104][2:9] == [30, 32, 32, 36, 32, 32, 30], "P104 flag rectangles")
require(beta[120][2:9] == [32, 32, 32, 36, 32, 32, 32], "P120 flag rectangles")
require(fac[104][5][0] * fac[104][5][1] == 36 and fac[120][5][0] * fac[120][5][1] == 36, "level 5 maximiser")
print("PASS_P104_E8_SUBSPACE_INVARIANTS")
