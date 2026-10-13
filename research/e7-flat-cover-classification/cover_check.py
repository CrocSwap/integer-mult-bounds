"""Covers of E7 by hyperplane flats: the exact classification behind README.md (no kappa claim).

Run from the repository root:  python3 -B research/e7-flat-cover-classification/cover_check.py
Standard library only, about two minutes.

E8 lines are in Construction-A coordinates (doubled, every line has squared norm 4). t is one line and E7 = the 63
lines orthogonal to t; every line of E8 is equivalent to t under W(E8), so the choice of t does not matter.

Exactness. All rank and span questions are decided over F_p with p = 2^31 - 1. A minor of r <= 8 rows of squared norm 4
has |det| <= 2^r <= 256 (Hadamard), so a minor vanishes mod p exactly when it vanishes over Q, and every rank below
equals the rational rank."""
import collections
import itertools
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
P = 2 ** 31 - 1
N_CHECKS = 0
T0 = time.time()


def check(name, ok, detail=''):
    global N_CHECKS
    N_CHECKS += 1
    print('%-4s %-52s %s' % ('ok' if ok else 'FAIL', name, detail), flush=True)
    if not ok:
        sys.exit(1)


# ---------------------------------------------------------------------------------------------------------------
# E8 lines and exact spans
# ---------------------------------------------------------------------------------------------------------------
def e8_lines():
    g = [(1, 1, 1, 1, 0, 0, 0, 0), (1, 1, 0, 0, 1, 1, 0, 0), (1, 0, 1, 0, 1, 0, 1, 0), (0, 1, 1, 0, 1, 0, 0, 1)]
    words = {tuple(sum(a[k] * g[k][i] for k in range(4)) % 2 for i in range(8))
             for a in itertools.product((0, 1), repeat=4)}
    out = [tuple(2 * (k == i) for k in range(8)) for i in range(8)]
    for w in sorted(words):
        if sum(w) != 4:
            continue
        idx = [i for i in range(8) if w[i]]
        for sg in itertools.product((1, -1), repeat=3):          # first nonzero coordinate positive
            v = [0] * 8
            v[idx[0]] = 1
            for i, s in zip(idx[1:], sg):
                v[i] = s
            out.append(tuple(v))
    return out


L = e8_lines()
V = len(L)
DOT = [[sum(a * b for a, b in zip(x, y)) for y in L] for x in L]
SUPP = [[(i, x[i]) for i in range(8) if x[i]] for x in L]
check('E8 lines', V == 120 and all(DOT[i][i] == 4 for i in range(V))
      and all(abs(DOT[i][j]) in (0, 2) for i in range(V) for j in range(V) if i != j),
      '120 lines, |<x,y>|/2 in {0, 1} for distinct lines')
ORTH = [sum(1 << j for j in range(V) if DOT[i][j] == 0) for i in range(V)]
check('63 orthogonal lines per line', all(m.bit_count() == 63 for m in ORTH), '')


def bits(m):
    out = []
    while m:
        b = m & -m
        out.append(b.bit_length() - 1)
        m ^= b
    return out


def kernel(rows):
    """basis mod P of {n : n.r = 0 for every row r}, and the rank of the rows"""
    A = [list(r) for r in rows]
    piv = []
    r = 0
    for c in range(8):
        k = next((i for i in range(r, len(A)) if A[i][c] % P), None)
        if k is None:
            continue
        A[r], A[k] = A[k], A[r]
        inv = pow(A[r][c], P - 2, P)
        A[r] = [x * inv % P for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] % P:
                f = A[i][c]
                A[i] = [(x - f * y) % P for x, y in zip(A[i], A[r])]
        piv.append(c)
        r += 1
    basis = []
    for f in (c for c in range(8) if c not in piv):
        n = [0] * 8
        n[f] = 1
        for i, c in enumerate(piv):
            n[c] = (-A[i][f]) % P
        basis.append(n)
    return basis, r


def closure(lines):
    """(mask of all E8 lines in the rational span of the given lines, rank)"""
    K, r = kernel([L[s] for s in lines])
    return sum(1 << s for s in range(V) if all(sum(n[i] * c for i, c in SUPP[s]) % P == 0 for n in K)), r


def extensions(F, universe, basis):
    """the flats of rank r+1 inside 'universe' that contain the rank-r flat F (spanned by 'basis'): the lines outside F
    fall into classes by the direction of their image in Q^8 / span(F); each class together with F is one flat"""
    K, _ = kernel([L[s] for s in basis])
    groups = {}
    for s in bits(universe & ~F):
        v = [sum(n[i] * c for i, c in SUPP[s]) % P for n in K]
        j = next(i for i, a in enumerate(v) if a)
        inv = pow(v[j], P - 2, P)
        key = tuple(a * inv % P for a in v)
        g = groups.get(key)
        if g is None:
            groups[key] = [1 << s, s]
        else:
            g[0] |= 1 << s
    return [(F | m, basis + [s]) for m, s in groups.values()]


