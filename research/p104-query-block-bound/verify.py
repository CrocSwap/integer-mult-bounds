#!/usr/bin/env python3
"""Exact checks for the query-block bound (no new kappa).  Python 3.12, standard library only.

Run:  python3 -I -B research/p104-query-block-bound/verify.py
Expected marker: PASS_QUERY_BLOCK_BOUND

All arithmetic is exact (Fraction, Gaussian rationals, integers).  Failures raise ValueError, so the checks stay
active under -O.  Sections:
  0  retained input bytes against retained/SOURCE-PINS.json
  1  Theorem 1 (rank Xi = N - r) on explicit involutions, with controls
  2  the 24 uniform Clifford cosets: subgroup, bimodule property, independence of the powers g^(x)f
  3  Theorem 2 / Lemma 3 in a noncommutative model (Q[S4], B = Q[D4]): expansion, rank identity, window bound
  4  the literal #6726 header at body variables = 1: N = 33, r = 32, N - r = 1, replicated copies, controls
"""
import hashlib
import itertools
import json
import random
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = {}


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def expect_error(fn, tag):
    try:
        fn()
    except ValueError:
        return tag
    raise ValueError('control accepted: ' + tag)


# ------------------------------------------------------------------ Gaussian rationals and matrices
class Z:
    """Element of Q(i)."""
    __slots__ = ('a', 'b')

    def __init__(s, a=0, b=0):
        s.a = a if isinstance(a, Fr) else Fr(a)
        s.b = b if isinstance(b, Fr) else Fr(b)

    @staticmethod
    def c(x):
        return x if isinstance(x, Z) else Z(x)

    def __add__(s, o):
        o = Z.c(o)
        return Z(s.a + o.a, s.b + o.b)
    __radd__ = __add__

    def __sub__(s, o):
        o = Z.c(o)
        return Z(s.a - o.a, s.b - o.b)

    def __rsub__(s, o):
        return Z.c(o) - s

    def __neg__(s):
        return Z(-s.a, -s.b)

    def __mul__(s, o):
        o = Z.c(o)
        return Z(s.a * o.a - s.b * o.b, s.a * o.b + s.b * o.a)
    __rmul__ = __mul__

    def inv(s):
        n = s.a * s.a + s.b * s.b
        need(n != 0, 'inverse of zero')
        return Z(s.a / n, -s.b / n)

    def __truediv__(s, o):
        return s * Z.c(o).inv()

    def __eq__(s, o):
        o = Z.c(o)
        return s.a == o.a and s.b == o.b

    def __ne__(s, o):
        return not s == o

    def __bool__(s):
        return s.a != 0 or s.b != 0

    def __hash__(s):
        return hash((s.a, s.b))

    def key(s):
        return (s.a, s.b)


I_ = Z(0, 1)


def mm(A, B):
    Bt = list(zip(*B))
    return [[sum((x * y for x, y in zip(r, c)), Z(0)) for c in Bt] for r in A]


def eye(n):
    return [[Z(int(i == j)) for j in range(n)] for i in range(n)]


def madd(A, B, s=1):
    return [[x + s * y for x, y in zip(r, t)] for r, t in zip(A, B)]


def rank(M):
    M = [[Z.c(x) for x in r] for r in M]
    rk = 0
    if not M:
        return 0
    for c in range(len(M[0])):
        p = next((i for i in range(rk, len(M)) if M[i][c]), None)
        if p is None:
            continue
        M[rk], M[p] = M[p], M[rk]
        inv = M[rk][c].inv()
        for i in range(rk + 1, len(M)):
            if M[i][c]:
                q = M[i][c] * inv
                M[i] = [a - q * b for a, b in zip(M[i], M[rk])]
        rk += 1
    return rk


def qmat(rows):
    return [[Z(x) for x in r] for r in rows]


# ------------------------------------------------------------------------------------------ 0 pins
def check_pins():
    pins = json.loads((HERE / 'retained/SOURCE-PINS.json').read_text())
    for p in pins:
        data = (HERE / p['local']).read_bytes()
        need(len(data) == p['bytes'], ('size', p['local']))
        need(hashlib.sha256(data).hexdigest() == p['sha256'], ('sha256', p['local']))
        need(hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == p['git_blob'], ('git blob', p['local']))
    OUT['retained_inputs'] = len(pins)


# --------------------------------------------------------------------- 1  Theorem 1: rank Xi = N - r
def word_product(xs, ys):
    """J = (I - x_N y_N^T) ... (I - x_1 y_1^T)."""
    n = len(xs[0])
    J = eye(n)
    for x, y in zip(xs, ys):
        T = [[Z(int(a == b)) - x[a] * y[b] for b in range(n)] for a in range(n)]
        J = mm(T, J)
    return J


