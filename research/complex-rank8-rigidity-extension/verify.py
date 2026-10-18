#!/usr/bin/env python3
"""Rank-8 rigidity of the E-graph system passes to supersets (Lemma 10), and the census of the
intermediate punctures P112 minus X that it reaches.

Standard library only, exact integer arithmetic. Independent of PR1212's code: own E8 model, frames,
reflections, stabiliser orbits, span checks and census. Run from the repository root:

    python3 -I -B research/complex-rank8-rigidity-extension/verify.py
"""

import itertools
import math
import sys
from collections import Counter
from fractions import Fraction

RESULTS = []


def check(tag, cond, info=''):
    RESULTS.append(tag)
    status = 'PASS' if cond else 'FAIL'
    print(f'{status} {tag}' + (f': {info}' if info else ''))
    if not cond:
        print(f'FAIL_COMPLEX_RANK8_RIGIDITY_EXTENSION: {tag}')
        sys.exit(1)


# ---------------------------------------------------------------- E8 model (doubled coordinates)

def lines_e8():
    """One representative per root line, roots in doubled coordinates (norm 8), canonical sign:
    the first nonzero coordinate is positive."""
    out = set()
    for i, j in itertools.combinations(range(8), 2):
        for sj in (2, -2):
            v = [0] * 8
            v[i], v[j] = 2, sj
            out.add(tuple(v))
    for s in itertools.product((1, -1), repeat=7):
        v = (1,) + s
        if v.count(-1) % 2 == 0:
            out.add(v)
    return sorted(out)


LINES = lines_e8()
NL = len(LINES)
IDX = {v: n for n, v in enumerate(LINES)}


def canon(v):
    v = tuple(v)
    first = next(a for a in v if a)
    return v if first > 0 else tuple(-a for a in v)


def ip(x, y):
    d = sum(a * b for a, b in zip(x, y))
    assert d % 4 == 0
    return d // 4


G = [[ip(LINES[i], LINES[j]) for j in range(NL)] for i in range(NL)]
ORTH = [[j for j in range(NL) if j != i and G[i][j] == 0] for i in range(NL)]
ORTH_MASK = [sum(1 << j for j in ORTH[i]) for i in range(NL)]

FRAME0 = frozenset(IDX[canon(v)] for v in [
    (2, 2, 0, 0, 0, 0, 0, 0), (2, -2, 0, 0, 0, 0, 0, 0), (0, 0, 2, 2, 0, 0, 0, 0), (0, 0, 2, -2, 0, 0, 0, 0),
    (0, 0, 0, 0, 2, 2, 0, 0), (0, 0, 0, 0, 2, -2, 0, 0), (0, 0, 0, 0, 0, 0, 2, 2), (0, 0, 0, 0, 0, 0, 2, -2)])
P112 = [i for i in range(NL) if i not in FRAME0]


def all_frames():
    out = []

    def grow(cur, cand):
        if len(cur) == 8:
            out.append(frozenset(cur))
            return
        c = cand
        while c:
            j = (c & -c).bit_length() - 1
            c &= c - 1
            grow(cur + [j], cand & ORTH_MASK[j] & ~((1 << (j + 1)) - 1))

    grow([], (1 << NL) - 1)
    return out


def reflection_perm(r):
    """Line permutation of the reflection in root r: v -> v - <v, r> r (Gram units)."""
    rv = LINES[r]
    return tuple(IDX[canon(tuple(a - G[i][r] * b for a, b in zip(LINES[i], rv)))] for i in range(NL))


def frame_type(F1, F2):
    """Multiplicities of the classes of F1 met by F2. A line f outside F1 is non-orthogonal to exactly four
    lines T_f of F1; its class is T_f together with the sign pattern of <r_f, r_e> (e in T_f) up to overall
    sign and parity (PR1212's Hadamard classes)."""
    F1s = sorted(F1)
    cls = Counter()
    for f in F2:
        T = tuple(e for e in F1s if G[f][e] != 0)
        signs = [G[f][e] for e in T]
        cls[(T, signs.count(-1) % 2)] += 1
    return tuple(sorted(cls.values(), reverse=True))


