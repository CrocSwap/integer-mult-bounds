#!/usr/bin/env python3
"""Owned-unit deletion bound on punctured complex E8 units: exact 8-term decoders.

Standard library only (python3.12).  Everything is generated from scratch (integers, bit masks, Fractions); the only
input is the Z16 witness file (repository file research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt), whose SHA256 is pinned below.

Statement checked (see owned_deletion_PROOF.md).  Let P be a puncture of p lines of the 120 E8 root lines (labels
S9(u_i,u_j) = (<r_i,r_j>+1) mod 2, h = 9), 0 <= p <= PMAX, and (A,B) an exact 8-term decoder on the live lines in the
normal form D = RA, T = RB, A B^T = 2I.  Then

        cst >= 56 - E(p),   E(p) = 0 (p<=24), 1 (p=25), 2 (26<=p<=35), 6 (36<=p<=38).

For punctures containing the sixteen lines Z16 of two disjoint orthogonal frames (the complement of the PR968
104-line clique) the same bound holds with E_Z(p) = 0 (p<=34), 1 (p=35), 2 (p=36,37).

Usage:  python3.12 -I -B owned_deletion.py            default run (PMAX = 38)
        python3.12 -I -B owned_deletion.py --pmax 40  longer run (sets of size up to 40; table beyond 38 printed, not asserted)
"""
import hashlib
import itertools
import os
import random
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction

T0 = time.perf_counter()
HERE = os.path.dirname(os.path.abspath(__file__))
PMAX = 38
if '--pmax' in sys.argv:
    PMAX = int(sys.argv[sys.argv.index('--pmax') + 1])
    assert 38 <= PMAX <= 40, '--pmax must be 38, 39 or 40'

Z16_FILE = 'research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt'  # repository file (PR968 input), pinned in SOURCES.json
Z16_SHA256 = '8e0178db02c14e1b29058cdbdbd50aac22f2b55a1ba21dc82f417610c9932526'

LOG = []


def say(msg):
    print('[%6.1fs] %s' % (time.perf_counter() - T0, msg), flush=True)


def expect(name, got, want):
    ok = got == want
    say('%s %s = %s%s' % ('ok  ' if ok else 'FAIL', name, got, '' if ok else '   (expected %s)' % (want,)))
    if not ok:
        raise SystemExit('FAILED: %s: got %r, expected %r' % (name, got, want))


def detected(name, changed, detail):
    say('control %s: %s' % (name, detail))
    if not changed:
        raise SystemExit('CONTROL NOT DETECTED: %s' % name)


def popc(m):
    return m.bit_count()


def members(m):
    out = []
    while m:
        low = m & -m
        out.append(low.bit_length() - 1)
        m ^= low
    return out


def mask_of(idx):
    m = 0
    for i in idx:
        m |= 1 << i
    return m


# ------------------------------------------------------------------------------------------------------
# 1. E8 lines, label pairing, functionals                                                  [PR968 (F0)]
# ------------------------------------------------------------------------------------------------------
def e8_roots():
    rs = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (2, -2):
            for sj in (2, -2):
                v = [0] * 8
                v[i] = si
                v[j] = sj
                rs.append(tuple(v))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            rs.append(signs)
    return rs


def canon(v):
    for x in v:
        if x:
            return tuple(v) if x > 0 else tuple(-y for y in v)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