def xi_data(xs, ys):
    N = len(xs)
    n = len(xs[0])
    J = word_product(xs, ys)
    invol = mm(J, J) == eye(n)
    r = rank(madd(J, eye(n), -1))
    G = [[sum((a * b for a, b in zip(ys[i], xs[j])), Z(0)) for j in range(N)] for i in range(N)]
    K = [[Z(int(i == j)) + (G[i][j] if i > j else 0) for j in range(N)] for i in range(N)]
    Xi = [[2 * K[i][j] - G[i][j] for j in range(N)] for i in range(N)]
    return N, n, invol, r, rank(Xi), G


def theorem1_instance(xs, ys, label):
    N, n, invol, r, rx, G = xi_data(xs, ys)
    need(invol, ('not an involution', label))
    need(rx == N - r, ('Theorem 1 fails', label, N, r, rx))
    return N, r


def relative_word(us, vs):
    """Units of M(-1) M(1)^-1 for M(S) = T_N(S)...T_1(S), T_i(S) = I + S u_i v_i^T (Lemma 1.1).
    Returns (x, y) lists with rel = (I - x_N y_N^T)...(I - x_1 y_1^T), first applied = index N of the input."""
    n, N = len(us[0]), len(us)
    A = eye(n)
    Ai = eye(n)
    res = []
    for i in range(N - 1, -1, -1):
        u, v = us[i], vs[i]
        tau = sum((a * b for a, b in zip(u, v)), Z(0))
        x = [sum((A[a][b] * u[b] for b in range(n)), Z(0)) * 2 / (1 + tau) for a in range(n)]
        y = [sum((v[a] * Ai[a][b] for a in range(n)), Z(0)) for b in range(n)]
        res.append((x, y))
        T = [[Z(int(a == b)) - u[a] * v[b] for b in range(n)] for a in range(n)]
        Tin = [[Z(int(a == b)) + u[a] * v[b] / (1 - tau) for b in range(n)] for a in range(n)]
        A = mm(A, T)
        Ai = mm(Tin, Ai)
    return [a for a, b in res], [b for a, b in res]


def M_of(us, vs, S):
    n = len(us[0])
    M = eye(n)
    for u, v in zip(us, vs):
        T = [[Z(int(a == b)) + S * u[a] * v[b] for b in range(n)] for a in range(n)]
        M = mm(T, M)
    return M


def inverse(A):
    n = len(A)
    R = [list(r) + e for r, e in zip(A, eye(n))]
    for j in range(n):
        k = next((k for k in range(j, n) if R[k][j]), None)
        need(k is not None, 'singular')
        R[j], R[k] = R[k], R[j]
        v = R[j][j].inv()
        R[j] = [x * v for x in R[j]]
        for k in range(n):
            if k != j and R[k][j]:
                w = R[k][j]
                R[k] = [x - w * y for x, y in zip(R[k], R[j])]
    return [r[n:] for r in R]


def vec(*c):
    return [Z(x) for x in c]


