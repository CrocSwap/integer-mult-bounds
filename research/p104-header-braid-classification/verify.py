#!/usr/bin/env python3
"""Exact checks for the saturated-header classification.  Python 3.12, standard library only.

Run:  python3 -I -B research/p104-header-braid-classification/verify.py
Expected marker: PASS_HEADER_BRAID_CLASSIFICATION

All checks are exact (int / Fraction).  Failures raise ValueError, so they stay active under -O.  Sections:
  0  pins of the retained input against retained/SOURCE-PINS.json
  1  sphere-braid relation on the chain of transvections (PROOF 2) and its negative controls
  2  saturated headers: product, sign Gram, rank-one identity, rigidity (PROOF 1, 3)
  3  path form: star -> path, tridiagonal Gram, converse, exhaustive n=2 search (PROOF 4)
  4  Hurwitz moves: legality in sector form, failure in path form, linear action of the Burau image (PROOF 5)
  5  orbit sizes mod 3, 4, 8 and the number of classes in a fixed frame (PROOF 6)
  6  arc law (PROOF 7)
  7  literal words between chain roots and the #6726 root; non-transitivity across frames (PROOF 8)
"""
import hashlib
import itertools
import json
import random
import sys
from fractions import Fraction as Q
from math import factorial
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import headerlib as H  # noqa: E402


def need(cond, msg):
    if not cond:
        raise ValueError(msg)


def expect_fail(fn, msg):
    """Negative control: fn() must return False."""
    need(not fn(), 'negative control passed but must fail: ' + msg)


# ----------------------------------------------------------------------------------------------------------------
def git_blob_id(b):
    return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()


def check_pins():
    pins = json.loads((HERE / 'retained' / 'SOURCE-PINS.json').read_text())
    need(len(pins) >= 1, 'no pins')
    for p in pins:
        b = (HERE / p['local']).read_bytes()
        need(len(b) == p['bytes'], 'size ' + p['local'])
        need(hashlib.sha256(b).hexdigest() == p['sha256'], 'sha256 ' + p['local'])
        need(git_blob_id(b) == p['git_blob'], 'git blob ' + p['local'])
    return len(pins)


# ---- 1. sphere relation on the chain of transvections ----------------------------------------------------------
def chain_matrices(N):
    """tau_i(v) = v + w(e_i, v) e_i on Z^N with w(e_i, e_{i+1}) = 1 = -w(e_{i+1}, e_i)."""
    def w(i, j):
        return (j == i + 1) - (j == i - 1)
    taus, tinv = [], []
    for i in range(N):
        t = [[int(a == j) + (a == i) * w(i, j) for j in range(N)] for a in range(N)]
        ti = [[int(a == j) - (a == i) * w(i, j) for j in range(N)] for a in range(N)]
        taus.append(t)
        tinv.append(ti)
    return taus, tinv


def imul(A, B):
    Bt = list(zip(*B))
    return [[sum(p * q for p, q in zip(r, c)) for c in Bt] for r in A]


def ieye(N):
    return [[int(i == j) for j in range(N)] for i in range(N)]


def word(mats, seq, N):
    P = ieye(N)
    for k in seq:           # left to right = leftmost factor first; palindromes are insensitive to direction
        P = imul(P, mats[k])
    return P


def check_sphere_relation():
    for N in range(1, 41):
        taus, tinv = chain_matrices(N)
        P = word(taus, list(range(N)) + list(range(N - 1, -1, -1)), N)
        rho = [sum((-1) ** k for k in range(i, N)) for i in range(N)]
        want = [[(-1 if a == b else 0) + 2 * rho[a] * (b == 0) for b in range(N)] for a in range(N)]
        need(P == want, 'P_N formula N=%d' % N)
        if N % 2 == 1:
            # rho = e_0 + e_2 + ... spans the radical of the form, and M(1) + M(-1) takes values in it
            need(rho == [int(i % 2 == 0) for i in range(N)], 'rho = sum of even e_i')
            w = lambda i, j: (j == i + 1) - (j == i - 1)  # noqa: E731
            need(all(sum(rho[i] * w(i, j) for i in range(N)) == 0 for j in range(N)), 'rho radical')
            M1 = word(taus, list(range(N - 1, -1, -1)), N)        # t_{N-1} ... t_0 (t_0 acts first)
            Mm = word(tinv, list(range(N - 1, -1, -1)), N)
            S = [[M1[a][b] + Mm[a][b] for b in range(N)] for a in range(N)]
            for b in range(N):
                col = [S[a][b] for a in range(N)]
                c = col[0]
                need(col == [c * r for r in rho], 'M(1)+M(-1) not in the radical, N=%d' % N)
        else:
            if N >= 2:
                expect_fail(lambda: P == [[-int(a == b) for b in range(N)] for a in range(N)], 'N even: P != -I')
    # negative controls: tampered words are not -I modulo the radical (N = 5)
    N = 5
    taus, tinv = chain_matrices(N)
    rad = [1, 0, 1, 0, 1]
    def minus_I_mod_rad(P):
        for b in range(N):
            col = [P[a][b] + (a == b) for a in range(N)]
            c = col[0]
            if col != [c * r for r in rad]:
                return False
        return True
    good = word(taus, list(range(N)) + list(range(N - 1, -1, -1)), N)
    need(minus_I_mod_rad(good), 'control base')
    expect_fail(lambda: minus_I_mod_rad(word(taus, list(range(N)) + list(range(N - 2, -1, -1)), N)), 'one letter missing')
    expect_fail(lambda: minus_I_mod_rad(word(taus, [0, 1, 2, 3, 4, 3, 4, 3, 2, 1, 0], N)), 'altered middle')
    mixed = [taus[k] for k in range(N)] + [tinv[k] for k in range(N - 1, -1, -1)]
    P = ieye(N)
    for m in mixed:
        P = imul(P, m)
    expect_fail(lambda: minus_I_mod_rad(P), 'inverse letters on one side')
    return 40