def flats_by_rank(universe, top):
    level = {1 << s: [s] for s in bits(universe)}
    out = {1: dict(level)}
    for k in range(2, top + 1):
        nxt = {}
        for F, b in level.items():
            for G, bb in extensions(F, universe, b):
                nxt.setdefault(G, bb)
        out[k] = nxt
        level = nxt
    return out


# ---------------------------------------------------------------------------------------------------------------
# 1. the hyperplane flats of E7 (reproduces main's D1 census)
# ---------------------------------------------------------------------------------------------------------------
t = 0
E7 = ORTH[t]
FL = flats_by_rank(E7, 6)
counts = {k: len(v) for k, v in FL.items()}
check('flats of E7 by rank', counts == {1: 63, 2: 1281, 3: 10395, 4: 33411, 5: 36435, 6: 8821}, str(counts))
H = sorted(FL[6], key=lambda m: (-m.bit_count(), m))
n = len(H)
pc = [m.bit_count() for m in H]
hist = dict(sorted(collections.Counter(pc).items()))
check('hyperplane flats by size', hist == {10: 5040, 13: 2016, 16: 1008, 21: 666, 30: 63, 36: 28}, str(hist))
check('every hyperplane flat is closed of rank 6', all(closure(FL[6][F]) == (F, 6) for F in H[:28] + H[-28:]),
      'spot check of the 56 extreme members; closure is exact by construction')
d1 = open(os.path.join(ROOT, 'research', 'format-limits', 'scripts', 'd1_cover_numbers.py')).read()
pins = ['bit_flats=8821,', 'bit_flats_hist={10: 5040, 13: 2016, 16: 1008, 21: 666, 30: 63, 36: 28},',
        'bit_union2=52,', 'bit_cover_number=3,']
check("agrees with main's D1 census (format-limits)", all(p in d1 for p in pins), ', '.join(p.rstrip(',') for p in pins))

# the D6 and E6 flats, by their root-system description
D6 = {E7 & ORTH[a]: a for a in bits(E7)}
check('D6 flats are E7 ∩ a⊥ (a in E7)', len(D6) == 63 and set(D6) == {F for F in H if F.bit_count() == 30}, '63 flats of 30 lines')
A2 = {}
for a in range(V):
    if a != t and DOT[t][a]:
        A2[closure([t, a])[0]] = None
E6 = {}
for S in A2:
    perp = E7
    for x in bits(S):
        perp &= ORTH[x]
    E6[perp] = S
check('E6 flats are E7 ∩ A⊥ (A an A2 through t)', len(A2) == 28 and all(S.bit_count() == 3 for S in A2)
      and set(E6) == {F for F in H if F.bit_count() == 36}, '28 A2 subsystems through t, 28 flats of 36 lines')

# ---------------------------------------------------------------------------------------------------------------
# 2. two flats never cover; covering triples
# ---------------------------------------------------------------------------------------------------------------
big = [i for i in range(n) if pc[i] >= 21]
best2 = max((H[i] | H[j]).bit_count() for a, i in enumerate(big) for j in big[a + 1:])
check('two hyperplane flats cover at most 52 of 63', best2 == 52,
      'a pair with union > 52 needs |A| + |B| > 52, so both are among the %d flats of size >= 21' % len(big))
FL_OF = {s: 0 for s in bits(E7)}
for k, F in enumerate(H):
    for s in bits(F):
        FL_OF[s] |= 1 << k


def triples_covering(target, avoid):
    """all unordered triples of hyperplane flats disjoint from 'avoid' whose union contains 'target'.
    Members are taken in size order |A| >= |B| >= |C|. Since 3 * 16 < 62, the largest member has size >= 21."""
    assert target.bit_count() > 48
    allowed = 0
    for i in range(n):
        if not H[i] & avoid:
            allowed |= 1 << i
    out = set()
    for i in bits(allowed):
        if pc[i] < 21:
            break
        A = H[i]
        for j in bits(allowed >> (i + 1)):
            j += i + 1
            R = target & ~(A | H[j])
            if R.bit_count() > pc[j]:
                continue                                       # C would have to be larger than B
            m = allowed >> (j + 1)
            for s in bits(R):
                m &= FL_OF[s] >> (j + 1)
                if not m:
                    break
            for k in bits(m):
                out.add((i, j, k + j + 1))
    return out


TRI = triples_covering(E7, 0)
types = collections.Counter(tuple(pc[x] for x in tr) for tr in TRI)
check('covering triples', len(TRI) == 315 and types == {(30, 30, 30): 315}, '315, all D6 + D6 + D6')
frames = [(a, b, c) for a, b, c in itertools.combinations(bits(E7), 3) if not (DOT[a][b] or DOT[a][c] or DOT[b][c])]
span_size = {f: closure([t, *f])[0].bit_count() for f in frames}
check('orthogonal 4-frames {t, a, b, c}', len(frames) == 4095
      and collections.Counter(span_size.values()) == {12: 315, 4: 3780},
      '315 span a D4 (12 lines), 3780 span only 4A1 (4 lines)')