def section1():
    res = {}
    # Whitehead word: three unipotent queries on two fields; at S = +-1 the word is +-[[0,1],[-1,0]].
    us = [vec(1, 0), vec(0, 1), vec(1, 0)]
    vs = [vec(0, 1), vec(-1, 0), vec(0, 1)]
    M1, Mm1 = M_of(us, vs, Z(1)), M_of(us, vs, Z(-1))
    need(Mm1 == [[-x for x in r] for r in M1], 'Whitehead word is odd in S')
    xs, ys = relative_word(us, vs)
    rel = mm(Mm1, inverse(M1))
    need(word_product(xs, ys) == rel, 'Lemma 1.1: telescoped relative word')
    N, r = theorem1_instance(xs, ys, 'whitehead')
    need((N, r) == (3, 2), 'Whitehead N, r')
    res['whitehead'] = [N, r]
    # the #6726 eight-field root: nine nilpotent queries with product -I (retained ROOT.json)
    R = json.loads((HERE / 'retained/pr6726/ROOT.json').read_text())
    need(R['fields'] == 8 and len(R['queries']) == 9, 'root shape')
    xs, ys = [], []
    for q in R['queries']:
        q = qmat([[Fr(c) for c in row] for row in q])
        p = next((i, j) for i in range(8) for j in range(8) if q[i][j])
        piv = q[p[0]][p[1]]
        need(rank(q) == 1 and mm(q, q) == [[Z(0)] * 8 for _ in range(8)], 'rank-one nilpotent query')
        xs.append([2 * q[i][p[1]] for i in range(8)])              # I - 2R = I - x y^T, R = col * row / piv
        ys.append([q[p[0]][j] / piv for j in range(8)])
    N, r = theorem1_instance(xs, ys, 'root8')
    need((N, r) == (9, 8), 'root N, r')
    J = word_product(xs, ys)
    need(J == [[Z(-int(i == j)) for j in range(8)] for i in range(8)], 'root product is -I')
    res['root8'] = [N, r]
    # conjugated, padded, summed and reflected variants (exact)
    rng = random.Random(6726)

    def rand_inv(n):
        while True:
            P = [[Z(rng.randint(-2, 2)) for _ in range(n)] for _ in range(n)]
            if rank(P) == n:
                return P
    n = 2
    P = rand_inv(n)
    Pi = inverse(P)
    cx = [[sum((P[a][b] * x[b] for b in range(n)), Z(0)) for a in range(n)] for x in relative_word(us, vs)[0]]
    cy = [[sum((y[a] * Pi[a][b] for a in range(n)), Z(0)) for b in range(n)] for y in relative_word(us, vs)[1]]
    res['conjugated'] = list(theorem1_instance(cx, cy, 'conjugated'))
    # insert a cancelling pair T, T^-1 (any tau != 1): N + 2, r unchanged
    x0, y0 = vec(3, 1), vec(1, 1)                                 # tau = 4
    tau = sum((a * b for a, b in zip(x0, y0)), Z(0))
    need(tau != 1, 'unit invertible')
    xw, yw = relative_word(us, vs)
    c = Z(1) / (1 - tau)
    inv_x = [c * a for a in x0]
    # (I - x y)^-1 = I + c x y with c = 1/(1 - tau) = I - (-c x) y
    xs2 = xw[:1] + [x0, [-t for t in inv_x]] + xw[1:]
    ys2 = yw[:1] + [y0, y0] + yw[1:]
    # first applied is index 0: word = ... T_inv T x_0-term ...; the pair is adjacent so J is unchanged
    need(word_product(xs2, ys2) == word_product(xw, yw), 'cancelling pair leaves J unchanged')
    res['padded_pair'] = list(theorem1_instance(xs2, ys2, 'padded'))
    need(res['padded_pair'] == [5, 2], 'padded N, r')
    # direct sum of two Whitehead words
    xa, ya = relative_word(us, vs)
    z2 = [Z(0)] * 2
    xs3 = [x + z2 for x in xa] + [z2 + x for x in xa]
    ys3 = [y + z2 for y in ya] + [z2 + y for y in ya]
    res['direct_sum'] = list(theorem1_instance(xs3, ys3, 'direct sum'))
    need(res['direct_sum'] == [6, 4], 'direct sum N, r')
    # a single reflection (tau = 2): N = r = 1 and Xi = 0
    res['reflection'] = list(theorem1_instance([vec(1, 0)], [vec(2, 0)], 'reflection'))
    need(res['reflection'] == [1, 1], 'reflection N, r')
    # window form: pairwise orthogonal units with tau != 2 inside a word whose pairings are those of J
    # (root8: Gamma has no two orthogonal units except far apart pairs; the check is the bound itself)
    # controls
    def c_noninvol():
        N_, n_, inv_, r_, rx_, G_ = xi_data([vec(1, 0)], [vec(0, 1)])    # a shear: J^2 != I
        need(inv_, 'not an involution')
    res['control_not_involution'] = expect_error(c_noninvol, 'shear is not an involution')
    N_, n_, inv_, r_, rx_, G_ = xi_data([vec(1, 0)], [vec(0, 1)])
    need(rx_ != N_ - r_, 'for a non-involution the rank identity genuinely fails')
    res['control_not_involution_values'] = [N_, r_, rx_]
    OUT['theorem1'] = res


# ------------------------------------------------------------------- 2  the 24 uniform Clifford cosets
def g2(a, b, c, d):
    return [[a, b], [c, d]]


def norm2(m):
    k = next(x for x in (m[0][0], m[0][1], m[1][0], m[1][1]) if x)
    inv = k.inv()
    return tuple(tuple(x * inv for x in r) for r in m)


def key2(m):
    return tuple(tuple(x.key() for x in r) for r in m)


def mono2(m):
    return all(sum(1 for x in r if x) == 1 for r in m) and all(sum(1 for r in m if r[j]) == 1 for j in range(2))