# ---- 2. saturated headers --------------------------------------------------------------------------------------
def lower_strict(G):
    N = len(G)
    return [[G[i][j] if i > j else 0 for j in range(N)] for i in range(N)]


def check_headers():
    for n in range(2, 19, 2):
        T = H.qt(H.int_canonical(n))
        N = n + 1
        need(H.is_header(T), 'header n=%d' % n)
        G = H.gram(T)
        need(G == H.sign_gram(N), 'sign gram n=%d' % n)
        # path of d_s = x_s - x_{s+1}: omega(d_s, d_t) = -1 for t = s+1, 0 otherwise (PROOF 1(b))
        for s_ in range(n):
            for t_ in range(n):
                val = G[s_][t_] - G[s_][t_ + 1] - G[s_ + 1][t_] + G[s_ + 1][t_ + 1]
                need(val == (-1 if t_ == s_ + 1 else (1 if t_ == s_ - 1 else 0)), 'omega on the d-path')
        # alternating relations
        for i in range(n):
            need(sum((-1) ** t * T[t][0][i] for t in range(N)) == 0, 'sum (-1)^t x_t')
            need(sum((-1) ** t * T[t][1][i] for t in range(N)) == 0, 'sum (-1)^t y_t')
        # rank-one identity of PROOF 1: units I - X y' with x' = 2x
        G2 = [[2 * v for v in r] for r in G]
        L = lower_strict(G2)
        K = [[(1 if i == j else 0) + L[i][j] for j in range(N)] for i in range(N)]
        R = [[2 * K[i][j] - G2[i][j] for j in range(N)] for i in range(N)]
        need(H.rank(R) == 1, 'rank(2K-Gamma) = 1, n=%d' % n)
        need(H.rank([list(x) for x, _ in T[:n]]) == n, 'x_0..x_{n-1} independent')
        # Omega
        Om = H.omega_of([([int(v) for v in x], [int(v) for v in y]) for x, y in T])
        need(Om == [[H.sgn(j - i) for j in range(n)] for i in range(n)], 'Omega = S_n')
    # expansion J = I - X K^{-1} Y on a random Gram (not a header): proves the formula used in PROOF 1
    random.seed(7)
    for _ in range(20):
        n = random.choice([2, 3, 4])
        N = random.choice([2, 3, 4, 5])
        tup = [([Q(random.randint(-2, 2)) for _ in range(n)], [Q(random.randint(-2, 2)) for _ in range(n)]) for _ in range(N)]
        tup = [(x, [y[i] - x[i] * 0 for i in range(n)]) for x, y in tup]
        J = H.eye(n)
        for x, y in tup:
            J = H.mul(H.unit(x, y, -1), J)
        Xm = [[tup[t][0][i] for t in range(N)] for i in range(n)]
        Ym = [list(tup[t][1]) for t in range(N)]
        Gm = [[H.dot(tup[i][1], tup[j][0]) for j in range(N)] for i in range(N)]
        Km = [[(1 if i == j else 0) + (Gm[i][j] if i > j else 0) for j in range(N)] for i in range(N)]
        Z = H.mul(Xm, H.mul(H.inverse(Km), Ym))
        need(all(J[a][b] == (1 if a == b else 0) - Z[a][b] for a in range(n) for b in range(n)), 'J = I - X K^-1 Y')
    # negative controls
    T = H.int_canonical(4)
    bad = [([v for v in x], [v for v in y]) for x, y in T]
    bad[1] = ([bad[1][0][0] + 1] + bad[1][0][1:], bad[1][1])
    expect_fail(lambda: H.is_header(H.qt(bad)), 'perturbed x_1')
    expect_fail(lambda: H.is_header(H.qt(T[:-1])), 'one unit missing')
    return 9


