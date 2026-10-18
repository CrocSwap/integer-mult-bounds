# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""Nomination of the punctured set P (not run by verify.sh).
Decoder: the nine pseudo-target totals HYP[p]|live span every live decoder row (1 + B(t,.))|live iff the classes of P
in E8/2E8 are affinely independent (odd subset sums of nine affinely independent points cover F2^8); checked here and,
independently, by the exact replay.  Class spaces: a D4 block spans 4 dimensions, a complementary pair 6 (affine rank
7), two pairs 8, so P meets at least two block pairs.
Eligibility for the shipped L3 plan (code/gen_p3.py): both (z,z) cells of p's 4-frame contain p, and qhost(p) is not
kline(p).  Cost model: 9 totals + sum over complementary blocks B of the B-lines a pseudo-target needs that no free
keeper or freed source of B holds (extra carriers) + junk wires max(0, k_X - k_comp(X)) per block X.
usage: python -I discovery/choose.py   (lines 0..7 stay live: PR #493's frame-zero residual isometry uses them)"""
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "e8-bit-carrier-skeleton", "code", "skeleton"))
import e8  # noqa: E402
from geom import Geom  # noqa: E402
from planio import load_plan  # noqa: E402
import gen_p3  # noqa: E402

V = e8.V
GI = e8.GI
BROW = [sum((int(GI[t, b]) & 1) << b for b in range(V)) for t in range(V)]


def rank(vecs):
    basis = []
    for v in vecs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def affine_ok(P):
    return rank([(1 << V) | BROW[p] for p in P]) == 9


G = Geom()
sol = load_plan(os.path.join(HERE, "..", "data", "plan-l3.json"))
freeline, assign = gen_p3.plan_thirds(G, sol, random.Random(0))
dcellof, keepline, home, qhostD6, zz = gen_p3.derive(G, sol, freeline)
dualcells = set(home.values())
Ex = {H: gen_p3.ex_part(G, sol, G.d6quads[H][0], H) ^ gen_p3.ex_part(G, sol, G.d6quads[H][1], H) for H in G.cells}
need = {}
for t in range(V):
    acc = e8.HYP[t] ^ (1 << keepline[dcellof[t]])
    for x in G.phi[t]:
        if x != t:
            acc ^= Ex[tuple(sorted((t, x)))]
    need[t] = set(e8.bits(acc & G.blocks[G.comp[G.blk[t]]]))
fk = {b: set() for b in range(len(G.blocks))}
for c in G.cells:
    if c not in dualcells:
        fk[G.cblk[c]].add(keepline[c])
elig = [p for p in range(8, V) if gen_p3.eligible(G, sol, dcellof, keepline, qhostD6, zz, p)[0]]
byframe = {}
for p in elig:
    byframe.setdefault(G.phi[p], []).append(p)
print("eligible lines", elig)


def cost(P):
    k = {}
    for p in P:
        k[G.blk[p]] = k.get(G.blk[p], 0) + 1
    junk = sum(max(0, k.get(X, 0) - k.get(G.comp[X], 0)) for X in range(10))
    extra = 0
    for B in range(10):
        ps = [p for p in P if G.comp[G.blk[p]] == B]
        if ps:
            freed = {keepline[dcellof[q]] for q in P if G.blk[q] == B}
            extra += len(set().union(*(need[p] for p in ps)) - set(P) - fk[B] - freed)
    return 9 + extra + junk, extra, junk


best = []
for fs in itertools.combinations(sorted(byframe), 9):
    for P in itertools.product(*(byframe[f] for f in fs)):
        if affine_ok(P):
            best.append((cost(P), tuple(sorted(P))))
best.sort()
for c, P in best[:5]:
    print(c, P, "blocks", [G.blk[p] for p in P])