def section2():
    res = {}
    h = Z(Fr(1, 2), Fr(1, 2))
    C = [[h, h * (-I_)], [h * (-I_), h]]
    S = [[Z(1), Z(0)], [Z(0), I_]]
    Xg = [[Z(0), Z(1)], [Z(1), Z(0)]]
    Zg = [[Z(1), Z(0)], [Z(0), Z(-1)]]
    need(mm(C, C) == Xg, 'C^2 = X (Q^2 is an ordinary monomial)')
    els = [eye(2)]
    seen = {key2(norm2(eye(2)))}
    i = 0
    while i < len(els):
        for g in (C, S, Xg, Zg):
            m = mm(g, els[i])
            k = key2(norm2(m))
            if k not in seen:
                seen.add(k)
                els.append(m)
        i += 1
    need(len(els) == 24, 'single-qubit Clifford group modulo scalars has 24 cosets')
    H = [m for m in els if mono2(m)]
    need(len(H) == 8, 'eight monomial cosets')
    Hk = {key2(norm2(m)) for m in H}
    for a in H:
        for b in H:
            need(key2(norm2(mm(a, b))) in Hk, 'monomial cosets are closed')
    Qk = key2(norm2(C))
    need(Qk not in Hk, 'Q is not monomial')
    out = [m for m in els if key2(norm2(m)) not in Hk]
    cnt = 0
    for a in H:
        for g in out:
            ag = mm(a, g)
            for b in H:
                need(key2(norm2(mm(ag, b))) not in Hk, 'B Q B misses B')
                cnt += 1
    res['bimodule_products_checked'] = cnt
    res['cosets'], res['monomial'] = len(els), len(H)
    # independence of the 24 matrices g^(x)f : evaluate all degree-f monomials in the four entries
    reps = [norm2(m) for m in els]
    ranks = {}
    for f in range(1, 8):
        exps = [(i, j, k, f - i - j - k) for i in range(f + 1) for j in range(f + 1 - i) for k in range(f + 1 - i - j)]
        rows = []
        for g in reps:
            ent = [g[0][0], g[0][1], g[1][0], g[1][1]]
            pw = [[Z(1)] for _ in ent]
            for t in range(4):
                for _ in range(f):
                    pw[t].append(pw[t][-1] * ent[t])
            rows.append([pw[0][e[0]] * pw[1][e[1]] * pw[2][e[2]] * pw[3][e[3]] for e in exps])
        ranks[f] = rank(rows)
    res['rank_of_24_powers_by_f'] = ranks
    need(all(ranks[f] == 24 for f in (5, 6, 7)), 'the 24 powers are independent for f = 5, 6, 7')
    need(ranks[4] < 24, 'control: dependent at f = 4')
    OUT['uniform_cosets'] = res


# --------------------------------------------- 3  noncommutative model: Q[S4] with B = Q[D4], Q a 3-cycle
def pmul(p, q):
    return tuple(p[q[x]] for x in range(4))


def pinv(p):
    r = [0] * 4
    for i, x in enumerate(p):
        r[x] = i
    return tuple(r)


ID4 = (0, 1, 2, 3)
GEN = [(1, 2, 3, 0), (2, 1, 0, 3)]


def closure(gens):
    G = {ID4}
    fr = [ID4]
    while fr:
        nf = []
        for a in fr:
            for g in gens:
                b = pmul(g, a)
                if b not in G:
                    G.add(b)
                    nf.append(b)
        fr = nf
    return G


D4 = sorted(closure(GEN))
S4 = sorted(closure([(1, 2, 3, 0), (1, 0, 2, 3)]))
QP = (1, 2, 0, 3)                                         # a 3-cycle
NONH = [g for g in S4 if g not in set(D4)]


def amul(a, b):
    r = {}
    for p, x in a.items():
        for q, y in b.items():
            k = pmul(p, q)
            r[k] = r.get(k, 0) + x * y
    return {k: v for k, v in r.items() if v != 0}


def aadd(a, b, s=1):
    r = dict(a)
    for k, v in b.items():
        r[k] = r.get(k, 0) + s * v
    return {k: v for k, v in r.items() if v != 0}


def Eproj(a):
    return {k: v for k, v in a.items() if k in set(D4)}


def mat_amul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    R = [[{} for _ in range(p)] for _ in range(n)]
    for i in range(n):
        for k in range(m):
            if not A[i][k]:
                continue
            for j in range(p):
                if B[k][j]:
                    R[i][j] = aadd(R[i][j], amul(A[i][k], B[k][j]))
    return R


def mat_aadd(A, B):
    return [[aadd(x, y) for x, y in zip(r, t)] for r, t in zip(A, B)]


def aeye(n):
    return [[{ID4: Fr(1)} if i == j else {} for j in range(n)] for i in range(n)]


def rho(a):
    """Left regular representation of an element of B = Q[D4] on the basis D4 (d = 8)."""
    idx = {g: i for i, g in enumerate(D4)}
    R = [[Z(0)] * 8 for _ in range(8)]
    for p, x in a.items():
        need(p in idx, 'element of B expected')
        for h in D4:
            R[idx[pmul(p, h)]][idx[h]] = R[idx[pmul(p, h)]][idx[h]] + Z(x)
    return R