def rank_int(vectors, target=None):
    """Exact rank by fraction-free incremental elimination; stops early at `target`."""
    basis = []  # list of (pivot, row)
    for v in vectors:
        v = list(v)
        for p, b in basis:
            if v[p]:
                v = [x * b[p] - y * v[p] for x, y in zip(v, b)]
        nz = [k for k, x in enumerate(v) if x]
        if nz:
            g = math.gcd(*v)
            basis.append((nz[0], [x // g for x in v]))
            if target is not None and len(basis) >= target:
                break
    return len(basis)


# ---------------------------------------------------------------- exact linear algebra for the controls

def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def rank_q(rows):
    M = [[Fraction(x) for x in r] for r in rows]
    rk, col = 0, 0
    ncol = len(M[0]) if M else 0
    while rk < len(M) and col < ncol:
        piv = next((r for r in range(rk, len(M)) if M[r][col] != 0), None)
        if piv is None:
            col += 1
            continue
        M[rk], M[piv] = M[piv], M[rk]
        for r in range(len(M)):
            if r != rk and M[r][col] != 0:
                f = M[r][col] / M[rk][col]
                M[r] = [a - f * b for a, b in zip(M[r], M[rk])]
        rk += 1
        col += 1
    return rk


def e_system_holds(K, live):
    """(E) on the live list: K_ii = 4 and K_ij = 0 on orthogonal live pairs; odd entries free."""
    for a, i in enumerate(live):
        if K[a][a] != 4:
            return False
        for b, j in enumerate(live):
            if a != b and G[i][j] == 0 and K[a][b] != 0:
                return False
    return True


def is_gauge(K, live):
    """K = D (2G) D^{-1}: K_ij = 0 iff G_ij = 0, and d_i/d_j recovered consistently along a spanning tree."""
    n = len(live)
    for a in range(n):
        for b in range(n):
            if (K[a][b] == 0) != (G[live[a]][live[b]] == 0):
                return False
    d = [None] * n
    d[0] = Fraction(1)
    stack = [0]
    while stack:
        a = stack.pop()
        for b in range(n):
            if d[b] is None and G[live[a]][live[b]] != 0:
                d[b] = d[a] * 2 * G[live[a]][live[b]] / K[a][b]  # K_ab = 2 G_ab d_a / d_b
                stack.append(b)
    if any(x is None for x in d):
        return False
    return all(K[a][b] == 2 * G[live[a]][live[b]] * d[a] / d[b] for a in range(n) for b in range(n))


def lcg(seed):
    x = seed
    while True:
        x = (x * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        yield x >> 33


def rand_nonzero(rng):
    v = 0
    while v == 0:
        v = next(rng) % 9 - 4
    return Fraction(v, next(rng) % 5 + 1)


def gauge_matrix(live, d):
    n = len(live)
    return [[2 * G[live[a]][live[b]] * d[a] / d[b] for b in range(n)] for a in range(n)]


# ---------------------------------------------------------------- checks

def main():
    check('model.lines', NL == 120 and all(G[i][i] == 2 for i in range(NL))
          and all(G[i][j] in (0, 1, -1) for i in range(NL) for j in range(NL) if i != j)
          and all(len(ORTH[i]) == 63 for i in range(NL)), '120 lines, off-diagonal Gram in {0,+-1}, 63 orthogonal')

    frames = all_frames()
    fset = set(frames)
    check('model.frames', len(frames) == 2025 and FRAME0 in fset, '2025 frames, FRAME0 among them')

    # W(E8) is transitive on frames (BFS under the 120 root reflections).
    refl = [reflection_perm(r) for r in range(NL)]
    seen = {FRAME0}
    todo = [FRAME0]
    while todo:
        F = todo.pop()
        for p in refl:
            H = frozenset(p[i] for i in F)
            if H not in seen:
                seen.add(H)
                todo.append(H)
    check('model.frame-transitivity', seen == fset, f'{len(seen)} frames in one orbit of W(E8)')

    # Frames inside P112, their three types, and that the types are exactly the FRAME0-stabiliser orbits.
    inside = [F for F in frames if not F & FRAME0]
    types = {F: frame_type(FRAME0, F) for F in inside}
    tcount = Counter(types.values())
    want = {(1,) * 8: 896, (2, 2, 2, 2): 336, (4, 4): 28}
    stab = [p for p in refl if frozenset(p[i] for i in FRAME0) == FRAME0]
    for p, q in itertools.combinations(refl, 2):
        pq = tuple(p[q[i]] for i in range(NL))
        if frozenset(pq[i] for i in FRAME0) == FRAME0:
            stab.append(pq)
    orbits = []
    left = set(inside)
    while left:
        F = left.pop()
        orb, todo = {F}, [F]
        while todo:
            H = todo.pop()
            for p in stab:
                J = frozenset(p[i] for i in H)
                if J not in orb:
                    orb.add(J)
                    todo.append(J)
        left -= orb
        orbits.append(orb)
    orbit_types = sorted((len(o), sorted({types[F] for F in o})) for o in orbits)
    check('unit.frame-orbits', len(inside) == 1260 and dict(tcount) == want and len(orbits) == 3
          and all(len(ts) == 1 and want[ts[0]] == n for n, ts in orbit_types),
          f'1260 frames in P112; stabiliser orbits {[n for n, _ in orbit_types]} = types (4,4), (2,2,2,2), (1,...,1); '
          f'{len(stab)} stabiliser generators')

    # Lemma 10 span condition: for every bi-frame unit L = E8 \ (FRAME0 u F) and every i in FRAME0 u F,
    # the lines of L orthogonal to i span r_i^perp (rank 7). By transitivity this covers every pair of
    # disjoint frames.
    worst = 63
    bad = 0
    for F in inside:
        R = FRAME0 | F
        for i in R:
            vecs = [LINES[j] for j in ORTH[i] if j not in R]
            worst = min(worst, len(vecs))
            if rank_int(vecs, 7) != 7:
                bad += 1
    check('lemma10.span-condition', bad == 0,
          f'1260 units x 16 new lines: orthogonal live lines span r_i^perp (at least {worst} such lines each)')

    # Census: FRAME0 u X lies in a union of two disjoint frames iff X lies in a frame inside P112.
    covers = set()
    for F1 in frames:
        A = F1 & FRAME0
        if not A:
            continue
        for F2 in frames:
            if not F2 & F1 and FRAME0 - A <= F2:
                covers.add(frozenset((F1 | F2) - FRAME0))
    check('census.biframe-covers', covers == set(inside),
          f'{len(covers)} maximal X; every one is a frame inside P112')

    # Every line of P112 lies in a type-(2,2,2,2) frame inside P112: P111 from PR1212 Theorem 1' alone.
    by2222 = set().union(*(F for F in inside if types[F] == (2, 2, 2, 2)))
    check('census.p111-from-2222', by2222 == set(P112), 'all 112 lines lie in a type-(2,2,2,2) frame')

    # Count, for each k, the X of size k inside a frame of P112, by the cheapest rigid unit available.
    pref = [((2, 2, 2, 2), 'PR1212'), ((1,) * 8, 'PR1399'), ((4, 4), 'PR1389')]
    rank_of = {t: n for n, (t, _) in enumerate(pref)}
    orth_count = Counter()
    p112_mask = sum(1 << i for i in P112)

    def cliques(size, cand):
        orth_count[size] += 1
        if size == 8:
            return
        c = cand
        while c:
            j = (c & -c).bit_length() - 1
            c &= c - 1
            cliques(size + 1, cand & ORTH_MASK[j] & ~((1 << (j + 1)) - 1))

    cliques(0, p112_mask)
    table = {}
    for k in range(1, 9):
        best = {}
        for F in inside:
            r = rank_of[types[F]]
            for X in itertools.combinations(sorted(F), k):
                if best.get(X, 9) > r:
                    best[X] = r
        dep = Counter(pref[r][1] for r in best.values())
        table[k] = (math.comb(112, k), orth_count[k], len(best), dep['PR1212'], dep['PR1399'], dep['PR1389'])
    expect = {1: (112, 112, 112, 112, 0, 0), 2: (6216, 3304, 3304), 7: (36227890512, 10592, 10080),
              8: (475491062970, 1260, 1260, 336, 896, 28)}
    ok = all(table[k][:len(v)] == v for k, v in expect.items())
    for k in range(1, 9):
        tot, orth, cov, a, b, c = table[k]
        print(f'     |X|={k}  P{112 - k}: {tot} X, {orth} orthogonal, {cov} inside a P112 frame '
              f'(PR1212 {a}, PR1399 {b}, PR1389 {c}); fraction {cov / tot:.3e}')
    check('census.table', ok, 'all orthogonal pairs covered; table above')

    # What is left at P110: the odd pairs, by FRAME0-stabiliser orbit (for the open next question).
    odd = [frozenset(x) for x in itertools.combinations(P112, 2) if G[x[0]][x[1]] != 0]
    left, sizes = set(odd), []
    while left:
        X = left.pop()
        orb, todo = {X}, [X]
        while todo:
            H = todo.pop()
            for p in stab:
                J = frozenset(p[i] for i in H)
                if J not in orb:
                    orb.add(J)
                    todo.append(J)
        left -= orb
        a, b = sorted(X)
        meet = len([e for e in FRAME0 if G[a][e] and G[b][e]])
        sizes.append((len(orb), meet))
    sizes.sort()
    check('census.p110-odd-orbits', len(odd) == 2912 and sizes == [(224, 4), (2688, 2)],
          'uncovered P110: 2912 odd pairs in two stabiliser orbits, 224 (same FRAME0 block) and 2688 '
          '(blocks meeting in 2)')

    controls(inside, types)

    n_cov = sum(table[k][2] for k in range(2, 8))
    print(f'PASS_COMPLEX_RANK8_RIGIDITY_EXTENSION: checks {len(RESULTS)}; Lemma 10 on all 1260 bi-frame units; '
          f'{n_cov} punctures P105-P110 covered (all {table[2][1]} orthogonal-pair P110); P111 from PR1212 alone; '
          f'P104 rigidity cited from PR1212/PR1389/PR1399')


def controls(inside, types):
    rng = lcg(20261013)
    # Base unit: a type-(2,2,2,2) bi-frame complement; superset L' adds one line i of the punctured frame F.
    F = min((F for F in inside if types[F] == (2, 2, 2, 2)), key=sorted)
    R = FRAME0 | F
    base = [j for j in range(NL) if j not in R]
    i = min(F)
    live = base + [i]
    d = [rand_nonzero(rng) for _ in live]
    K = gauge_matrix(live, d)
    check('lemma10.positive', e_system_holds(K, live) and is_gauge(K, live)
          and rank_q([r[:] for r in K]) == 8, f'gauge solution on {len(live)} lines satisfies (E), rank 8')

    # Lemma 10 mechanism, exactly: new row i equals 2 u^T R^T D^{-1} on the base; the zeros at base lines
    # orthogonal to i put u in the annihilator of 7 independent vectors of r_i^perp, i.e. on the line of r_i.
    zs = [LINES[j] for j in ORTH[i] if j not in R]
    check('lemma10.row-forced', rank_q(zs) == 7 and all(ip(LINES[i], z) == 0 for z in zs),
          f'{len(zs)} orthogonal base lines: u in their annihilator, which is spanned by r_i')

    # Control 1: rank 9 escapes. Add a rank-one term supported on row i and odd columns only; (E) still holds.
    odd_cols = [b for b, j in enumerate(live) if j != i and G[i][j] != 0]
    K9 = [r[:] for r in K]
    for b in odd_cols[:3]:
        K9[-1][b] += rand_nonzero(rng)
    check('control.rank9-escapes', e_system_holds(K9, live) and not is_gauge(K9, live)
          and rank_q(K9) == 9, 'rank-9 perturbation on odd entries of the new row satisfies (E), not gauge')

    # Control 2: span condition needed. Choose n in r_i^perp and drop every base line orthogonal to i but not
    # to n. The surviving orthogonal lines span only a hyperplane of r_i^perp; build a rank-8 non-gauge
    # extension with new row u = c (r_i + t n) and column w = r_i / c (doubled-coordinate vectors).
    n_vec = next(LINES[j] for j in ORTH[i] if j not in R)
    drop = {j for j in ORTH[i] if j not in R and ip(LINES[j], n_vec) != 0}
    base2 = [j for j in base if j not in drop]
    zs2 = [LINES[j] for j in ORTH[i] if j in base2]
    rows = [LINES[j] for j in base2]
    full = rank_q(rows)
    live2 = base2 + [i]
    d2 = [rand_nonzero(rng) for _ in base2]
    c, t = rand_nonzero(rng), rand_nonzero(rng)
    u = [c * (a + t * b) for a, b in zip(LINES[i], n_vec)]
    w = [Fraction(a) / c for a in LINES[i]]
    X = [[d2[a] * x for x in LINES[j]] for a, j in enumerate(base2)] + [u]
    Y = [[x / d2[a] for x in LINES[j]] for a, j in enumerate(base2)] + [w]
    # K = X Y^T / 4 * 2: roots are doubled (norm 8), so <x, y>_Gram = x.y / 4 and K = 2 <.,.>.
    K2 = [[Fraction(2) * sum(p * q for p, q in zip(x, y)) / 4 for y in Y] for x in X]
    check('control.span-needed', full == 8 and rank_q(zs2) == 6 and e_system_holds(K2, live2)
          and not is_gauge(K2, live2) and rank_q(K2) == 8,
          f'dropping {len(drop)} lines leaves rank 6 in r_i^perp; a rank-8 non-gauge extension satisfies (E)')

    # Control 3: a perturbed orthogonal entry of the extended gauge solution violates (E).
    Kp = [r[:] for r in K]
    b = next(b for b, j in enumerate(live) if j != i and G[i][j] == 0)
    Kp[-1][b] = Fraction(1, 7)
    check('control.perturbed-fails', not e_system_holds(Kp, live), 'nonzero orthogonal entry is rejected')


if __name__ == '__main__':
    main()
