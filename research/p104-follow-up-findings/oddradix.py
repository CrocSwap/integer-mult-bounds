#!/usr/bin/env python3
"""ODDRADIX checker: odd-radix framework facts (symmetric rank-1 counts, endpoint wrapper identity, Lemma Z admissibility).

Own code (DreamingOfClouds with Claude Opus 5.5), standard library only.  Tags: [C] exact computation.
Lemma Z and the endpoint lemma are proved in PROOF.md; this script only checks instances.  The exhaustive m=4 search
(548,000 rank-1 unit conjugates) and the m=2 complete tables over F_7/F_13 are lane computations not re-run here ([C-lane]).

Checks
  A. Minimal number of rank-1 symmetric terms c v v^T summing to a symmetric B over F_p equals rank B, except over F_2 where
     it is rank B + 1 exactly when B is alternating and nonzero.  Exhaustive BFS over all symmetric m x m matrices for
     (p,m) in (2,2),(2,3),(2,4),(3,2),(3,3),(5,2),(5,3); 0 mismatches; F_2 m=4 table asserted.
  B. Endpoint wrapper identity in exact Z[zeta_p] arithmetic: for every non-isotropic line v, c != 0, j != 0:
     K_{v,c}^j = r D_a P_s K_{v,c} D_b (r = +-zeta^k).  p=3 m=1 (4/4), p=3 m=2 (16/16), p=5 m=1 (16/16);
     T2 wrappers along v commute with K_u for u perp v (p=3 m=2: 12/12); T5 K^2 is not monomial.
     Default run also does p=3 m=3 (36/36, T2 108/108, T3) and p=5 m=2 (64/64, T2 12/12, T3); --quick skips those two (~3 s total).
     T3: on an isotropic line no wrapper of this form exists (checked where an isotropic line exists: p=3 m=3 and p=5 m=2).
  C. Lemma Z (parts a, e, f of the lane check) in pure-python mod-7 matrices, polynomials in k mod k^3 - 1, omega = 2:
     admissibility table rank(u_0) vs m - o for H3 park, live planes, QUERY, QSELF, park1, C3 swap (m = 2, 4, 6, 36);
     positive control (product of m/2 C3 swap planes under a random conjugation reaches the split target at cost m);
     witness QUERY(row0 += -k row1) * H3 at m = 2 has cost m+1 = 3 and is a split target.
Prints PASS_ODD_RADIX.
"""
import itertools, random, sys


def fail(msg):
    print('FAIL:', msg); sys.exit(1)


def expect(name, got, want):
    ok = got == want
    print(('ok   ' if ok else 'FAIL ') + name + ': ' + str(got))
    if not ok:
        fail('%s: got %r want %r' % (name, got, want))


# ---------------------------------------------------------------- A
def rank_mod(M, p):
    M = [[x % p for x in r] for r in M]; n = len(M); nc = len(M[0]); r = 0
    for c in range(nc):
        piv = next((i for i in range(r, n) if M[i][c]), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]; inv = pow(M[r][c], p - 2, p)
        M[r] = [x * inv % p for x in M[r]]
        for i in range(n):
            if i != r and M[i][c]:
                f = M[i][c]; M[i] = [(a - f * b) % p for a, b in zip(M[i], M[r])]
        r += 1
    return r


def sqcount(p, m):
    idx = [(i, j) for i in range(m) for j in range(i, m)]
    terms = set()
    for v in itertools.product(range(p), repeat=m):
        if any(v):
            for c in range(1, p):
                terms.add(tuple(c * v[i] * v[j] % p for i, j in idx))
    terms = list(terms)
    zero = tuple([0] * len(idx))
    dist = {zero: 0}; frontier = [zero]
    while frontier:
        nf = []
        for s in frontier:
            for t in terms:
                u = tuple((a + b) % p for a, b in zip(s, t))
                if u not in dist: dist[u] = dist[s] + 1; nf.append(u)
        frontier = nf
    bad = 0; stats = {}
    for s, k in dist.items():
        M = [[0] * m for _ in range(m)]
        for (i, j), x in zip(idx, s): M[i][j] = M[j][i] = x
        r = rank_mod(M, p); alt = (p == 2 and all(M[i][i] == 0 for i in range(m)) and r > 0)
        pred = r + 1 if alt else r
        stats[(r, alt, k)] = stats.get((r, alt, k), 0) + 1
        bad += (k != pred)
    return len(dist), bad, dict(sorted(stats.items()))