def check_rigidity():
    """Any two normalised headers on Q^n differ by one g in GL_n(Q): g x_t = x'_t and y'_t = y_t g^-1."""
    base = {8: H.int_canonical(8)}
    cases = {'chain(3|3)': H.chain_root(3, 3), 'chain(1|5)': H.chain_root(1, 5),
             'chain(2|2) n=6': H.chain_root(2, 2), 'root of #6726': H.sixsix_root(str(HERE / 'retained' / 'pr6726' / 'ROOT.json'))}
    count = 0
    for name, T in cases.items():
        n = len(T[0][0])
        need(H.is_normalised(H.qt(T)), name + ' normalised')
        can = H.int_canonical(n)
        X = [[Q(v) for v in T[t][0]] for t in range(n)]
        Xc = [[Q(v) for v in can[t][0]] for t in range(n)]
        # rows are vectors: want g with g x_t = c_t, i.e. X^T g^T = Xc^T
        g = H.mul(H.transpose(Xc), H.inverse(H.transpose(X)))      # g x_t = x'_t for t < n
        gi = H.inverse(g)
        for t in range(n + 1):
            need(H.mv(g, [Q(v) for v in T[t][0]]) == [Q(v) for v in can[t][0]], name + ' g x_t')
            need(H.vm([Q(v) for v in T[t][1]], gi) == [Q(v) for v in can[t][1]], name + ' y g^-1')
        count += 1
    # negative control: with more than n+1 units rigidity fails.  Insert V, V^-1 (V a unit) after the 3 units of the
    # n=2 header: the products are still -I, the x-vectors have different linear relations, no g carries one to the other.
    can = [([Q(v) for v in x], [Q(v) for v in y]) for x, y in H.int_canonical(2)]
    def padded(V):
        x, y = V
        return can + [([Q(v) for v in x], [Q(v) for v in y]), ([Q(v) for v in x], [Q(-v) for v in y])]
    Ta, Tb = padded(([1, 0], [0, 1])), padded(([0, 1], [1, 0]))
    need(H.is_scalar(H.product(Ta), -1) and H.is_scalar(H.product(Tb), -1), 'padded products are -I')
    Xa = H.transpose([list(x) for x, _ in Ta[:2]])
    Xb = H.transpose([list(x) for x, _ in Tb[:2]])
    g = H.mul(Xb, H.inverse(Xa))
    expect_fail(lambda: all(H.mv(g, Ta[t][0]) == Tb[t][0] for t in range(5)), 'rigidity needs exactly n+1 units')
    return count


# ---- 3. path form ---------------------------------------------------------------------------------------------
def star_to_path(T):
    """a_t = P_t x_t, b_t = y_t P_t^-1, t_t = I + a_t b_t, P_{t+1} = t_t P_t  (t acts first on position 0)."""
    n = len(T[0][0])
    P = H.eye(n)
    Pi = H.eye(n)
    out = []
    for x, y in T:
        x = [Q(v) for v in x]
        y = [Q(v) for v in y]
        a = H.mv(P, x)
        b = H.vm(y, Pi)
        out.append((a, b))
        P = H.mul(H.unit(a, b, 1), P)
        Pi = H.mul(Pi, H.unit(a, b, -1))
    return out


def path_M(path, q):
    n = len(path[0][0])
    M = H.eye(n)
    for a, b in path:
        M = H.mul(H.unit(a, b, q), M)
    return M


def path_gram(path):
    return [[H.dot(b, a2) for (a2, _) in path] for (_, b) in path]


def tridiagonal_minus_one(G):
    N = len(G)
    return (all(G[i][j] == 0 for i in range(N) for j in range(N) if abs(i - j) != 1)
            and all(G[i][i + 1] * G[i + 1][i] == -1 for i in range(N - 1)))


def path_to_star(path):
    """Telescoping: units X_i = I - 2 a_i b_i conjugated by A_i = t_n^-1 ... t_{i+1}^-1; returned in acting order."""
    n = len(path[0][0])
    N = len(path)
    out = []
    for i in range(N):
        A = H.eye(n)
        for k in range(N - 1, i, -1):
            A = H.mul(A, H.unit(path[k][0], path[k][1], -1))
        Ai = H.inverse(A)
        out.append((H.mv(A, path[i][0]), H.vm(path[i][1], Ai)))
    return out[::-1]


def sign_normalise(T):
    N = len(T)
    G = H.gram(T)
    need(all(abs(G[0][j]) == 1 for j in range(1, N)), 'unit Gram entries in the first row')
    e = [1] + [-G[0][j] for j in range(1, N)]
    out = [([e[t] * v for v in T[t][0]], [e[t] * v for v in T[t][1]]) for t in range(N)]
    need(H.gram(out) == H.sign_gram(N), 'sign normalisation')
    return out


def chain_path(N):
    """The path form of the chain of transvections on V/rad (N odd): a_i = e_i, a_{N-1} = -(e_0 + e_2 + ... + e_{N-3})."""
    n = N - 1
    def w_full(i, j):
        return (j == i + 1) - (j == i - 1)
    def vec(i):
        v = [Q(0)] * n
        if i < n:
            v[i] = Q(1)
        else:
            for k in range(0, n - 1, 2):
                v[k] = Q(-1)
        return v
    def w(u, v):   # form on V/rad, extended bilinearly from basis e_0..e_{n-1}
        return sum(u[i] * v[j] * w_full(i, j) for i in range(n) for j in range(n))
    basis = [[Q(int(i == j)) for j in range(n)] for i in range(n)]
    out = []
    for i in range(N):
        a = vec(i)
        b = [w(a, basis[j]) for j in range(n)]
        out.append((a, b))
    return out


