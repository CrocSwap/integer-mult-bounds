"""Counted facts on the port systems and the weighted star bound of Theorem 3 (THEOREM.md), exact.
Systems: P104 (data), P120 (all 120 vectors of F_2^9 of weight 3 mod 4), P112 (P104 plus one of the two
odd 8-cliques that P120 deletes). Everything is enumeration; nothing is read from a solver."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import itertools, collections
from fractions import Fraction as Fr
from common import *

# ---- ports and the three systems --------------------------------------------------------------------------
req(len(PORTS) == 104 and len(set(PORTS)) == 104, 'P104: 104 distinct vectors of F_2^9')
req(all(wt(p) % 4 == 3 for p in PORTS), 'every port has weight 3 mod 4 (so dot(p,p)=1 and weight is odd)')
req(sorted(collections.Counter(wt(p) for p in PORTS).items()) == [(3, 70), (7, 34)], 'P104 weights: 70 of weight 3, 34 of weight 7')
req(len(P120) == 120 and set(PORTS) <= set(P120), 'P120 = vectors of weight 3 mod 4: 120 of them, P104 inside')
deleted = sorted(set(P120) - set(PORTS))
req(len(deleted) == 16, 'P120 minus P104 is 16 vectors')
odd = lambda a, b: dot(a, b) == 1
orth = lambda a, b: dot(a, b) == 0
frames = [c for c in maximal_cliques(deleted, odd) if len(c) == 8]
req(len(frames) == 2 and set(frames[0]) | set(frames[1]) == set(deleted) and not set(frames[0]) & set(frames[1]),
    'the 16 deleted vectors split into exactly two odd 8-cliques (pairwise dot 1)')
SYS = {'P104': list(PORTS), 'P112a': list(PORTS) + list(frames[0]), 'P112b': list(PORTS) + list(frames[1]), 'P120': list(P120)}
deg = lambda V: sorted({sum(odd(a, b) for b in V if b != a) for a in V})
req(deg(SYS['P104']) == [55] and deg(SYS['P120']) == [63], 'odd graph degrees: P104 is 55-regular, P120 is 63-regular')

# ---- orthogonal 8-sets ------------------------------------------------------------------------------------
CL = {}
for name, V in SYS.items():
    CL[name] = maximal_cliques(V, orth)
    sizes = collections.Counter(len(c) for c in CL[name])
    req(max(sizes) == 8, '%s: no 9 pairwise orthogonal ports (largest orthogonal set has 8)' % name)
want = {'P104': 1728, 'P112a': 4032, 'P112b': 4032, 'P120': 8640}
for name in SYS:
    n8 = sum(len(c) == 8 for c in CL[name])
    req(n8 == want[name], '%s: %d orthogonal 8-sets' % (name, n8))
odd8 = [c for c in maximal_cliques(PORTS, odd) if len(c) == 8]
per = collections.Counter(p for c in odd8 for p in c)
req(len(odd8) == 759 and sorted(collections.Counter(per[p] for p in PORTS).items()) == [(57, 32), (58, 48), (61, 24)],
    'P104: 759 odd 8-cliques; ports lie in 57 (32 ports), 58 (48) or 61 (24) of them, so P104 is not vertex-transitive')

# ---- structure of a port relative to an orthogonal 8-set K ------------------------------------------------
def nbrs(t, K):
    return tuple(c for c in K if dot(t, c))

def edge_data(V, K):
    """Edge ports of K: ports outside K with exactly two odd K-neighbours, as {port: (c, d)}."""
    Ed = {t: nbrs(t, K) for t in V if t not in K}
    return {t: A for t, A in Ed.items() if len(A) == 2}

K0 = next(c for c in CL['P120'] if len(c) == 8)
cnt = collections.Counter(len(nbrs(t, K0)) for t in P120)
req(dict(cnt) == {1: 8, 2: 28, 5: 56, 6: 28} or sorted(cnt.items()) == [(1, 8), (2, 28), (5, 56), (6, 28)],
    'P120 relative to an orthogonal 8-set: ports have 1, 2, 5 or 6 odd K-neighbours, 8 + 28 + 56 + 28')
# the unit vector v completing K to an orthonormal basis of F_2^9 is 1 + sum K; a port is sum_{c in A} c + eps v
v0 = 0x1FF
for c in K0:
    v0 ^= c
req(dot(v0, v0) == 1 and all(dot(v0, c) == 0 for c in K0), 'v = 1 + sum(K) is a unit vector orthogonal to K, so K and v form an orthonormal basis')
def coords(t, K):
    return tuple(dot(t, c) for c in K) + (dot(t, v0),)
req(all(sum(coords(t, K0)) % 2 == 1 for t in P120), 'dot(t,t) = 1 reads sum of the coordinates = 1 (mod 2), which fixes eps from A')

def hypothesis_H(V, K):
    """(H1) distinct edge ports have distinct pairs; (H2) edge ports sharing exactly one K-vertex are orthogonal;
    (H3) edge ports with disjoint pairs are adjacent (dot 1; not needed by the proof, recorded)."""
    Ed = edge_data(V, K)
    h1 = len(set(Ed.values())) == len(Ed)
    h2 = all(dot(s, t) == 0 for s, t in itertools.combinations(Ed, 2) if len(set(Ed[s]) & set(Ed[t])) == 1)
    h3 = all(dot(s, t) == 1 for s, t in itertools.combinations(Ed, 2) if not set(Ed[s]) & set(Ed[t]))
    return h1, h2, h3

# ---- weighted star bound ----------------------------------------------------------------------------------
def star_bound(Ed, K, a):
    """a: dict vertex -> weight. Checks the hypotheses of Theorem 3 and returns (E - mu)/(mu + rho) exactly,
    or None if a hypothesis fails."""
    d = collections.Counter(c for A in Ed.values() for c in A)
    if any(a[c] < 0 for c in K):
        return None
    if any(a[c] + a[e] > 1 for c, e in Ed.values()):
        return None
    if any(a[c] * (d[c] - 2) > 2 for c in K):
        return None
    mu = sum(1 + a[c] for c in K)
    rho = sum(1 - a[c] - a[e] for c, e in Ed.values())
    return (Fr(len(Ed)) - mu) / (mu + rho)

def best_on_grid(Ed, K, den=30):
    d = collections.Counter(c for A in Ed.values() for c in A)
    classes = sorted({d[c] for c in K})
    grid = [Fr(i, den) for i in range(den + 1)]
    best = (Fr(0), None)
    for combo in itertools.product(grid, repeat=len(classes)):
        w = dict(zip(classes, combo))
        v = star_bound(Ed, K, {c: w[d[c]] for c in K})
        if v is not None and v > best[0]:
            best = (v, w)
    return best

types = {}
for name in SYS:
    for K in (c for c in CL[name] if len(c) == 8):
        Ed = edge_data(SYS[name], K)
        h = hypothesis_H(SYS[name], K)
        if not (h[0] and h[1]):
            fail('%s: hypothesis (H1)/(H2) fails on K %s' % (name, K))
        d = collections.Counter(c for A in Ed.values() for c in A)
        key = (name, len(Ed), tuple(sorted(d[c] for c in K)))
        types.setdefault(key, [0, K, Ed, h[2]])[0] += 1
for name in SYS:
    req(True, '%s: (H1) distinct pairs and (H2) orthogonality of edge ports sharing one vertex hold for all %d orthogonal 8-sets' % (name, want[name]))
want_types = {
    ('P104', 22, (5, 5, 5, 5, 6, 6, 6, 6)): 960,
    ('P104', 22, (5, 5, 5, 5, 5, 6, 6, 7)): 384,
    ('P104', 21, (5, 5, 5, 5, 5, 5, 6, 6)): 384,
    ('P112a', 25, (6, 6, 6, 6, 6, 6, 7, 7)): 3584, ('P112a', 24, (6, 6, 6, 6, 6, 6, 6, 6)): 448,
    ('P112b', 25, (6, 6, 6, 6, 6, 6, 7, 7)): 3584, ('P112b', 24, (6, 6, 6, 6, 6, 6, 6, 6)): 448,
    ('P120', 28, (7,) * 8): 8640,
}
req({k: v[0] for k, v in types.items()} == want_types, 'types (system, E, degree sequence) and their counts: P104 has 960 with E=22 and degrees (5,5,5,5,6,6,6,6), 384 with E=22 and (5,5,5,5,5,6,6,7), 384 with E=21; P112 and P120 as listed')
req(all(v[3] for v in types.values()), '(H3) disjoint edge pairs are adjacent, on every type (recorded; not used)')

# the explicit weights of THEOREM.md, Theorem 3
def weights(key):
    name, E, ds = key
    return {5: Fr(1, 2), 6: Fr(1, 2), 7: Fr(2, 5)} if name != 'P120' else {7: Fr(2, 5)}
expected = {
    ('P104', 22, (5, 5, 5, 5, 6, 6, 6, 6)): Fr(5, 6), ('P104', 22, (5, 5, 5, 5, 5, 6, 6, 7)): Fr(101, 126),
    ('P104', 21, (5, 5, 5, 5, 5, 5, 6, 6)): Fr(3, 4),
    ('P112a', 25, (6, 6, 6, 6, 6, 6, 7, 7)): Fr(1), ('P112a', 24, (6, 6, 6, 6, 6, 6, 6, 6)): Fr(1),
    ('P112b', 25, (6, 6, 6, 6, 6, 6, 7, 7)): Fr(1), ('P112b', 24, (6, 6, 6, 6, 6, 6, 6, 6)): Fr(1),
    ('P120', 28, (7,) * 8): Fr(1),
}
for key, (n, K, Ed, _) in sorted(types.items()):
    d = collections.Counter(c for A in Ed.values() for c in A)
    w = weights(key)
    val = star_bound(Ed, K, {c: w[d[c]] for c in K})
    used = {x: str(w[x]) for x in sorted(set(d[c] for c in K))}
    req(val == expected[key], 'weights by degree %s give j/k >= %s on %s, E=%d, degrees %s' % (used, val, key[0], key[1], key[2]))
    bg, wg = best_on_grid(Ed, K)
    req(bg == expected[key], '  best over the grid of multiples of 1/30 (weights constant on degree classes) is the same value %s' % bg)

# controls: the hypotheses on the weights are necessary, and the bound is checked against a representation that attains it
K1 = types[('P120', 28, (7,) * 8)][1]; Ed1 = types[('P120', 28, (7,) * 8)][2]
bad = {c: Fr(1, 2) for c in K1}
req(star_bound(Ed1, K1, bad) is None, 'control: weights 1/2 on P120 violate a(d-2) <= 2 (d = 7) and are rejected')
mu = sum(1 + bad[c] for c in K1)
req((28 - mu) / mu == Fr(4, 3), 'control: the formula without that hypothesis would give 4/3 > 1 on P120, which the rank-9 representation (j/k = 1) contradicts')
bad2 = {c: Fr(3, 5) for c in K1}
req(star_bound(Ed1, K1, bad2) is None, 'control: weights 3/5 violate a_c + a_d <= 1 and are rejected')

# ---- the corollary table: rank >= 8k + ceil(5k/6) ------------------------------------------------------
rows = []
for k in range(1, 13):
    r = 8 * k + -(-5 * k // 6)
    rows.append((k, r, 9 * k, r < 9 * k))
req([k for k, r, n, lt in rows if lt][0] == 6 and rows[5][1] == 53, 'k = 1..5: the floor is 9, 18, 27, 36, 45 = 9k (rank below 9k excluded); k = 6 is the first with floor 53 < 54')
req([r for k, r, n, lt in rows[:5]] == [9, 18, 27, 36, 45], 'floor ceil(53k/6) for k = 1..5 is 9, 18, 27, 36, 45; so k=2 rank 17, k=3 rank 26, k=4 rank 34 and 35 are excluded')
req([ (k, r) for k, r, n, lt in rows if lt] == [(6, 53), (7, 62), (8, 71), (9, 80), (10, 89), (11, 98), (12, 106)], 'for k = 6..12 the floor is below 9k (53, 62, 71, 80, 89, 98, 106): first open case k = 6, rank 53')

# ---- upper bound 9 in characteristic 2: the Gram matrix --------------------------------------------------
for name in ('P104', 'P112a', 'P120'):
    V = SYS[name]
    B = [[dot(a, b) for b in V] for a in V]
    diag = all(B[i][i] == 1 for i in range(len(V)))
    mask = all(B[i][j] == 0 for i in range(len(V)) for j in range(len(V)) if i != j and dot(V[i], V[j]) == 0)
    req(diag and mask and rank_mod(B, 2) == 9, '%s: Gram matrix over F_2 has unit diagonal, zeros on orthogonal pairs, rank 9' % name)
# control: a matrix with one planted nonzero entry on an orthogonal pair fails the mask test
V = SYS['P104']
B = [[dot(a, b) for b in V] for a in V]
mask_ok = lambda B: all(B[i][j] == 0 for i in range(len(V)) for j in range(len(V)) if i != j and dot(V[i], V[j]) == 0)
i0, j0 = next((i, j) for i in range(len(V)) for j in range(len(V)) if i != j and dot(V[i], V[j]) == 0)
req(mask_ok(B), 'P104 Gram matrix passes the mask test')
B[i0][j0] = 1
req(not mask_ok(B), 'control: one planted nonzero entry on an orthogonal pair fails the mask test')
finish('PASS_GRAPH_COUNTS')