d4_triples = {frozenset(E7 & ORTH[x] for x in f) for f in frames if span_size[f] == 12}
a1_triples = {frozenset(E7 & ORTH[x] for x in f) for f in frames if span_size[f] == 4}
covers = {frozenset(H[x] for x in tr) for tr in TRI}
check('covering triples = D4 frames through t', covers == d4_triples,
      'exactly the {E7∩a⊥, E7∩b⊥, E7∩c⊥} for {t,a,b,c} a frame of a D4 subsystem')
worst = min(63 - (A | B | C).bit_count() for A, B, C in map(tuple, a1_triples))
check('4A1 frames do not cover', len(a1_triples) == 3780 and worst > 0, 'each leaves >= %d lines uncovered' % worst)
D4 = collections.Counter(closure([t, *f])[0] for f in frames if span_size[f] == 12)
check('D4 subsystems through t', len(D4) == 315 and set(D4.values()) == {1},
      '315, each with exactly one orthogonal frame through t: covering triples <-> D4 subsystems through t')

# ---------------------------------------------------------------------------------------------------------------
# 3. near-covers: triples covering exactly 62 of the 63 lines, for every missing line
# ---------------------------------------------------------------------------------------------------------------
near = {}
for m in bits(E7):
    for tr in triples_covering(E7 & ~(1 << m), 1 << m):
        near[frozenset(H[x] for x in tr)] = m
types = collections.Counter(tuple(sorted(F.bit_count() for F in tr)) for tr in near)
per_m = collections.Counter(near.values())
check('near-covers (exactly one line missed)', len(near) == 378 and types == {(30, 36, 36): 378}
      and set(per_m.values()) == {6}, '378 = 63 x 6, all E6 + E6 + D6')
A3 = {}
for a in range(V):
    for b in range(a + 1, V):
        if t in (a, b) or not (DOT[t][a] or DOT[t][b]):
            continue
        S, r = closure([t, a, b])
        if r == 3 and S.bit_count() == 6:
            A3[S] = None
A3_near = {}
for S in A3:
    m = [x for x in bits(S) if x != t and DOT[t][x] == 0]
    sub = [A for A in A2 if A & S == A]
    perps = []
    for A in sub:
        p = E7
        for x in bits(A):
            p &= ORTH[x]
        perps.append(p)
    A3_near[frozenset(perps + [E7 & ORTH[m[0]]])] = (len(m), len(sub), m[0])
ok = (len(A3) == 378 and all(v[:2] == (1, 2) for v in A3_near.values())
      and set(A3_near) == set(near) and all(near[k] == v[2] for k, v in A3_near.items()))
check('near-covers = A3 subsystems through t', ok,
      'E6(A)+E6(B)+D6(m) misses exactly m: A, B the two A2s of the A3 through t, m its line orthogonal to t')

# ---------------------------------------------------------------------------------------------------------------
# 4. inside a covering triple: what a cover argument says about one D6 "pool"
# ---------------------------------------------------------------------------------------------------------------
A, B, C = sorted(next(iter(covers)))
priv = [X & ~(Y | Z) for X, Y, Z in ((A, B, C), (B, A, C), (C, A, B))]
shared = (A & B) | (A & C) | (B & C)
check('a covering triple', [X.bit_count() for X in priv] == [16] * 3 and (A & B & C).bit_count() == 12
      and shared.bit_count() == 15 and all(closure(bits(X))[1] == 6 for X in priv),
      'each D6 has 16 lines covered once (spanning the D6); 15 lines are shared, 12 by all three')
F5 = {}
for X in (A, B, C):
    F5[X] = list(flats_by_rank(X, 5)[5])
sizes = dict(sorted(collections.Counter(F.bit_count() for F in F5[A]).items()))
check('rank-5 subflats of a D6', len(F5[A]) == 268 and sizes == {8: 120, 9: 80, 13: 30, 15: 32, 20: 6}, str(sizes))
best = max((F5[A][i] | F5[A][j]).bit_count() for i in range(268) for j in range(i + 1, 268))
check('two rank-5 subflats cover at most 28 of a D6', best == 28, 'so a D6 is never covered by two of them')
pairs = {}
for X, Y in zip((A, B, C), priv):
    pairs[X] = [(F5[X][i], F5[X][j]) for i in range(268) for j in range(i, 268) if Y & ~(F5[X][i] | F5[X][j]) == 0]
check('two rank-5 subflats do cover the 16 private lines', all(len(p) > 0 for p in pairs.values()),
      '%s admissible pairs per D6' % [len(p) for p in pairs.values()])
sh = bits(shared)
pos = {s: k for k, s in enumerate(sh)}
pat = {X: {sum(1 << pos[s] for s in bits((F | G) & shared)) for F, G in pairs[X]} for X in (A, B, C)}
full = (1 << len(sh)) - 1
six = next(((a, b, c) for a in pat[A] for b in pat[B] for c in pat[C] if a | b | c == full), None)
check('six rank-5 flats, two per D6, cover E7', six is not None,
      'a cover count alone forces only 2 registers per D6 at rank 5, not 3')
print('PASS_E7_FLAT_COVER_CLASSIFICATION (%d checks, %.0f s)' % (N_CHECKS, time.time() - T0))