def check_path():
    cases = [('canonical n=%d' % n, H.int_canonical(n)) for n in (2, 4, 6, 8, 10)]
    cases += [('chain(3|3)', H.chain_root(3, 3)), ('chain(4|4)', H.chain_root(4, 4)), ('chain(5|3)', H.chain_root(5, 3)),
              ('root of #6726', H.sixsix_root(str(HERE / 'retained' / 'pr6726' / 'ROOT.json')))]
    for name, T in cases:
        P = star_to_path(T)
        n = len(T[0][0])
        need(all(H.dot(b, a) == 0 for a, b in P), name + ' b_i a_i = 0')
        need(tridiagonal_minus_one(path_gram(P)), name + ' path Gram tridiagonal, products -1')
        M1, Mm = path_M(P, 1), path_M(P, -1)
        need(all(Mm[i][j] == -M1[i][j] for i in range(n) for j in range(n)), name + ' M(-1) = -M(1)')
    # converse: the chain of transvections (the sphere relation) gives a saturated header
    for N in (3, 5, 7, 9, 11):
        P = chain_path(N)
        n = N - 1
        need(all(H.dot(b, a) == 0 for a, b in P), 'chain path b a = 0')
        need(tridiagonal_minus_one(path_gram(P)), 'chain path Gram: tridiagonal with products -1')
        M1, Mm = path_M(P, 1), path_M(P, -1)
        need(all(Mm[i][j] == -M1[i][j] for i in range(n) for j in range(n)), 'sphere relation on V/rad: M(-1) = -M(1)')
        S = sign_normalise(path_to_star(P))
        need(H.is_normalised(S), 'star of the chain path is a normalised header')
        can = H.int_canonical(n)
        X = [[Q(v) for v in S[t][0]] for t in range(n)]
        Xc = [[Q(v) for v in can[t][0]] for t in range(n)]
        g = H.mul(H.transpose(Xc), H.inverse(H.transpose(X)))
        need(all(H.mv(g, [Q(v) for v in S[t][0]]) == [Q(v) for v in can[t][0]] for t in range(N)), 'rigidity of the star of the chain')
    # path form with t != -1 is not a header: scale the path Gram of N=3 (n=2): t = -2
    P = chain_path(3)
    Pbad = [P[0], (P[1][0], [2 * v for v in P[1][1]]), P[2]]
    M1, Mm = path_M(Pbad, 1), path_M(Pbad, -1)
    expect_fail(lambda: all(Mm[i][j] == -M1[i][j] for i in range(2) for j in range(2)), 'path with t != -1 (b_1 doubled)')
    # exhaustive n = 2 search: every triple of rank-one units with entries in {-1,0,1} and M(-1) = -M(1)
    vecs = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
    units = [(x, y) for x in vecs for y in vecs if x[0] * y[0] + x[1] * y[1] == 0]
    def m2(a, b, q):
        return ((1 + q * a[0] * b[0], q * a[0] * b[1]), (q * a[1] * b[0], 1 + q * a[1] * b[1]))
    def mm(A, B):
        return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(2)) for j in range(2)) for i in range(2))
    pre = {u: (m2(u[0], u[1], 1), m2(u[0], u[1], -1)) for u in units}
    found = 0
    for u0, u1, u2 in itertools.product(units, repeat=3):
        M1 = mm(pre[u2][0], mm(pre[u1][0], pre[u0][0]))
        Mm = mm(pre[u2][1], mm(pre[u1][1], pre[u0][1]))
        if all(Mm[i][j] == -M1[i][j] for i in range(2) for j in range(2)):
            found += 1
            G = [[u[1][0] * v[0][0] + u[1][1] * v[0][1] for v in (u0, u1, u2)] for u in (u0, u1, u2)]
            need(tridiagonal_minus_one(G), 'path theorem fails on an exhaustive instance')
    need(found > 0, 'exhaustive search found no solution (control)')
    return found


# ---- 4. Hurwitz moves ------------------------------------------------------------------------------------------
def d_transvection(T, i, c=1):
    n = len(T[0][0])
    d = [p - q for p, q in zip(T[i][0], T[i + 1][0])]
    yd = [p - q for p, q in zip(T[i][1], T[i + 1][1])]
    return [[Q(int(a == b)) + c * d[a] * yd[b] for b in range(n)] for a in range(n)]


def act(g, T):
    gi = H.inverse(g)
    return [(H.mv(g, [Q(v) for v in x]), H.vm([Q(v) for v in y], gi)) for x, y in T]