def part_a():
    print('== A. rank-1 symmetric decomposition counts')
    for p, m in [(2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (5, 2), (5, 3)]:
        n, bad, stats = sqcount(p, m)
        print('  p=%d m=%d: tables (rank,alternating,k):count = %s' % (p, m, stats))
        expect('A p=%d m=%d all %d symmetric matrices reached' % (p, m, p ** (m * (m + 1) // 2)), n, p ** (m * (m + 1) // 2))
        expect('A p=%d m=%d mismatches vs prediction' % (p, m), bad, 0)
        if (p, m) == (2, 4):
            expect('A F2 m=4 table', stats, {(0, False, 0): 1, (1, False, 1): 15, (2, False, 2): 105, (2, True, 3): 35,
                                             (3, False, 3): 420, (4, False, 4): 420, (4, True, 5): 28})


# ---------------------------------------------------------------- B
def wrapaudit(p, M, label_t3=True):
    def add(a, b): return tuple(x + y for x, y in zip(a, b))
    def mul(a, b):
        r = [0] * p
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    if y: r[(i + j) % p] += x * y
        return tuple(r)
    def norm(a): m = a[-1]; return tuple(x - m for x in a)
    Z0 = tuple([0] * p)
    def zp(k): r = [0] * p; r[k % p] = 1; return tuple(r)
    def sc(k, a): return tuple(k * x for x in a)
    A = list(itertools.product(range(p), repeat=M)); N = len(A); idx = {a: i for i, a in enumerate(A)}
    dot = lambda x, y: sum(i * j for i, j in zip(x, y)) % p
    def mm(X, Y):
        R = [[Z0] * N for _ in range(N)]
        for i in range(N):
            Xi = X[i]
            for k in range(N):
                if Xi[k] != Z0:
                    xk = Xi[k]; Yk = Y[k]
                    R[i] = [add(R[i][j], mul(xk, Yk[j])) if Yk[j] != Z0 else R[i][j] for j in range(N)]
        return R
    def canon(X): return [[norm(e) for e in row] for row in X]
    def eq_up_to(X, Y):
        cx = canon(X)
        for s in (1, -1):
            for k in range(p):
                if canon([[sc(s, mul(zp(k), e)) for e in row] for row in Y]) == cx: return (s, k)
        return None
    Fm = [[zp(dot(y, x)) for x in A] for y in A]; Fi = [[zp(-dot(y, x)) for x in A] for y in A]
    def diag(f): return [[f(A[i]) if i == j else Z0 for j in range(N)] for i in range(N)]
    def kern(v, c): return mm(mm(Fm, diag(lambda x: zp(c * dot(v, x) ** 2))), Fi)
    def chirp(v, a): return diag(lambda x: zp(a * dot(v, x) ** 2))
    def Ps(v, s):
        if dot(v, v) == 0: f = lambda x: tuple((s * xi) % p for xi in x)
        else:
            inv = pow(dot(v, v), -1, p)
            f = lambda x: tuple((xi + (s - 1) * dot(v, x) * inv * vi) % p for xi, vi in zip(x, v))
        P = [[Z0] * N for _ in range(N)]
        for a in A: P[idx[f(a)]][idx[a]] = zp(0)
        return P
    vecs = [v for v in A if any(v) and next(x for x in v if x) == 1]
    noniso = [v for v in vecs if dot(v, v) != 0]; iso = [v for v in vecs if dot(v, v) == 0]
    print('  p=%d m=%d: %d non-isotropic lines, %d isotropic lines' % (p, M, len(noniso), len(iso)))
    Kc = {}
    def K(v, c):
        if (v, c) not in Kc: Kc[(v, c)] = kern(v, c % p)
        return Kc[(v, c)]
    def wrap(v, c, j):
        T = K(v, j * c)
        for s, a, b in itertools.product(range(1, p), range(p), range(p)):
            W = mm(mm(mm(chirp(v, a), Ps(v, s)), K(v, c)), chirp(v, b))
            if eq_up_to(T, W): return (s, a, b)
        return None
    res = {}
    cnt = ok = 0
    for v in noniso:
        for c in range(1, p):
            for j in range(1, p):
                cnt += 1; ok += wrap(v, c, j) is not None
    res['T1'] = (ok, cnt)
    if iso:
        res['T3'] = wrap(iso[0], 1, p - 1)    # expected None (no solution)
        res['T3line'] = iso[0]
    if M >= 2:
        c2 = g2 = 0
        for v in noniso:
            s, a, b = wrap(v, 1, p - 1)
            Ws = [chirp(v, a), chirp(v, b), Ps(v, s)]
            for u in vecs:
                if u != v and dot(u, v) == 0:
                    Ku = K(u, 1)
                    for W in Ws:
                        c2 += 1; g2 += canon(mm(W, Ku)) == canon(mm(Ku, W))
        res['T2'] = (g2, c2)
    G = K(noniso[0], 2)
    res['T5'] = max(sum(1 for e in row if norm(e) != Z0) for row in canon(G))
    return res


def part_b(quick):
    print('== B. endpoint wrapper identity in Z[zeta_p]')
    cases = [(3, 1, (4, 4), None, 3), (3, 2, (16, 16), (12, 12), 3), (5, 1, (16, 16), None, 5)]
    if not quick: cases += [(3, 3, (36, 36), (108, 108), 3), (5, 2, (64, 64), (12, 12), 5)]
    for p, M, t1, t2, t5 in cases:
        r = wrapaudit(p, M)
        expect('B p=%d m=%d T1 wrapper identity (ok/total)' % (p, M), r['T1'], t1)
        if t2: expect('B p=%d m=%d T2 wrappers commute with K_u (ok/total)' % (p, M), r['T2'], t2)
        if 'T3' in r: expect('B p=%d m=%d T3 isotropic line %s has no wrapper' % (p, M, r['T3line']), r['T3'], None)
        else: print('  p=%d m=%d: no isotropic line, T3 not applicable' % (p, M))
        expect('B p=%d m=%d T5 K^2 max nonzeros/row (monomial would be 1)' % (p, M), r['T5'], t5)
    if quick: print('  (--quick skipped p=3 m=3 and p=5 m=2, the only cases with isotropic lines / T3)')


# ---------------------------------------------------------------- C
P = 7; W3 = 2


def zeros(m): return [[0] * m for _ in range(m)]
def eye(m): return [[int(i == j) for j in range(m)] for i in range(m)]
def mmul(A, B):
    n = len(A); k = len(B); mcol = len(B[0])
    return [[sum(A[i][t] * B[t][j] for t in range(k) if A[i][t]) % P for j in range(mcol)] for i in range(n)]
def madd(A, B, f=1): return [[(a + f * b) % P for a, b in zip(r, s)] for r, s in zip(A, B)]
def mscale(A, f): return [[x * f % P for x in r] for r in A]
def minv(A):
    n = len(A); M = [[x % P for x in r] + [int(i == j) for j in range(n)] for i, r in enumerate(A)]
    for c in range(n):
        q = next(r for r in range(c, n) if M[r][c]); M[c], M[q] = M[q], M[c]
        iv = pow(M[c][c], P - 2, P); M[c] = [x * iv % P for x in M[c]]
        for r in range(n):
            if r != c and M[r][c]:
                f = M[r][c]; M[r] = [(x - f * y) % P for x, y in zip(M[r], M[c])]
    return [r[n:] for r in M]


def coeffs(entries, m, plane=(0, 1)):
    U = [zeros(m) for _ in range(3)]
    for i in range(m):
        if i not in plane: U[0][i][i] = 1
    for a, i in enumerate(plane):
        for b, j in enumerate(plane):
            c, d = entries[a][b]; U[d % 3][i][j] = (U[d % 3][i][j] + c) % P
    return U


def evals(U):
    m = len(U[0]); out = []
    for t in range(3):
        E = zeros(m)
        for d in range(3): E = madd(E, U[d], pow(pow(W3, t, P), d, P))
        out.append(E)
    return out


def o_of(U):
    E = evals(U); m = len(E[0]); B = mmul(E[1], minv(E[0]))
    return rank_mod(madd(B, eye(m), -1), P)


def pmul(A, B):
    m = len(A[0]); C = [zeros(m) for _ in range(3)]
    for i in range(3):
        for j in range(3): C[(i + j) % 3] = madd(C[(i + j) % 3], mmul(A[i], B[j]))
    return C


def conj(U, c, ci): return [mmul(mmul(c, x), ci) for x in U]


def target_kind(T):
    E = evals(T); m = len(E[0]); E0i = minv(E[0])
    B1 = mmul(E[1], E0i); B2 = mmul(E[2], E0i)
    if mmul(B1, B1) != B2: return None
    I = eye(m)
    a = m - rank_mod(madd(B1, I, -W3), P); b = m - rank_mod(madd(B1, I, -W3 * W3 % P), P)
    return (a, b) if a + b == m else None


H3 = [[(1, 0), (-1, 1)], [(1, 2), (0, 0)]]
ALPHA = [
    ('H3', H3), ('live2', [[(1, 0), (1, 1)], [(1, 2), (2, 0)]]), ('live2b', [[(1, 0), (1, 1)], [(1, 1), (2, 0)]]),
    ('live1', [[(1, 0), (1, 0)], [(1, 1), (3, 0)]]), ('QUERY', [[(1, 0), (0, 0)], [(1, 1), (1, 0)]]),
    ('QSELF', [[(1, 1), (0, 0)], [(0, 0), (1, 0)]]), ('park1', [[(1, 0), (1, 0)], [(1, 1), (0, 0)]]),
    ('swap', [[(0, 0), (1, 1)], [(1, 2), (0, 0)]]),
]
ADM_WANT = {'H3': False, 'live2': False, 'live2b': False, 'live1': False, 'QUERY': False, 'QSELF': True, 'park1': True, 'swap': True}


def part_c():
    print('== C. Lemma Z admissibility over F_7 (omega = 2)')
    for m in (2, 4, 6, 36):
        row = []
        for name, ent in ALPHA:
            U = coeffs(ent, m); o = o_of(U); r0 = rank_mod(U[0], P); adm = (r0 == m - o)
            row.append('%s:o=%d,rk0=%d,%s' % (name, o, r0, 'ADM' if adm else 'no'))
            expect('C m=%d %s admissible' % (m, name), adm, ADM_WANT[name])
            if name == 'H3': expect('C m=%d H3 rank u0 = m-1' % m, (r0, o), (m - 1, 2))
            if name in ('live2', 'QUERY'): expect('C m=%d %s rank u0 = m' % (m, name), r0, m)
        print('  m=%2d: ' % m + ' | '.join(row))
    rng = random.Random(1)
    def rand_gl(m):
        while True:
            c = [[rng.randrange(P) for _ in range(m)] for _ in range(m)]
            if rank_mod(c, P) == m: return c
    sw = dict(ALPHA)['swap']
    for m in (4, 6):
        T = [eye(m), zeros(m), zeros(m)]; cost = 0
        for j in range(m // 2):
            U = coeffs(sw, m, plane=(2 * j, 2 * j + 1)); cost += o_of(U); T = pmul(T, U)
        c = rand_gl(m); T = conj(T, c, minv(c))
        tk = target_kind(T)
        expect('C(e) m=%d swap planes cost' % m, cost, m)
        expect('C(e) m=%d eigen-split (#w,#w^2) sums to m' % m, tk is not None and sum(tk) == m, True)
        print('     split = %s' % (tk,))
    Q = coeffs([[(1, 0), (0, 0)], [(-1, 1), (1, 0)]], 2, plane=(1, 0)); Hm = coeffs(H3, 2)
    T = pmul(Q, Hm)
    expect('C(f) m=2 witness cost m+1', o_of(Q) + o_of(Hm), 3)
    tk = target_kind(T)
    expect('C(f) m=2 witness is a split target', tk is not None, True)
    print('     witness k-coeffs %s target %s' % (T, tk))


if __name__ == '__main__':
    part_a(); part_b('--quick' in sys.argv); part_c()
    print('PASS_ODD_RADIX')