ROOTS = e8_roots()                       # 240 roots, doubled integer coordinates (norm 8)
ROOTSET = set(ROOTS)
LINES = sorted(set(canon(v) for v in ROOTS))
NL = 120
LIDX = {l: i for i, l in enumerate(LINES)}
G = [[dot(LINES[i], LINES[j]) // 4 for j in range(NL)] for i in range(NL)]    # true inner products
FULL = (1 << NL) - 1


def f2rank(rows):
    basis = []
    for r in rows:
        for b in basis:
            r = min(r, r ^ b)
        if r:
            basis.append(r)
    return len(basis)


def build_functionals(rows):
    """rows[i] = bit mask of the pairing row of line i.  Returns (rank, FUNC) with FUNC[c], c = 1..2^rank-1, the
    violator masks Viol(lambda_c) of the nonzero functionals lambda_c = sum_t c_t row(B_t) on independent rows B_t."""
    bas, B = [], []
    for i, r in enumerate(rows):
        rr = r
        for b in bas:
            rr = min(rr, rr ^ b)
        if rr:
            bas.append(rr)
            B.append(i)
    rk = len(B)
    func = [0] * (1 << rk)
    for c in range(1, 1 << rk):
        low = c & -c
        func[c] = func[c ^ low] ^ rows[B[low.bit_length() - 1]]
    return rk, func


ROW = [mask_of(j for j in range(NL) if G[i][j] % 2 == 0) for i in range(NL)]    # S9(u_i,u_j)=1 iff <r_i,r_j> even


def section1():
    say('== 1. E8 lines and label pairing')
    expect('E8 root lines', (len(ROOTS), NL), (240, 120))
    expect('norms (true <r,r>) all 2', set(G[i][i] for i in range(NL)), {2})
    expect('inner products on lines', sorted(set(G[i][j] for i in range(NL) for j in range(NL))), [-1, 0, 1, 2])
    rk = f2rank(ROW)
    expect('F2 rank of the 120x120 pairing S9', rk, 9)
    expect('distinct pairing rows', len(set(ROW)), 120)
    rk2, F = build_functionals(ROW)
    expect('nonzero functionals', len(F) - 1, 511)
    expect('distinct violator masks', len(set(F[1:])), 511)
    return F


FUNC = section1()
SUB2 = [(a, b) for a in range(1, 512) for b in range(a + 1, 512) if (a ^ b) > b]      # each 2-dim subspace once
assert len(SUB2) == 43435


def reflection_perm(a):
    av = LINES[a]
    out = []
    for l in LINES:
        d = dot(l, av) // 4
        out.append(LIDX[canon(tuple(x - d * y for x, y in zip(l, av)))])
    return out


REFL = [reflection_perm(a) for a in range(NL)]


def apply_perm(m, perm):
    r = 0
    while m:
        low = m & -m
        r |= 1 << perm[low.bit_length() - 1]
        m ^= low
    return r


def table_for(C, func=None):
    """(min, next, pi7): smallest and second smallest |Viol(l) & C| over nonzero l, and the minimum of
    |(Viol(l1)|Viol(l2)|Viol(l1+l2)) & C| over 2-dim subspaces."""
    func = func or FUNC
    singles = sorted(popc(func[c] & C) for c in range(1, len(func)))
    pi7 = min(popc((func[a] | func[b] | func[a ^ b]) & C) for a, b in SUB2)
    return singles[0], singles[1], pi7


def cmask_of_vec(v):
    return mask_of(j for j in range(NL) if dot(LINES[j], v) != 0)


# ------------------------------------------------------------------------------------------------------
# 2. W(E8) invariance and the hyperplane-flat census                                       [PR968 section 3]
# ------------------------------------------------------------------------------------------------------
def section2():
    say('== 2. invariance and the hyperplane-flat census')
    ok = all(abs(G[REFL[a][i]][REFL[a][j]]) == abs(G[i][j]) for a in range(NL) for i in range(NL) for j in range(0, NL, 7))
    expect('reflections preserve the inner products (sampled columns)', ok, True)
    rnd = random.Random(1)
    for a in rnd.sample(range(NL), 3):
        img = [apply_perm(FUNC[c], REFL[a]) for c in range(1, 512)]
        expect('reflection %d permutes the 511 violator masks' % a, set(img) == set(FUNC[1:]), True)
    # F2: every root has a unique single violator {alpha}, all other functionals need >= 24
    mins = Counter()
    for a in range(NL):
        C = cmask_of_vec(LINES[a])
        sz = sorted((popc(FUNC[c] & C), c) for c in range(1, 512))
        mins[(sz[0][0], sz[1][0])] += 1
        assert FUNC[sz[0][1]] == ROW[a] and popc(ROW[a] & C) == 1 and (ROW[a] & C) == 1 << a
    expect('root normals: (min, next) |Viol & C| over all 120 roots', dict(mins), {(1, 24): 120})

    # simple roots from a generic positive system
    f = [3 ** i for i in range(8)]
    pos = [r for r in ROOTS if dot(r, f) > 0]
    posset = set(pos)
    simple = [r for r in pos if not any(tuple(x - y for x, y in zip(r, q)) in posset for q in pos)]
    expect('positive roots / simple roots', (len(pos), len(simple)), (120, 8))
    A = [[dot(a, b) // 4 for b in simple] for a in simple]
    nbrs = [[j for j in range(8) if j != i and A[i][j] == -1] for i in range(8)]
    expect('Cartan off-diagonals in {0,-1}', set(A[i][j] for i in range(8) for j in range(8) if i != j), {0, -1})
    expect('Dynkin diagram: edges, degree sequence', (sum(map(len, nbrs)) // 2, sorted(map(len, nbrs))), (7, [1, 1, 1, 2, 2, 2, 2, 3]))
    # inverse Cartan matrix (exact), fundamental weights in doubled coordinates
    M = [[Fraction(A[i][j]) for j in range(8)] + [Fraction(int(i == j)) for j in range(8)] for i in range(8)]
    for c in range(8):
        p = next(r for r in range(c, 8) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        M[c] = [x / M[c][c] for x in M[c]]
        for r in range(8):
            if r != c and M[r][c] != 0:
                M[r] = [x - M[r][c] * y for x, y in zip(M[r], M[c])]
    Ainv = [[M[i][8 + j] for j in range(8)] for i in range(8)]
    assert all(x.denominator == 1 for row in Ainv for x in row)
    expect('det of the Cartan matrix (inverse is integral)', True, True)
    omega = [[sum(int(Ainv[i][j]) * simple[j][t] for j in range(8)) for t in range(8)] for i in range(8)]
    for i in range(8):
        assert [dot(omega[i], simple[j]) // 4 for j in range(8)] == [int(i == j) for j in range(8)]

    # W-orbit of each omega_i by simple reflections on packed Dynkin labels (bias 128 per byte)
    sh = [8 * i for i in range(8)]
    unit = [1 << s for s in sh]
    nb = [sum(1 << (8 * j) for j in nbrs[i]) for i in range(8)]
    bias = sum(128 << s for s in sh)
    steps = [(sh[i], 2 * unit[i], nb[i]) for i in range(8)]
    orbits = []
    for k in range(8):
        start = bias + unit[k]
        seen = {start}
        frontier = [start]
        while frontier:
            new = []
            for v in frontier:
                for s, u2, n in steps:
                    x = ((v >> s) & 255) - 128
                    if x:
                        w = v - x * u2 + x * n
                        if w not in seen:
                            seen.add(w)
                            new.append(w)
            frontier = new
        orbits.append(list(seen))
    # type of omega_k^perp
    types = {}
    for k in range(8):
        flat = sum(1 for l in LINES if dot(l, omega[k]) == 0)
        types[k] = flat
    order = sorted(range(8), key=lambda k: -types[k])
    expect('flat sizes of the eight omega_k^perp', [types[k] for k in order], [63, 42, 37, 28, 23, 22, 16, 14])
    sizes = [len(orbits[k]) for k in order]
    expect('orbit sizes of the omega_k (vectors)', sizes, [240, 2160, 6720, 17280, 60480, 69120, 241920, 483840])
    lines_total = sum(sizes) // 2
    expect('hyperplane-flat normals (lines), W-orbits of the eight types', lines_total, 440880)

    def vec_of(v, k=None):
        x = [((v >> sh[i]) & 255) - 128 for i in range(8)]
        return tuple(sum(x[i] * omega[i][t] for i in range(8)) for t in range(8))

    # per-type table at the standard representative
    want = {63: (1, 24, 25), 42: (14, 34, 42), 37: (27, 28, 51), 28: (28, 35, 56),
            23: (33, 41, 61), 22: (35, 35, 62), 16: (40, 43, 68), 14: (43, 43, 70)}
    names = {63: 'E7 ', 42: 'D7 ', 37: 'E6+A1', 28: 'A7', 23: 'D5+A2', 22: 'A6+A1', 16: 'A4+A3', 14: 'A4+A2+A1'}
    say('type       flat  |C|  min next  pi7   (PR968 table)')
    pi7 = {}
    for k in order:
        C = cmask_of_vec(omega[k])
        assert f2rank([ROW[i] for i in members(C)]) == 9          # (F1) label span of C is 9-dim
        t = table_for(C)
        fl = types[k]
        say('%-9s %4d %4d %4d %4d %4d' % (names[fl], fl, popc(C), t[0], t[1], t[2]))
        expect('table row %s (min, next, pi7)' % names[fl], t, want[fl])
        pi7[fl] = t[2]
    # orbit invariance, tested on random members of every orbit (direct computation, not by symmetry)
    rnd = random.Random(2)
    for k in order:
        fl = types[k]
        for v in rnd.sample(orbits[k], 3):
            w = vec_of(v)
            C = cmask_of_vec(w)
            assert 120 - popc(C) == fl and popc(C) == 120 - fl
            t = table_for(C)
            assert t == want[fl], (fl, t)
    expect('random members of every orbit reproduce their type row (24 normals)', True, True)
    return pi7


PI7 = section2()
D7_PI7 = PI7[42]
OTHER_FLAT_MIN = min(v for fl, v in PI7.items() if fl not in (63, 42))
expect('D7 pi7', D7_PI7, 42)
expect('every other non-root flat type pi7 >=', OTHER_FLAT_MIN, 51)
NONROOT_FLAT_MIN = min(v for fl, v in PI7.items() if fl != 63)
expect('smallest pi7 over non-root hyperplane-flat normals', NONROOT_FLAT_MIN, 42)

# ------------------------------------------------------------------------------------------------------
# 3. normals that are not hyperplane-flat
# ------------------------------------------------------------------------------------------------------
def section3():
    say('== 3. non-flat normals: unions over two containing root-spanned hyperplanes')
    # A normal a whose orthogonal roots span <= 6 dimensions lies on two distinct root-spanned hyperplanes with
    # normals w1, w2 and C(w1) u C(w2) subset of C(a).  If a containing normal is not a root, pi7 >= 42 already.
    # If both are roots, |R(a,W)| >= |R(al1,W) u R(al2,W)|.  Root pairs: two classes (orthogonal / not), W transitive.
    cls = {}
    for j in range(1, NL):
        cls.setdefault(abs(G[0][j]), []).append(j)
    assert set(cls) == {0, 1}
    C0 = cmask_of_vec(LINES[0])
    out = {}
    rnd = random.Random(3)
    for g, js in sorted(cls.items()):
        vals = []
        for j in [js[0]] + rnd.sample(js, 2):
            Cj = cmask_of_vec(LINES[j])
            U = C0 | Cj
            m1 = min(popc(FUNC[c] & U) for c in range(1, 512))
            m2 = min(popc((FUNC[a] | FUNC[b] | FUNC[a ^ b]) & U) for a, b in SUB2)
            vals.append((m1, m2))
        assert len(set(vals)) == 1, vals
        out[g] = vals[0]
        say('root pair <a,b>=%d: |C u C| = %d, min single union %d, min 2-dim union %d' % (g, popc(U), vals[0][0], vals[0][1]))
    nonflat = min(v[1] for v in out.values())
    expect('non-flat normals: red-2 needs at least (pair unions)', nonflat, 52)
    return nonflat


NONFLAT_MIN = section3()
NONROOT_MIN = min(NONROOT_FLAT_MIN, NONFLAT_MIN)
expect('smallest puncture giving ANY non-root normal red >= 2', NONROOT_MIN, 42)
assert PMAX < NONROOT_MIN, 'PMAX must stay below the non-root threshold'

# ------------------------------------------------------------------------------------------------------
# 4. root normals: reduction sets
# ------------------------------------------------------------------------------------------------------
CMASK = [cmask_of_vec(LINES[a]) for a in range(NL)]
LAMBDA_ALPHA = {a: FUNC.index(ROW[a]) for a in range(NL)}


def red2_masks(C, cap):
    """distinct reduction masks R(W) = (union of Viol over the 2-dim subspace W) & C with |R| <= cap, and the W's."""
    out = defaultdict(list)
    for a, b in SUB2:
        m = (FUNC[a] | FUNC[b] | FUNC[a ^ b]) & C
        if popc(m) <= cap:
            out[m].append((a, b, a ^ b))
    return out


def section4():
    say('== 4. root normals: red-2, red-3, red-4 sets')
    CAP = 45
    # direct red-2 masks for all 120 roots (no symmetry used)
    R2 = []
    hist0 = None
    for a in range(NL):
        d = red2_masks(CMASK[a], CAP)
        R2.append(d)
        h = Counter(popc(m) for m in d)
        if a == 0:
            hist0 = h
        assert h == hist0, a
    say('root 0: |C| = %d; distinct red-2 sets by size (size: sets) %s' % (popc(CMASK[0]), sorted(hist0.items())))
    expect('min red-2 set size for a root normal', min(hist0), 25)
    expect('all 120 roots have the same red-2 size histogram', True, True)
    small = {s: n for s, n in hist0.items() if s <= 40}
    expect('red-2 sets of size <= 40 by size', small, {25: 63, 29: 128, 33: 63, 36: 336, 37: 336, 40: 4977})
    # lambda_alpha and alpha inside the small sets
    for m, ws in R2[0].items():
        if popc(m) <= 35:
            assert m & 1 and all(LAMBDA_ALPHA[0] in w for w in ws)
    expect('every red-2 set of <= 35 lines contains alpha, and lambda_alpha lies in its W', True, True)
    notin = sum(1 for m, ws in R2[0].items() if popc(m) in (36, 37) and not all(LAMBDA_ALPHA[0] in w for w in ws))
    say('red-2 sets of 36-37 lines whose W omits lambda_alpha (info): %d' % notin)

    # red-3 and red-4 for root 0 (all by exhaustive extension of red-2 W's)
    C0 = CMASK[0]
    W2 = [(a, b, a ^ b, m) for a, b in SUB2 for m in [(FUNC[a] | FUNC[b] | FUNC[a ^ b]) & C0] if popc(m) <= CAP]
    W3 = {}
    for a, b, ab, m in W2:
        sp = {a, b, ab}
        for c in range(1, 512):
            if c in sp:
                continue
            m1 = m | (FUNC[c] & C0)
            if popc(m1) > CAP:
                continue
            m3 = m1
            for x in (a ^ c, b ^ c, ab ^ c):
                m3 |= FUNC[x] & C0
            if popc(m3) <= CAP:
                W3[tuple(sorted((a, b, ab, c, a ^ c, b ^ c, ab ^ c)))] = m3
    h3 = Counter(popc(m) for m in W3.values())
    say('root 0: red-3 sets (3-dim W) of size <= %d by size %s' % (CAP, sorted(h3.items())))
    expect('min red-3 set size for a root normal', min(h3), 37)
    expect('number of 3-dim W with |R| = 37', h3[37], 336)
    h4 = Counter()
    for key, m3 in W3.items():
        ks = set(key)
        for d in range(1, 512):
            if d in ks:
                continue
            m4 = m3 | (FUNC[d] & C0)
            if popc(m4) > CAP:
                continue
            for x in key:
                m4 |= FUNC[x ^ d] & C0
            if popc(m4) <= CAP:
                h4[popc(m4)] += 1
    say('root 0: red-4 sets (4-dim W) of size <= %d by size %s' % (CAP, sorted(h4.items())))
    expect('min red-4 set size for a root normal', min(h4), 45)
    red3 = sorted(set(m for m in W3.values() if popc(m) <= PMAX), key=lambda m: (popc(m), m))
    return R2, red3


R2, RED3_0 = section4()

# Stab(root 0) = W(E7) x {+-1}: generated by the reflections in the 63 lines orthogonal to root 0
STAB_GENS = [REFL[a] for a in range(1, NL) if G[0][a] == 0]
expect('lines orthogonal to root 0', len(STAB_GENS), 63)


def stab_orbit_reps(masks):
    left = set(masks)
    reps = []
    while left:
        s = min(left, key=lambda m: (popc(m), m))
        orb = {s}
        fr = [s]
        while fr:
            nf = []
            for m in fr:
                for g in STAB_GENS:
                    w = apply_perm(m, g)
                    if w not in orb:
                        orb.add(w)
                        nf.append(w)
            fr = nf
        assert orb <= set(masks)
        reps.append((popc(s), len(orb), s))
        left -= orb
    return reps


REPS = stab_orbit_reps([m for m in R2[0] if popc(m) <= PMAX])
say('Stab(root 0) orbit representatives of red-2 sets (size, orbit length): %s' % [(s, n) for s, n, _ in REPS])
if PMAX == 38:
    expect('orbit-representative sizes of root-0 red-2 sets', [s for s, _, _ in REPS], [25, 29, 29, 33, 36, 37])


# Weyl elements g_a with g_a(0) = a, to move root-0 data to root a
def weyl_to(a):
    if a == 0:
        return list(range(NL))
    if G[0][a] != 0:
        v = tuple(x - (1 if G[0][a] > 0 else -1) * y for x, y in zip(LINES[0], LINES[a]))
        b = LIDX[canon(v)]
        assert REFL[b][0] == a
        return REFL[b]
    c = next(c for c in range(1, NL) if G[0][c] != 0 and G[c][a] != 0)
    v = tuple(x - (1 if G[c][a] > 0 else -1) * y for x, y in zip(LINES[c], LINES[a]))
    b = LIDX[canon(v)]
    gc = weyl_to(c)
    g = [REFL[b][gc[i]] for i in range(NL)]
    assert g[0] == a
    return g


WEYL = [weyl_to(a) for a in range(NL)]


# option sets: (mask, root, level) for level 2 (red-2) and 3 (red-3)
def build_entries(pmax):
    ent = {}
    for a in range(NL):
        for m in R2[a]:
            if popc(m) <= pmax:
                ent[(m, a)] = 2
    for m in RED3_0:
        if popc(m) <= pmax:
            for a in range(NL):
                ent[(apply_perm(m, WEYL[a]), a)] = 3
    return [(m, a, l) for (m, a), l in ent.items()]


ENTRIES = build_entries(PMAX)
say('option sets for the DFS (|set| <= %d): red-2 %d, red-3 %d' % (PMAX, sum(1 for e in ENTRIES if e[2] == 2), sum(1 for e in ENTRIES if e[2] == 3)))
# cross-check the transported red-3 sets against a direct computation for two other roots
for a in (17, 101):
    Ca = CMASK[a]
    moved = set(apply_perm(m, WEYL[a]) for m in RED3_0 if popc(m) <= PMAX)
    direct = set()
    for m, ws in R2[a].items():
        if popc(m) > PMAX:
            continue
        for a1, b1, ab1 in ws[:1]:
            sp = {a1, b1, ab1}
            for c in range(1, 512):
                if c not in sp:
                    m3 = m | ((FUNC[c] | FUNC[a1 ^ c] | FUNC[b1 ^ c] | FUNC[ab1 ^ c]) & Ca)
                    if popc(m3) <= PMAX:
                        direct.add(m3)
    assert moved <= direct, a
expect('transported red-3 sets agree with a direct computation at roots 17 and 101', True, True)


# ------------------------------------------------------------------------------------------------------
# 5. the covering DFS:  E(p)
# ------------------------------------------------------------------------------------------------------
def e_main(r, in_p):
    # extra saving of a root normal with reduction r >= 2: one side only: r-1; parallel term a_k || b_k = alpha:
    # s <= 2r-1 if alpha is punctured (u_alpha in V^perp \ V), s <= 2r otherwise; the base saving of a term is 2.
    return max(r - 1, 2 * r - 3) if in_p else 2 * r - 2


def e_relaxed(r, in_p):
    return 2 * r - 2 if in_p else 2 * r - 2


def dfs(entries, seeds, pmax, scorers=(e_main,)):
    """Exact enumeration of all unions U of option sets with |U| <= pmax reachable from a seed by adding only
    'useful' sets (a set whose root is not yet at that level).  Returns best[k][s] = (E, roots, U) for the best
    score of scorer k over unions of size exactly s, and the node count."""
    best = [dict() for _ in scorers]
    visited = set()
    nodes = [0]

    def rec(U, cands):
        if U in visited:
            return
        visited.add(U)
        nodes[0] += 1
        lev = {}
        for m, a, l in cands:
            if m & ~U == 0 and lev.get(a, 0) < l:
                lev[a] = l
        s = popc(U)
        for k, sc in enumerate(scorers):
            E = sum(sc(r, bool(U >> a & 1)) for a, r in lev.items() if r >= 2)
            if s not in best[k] or E > best[k][s][0]:
                best[k][s] = (E, sorted(lev.items()), U)
        for m, a, l in cands:
            if lev.get(a, 0) >= l:
                continue
            V = U | m
            sV = popc(V)
            if sV > pmax or V in visited:
                continue
            slack = pmax - sV
            rec(V, [c for c in cands if popc(c[0] & ~V) <= slack])

    for U0 in seeds:
        slack = pmax - popc(U0)
        rec(U0, [c for c in entries if popc(c[0] & ~U0) <= slack])
    return best, nodes[0]


def cumulative(best_k, pmax, lo=0):
    out, cur = {}, 0
    for q in range(lo, pmax + 1):
        if q in best_k and best_k[q][0] > cur:
            cur = best_k[q][0]
        out[q] = cur
    return out


def run_main():
    say('== 5. E(p): complete DFS over unions of reduction sets, root 0 covered WLOG (Stab orbit representatives)')
    seeds = [m for s, n, m in REPS]
    best, nodes = dfs(ENTRIES, seeds, PMAX, (e_main, e_relaxed))
    say('DFS nodes (distinct unions): %d' % nodes)
    E = cumulative(best[0], PMAX)
    for q in range(24, PMAX + 1):
        if q in best[0]:
            Ev, lev, U = best[0][q]
            if Ev > 0 and (q == 25 or Ev > E.get(q - 1, 0)):
                say('  first reached at p=%d: E=%d, reduced roots (root, red) %s' % (q, Ev, [(a, r) for a, r in lev if r >= 2]))
    for q in range(20, PMAX + 1):
        say('E(%2d) = %d   ->  C >= %d' % (q, E[q], 56 - E[q]))
    return best, E


MAIN_BEST, E_TABLE = run_main()
WANT_E = {}
for q in range(0, PMAX + 1):
    WANT_E[q] = 0 if q <= 24 else 1 if q == 25 else 2 if q <= 35 else 6 if q <= 38 else None
for q in range(24, min(PMAX, 38) + 1):
    expect('E(%d)' % q, E_TABLE[q], WANT_E[q])
for q in range(0, 25):
    assert E_TABLE.get(q, 0) == 0
expect('E(p) = 0 for p <= 24', True, True)
# the p = 36 optimum
Ev, lev, U36 = MAIN_BEST[0][36]
red36 = [(a, r) for a, r in lev if r >= 2]
expect('p=36 optimum: reduced roots (all red 2, all in the puncture)', (len(red36), all(r == 2 and U36 >> a & 1 for a, r in red36)), (6, True))
expect('C = 48 impossible for n >= 82: smallest C bound over 0 <= p <= 38', min(56 - E_TABLE[q] for q in range(0, 39)), 50)
expect('C bound for n >= 85 (p <= 35)', min(56 - E_TABLE[q] for q in range(0, 36)), 54)


# 5b. cross-check without the Stab reduction: seed with EVERY red-2 set of root 0 (still using W-transitivity on roots)
if PMAX == 38:
    all0 = sorted(m for m in R2[0] if popc(m) <= PMAX)
    best_b, nodes_b = dfs(ENTRIES, all0, PMAX, (e_main,))
    E_B = cumulative(best_b[0], PMAX)
    say('DFS from all %d red-2 sets of root 0 (no orbit reduction): %d nodes' % (len(all0), nodes_b))
    expect('E(p) table without the orbit reduction equals the table with it', [E_B[q] for q in range(PMAX + 1)], [E_TABLE[q] for q in range(PMAX + 1)])


# ------------------------------------------------------------------------------------------------------
# 6. Z16-constrained bound: punctures containing the 16 lines of two orthogonal frames
# ------------------------------------------------------------------------------------------------------
def derive_z16():
    path = os.path.join(os.path.dirname(os.path.dirname(HERE)), Z16_FILE)
    if not os.path.exists(path):
        raise SystemExit('missing repository file %s' % Z16_FILE)
    raw = open(path, 'rb').read()
    expect('SHA256 of repository file %s' % Z16_FILE, hashlib.sha256(raw).hexdigest(), Z16_SHA256)
    L = raw.decode().split('\n')
    Dr = [[int(x) for x in l[3:].split()] for l in L if l.startswith(' d:')]
    Tr = [[int(x) for x in l[3:].split()] for l in L if l.startswith(' t:')]
    n = len(Dr[0])
    expect('PR968 decoder file: terms, ports', (len(Dr), len(Tr), n), (8, 8, 104))
    g = [[sum(Dr[k][i] * Tr[k][j] for k in range(8)) for j in range(n)] for i in range(n)]
    assert all(x % 2 == 0 for r in g for x in r)
    g = [[x // 2 for x in r] for r in g]                       # Gram matrix of the 104 live lines: D T^T / 2
    assert all(g[i][j] == g[j][i] for i in range(n) for j in range(n))
    expect('Gram of the 104 live lines: diagonal, off-diagonal values', (set(g[i][i] for i in range(n)), sorted(set(g[i][j] for i in range(n) for j in range(n) if i != j))), ({2}, [-1, 0, 1]))

    def rank_of(idx):
        M = [[Fraction(g[i][j]) for j in idx] for i in idx]
        r = 0
        for c in range(len(idx)):
            p = next((q for q in range(r, len(idx)) if M[q][c] != 0), None)
            if p is None:
                continue
            M[r], M[p] = M[p], M[r]
            for q in range(len(idx)):
                if q != r and M[q][c] != 0:
                    f = M[q][c] / M[r][c]
                    M[q] = [x - f * y for x, y in zip(M[q], M[r])]
            r += 1
        return r

    B = []
    for i in range(n):
        if rank_of(B + [i]) == len(B) + 1:
            B.append(i)
        if len(B) == 8:
            break
    N = 8
    M = [[Fraction(g[bi][bj]) for bj in B] + [Fraction(int(r == c)) for c in range(N)] for r, bi in enumerate(B)]
    for c in range(N):
        p = next(r for r in range(c, N) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        M[c] = [x / M[c][c] for x in M[c]]
        for r in range(N):
            if r != c and M[r][c] != 0:
                M[r] = [x - M[r][c] * y for x, y in zip(M[r], M[c])]
    GBi = [[M[i][N + j] for j in range(N)] for i in range(N)]
    coef = [[sum(g[j][B[t]] * GBi[t][k] for t in range(N)) for k in range(N)] for j in range(n)]
    found = []

    def bt(ch):
        if found:
            return
        k = len(ch)
        if k == 8:
            imgs = []
            for j in range(n):
                v = tuple(sum(coef[j][t] * ch[t][s] for t in range(8)) for s in range(8))
                if any(Fraction(x).denominator != 1 for x in v):
                    return
                v = tuple(int(x) for x in v)
                if v not in ROOTSET:
                    return
                imgs.append(LIDX[canon(v)])
            found.append(imgs)
            return
        for r in ROOTS:
            if all(dot(r, ch[t]) // 4 == g[B[k]][B[t]] for t in range(k)):
                bt(ch + [r])
                if found:
                    return

    bt([ROOTS[0]])
    if not found:
        raise SystemExit('could not embed the 104-line clique into E8')
    imgs = found[0]
    expect('embedded lines are 104 distinct E8 lines with the same |Gram|', (len(set(imgs)), all(abs(G[imgs[i]][imgs[j]]) == abs(g[i][j]) for i in range(n) for j in range(n))), (104, True))
    z = sorted(set(range(NL)) - set(imgs))
    expect('complement Z16 size', len(z), 16)
    # the non-orthogonality graph on Z16 is bipartite with both sides mutually orthogonal: two disjoint frames
    color = {z[0]: 0}
    queue = [z[0]]
    while queue:
        i = queue.pop()
        for j in z:
            if j != i and G[i][j] != 0:
                if j not in color:
                    color[j] = 1 - color[i]
                    queue.append(j)
                assert color[j] == 1 - color[i], 'non-orthogonality graph on Z16 is not bipartite'
    F0 = [i for i in z if color.get(i) == 0]
    F1 = [i for i in z if color.get(i) == 1]
    expect('Z16 = F0 + F1: sizes, each side mutually orthogonal',
           (len(F0), len(F1), all(G[i][j] == 0 for i in F0 for j in F0 if i != j), all(G[i][j] == 0 for i in F1 for j in F1 if i != j)),
           (8, 8, True, True))
    deg = sorted(sum(1 for j in F1 if G[i][j] != 0) for i in F0)
    expect('every F0 line is non-orthogonal to exactly four F1 lines', deg, [4] * 8)
    return z


Z16 = derive_z16()
UZ = mask_of(Z16)
bestz, nodesz = dfs(ENTRIES, [UZ], PMAX, (e_main,))
EZ = cumulative(bestz[0], PMAX, lo=16)
say('Z16 DFS nodes: %d' % nodesz)
for q in range(30, PMAX + 1):
    say('E_Z(%d) = %d   ->  C >= %d' % (q, EZ[q], 56 - EZ[q]))
for q in range(33, min(PMAX, 38) + 1):
    expect('E_Z(%d)' % q, EZ[q], 0 if q <= 34 else 1 if q == 35 else 2)
assert all(EZ[q] == 0 for q in range(16, 35))
expect('E_Z(p) = 0 for 16 <= p <= 34', True, True)
expect('Z16 case: smallest C bound over Z16-containing punctures with p <= 37', min(56 - EZ[q] for q in range(16, 38)), 54)
if PMAX > 38:
    for q in range(39, PMAX + 1):
        say('E(%d) = %d, E_Z(%d) = %d  (not asserted)' % (q, E_TABLE[q], q, EZ[q]))


# ------------------------------------------------------------------------------------------------------
# 7. controls: perturbations that must change a checked number
# ------------------------------------------------------------------------------------------------------
def controls():
    say('== 7. controls')
    # (a) perturbed pairing: flip one symmetric entry of S9
    rows = list(ROW)
    rows[0] ^= 1 << 1
    rows[1] ^= 1 << 0
    rk, _ = build_functionals(rows)
    detected('perturbed pairing (one symmetric entry flipped)', rk != 9, 'F2 rank becomes %d instead of 9' % rk)
    # (b) pairing without the unit coordinate: S8 = <r_i,r_j> mod 2
    rows8 = [mask_of(j for j in range(NL) if G[i][j] % 2 != 0) for i in range(NL)]
    rk8, F8 = build_functionals(rows8)
    subs8 = [(a, b) for a in range(1, 1 << rk8) for b in range(a + 1, 1 << rk8) if (a ^ b) > b]
    C0 = CMASK[0]
    h8 = Counter(popc((F8[a] | F8[b] | F8[a ^ b]) & C0) for a, b in subs8)
    single8 = min(popc(F8[c] & C0) for c in range(1, 1 << rk8))
    base = (min(popc(FUNC[c] & C0) for c in range(1, 512)), min(popc((FUNC[a] | FUNC[b] | FUNC[a ^ b]) & C0) for a, b in SUB2))
    detected('pairing without the unit coordinate', (single8, min(h8)) != base,
             'rank %d; (min single, min red-2) = (%d, %d) instead of %s' % (rk8, single8, min(h8), base))
    # (c) drop one orbit representative (the 25-line one): the exact E(25) must fall
    ent26a = [e for e in ENTRIES if popc(e[0]) <= 26]
    seeds = [m for s_, n_, m in REPS if s_ <= 26]
    full_b, _ = dfs(ent26a, seeds, 26)
    miss_b, _ = dfs(ent26a, [m for s_, n_, m in REPS if s_ <= 26 and s_ != 25], 26)
    Ef, Em = cumulative(full_b[0], 26)[25], cumulative(miss_b[0], 26)[25]
    detected('missing orbit representative (size 25)', Em != Ef, 'E(25) = %d with the 25-line representative, %d without it' % (Ef, Em))
    # (d) relaxed parallel rule (no -1 for a punctured root): E(36) from the stored run
    Er = cumulative(MAIN_BEST[1], PMAX)
    detected('relaxed parallel rule (2r-2 even for a punctured root)', Er[36] != E_TABLE[36], 'E(36) = %d instead of %d' % (Er[36], E_TABLE[36]))
    # (e) relaxed red rule: the root's own line need not be punctured
    ent_r = [(m & ~(1 << a), a, l) for m, a, l in ENTRIES if popc(m) <= 26]
    seeds_r = sorted(set(m & ~1 for m in R2[0] if popc(m) <= 26))
    best_r, _ = dfs(ent_r, seeds_r, 26)
    Err = cumulative(best_r[0], 26)
    detected('relaxed red rule (own line not required)', Err[24] > 0, 'E(24) = %d instead of 0' % Err[24])
    # (f) Z16 replaced by 16 lines inside a minimal red-2 set
    m25 = min((m for m in R2[0] if popc(m) == 25))
    fake = mask_of(members(m25)[:16])
    ent26 = [e for e in ENTRIES if popc(e[0]) <= 26]
    best_f, _ = dfs(ent26, [fake], 26)
    Ef_ = cumulative(best_f[0], 26, lo=16)
    detected('Z16 replaced by 16 lines of a 25-line reduction set', Ef_[25] > 0 and EZ[25] == 0, 'E_Z(25) = %d instead of %d' % (Ef_[25], EZ[25]))


controls()
say('all checks passed; total runtime %.1fs' % (time.perf_counter() - T0))
print('PASS_OWNED_DELETION_BOUND')