def rho_mat(A):
    n, m = len(A), len(A[0])
    out = [[Z(0)] * (8 * m) for _ in range(8 * n)]
    for i in range(n):
        for j in range(m):
            blk = rho(A[i][j])
            for a in range(8):
                for b in range(8):
                    out[8 * i + a][8 * j + b] = blk[a][b]
    return out


def rand_b(rng):
    a = {}
    for _ in range(rng.randint(0, 3)):
        g = rng.choice(D4)
        a[g] = a.get(g, 0) + Fr(rng.randint(-2, 2))
    return {k: v for k, v in a.items() if v != 0}


def rand_any(rng):
    a = rand_b(rng)
    g = rng.choice(NONH)
    a[g] = a.get(g, 0) + Fr(rng.randint(1, 2))
    return {k: v for k, v in a.items() if v != 0}


def build_word(rng, n, N, outside=False, Qel=None):
    Qel = Qel or {QP: Fr(1)}
    gen = rand_any if outside else rand_b
    U = [[gen(rng) for _ in range(n)] for _ in range(N)]                 # u_i column entries
    V = [[gen(rng) for _ in range(n)] for _ in range(N)]                 # v_i row entries
    return U, V, Qel


def word_data(U, V, Qel, n, N):
    # M = T_N ... T_1, T_i = I + u_i Q v_i
    M = aeye(n)
    for i in range(N):
        T = [[aadd({ID4: Fr(int(a == b))} if a == b else {}, amul(amul(U[i][a], Qel), V[i][b])) for b in range(n)]
             for a in range(n)]
        M = mat_amul(T, M)
    G = [[{} for _ in range(N)] for _ in range(N)]
    for i in range(N):
        for j in range(N):
            g = {}
            for k in range(n):
                g = aadd(g, amul(V[i][k], U[j][k]))
            G[i][j] = g
    Gl = [[G[i][j] if i > j else {} for j in range(N)] for i in range(N)]
    QG = [[amul(Qel, Gl[i][j]) if Gl[i][j] else {} for j in range(N)] for i in range(N)]
    term = [[Qel if i == j else {} for j in range(N)] for i in range(N)]
    W = [r[:] for r in term]
    for _ in range(N):
        term = mat_amul(QG, term)
        if not any(x for r in term for x in r):
            break
        W = mat_aadd(W, term)
    return M, G, W


def section3():
    res = {}
    need(len(D4) == 8 and len(S4) == 24 and QP not in set(D4), 'model groups')
    for h in D4:
        for g in NONH:
            for k in D4:
                need(pmul(pmul(h, g), k) not in set(D4), 'D4 g D4 misses D4')
    rng = random.Random(24)
    trials = 0
    for (n, N) in [(2, 3), (2, 4), (3, 4), (3, 5), (2, 5)]:
        for _ in range(6):
            U, V, Qel = build_word(rng, n, N)
            M, G, W = word_data(U, V, Qel, n, N)
            # M = I + U W V (the expansion; W_ii = Q, W_ij = 0 for i < j)
            UWV = [[{} for _ in range(n)] for _ in range(n)]
            for a in range(n):
                for b in range(n):
                    s = {}
                    for i in range(N):
                        for j in range(N):
                            if W[i][j]:
                                s = aadd(s, amul(amul(U[i][a], W[i][j]), V[j][b]))
                    UWV[a][b] = s
            need(M == mat_aadd(aeye(n), UWV), 'expansion M = I + U W V')
            need(all(not W[i][j] for i in range(N) for j in range(N) if i < j), 'W lower triangular')
            need(all(W[i][i] == Qel for i in range(N)), 'W_ii = Q')
            F = [[Eproj(x) for x in r] for r in W]
            need(all(not F[i][j] for i in range(N) for j in range(N) if i <= j), 'F = E(W) strictly lower')
            EM = [[Eproj(x) for x in r] for r in M]
            UFV = [[{} for _ in range(n)] for _ in range(n)]
            for a in range(n):
                for b in range(n):
                    s = {}
                    for i in range(N):
                        for j in range(N):
                            if F[i][j]:
                                s = aadd(s, amul(amul(U[i][a], F[i][j]), V[j][b]))
                    UFV[a][b] = s
            need(EM == mat_aadd(aeye(n), UFV), 'E(M) = I + U F V exactly')
            H = mat_aadd(aeye(N), mat_amul(F, G))
            rM = rank(rho_mat(EM))
            rH = rank(rho_mat(H))
            need(rH - 8 * N == rM - 8 * n, 'Sylvester: rank(I+FG) - N d = rank E(M) - n d')
            trials += 1
    res['random_words_checked'] = trials
    # control: ordinary entries outside B break E(UWV) = U E(W) V
    bad = 0
    for s in range(12):
        rng2 = random.Random(100 + s)
        U, V, Qel = build_word(rng2, 2, 3, outside=True)
        M, G, W = word_data(U, V, Qel, 2, 3)
        F = [[Eproj(x) for x in r] for r in W]
        EM = [[Eproj(x) for x in r] for r in M]
        UFV = [[{} for _ in range(2)] for _ in range(2)]
        for a in range(2):
            for b in range(2):
                t = {}
                for i in range(3):
                    for j in range(3):
                        if F[i][j]:
                            t = aadd(t, amul(amul(U[i][a], F[i][j]), V[j][b]))
                UFV[a][b] = t
        if EM != mat_aadd(aeye(2), UFV):
            bad += 1
    need(bad > 0, 'control: controls outside B must break the exact identity')
    res['control_controls_outside_B_failing_of_12'] = bad
    # control: Q inside B (E(Q) != 0) is not covered: E(Q) = Q
    need(Eproj({ID4: Fr(1)}) != {} and Eproj({QP: Fr(1)}) == {}, 'E(1) = 1, E(Q) = 0')
    OUT['model_S4'] = res