def check_hurwitz():
    cases = [('canonical n=%d' % n, H.int_canonical(n)) for n in (2, 4, 6, 8)] + [('chain(3|3)', H.chain_root(3, 3))]
    random.seed(11)
    moves_checked = 0
    for name, T in cases:
        n = len(T[0][0])
        N = n + 1
        Om = H.omega_of(T)
        gs = [d_transvection(T, i) for i in range(n)]
        # braid relations of the images
        for i in range(n - 1):
            need(H.mul(gs[i], H.mul(gs[i + 1], gs[i])) == H.mul(gs[i + 1], H.mul(gs[i], gs[i + 1])), name + ' braid relation')
        for i in range(n):
            for j in range(i + 2, n):
                need(H.mul(gs[i], gs[j]) == H.mul(gs[j], gs[i]), name + ' far commutation')
        for i in range(n):
            for s in (1, -1):
                T2 = H.move(T, i, s)
                need(H.is_normalised(H.qt(T2)), name + ' move keeps a normalised header')
                need(H.omega_of(T2) == Om, name + ' move keeps Omega')
                g = d_transvection(T, i, 1 if s == 1 else -1)
                if s == 1:
                    A = act(gs[i], T)
                    need(all(A[t][0] == [Q(v) for v in T2[t][0]] and A[t][1] == [Q(v) for v in T2[t][1]] for t in range(N)),
                         name + ' move = g_i . tuple')
                else:
                    A = act(H.inverse(gs[i]), T)
                    need(all(A[t][0] == [Q(v) for v in T2[t][0]] and A[t][1] == [Q(v) for v in T2[t][1]] for t in range(N)),
                         name + ' inverse move = g_i^-1 . tuple')
                # locality: all other units unchanged, prefix products unchanged except at the cut i
                for t in range(N):
                    if t not in (i, i + 1):
                        need(T2[t] == T[t], name + ' other units unchanged')
                P1, P2 = H.eye(n), H.eye(n)
                for t in range(N):
                    P1 = H.mul(H.unit([Q(v) for v in T[t][0]], [Q(v) for v in T[t][1]]), P1)
                    P2 = H.mul(H.unit([Q(v) for v in T2[t][0]], [Q(v) for v in T2[t][1]]), P2)
                    if t != i:
                        need(P1 == P2, name + ' prefix products agree off the cut')
                x_i, x_j = T[i][0], T[i + 1][0]
                for k in (i, i + 1):
                    for vec_t, vec_o in ((T2[k][0], (x_i, x_j)), (T2[k][1], (T[i][1], T[i + 1][1]))):
                        need(all((vec_t[c] != 0) <= (vec_o[0][c] != 0 or vec_o[1][c] != 0) for c in range(n)),
                             'moved units are supported in the union of the two old supports')
                moves_checked += 1
        # a random word equals the product of the fixed images g_j^{s}
        for _ in range(5):
            w = [(random.randrange(n), random.choice((1, -1))) for _ in range(12)]
            Tw = H.apply_word(T, w)
            rho = H.eye(n)
            for i, s in w:
                rho = H.mul(rho, gs[i] if s == 1 else H.inverse(gs[i]))
            B = act(rho, T)
            need(all(B[t][0] == [Q(v) for v in Tw[t][0]] and B[t][1] == [Q(v) for v in Tw[t][1]] for t in range(N)),
                 name + ' word = product of images')
    # legality in the two forms: components at q = +1 and q = -1 of F[q]/(q^2-1) = F x F
    for name, T in cases[:3] + cases[4:]:
        n = len(T[0][0])
        N = n + 1
        Tq = H.qt(T)
        for i in range(n):
            Ui, Uj = H.unit(*Tq[i]), H.unit(*Tq[i + 1])
            Uji = H.inverse(Uj)
            conj = H.mul(Uj, H.mul(Ui, Uji))        # q = -1 component of the moved unit; q = +1 component is I
            Rp = [[(H.eye(n)[a][b] - conj[a][b]) / 2 for b in range(n)] for a in range(n)]
            xs = H.mv(Uj, Tq[i][0])
            ys = H.vm(Tq[i][1], Uji)
            need(Rp == [[xs[a] * ys[b] for b in range(n)] for a in range(n)], 'sector: conjugate unit is again I - 2 x y with q-free x, y')
            need(H.dot(ys, xs) == 0, 'sector: square-zero preserved')
        # path form: the moved unit t_{i+1}^{-q} t_i^q t_{i+1}^q at q = +1 and q = -1 has a nonzero q-even part
        P = star_to_path(T)
        for i in range(n):
            ti = {q: H.unit(P[i][0], P[i][1], q) for q in (1, -1)}
            tj = {q: H.unit(P[i + 1][0], P[i + 1][1], q) for q in (1, -1)}
            tji = {q: H.inverse(tj[q]) for q in (1, -1)}
            c1 = H.mul(tji[1], H.mul(ti[1], tj[1]))
            cm = H.mul(tji[-1], H.mul(ti[-1], tj[-1]))
            even = [[(c1[a][b] + cm[a][b]) / 2 - (1 if a == b else 0) for b in range(n)] for a in range(n)]
            need(any(any(r) for r in even), 'path form: adjacent Hurwitz conjugate has a nonzero q-even part')
        for i in range(n - 1):
            for j in range(i + 2, n):
                ti = {q: H.unit(P[i][0], P[i][1], q) for q in (1, -1)}
                tj = {q: H.unit(P[j][0], P[j][1], q) for q in (1, -1)}
                c1 = H.mul(H.inverse(tj[1]), H.mul(ti[1], tj[1]))
                need(c1 == ti[1], 'control: commuting path units move freely')
    return moves_checked


