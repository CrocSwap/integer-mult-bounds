"""Every inequality of the proof of Theorem 3 (rank lemma, star, block, edge) evaluated on explicit representations,
with a planted failure; the rank lemma on random matrices; tensor lift and column restriction (Theorem 5)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import itertools, random
from common import *

rnd = random.Random(2026)
hc = lambda A, B: [a + b for a, b in zip(A, B)]
rk = rank_mod
T = transpose

def lemma(p, N=300):
    """rk(A + B) >= rk A + rk B - dim(col A meet col B) - dim(row A meet row B), on random low-rank A, B (overlap forced in 60%)."""
    bad = 0
    for _ in range(N):
        m, n, a, b = rnd.randint(2, 7), rnd.randint(2, 7), rnd.randint(1, 3), rnd.randint(1, 3)
        F = lambda u: mat_mul([[rnd.randrange(p) for _ in range(u)] for _ in range(m)], [[rnd.randrange(p) for _ in range(n)] for _ in range(u)], p)
        A, B = F(a), F(b)
        if rnd.random() < .6:
            B = [[(x - y) % p for x, y in zip(r, s)] for r, s in zip(F(1), A)]
        ic = rk(A, p) + rk(B, p) - rk(hc(A, B), p)      # dim of the column-space meet
        ir = rk(A, p) + rk(B, p) - rk(A + B, p)         # dim of the row-space meet
        S = [[(x + y) % p for x, y in zip(r, s)] for r, s in zip(A, B)]
        bad += rk(S, p) < rk(A, p) + rk(B, p) - ic - ir
    return bad

def chain(name, U, W, K, edges, k, p, r):
    """U, W: vertex -> k x r matrices. K: vertex -> its k coordinates. edges: edge port -> (c, d). Coordinates outside K are x.
    Evaluates: gauge, forced zeros off the diagonal of each star, and the star, block and edge inequalities. Raises on a violated
    premise; returns False if an inequality of the proof fails."""
    Kc = {c for v in K.values() for c in v}
    xc = [i for i in range(r) if i not in Kc]
    j = len(xc)
    sub = lambda M, idx: [[row[i] for i in idx] for row in M]
    for c, idx in K.items():
        assert mat_mul(sub(W[c], idx), T(sub(U[c], idx)), p) == [[int(a == b) for b in range(k)] for a in range(k)], 'gauge'
    Xb = lambda S, Y: mat_mul(sub(W[S], xc), T(sub(U[Y], xc)), p) if j else [[0] * k for _ in range(k)]
    star = {c: [t for t, e in edges.items() if c in e] for c in K}
    g, info, good = {}, {}, True
    for c, st in star.items():
        if not st:
            continue
        bl = lambda f: [sum((f(a, b)[i] for b in st), []) for a in st for i in range(k)]
        A = lambda a, b: mat_mul(sub(W[a], K[c]), T(sub(U[b], K[c])), p)
        M, X = bl(A), bl(Xb)
        D = [[(x + y) % p for x, y in zip(r1, r2)] for r1, r2 in zip(M, X)]
        for ia, a in enumerate(st):
            for ib, b in enumerate(st):
                if a != b and any(D[ia * k + u][ib * k + v] for u in range(k) for v in range(k)):
                    raise ValueError('off-diagonal block of D_c nonzero at %s' % str((c, a, b)))
        for ia, a in enumerate(st):
            g[a, c] = rk([D[ia * k + u][ia * k:ia * k + k] for u in range(k)], p)
        x, rD = rk(X, p), rk(D, p)
        ic = rD + x - rk(hc(D, X), p); ir = rD + x - rk(D + X, p)
        y, yy = x - ic, x - ir
        good &= rk(M, p) <= k and rk(M, p) >= rD + x - ic - ir and rD == sum(g[a, c] for a in st) and rD <= k + x - y - yy and x <= j
        info[c] = (x, y, yy)
    for t, (c, d) in edges.items():
        s = rk(Xb(t, t), p)
        _, y1, yy1 = info[c]; _, y2, yy2 = info[d]
        good &= s <= g[t, c] + min(y1, yy1) and s <= g[t, d] + min(y2, yy2) and s <= j and k <= g[t, c] + g[t, d] + s
    req(good, '%s: k=%d, inner dimension %d, j=%d, F_%d, %d edge ports: star, block and edge inequalities hold' % (name, k, r, j, p, len(edges)))
    return good

for p in (2, 3, 101):
    req(lemma(p) == 0, 'rank lemma on 300 random pairs over F_%d: no violation' % p)

# ---- Gram representations in K-coordinates ----------------------------------------------------------------
def inv_mod2(Rm, k):
    A = [r_[:] + [int(i == j) for j in range(k)] for i, r_ in enumerate(Rm)]
    piv = 0
    for c in range(k):
        q = next(i for i in range(piv, k) if A[i][c]); A[piv], A[q] = A[q], A[piv]
        for i in range(k):
            if i != piv and A[i][c]: A[i] = [(x + y) % 2 for x, y in zip(A[i], A[piv])]
        piv += 1
    return [r_[k:] for r_ in A]

def gram(plist, K, k=1, scale=False):
    """Gram representation tensored with I_k: port t has coordinates (dot(t,c))_c and dot(t,v) in the orthonormal basis K + v;
    optionally every non-K port is rescaled by a random invertible R (W -> R^-T, U -> R) so that B stays identity-diagonal."""
    idx = {c: [i * k + a for a in range(k)] for i, c in enumerate(K)}
    r = 9 * k; U = {}; W = {}
    for t in plist:
        co = [dot(t, c) for c in K]; ev = (1 + sum(co)) % 2
        u1 = co + [ev]
        Ut = [[(u1[i] if a == b else 0) for i in range(9) for b in range(k)] for a in range(k)]
        if scale and t not in K:
            while True:
                Rm = [[rnd.randrange(2) for _ in range(k)] for _ in range(k)]
                if rk(Rm, 2) == k: break
            Ri = inv_mod2(Rm, k)
            U[t] = mat_mul(Rm, Ut, 2); W[t] = mat_mul(T(Ri), Ut, 2)
        else:
            U[t] = Ut; W[t] = [r_[:] for r_ in Ut]
    return U, W, idx, r

def edges_of(plist, K):
    Ed = {}
    for t in plist:
        if t not in K:
            A = tuple(c for c in K if dot(t, c))
            if len(A) == 2: Ed[t] = A
    return Ed

K0idx = [62, 63, 69, 74, 81, 86, 91, 99]
KP = [PORTS[i] for i in K0idx]
for nm, pl in (('P104', PORTS), ('P120', P120)):
    Ed = edges_of(pl, KP)
    U, W, idx, r = gram(pl, KP); chain(nm + ' Gram', U, W, idx, Ed, 1, 2, r)
    U, W, idx, r = gram(pl, KP, 3, True); chain(nm + ' Gram tensor I_3 with random port scalings', U, W, idx, Ed, 3, 2, r)

# ---- the 14-port representation in K coordinates, over F_2 and F_101 -------------------------------------------
Wd = load('witness14.json'); coords = {int(t): c for t, c in Wd['coords'].items()}
for p in (2, 101):
    Rr = Wd['inner_dim']
    U = {PORTS[t]: [[int(i == c) for i in range(Rr)] for c in cs] for t, cs in coords.items()}
    Ed = {PORTS[t]: tuple(PORTS[c] for c in K0idx if dot(PORTS[t], PORTS[c])) for t in Wd['others']}
    idx = {PORTS[c]: coords[c] for c in K0idx}
    chain('14-port representation', U, U, idx, Ed, 2, p, Rr)

# ---- clique-cover representations of the graphs G_n (n points, all pairs; point ~ pair iff contained, pairs ~ iff disjoint)
def gn(n, p):
    Pt = [('p', i) for i in range(n)]; Pr = [('e', a, b) for a, b in itertools.combinations(range(n), 2)]
    pairs = list(itertools.combinations(range(n), 2))
    def matchings(pp, used=frozenset()):
        out = []
        for q in pp:
            if not set(q) & used:
                rest = [z for z in pp if z > q]
                out.append([q]); out += [[q] + m for m in matchings(rest, used | set(q))]
        return out
    M2 = [m for m in matchings(pairs) if len(m) == n // 2]
    cov = {e: 2 + sum(e[1:] in m for m in M2) for e in Pr}; k = max(cov.values())
    co = {v: [] for v in Pt + Pr}; r = 0; Kc = {}
    for i in range(n):
        for _ in range(k): co[('p', i)].append(r); r += 1
        Kc[('p', i)] = co[('p', i)][:]
    assert n - 1 <= k
    for e in Pr:
        a, b = e[1:]
        co[e] += [Kc[('p', a)][b - (b > a)], Kc[('p', b)][a - (a > b)]]
    for m in M2:
        for q in m: co[('e',) + q].append(r)
        r += 1
    U = {v: [[int(i == c) for i in range(r)] for c in cs] for v, cs in co.items()}
    Ed = {e: (('p', e[1]), ('p', e[2])) for e in Pr}
    assert {len(c) for c in co.values()} == {k}
    return chain('G_%d clique cover' % n, U, U, Kc, Ed, k, p, r)
for n, p in ((4, 2), (4, 101), (6, 2)):
    gn(n, p)

# ---- planted failure: two edge ports at one vertex that also share a coordinate must trip the premise ---------
try:
    Uf = {PORTS[t]: [[int(i == c) for i in range(17)] for c in cs] for t, cs in coords.items()}
    rows62 = [[int(i == c) for i in range(17)] for c in coords[62]]
    Uf[PORTS[57]] = [r_[:] for r_ in rows62]
    Uf[PORTS[68]] = [r_[:] for r_ in rows62]
    Ed = {PORTS[57]: (PORTS[62], PORTS[91]), PORTS[68]: (PORTS[62], PORTS[99])}
    chain('planted', Uf, Uf, {PORTS[c]: coords[c] for c in K0idx}, Ed, 2, 2, 17)
    fail('control: planted shared coordinate was not caught')
except ValueError as e:
    ok('control: two edge ports of one star that share coordinates break the block-diagonal premise (%s)' % str(e)[:50])

# ---- tensor lift and column restriction (Theorem 5) ----------------------------------------------------------
def kron_eye(B, f):
    n = len(B)
    return [[B[i // f][j // f] if i % f == j % f else 0 for j in range(n * f)] for i in range(n * f)]
G = [[dot(a, b) for b in PORTS] for a in PORTS]
for f in (1, 2, 3, 4):
    req(rk(kron_eye(G, f), 2) == 9 * f, 'tensor lift: Gram of P104 tensor I_%d has rank %d = 9f, ratio 9' % (f, 9 * f))
def restr_trials(Om, kk, trials=200, J=False):
    n = len(Om); bad = 0
    for _ in range(trials):
        Rs = [(s, i) for s in range(n) for i in range(kk) if rnd.random() < 0.3]
        As = [(t, j) for t in range(n) for j in range(kk) if rnd.random() < 0.3]
        if not Rs or not As: continue
        Mk = [[Om[s][t] * (1 if J else int(i == j)) for (t, j) in As] for (s, i) in Rs]
        lhs = rk(Mk, 2)
        rhs = 0
        for i in range(kk):
            Ri = [s for (s, ii) in Rs if ii == i]; Ai = [t for (t, jj) in As if jj == i]
            rhs += rk([[Om[s][t] for t in Ai] for s in Ri], 2) if Ri and Ai else 0
        bad += lhs != rhs
    return bad
req(restr_trials(G, 3) == 0, 'column restriction: rank of (Gram tensor I_3)[R, A] equals the sum over copies of rank Gram[R_i, A_i], on 200 random supports')
req(restr_trials(G, 3, J=True) > 0, 'control: for Gram tensor J_3 (not a tensor with I) the identity fails on random supports')
finish('PASS_STAR_BOUND')