def window_lemma_scan():
    """Lemma 3 on random strictly lower F and G with G_AA = 0 over Q (d = 1): rank(I+FG) >= w."""
    res = {'cases': 0, 'min_rank_minus_w': 99}
    rng = random.Random(104)
    for _ in range(6000):
        N = rng.randint(2, 6)
        w = rng.randint(1, N)
        k = rng.randint(0, N - w)
        A = set(range(k, k + w))
        dens = rng.choice([0.2, 0.4, 0.7])
        F = [[Z(rng.choice([-1, 1, 2])) if (i > j and rng.random() < dens) else Z(0) for j in range(N)] for i in range(N)]
        G = [[Z(rng.choice([-1, 1, 2])) if (rng.random() < dens and not (i in A and j in A)) else Z(0)
              for j in range(N)] for i in range(N)]
        H = madd(eye(N), mm(F, G))
        rk = rank(H)
        need(rk >= w, ('window lemma violated', N, w, k))
        res['cases'] += 1
        res['min_rank_minus_w'] = min(res['min_rank_minus_w'], rk - w)
    need(res['min_rank_minus_w'] == 0, 'the bound is attained in the scan')
    OUT['window_scan'] = res


def whitehead_control():
    """Whitehead word in A = Q[q]/(q^2-1), B = Q, E = even part: N = 3, r = 2, N - r = 1, and
    the only pair of commuting square-zero units is not consecutive."""
    us = [vec(1, 0), vec(0, 1), vec(1, 0)]
    vs = [vec(0, 1), vec(-1, 0), vec(0, 1)]
    N = 3
    G = [[sum((vs[i][k] * us[j][k] for k in range(2)), Z(0)) for j in range(N)] for i in range(N)]
    Gl = [[G[i][j] if i > j else Z(0) for j in range(N)] for i in range(N)]
    # Q = q, Q^2 = 1: F = E(W) = sum over odd k of G_<^k
    G2 = mm(Gl, Gl)
    G3 = mm(G2, Gl)
    need(all(not x for r in G3 for x in r), 'G_<^3 = 0')
    F = Gl
    H = madd(eye(N), mm(F, G))
    need(rank(H) == N - 2, 'rank(I+FG) = N - r = 1 for the Whitehead word')
    # the target q [[0,1],[-1,0]]: M(q) = [[1-q^2, 2q-q^3], [-q, 1-q^2]] with q^2 = 1
    windows = []
    for w in (2, 3):
        for k in range(0, N - w + 1):
            A = range(k, k + w)
            zero = all(not G[i][j] for i in A for j in A)
            windows.append((w, k, zero))
    need(not any(z for (w, k, z) in windows), 'no consecutive window of width >= 2 has G_AA = 0')
    need(not G[0][0] and not G[2][2] and not G[0][2] and not G[2][0], 'units 1 and 3 are orthogonal but not consecutive')
    OUT['whitehead_control'] = {'N': 3, 'r': 2, 'rank_I_plus_FG': 1, 'orthogonal_pair_not_consecutive': [1, 3]}