# ---- 5. orbits mod m and classes in a fixed frame -----------------------------------------------------------
def sp2_order(n):
    g = n // 2
    r = 2 ** (g * g)
    for i in range(1, g + 1):
        r *= 2 ** (2 * i) - 1
    return r


def sp_odd_prime_order(n, p):
    g = n // 2
    r = p ** (g * g)
    for i in range(1, g + 1):
        r *= p ** (2 * i) - 1
    return r


def check_orbits():
    T2, T4 = H.int_canonical(2), H.int_canonical(4)
    res = {}
    res['n2 m3'] = H.orbit_size_mod(T2, 3)
    need(res['n2 m3'] == sp_odd_prime_order(2, 3) // 2, 'n=2 mod 3: |Sp_2(3)|/2')
    res['n2 m4'] = H.orbit_size_mod(T2, 4)
    need(res['n2 m4'] == factorial(3) * 2 ** 3 // 2, 'n=2 mod 4 = 3! 2^3 / 2 = 24')
    res['n2 m8'] = H.orbit_size_mod(T2, 8)
    need(res['n2 m8'] == 96, 'n=2 mod 8 = 6 * 64 / 4 = 96 (four scalar units s with s^2 = 1 mod 8)')
    res['n4 m3'] = H.orbit_size_mod(T4, 3)
    need(res['n4 m3'] == sp_odd_prime_order(4, 3) // 2, 'n=4 mod 3: |Sp_4(3)|/2 = 25920')
    res['n4 m4'] = H.orbit_size_mod(T4, 4)
    need(res['n4 m4'] == factorial(5) * 2 ** 10 // 2, 'n=4 mod 4 = 5! 2^10 / 2 = 61440')
    # negative control: the formula without the factor 1/2 (the scalar -1) is wrong
    expect_fail(lambda: res['n4 m4'] == factorial(5) * 2 ** 10, 'missing 1/2')
    # classes in a fixed frame: orbit of the mod-2 multiset under Sp_n(F_2) has |Sp_n(F_2)| / (n+1)! elements
    for n, expected in ((2, 1), (4, 6), (6, 288)):
        T = H.int_canonical(n)
        S = H.S_matrix(n)
        def w2(u, v):
            return sum(u[i] * S[i][j] * v[j] for i in range(n) for j in range(n)) & 1
        vecs = [tuple((v >> k) & 1 for k in range(n)) for v in range(1, 2 ** n)]
        def tv(vv, x):
            return tuple((x[k] + (vv[k] if w2(vv, x) else 0)) & 1 for k in range(n))
        m0 = tuple(sorted(tuple(v % 2 for v in x) for x, _ in T))
        seen = {m0}
        fr = [m0]
        while fr:
            nx = []
            for m in fr:
                for vv in vecs:
                    m2 = tuple(sorted(tv(vv, x) for x in m))
                    if m2 not in seen:
                        seen.add(m2)
                        nx.append(m2)
            fr = nx
        need(len(seen) == sp2_order(n) // factorial(n + 1) == expected, 'class count n=%d' % n)
        res['classes n=%d' % n] = len(seen)
    # a class different from the canonical one in the same frame: image under a transvection of Sp_4(Z)
    T = H.int_canonical(4)
    n = 4
    S = H.S_matrix(n)
    found = None
    for v in [[(m >> a) & 1 for a in range(n)] for m in range(1, 2 ** n)]:
        g = [[Q(int(a == b)) + v[a] * sum(v[c] * S[c][b] for c in range(n)) for b in range(n)] for a in range(n)]
        A = [([int(t) for t in x], [int(t) for t in y]) for x, y in act(g, T)]
        need(H.is_normalised(H.qt(A)) and H.omega_of(A) == H.omega_of(T), 'image under Sp_4(Z) is a header with the same Omega')
        if H.mod2_multiset(A) != H.mod2_multiset(T):
            found = v
            break
    need(found is not None, 'a transvection of Sp_4(Z) leaves the orbit of the canonical header (different mod-2 multiset)')
    res['transvection leaving the orbit'] = found
    return res


# ---- 6. arc law -----------------------------------------------------------------------------------------------
def arc_cells(n, a, b):
    """The two cyclic arcs from a to b (inclusive) on positions 0..n-1, as frozensets."""
    a, b = min(a, b), max(a, b)
    inner = frozenset(range(a, b + 1))
    outer = frozenset(list(range(0, a + 1)) + list(range(b, n)))
    return inner, outer


def arc_statement(x, n):
    S = H.S_matrix(n)
    y = [sum(x[i] * S[i][j] for i in range(n)) for j in range(n)]
    M = frozenset(i for i in range(n) if x[i] or y[i])
    W = [i for i in range(n) if x[i] % 2]
    if not W:
        return True
    if len(W) % 2 == 1:
        return len(M) == n
    par = [sum(1 for w in W if w < f) % 2 for f in range(n)]
    gaps = [f for f in range(n) if f not in M]
    ok = len({par[f] for f in gaps}) <= 1
    if len(W) == 2:
        inner, outer = arc_cells(n, W[0], W[1])
        ok = ok and (inner <= M or outer <= M)
    return ok


def check_arcs():
    count = 0
    for n, rng in ((4, range(-3, 4)), (6, range(-2, 3)), (8, (-1, 0, 1, 2))):
        for x in itertools.product(rng, repeat=n):
            need(arc_statement(list(x), n), 'arc law fails at x=%s' % (x,))
            count += 1
    # y alone is not enough (negative control): x_f != 0 off supp(y) with W = {A, j} and no arc in supp(y)
    n = 4
    S = H.S_matrix(n)
    hit = None
    for x in itertools.product(range(-2, 3), repeat=n):
        W = [i for i in range(n) if x[i] % 2]
        if len(W) != 2:
            continue
        y = [sum(x[i] * S[i][j] for i in range(n)) for j in range(n)]
        My = frozenset(i for i in range(n) if y[i])
        inner, outer = arc_cells(n, W[0], W[1])
        if not (inner <= My or outer <= My):
            hit = (x, sorted(My))
            break
    need(hit is not None, 'control: the arc law needs x supported in M as well as y')
    # on literal headers: every unit of chain roots, of the #6726 root, and of random Hurwitz walks
    roots = [('chain(3|3)', H.chain_root(3, 3)), ('chain(9|9)', H.chain_root(9, 9)),
             ('root of #6726', H.sixsix_root(str(HERE / 'retained' / 'pr6726' / 'ROOT.json')))]
    random.seed(5)
    checked = 0
    for name, T in roots:
        fr = H.s_frames(T)
        need(len(fr) > 0, name + ' has an S frame')
        n = len(T[0][0])
        walk = fr[0]
        steps = 0
        while steps < (150 if n <= 8 else 20):
            for x, y in walk:
                need(arc_statement(list(x), n), name + ' unit violates the arc law')
                checked += 1
            walk = H.move(walk, random.randrange(n), random.choice((1, -1)))
            steps += 1
    return count + checked


# ---- 7. literal words, frames -------------------------------------------------------------------------------
def first_s_frame(T):
    f = H.s_frames(T)
    need(len(f) > 0, 'S frame')
    return f


def check_words():
    out = {}
    # chains with the same n: equal invariants and a literal word
    pairs = [((3, 2), (1, 4)), ((2, 2), (3, 2)), ((3, 3), (5, 1)), ((3, 3), (1, 5)), ((5, 5), (7, 3))]
    for a, b in pairs:
        Ta, Tb = H.chain_root(*a), H.chain_root(*b)
        need(len(Ta[0][0]) == len(Tb[0][0]), 'same n')
        Fa, Fb = first_s_frame(Ta)[0], first_s_frame(Tb)[0]
        need(H.omega_of(Fa) == H.omega_of(Fb) == H.S_matrix(len(Fa[0][0])), 'same Omega')
        need(H.mod2_multiset(Fa) == H.mod2_multiset(Fb), 'same mod-2 multiset %s %s' % (a, b))
        r = H.shortest_word(Fa, Fb, max_len=8)
        need(r is not None, 'word within length 8 for %s %s' % (a, b))
        L, w = r
        need(H.key(H.apply_word(Fa, w)) == H.key(Fb), 'word reaches the target')
        out['%s-%s' % (a, b)] = L
    # every chain of the same n has the same Omega (= S_n in its own frame) and the same mod-2 multiset
    nchains = 0
    for n in (4, 6, 8, 10, 12):
        ref = None
        for a in range(1, n):
            for b in range(1, n):
                nf = 1 + a + b
                if nf + nf % 2 != n or (a % 2 == 0 and b % 2 == 1):
                    continue
                F = first_s_frame(H.chain_root(a, b))[0]
                need(H.omega_of(F) == H.S_matrix(n), 'Omega of chain (%d|%d)' % (a, b))
                m = H.mod2_multiset(F)
                ref = ref or m
                need(m == ref, 'chain (%d|%d) mod-2 multiset' % (a, b))
                nchains += 1
    out['chains with equal invariants'] = nchains
    # the #6726 root versus chain (3|3)
    C = H.chain_root(3, 3)
    R = H.sixsix_root(str(HERE / 'retained' / 'pr6726' / 'ROOT.json'))
    FC = first_s_frame(C)[0]
    fr = H.s_frames(R)
    match = [F for F in fr if H.mod2_multiset(F) == H.mod2_multiset(FC)]
    need(len(match) >= 1, 'a relabeling of the #6726 root with the chain invariants exists')
    L, w = H.shortest_word(FC, match[0], max_len=8)
    need(H.key(H.apply_word(FC, w)) == H.key(match[0]), '#6726 word reaches the target')
    out['chain(3|3)-#6726'] = L
    need(L == 5, 'distance 5 (balls of radii 2 and 2 are disjoint, so no word of length <= 4)')
    others = [F for F in fr if H.mod2_multiset(F) != H.mod2_multiset(FC)]
    need(len(match) == 1 and len(others) == len(fr) - 1 and len(fr) == 8,
         'only one of the eight relabelings carries the chain invariants; the others are in other orbits')
    # the same fixed frame is necessary: Omega differs between chain (3|3) in its own coordinates and a flat header
    flat = flat_root(8)
    need(H.is_normalised(H.qt(flat)), 'flat header is a header')
    Om_c = H.omega_of(C)
    Om_f = H.omega_of(flat)
    nz = lambda M: sum(1 for r in M for v in r if v)  # noqa: E731
    need((nz(Om_c), nz(Om_f)) == (56, 8), 'Omega nonzeros 56 versus 8')
    for _ in range(40):
        flat = H.move(flat, random.randrange(8), random.choice((1, -1)))
        C = H.move(C, random.randrange(8), random.choice((1, -1)))
    need(H.omega_of(flat) == Om_f and H.omega_of(C) == Om_c, 'moves keep Omega: the two frames never meet')
    out['Omega nnz'] = (56, 8)
    # observation on the transcription of the thin queries for (even|odd) shapes
    for a, b in ((2, 1), (2, 3), (4, 1)):
        expect_fail(lambda: H.is_normalised(H.qt(H.chain_root(a, b))), '(even|odd) closed form (%d|%d)' % (a, b))
    for a, b in ((3, 1), (1, 4), (2, 2), (4, 4), (9, 9)):
        need(H.is_normalised(H.qt(H.chain_root(a, b))), 'chain (%d|%d)' % (a, b))
    return out


def sym_basis_change(S):
    """Integer P with P^T S P = J^{(n/2)} for a unimodular skew integer matrix S (symplectic Gram-Schmidt)."""
    n = len(S)
    def w(u, v):
        return sum(u[i] * S[i][j] * v[j] for i in range(n) for j in range(n))
    def egcd(a, b):
        if b == 0:
            return (abs(a), (1 if a >= 0 else -1), 0)
        g, s, t = egcd(b, a % b)
        return g, t, s - (a // b) * t
    rest = [[int(i == j) for j in range(n)] for i in range(n)]
    cols = []
    while rest:
        u = rest[0]
        coef = [w(u, r) for r in rest]
        g, c = 0, [0] * len(rest)
        for k, a in enumerate(coef):
            g2, s, t = egcd(g, a)
            c = [s * ci for ci in c]
            c[k] += t
            g = g2
        need(g == 1, 'unimodular')
        v = [sum(c[k] * rest[k][i] for k in range(len(rest))) for i in range(n)]
        need(w(u, v) == 1, 'pair')
        proj = []
        for r in rest:
            rp = [r[i] - w(u, r) * v[i] + w(v, r) * u[i] for i in range(n)]
            proj.append(rp)
        cols += [u, v]
        rest = reduce_basis(proj, w, u, v)
    P = [[cols[j][i] for j in range(n)] for i in range(n)]
    return P


def reduce_basis(proj, w, u, v):
    """Complement lattice basis: integer row-reduce the projected vectors and drop the two zero rows."""
    rows = [list(r) for r in proj]
    n = len(rows[0])
    basis = []
    for c in range(n):
        while True:
            nz = [r for r in rows if r[c]]
            if len(nz) <= 1:
                break
            nz.sort(key=lambda r: abs(r[c]))
            p = nz[0]
            for r in nz[1:]:
                f = r[c] // p[c]
                for k in range(n):
                    r[k] -= f * p[k]
        nz = [r for r in rows if r[c]]
        if nz:
            basis.append(nz[0])
            rows.remove(nz[0])
    return [list(r) for r in basis if any(r)]


def flat_root(n):
    """A saturated normalised header on Z^n whose Omega is the direct sum of n/2 copies of [[0,1],[-1,0]]."""
    T = H.int_canonical(n)
    S = H.S_matrix(n)
    P = sym_basis_change(S)
    Pq = [[Q(v) for v in r] for r in P]
    Pi = H.inverse(Pq)
    flat = []
    for x, y in T:
        xp = H.mv(Pi, [Q(v) for v in x])
        yp = H.vm([Q(v) for v in y], Pq)
        flat.append(([int(v) for v in xp], [int(v) for v in yp]))
    J = [[0] * n for _ in range(n)]
    for k in range(0, n, 2):
        J[k][k + 1], J[k + 1][k] = 1, -1
    need(H.omega_of(flat) == [[Q(v) for v in r] for r in J], 'flat Omega')
    return flat


def main():
    out = {}
    out['pins'] = check_pins()
    out['sphere'] = check_sphere_relation()
    out['headers'] = check_headers()
    out['rigidity'] = check_rigidity()
    out['path'] = check_path()
    out['hurwitz'] = check_hurwitz()
    out['orbits'] = check_orbits()
    out['arcs'] = check_arcs()
    out['words'] = check_words()
    print(json.dumps(out, default=str, sort_keys=True))
    print('PASS_HEADER_BRAID_CLASSIFICATION')


if __name__ == '__main__':
    main()