# --------------------------------------------------------- 4  the literal #6726 header at D = 1
def replay_header(events, n, q, diag):
    """Left-multiplication replay at body variables = 1 for the character q (a 4th root of unity)."""
    S = eye(n)
    q2 = q * q
    qinv = q.inv()
    for e in events:
        op = e[0]
        if op == 'ADD':
            _, dst, src, c = e
            c = Fr(c)
            S[dst] = [a + c * b for a, b in zip(S[dst], S[src])]
        elif op == 'SCALE':
            _, dst, c = e
            c = Fr(c)
            S[dst] = [c * a for a in S[dst]]
        elif op == 'SWAP':
            _, a, b = e
            S[a], S[b] = S[b], S[a]
        elif op in ('QUERY', 'LOCAL'):
            if op == 'LOCAL':
                _, _, src, dst = e
                ex = -1
            else:
                _, dst, src, ex = e
            need(ex == -1, 'query exponent')
            S[dst] = [a + qinv * b for a, b in zip(S[dst], S[src])]
        elif op == 'LAMBDA':
            _, r, sign = e
            lam0 = Z(Fr(1, 2), Fr(sign, 2))
            lam1 = Z(Fr(1, 2), Fr(-sign, 2))
            old = S[r]
            S[r] = [lam0 * a + lam1 * q2 * a for a in old]
        elif op in ('IDLE', 'IDLE_ONE'):
            pass                      # only shifts the body exponents, trivial at body variables = 1
        else:
            raise ValueError('unknown event ' + op)
    return S


def unit_structure(events, n, p):
    """Sector q^2 = p (p = +-1): the N unit events as (dst, src) and the conjugated ordinary vectors."""
    Pm = eye(n)
    Pinv = eye(n)
    units = []
    U, V = [], []
    for e in events:
        op = e[0]
        if op == 'ADD':
            _, dst, src, c = e
            c = Fr(c)
            Pm[dst] = [a + c * b for a, b in zip(Pm[dst], Pm[src])]
            for row in Pinv:
                row[src] = row[src] - c * row[dst]
        elif op == 'SCALE':
            _, dst, c = e
            c = Fr(c)
            Pm[dst] = [c * a for a in Pm[dst]]
            for row in Pinv:
                row[dst] = row[dst] / c
        elif op == 'SWAP':
            _, a, b = e
            Pm[a], Pm[b] = Pm[b], Pm[a]
            for row in Pinv:
                row[a], row[b] = row[b], row[a]
        elif op == 'LAMBDA':
            _, r, sign = e
            lam = Z(Fr(1, 2), Fr(sign, 2)) + Z(Fr(1, 2), Fr(-sign, 2)) * p
            need(lam, 'lambda is a unit')
            Pm[r] = [lam * a for a in Pm[r]]
            for row in Pinv:
                row[r] = row[r] / lam
        elif op in ('QUERY', 'LOCAL'):
            if op == 'LOCAL':
                _, _, src, dst = e
            else:
                _, dst, src, _ = e
            units.append((dst, src))
            U.append([Pinv[a][dst] for a in range(n)])          # u~ = P^-1 e_dst
            V.append(list(Pm[src]))                              # v~ = e_src^T P
        elif op in ('IDLE', 'IDLE_ONE'):
            pass
    return units, U, V, Pm


def header_sector(events, n, diag, p):
    units, U, V, O = unit_structure(events, n, p)
    N = len(units)
    G = [[sum((V[i][k] * U[j][k] for k in range(n)), Z(0)) for j in range(N)] for i in range(N)]
    need(all(not G[i][i] for i in range(N)), 'every query is square-zero: v_i u_i = 0')
    Gl = [[G[i][j] if i > j else Z(0) for j in range(N)] for i in range(N)]
    G2 = mm(Gl, Gl)
    # F = E(W) = sum_{m>=1} p^m G_<^(2m-1) = p G_< (I - p G_<^2)^-1 (Q^2 = q^-2 = p)
    X = eye(N)
    term = eye(N)
    for _ in range(N):
        term = [[p * x for x in r] for r in mm(term, G2)]
        if not any(x for r in term for x in r):
            break
        X = madd(X, term)
    F = [[p * x for x in r] for r in mm(Gl, X)]
    need(all(not F[i][j] for i in range(N) for j in range(N) if i <= j), 'F strictly lower')
    Um = [[U[i][a] for i in range(N)] for a in range(n)]                     # n x N
    Vm = [V[i][:] for i in range(N)]                                         # N x n
    EM_units = madd(eye(n), mm(Um, mm(F, Vm)))
    EM = mm(O, EM_units)
    # independent evaluation: E(M) = (M(q0) + M(-q0)) / 2 from full replays
    q0 = Z(1) if p == 1 else I_
    Mp, Mn = replay_header(events, n, q0, diag), replay_header(events, n, -q0, diag)
    for i in range(n):
        d = diag[i][0] % 4
        need(Mp[i] == [(pw(q0, d) if j == i else Z(0)) for j in range(n)], 'replay is diag(q^d) at q0')
        need(Mn[i] == [(pw(-q0, d) if j == i else Z(0)) for j in range(n)], 'replay is diag(q^d) at -q0')
    Eref = [[(Mp[i][j] + Mn[i][j]) / 2 for j in range(n)] for i in range(n)]
    need(EM == Eref, 'E(M) = O (I + U F V) matches the replay')
    r = sum(1 for i in range(n) if diag[i][0] % 2)
    need(Eref == [[Z(int(i == j and diag[i][0] % 2 == 0)) for j in range(n)] for i in range(n)], 'E(M) = diag(0 on q-odd targets, 1 on identities)')
    H = madd(eye(N), mm(F, G))
    return N, r, rank(H), G, F


def pw(z, k):
    r = Z(1)
    for _ in range(k % 4):
        r = r * z
    return r


def section4():
    res = {}
    data = json.loads((HERE / 'retained/pr6726/CONTROLLER.json').read_text())
    events, n, diag = data['events'], data['roles'], data['diagonal']
    need(n == 34 and len(events) == 606, 'caller shape')
    census = {}
    for e in events:
        census[e[0]] = census.get(e[0], 0) + 1
    need(census.get('LOCAL') == 18 and census.get('QUERY') == 15, 'caller census: 18 LOCAL + 15 QUERY')
    res['census'] = census
    sec = {}
    for p in (1, -1):
        N, r, rk, G, F = header_sector(events, n, diag, p)
        need((N, r) == (33, 32), 'N = 33 header queries, r = 32 q-odd targets')
        need(rk == N - r == 1, 'rank(I+FG) = N - r = 1')
        sec['p=%d' % p] = {'N': N, 'r': r, 'rank_I_plus_FG': rk, 'N_minus_r': N - r}
        if p == 1:
            G1, F1, N1 = G, F, N
    res['sectors'] = sec
    # w independent copies: pairings across copies are zero.  Window = the k-th unit of every copy.
    w = 3
    Nw = w * N1
    Gw = [[Z(0)] * Nw for _ in range(Nw)]
    Fw = [[Z(0)] * Nw for _ in range(Nw)]
    for c in range(w):
        for i in range(N1):
            for j in range(N1):
                Gw[c * N1 + i][c * N1 + j] = G1[i][j]
                Fw[c * N1 + i][c * N1 + j] = F1[i][j]
    # reorder copy-major -> unit-major (copies commute, so the product is unchanged), window = w consecutive units
    perm = [c * N1 + i for i in range(N1) for c in range(w)]
    Gp = [[Gw[a][b] for b in perm] for a in perm]
    Fp = [[Fw[a][b] for b in perm] for a in perm]
    need(all(not Fp[i][j] for i in range(Nw) for j in range(Nw) if i <= j), 'reordered F still strictly lower')
    rw = w * 32
    Hw = madd(eye(Nw), mm(Fp, Gp))
    rk = rank(Hw)
    need(rk == Nw - rw == w, 'replicated copies: N - r = w')
    wins = 0
    for k in range(N1):
        A = range(k * w, k * w + w)
        if all(not Gp[i][j] for i in A for j in A):
            wins += 1
    need(wins == N1, 'every unit position gives a width-w window with zero pairing')
    res['replication'] = {'copies': w, 'N': Nw, 'r': rw, 'N_minus_r': Nw - rw, 'rank_I_plus_FG': rk,
                          'windows_with_zero_pairing': wins}
    # control: dropping one query event leaves the endpoint: the word no longer computes diag(q^d)
    def c_drop():
        idx = next(i for i, e in enumerate(events) if e[0] == 'QUERY')
        ev = events[:idx] + events[idx + 1:]
        S = replay_header(ev, n, Z(1), diag)
        need(all(S[i] == [(pw(Z(1), diag[i][0] % 4) if j == i else Z(0)) for j in range(n)] for i in range(n)), 'endpoint')
    res['control_drop_query'] = expect_error(c_drop, 'N = 32 header does not reach the endpoint')
    # control: a single-copy window of width 2 inside one copy is not orthogonal (consecutive header units pair)
    nz = sum(1 for i in range(N1 - 1) if G1[i][i + 1] or G1[i + 1][i])
    need(nz > 0, 'consecutive header units of one copy pair nontrivially')
    res['header_consecutive_pairs_nonzero'] = nz
    OUT['header'] = res


def main():
    check_pins()
    section1()
    section2()
    section3()
    window_lemma_scan()
    whitehead_control()
    section4()
    print(json.dumps(OUT, indent=1, sort_keys=True, default=str))
    print('PASS_QUERY_BLOCK_BOUND')


if __name__ == '__main__':
    main()
