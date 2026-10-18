#!/usr/bin/env python3
"""E6 / D5 rank-T realisations: E6 local rigidity at the Gram point, D5 non-Gram
family, D5 normal form and floor 20 (#2277 open question 4).

Standard library only, exact arithmetic (integers, Fractions, ranks modulo
primes used only in the safe direction).  Run:  python3 -I verify.py
Options: --skip-e7 (drop the 63-line E7 control), --e8 (add the slow E8 control).

Prepared by thakrarsagar with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5).  Apache-2.0.

Rigour of the prime-rank steps.  For an integer matrix A and a prime p,
rank_p(A mod p) <= rank_Q(A) (a nonzero minor mod p is a nonzero integer).  So
  * a prime rank of the tangent system bounds the rational SOLUTION dimension
    from above, and
  * a prime rank of an explicit family of rational tangent vectors bounds
    their rational SPAN from below.
Every load-bearing dimension is certified either by such a matching pair of
bounds or by an exact Fraction rank (rank_frac, tangent_exact); it is then exact
over Q (and over every field of characteristic 0).  Negative controls whose
exact value would need the unsafe direction of a prime rank are computed with
rank_frac or with an explicit lower-bound family.  Proof-relevant intermediate
checks use assert, so the script refuses to run under python -O.
"""
import itertools
import sys
import time
from fractions import Fraction as F

P1 = 1000003
P2 = 998244353
CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (" :: " + detail if detail else ""), flush=True)
    if not cond:
        raise SystemExit("verification failed: " + name)


# ---------------------------------------------------------------- units
def cartan(kind, n):
    C = [[2 if i == j else 0 for j in range(n)] for i in range(n)]

    def link(a, b):
        C[a][b] = C[b][a] = -1
    if kind == "D":
        for i in range(n - 2):
            link(i, i + 1)
        link(n - 3, n - 1)
    elif kind == "E":  # Bourbaki numbering 1-3-4-5-6-(7-8), 2-4 (0-based here)
        link(0, 2); link(2, 3); link(1, 3)
        for k in range(3, n - 1):
            link(k, k + 1)
    else:
        raise ValueError(kind)
    return C


def positive_roots(C):
    """All positive roots in simple-root coordinates (reflection closure)."""
    n = len(C)
    simple = [tuple(int(i == j) for i in range(n)) for j in range(n)]
    seen, frontier = set(simple), list(simple)
    while frontier:
        nxt = []
        for c in frontier:
            Cc = [sum(C[i][k] * c[k] for k in range(n)) for i in range(n)]
            for i in range(n):
                r = list(c); r[i] -= Cc[i]; r = tuple(r)
                if r not in seen and (all(x >= 0 for x in r) or all(x <= 0 for x in r)):
                    seen.add(r); nxt.append(r)
        frontier = nxt
    return sorted(r for r in seen if all(x >= 0 for x in r))


def simple_root_unit(kind, n):
    """Lines = positive roots; X = simple-root coordinates, Y = X C; G = X Y^T."""
    C = cartan(kind, n)
    X = [list(r) for r in positive_roots(C)]
    Y = [[sum(C[i][k] * x[k] for k in range(n)) for i in range(n)] for x in X]
    return X, Y


def dn_lines(n):
    return [(i, j, s) for i, j in itertools.combinations(range(n), 2) for s in (1, -1)]


def dn_unit(n):
    X = []
    for i, j, s in dn_lines(n):
        r = [0] * n; r[i] = 1; r[j] = s; X.append(r)
    return X, [list(r) for r in X]


def dot(u, w):
    return sum(a * b for a, b in zip(u, w))


def mat(X, Y):
    return [[dot(x, y) for y in Y] for x in X]


# ---------------------------------------------------------------- linear algebra
def rank_mod(rows, ncols, p):
    rows = [[x % p for x in r] for r in rows]
    rows = [r for r in rows if any(r)]
    rk = 0
    for c in range(ncols):
        piv = next((i for i in range(rk, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        inv = pow(rows[rk][c], p - 2, p)
        pr = [x * inv % p for x in rows[rk]]
        rows[rk] = pr
        for i in range(rk + 1, len(rows)):
            f = rows[i][c]
            if f:
                rows[i] = [(a - f * b) % p for a, b in zip(rows[i], pr)]
        rk += 1
    return rk


def rank_frac(rows):
    rows = [[F(x) for x in r] for r in rows if any(r)]
    if not rows:
        return 0
    rk = 0
    for c in range(len(rows[0])):
        piv = next((i for i in range(rk, len(rows)) if rows[i][c] != 0), None)
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        pr = rows[rk]
        for i in range(rk + 1, len(rows)):
            f = rows[i][c] / pr[c]
            if f:
                rows[i] = [a - f * b for a, b in zip(rows[i], pr)]
        rk += 1
    return rk


# ---------------------------------------------------------------- tangent machinery
def orth_pairs(G, drop=()):
    v = len(G)
    return [(t, s) for t in range(v) for s in range(v)
            if t != s and G[t][s] == 0 and (t, s) not in drop and (s, t) not in drop]


def tangent_system(X, Y, pairs):
    """Rows of (dX, dY) -> (dX Y^T + X dY^T)_{ts} for the constrained pairs."""
    v, T = len(X), len(X[0])
    rows = []
    for t, s in pairs:
        r = [0] * (2 * v * T)
        for a in range(T):
            r[t * T + a] = Y[s][a]
            r[v * T + s * T + a] = X[t][a]
        rows.append(r)
    return rows


def tangent_upper(X, Y, pairs, p):
    """Upper bound on dim T_M V (exact when matched by a lower bound).

    T_M(rank<=T) = {dX Y^T + X dY^T}; the kernel of (dX,dY) -> dX Y^T + X dY^T is
    {(XA, -YA^T)}, of dimension T^2 when rank X = rank Y = T."""
    v, T = len(X), len(X[0])
    assert rank_mod(X, T, p) == T and rank_mod(Y, T, p) == T
    rk = rank_mod(tangent_system(X, Y, pairs), 2 * v * T, p)
    return 2 * v * T - rk - T * T, rk


def orbit_tangent_vectors(M):
    """Delta1 M + M Delta2: row and column scalings, as vectors in K^{v*v}."""
    v = len(M)
    vecs = []
    for t in range(v):
        z = [0] * (v * v)
        for s in range(v):
            z[t * v + s] = M[t][s]
        vecs.append(z)
    for s in range(v):
        z = [0] * (v * v)
        for t in range(v):
            z[t * v + s] = M[t][s]
        vecs.append(z)
    return vecs


def orbit_dim_combinatorial(M):
    """Exact dim of {Delta1 M + M Delta2}: (Delta1 M + M Delta2)_ts = (d1_t + d2_s) M_ts,
    whose kernel has one free parameter per connected component of the bipartite
    support graph (rows + columns, edge where M_ts != 0); so dim = 2v - #components."""
    v = len(M)
    parent = list(range(2 * v))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for t in range(v):
        for s in range(v):
            if M[t][s] != 0:
                parent[find(t)] = find(v + s)
    return 2 * v - len({find(a) for a in range(2 * v)})


def in_pattern(vec, v, pairs):
    return all(vec[t * v + s] == 0 for t, s in pairs)


def rigidity_report(name, X, Y, primes=(P1,), drop=()):
    G = mat(X, Y)
    v, T = len(X), len(X[0])
    pairs = orth_pairs(G, drop)
    assert all(G[t][t] != 0 for t in range(v))
    t0 = time.time()
    ups = [tangent_upper(X, Y, pairs, p) for p in primes]
    # orbit tangent vectors lie in T_G V: they have the form dX Y^T + X dY^T
    # (dX = Delta1 X, dY = Delta2 Y) and vanish on every constrained pair.
    olow = orbit_dim_combinatorial(G)
    if v <= 63:   # independent prime-rank recomputation (skipped for E8: 240 x 14400)
        orbit = orbit_tangent_vectors(G)
        assert all(in_pattern(z, v, pairs) for z in orbit)
        assert rank_mod(orbit, v * v, primes[0]) == olow
    return dict(name=name, v=v, T=T, pairs=len(pairs), upper=[u for u, _ in ups],
                sysrank=[r for _, r in ups], orbit=olow, secs=round(time.time() - t0, 2))


def alpha_perp(G):
    v = len(G)
    nb = [{s for s in range(v) if s != t and G[t][s] == 0} for t in range(v)]
    best = 0

    def grow(clique, cand):
        nonlocal best
        best = max(best, len(clique))
        for c in sorted(cand):
            if c > (clique[-1] if clique else -1):
                grow(clique + [c], cand & nb[c])
    grow([], set(range(v)))
    return best


def e6_in_e8_coordinates():
    """Second, independent model of E6 (the #2277 convention): the E8 lines in
    doubled integer coordinates orthogonal to two roots at 120 degrees.  X = Y =
    the 36 integer line vectors in Z^8 (rank 6, ambient 8)."""
    E8 = []
    for i, j in itertools.combinations(range(8), 2):
        for s in (2, -2):
            for t in (2, -2):
                r = [0] * 8; r[i] = s; r[j] = t; E8.append(r)
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            E8.append(list(signs))
    a = E8[0]
    b = next(r for r in E8 if dot(a, r) == -4)
    lines = {}
    for r in E8:
        if dot(a, r) == 0 and dot(b, r) == 0:
            k = max(tuple(r), tuple(-x for x in r))
            lines[k] = list(k)
    X = sorted(lines.values())
    return X, [list(x) for x in X]


def tangent_exact(X, Y, pairs):
    """Exact dim T_M V over Q (Fraction elimination; small units only)."""
    v, T = len(X), len(X[0])
    assert rank_frac(X) == T and rank_frac(Y) == T
    return 2 * v * T - rank_frac(tangent_system(X, Y, pairs)) - T * T


def tangent_upper_ambient(X, pairs, p, T):
    """Same tangent space with X = Y of rank T inside K^n (n > T), positive
    definite form: the kernel of (dX, dY) -> dX X^T + X dY^T is T^2 + 2 v (n - T)
    (components orthogonal to the row space are free), so
    dim T_G V <= 2 v n - rank_p - T^2 - 2 v (n - T)."""
    v, n = len(X), len(X[0])
    assert rank_mod(X, n, p) == T
    rk = rank_mod(tangent_system(X, X, pairs), 2 * v * n, p)
    return 2 * v * n - rk - T * T - 2 * v * (n - T)


# ---------------------------------------------------------------- D5 family
D5_LINES = dn_lines(5)
D5_EDGES = list(itertools.combinations(range(5), 2))


def d5_family(par, sign_bug=False):
    """x_{ij+}=e_i+a e_j, x_{ij-}=e_i-b e_j, y_{ij+}=e_i+b^{-1} e_j, y_{ij-}=e_i-a^{-1} e_j."""
    X, Y = [], []
    for i, j, s in D5_LINES:
        a, b = (F(z) for z in par[(i, j)])
        x = [F(0)] * 5; y = [F(0)] * 5
        x[i] = y[i] = F(1)
        if s == 1:
            x[j] = a; y[j] = 1 / b
        else:
            x[j] = -b; y[j] = (1 / a) if sign_bug else -1 / a
        X.append(x); Y.append(y)
    return X, Y


GRAM_PAR = {e: (1, 1) for e in D5_EDGES}
# Three explicit generic rational parameter points (fixed, not searched).
D5_POINTS = {
    "pt1": {e: (F(2 + k, 3), F(5, 7 + 2 * k)) for k, e in enumerate(D5_EDGES)},
    "pt2": {e: (F(-3, 4 + k), F(11 + k, 6)) for k, e in enumerate(D5_EDGES)},
    "pt3": {e: (F(7 * k + 1, 13), F(-(k + 2), 9)) for k, e in enumerate(D5_EDGES)},
}


def nonscaling_witnesses(M, G):
    """Pairs violating the D1 G D2 invariant M_ts M_st G_tt G_ss = G_ts^2 M_tt M_ss
    (G symmetric); any violation proves M != D1 G D2."""
    v = len(M)
    return sum(1 for t in range(v) for s in range(v)
               if G[t][s] != 0 and M[t][s] * M[s][t] * G[t][t] * G[s][s] != G[t][s] ** 2 * M[t][t] * M[s][s])


def family_tangent_vectors(n=5):
    """d/da_e and d/db_e of the D_n edge family M(a,b) = X Y^T at a = b = 1
    (exact derivative; x_{ij+}=e_i+a e_j, x_{ij-}=e_i-b e_j, y_{ij+}=e_i+b^{-1} e_j,
    y_{ij-}=e_i-a^{-1} e_j)."""
    X, Y = dn_unit(n)
    v = len(X)
    lines = dn_lines(n)
    idx = {l: k for k, l in enumerate(lines)}
    vecs = []
    for (i, j) in itertools.combinations(range(n), 2):
        tp, tm = idx[(i, j, 1)], idx[(i, j, -1)]
        for which in "ab":
            dX = [[0] * n for _ in range(v)]; dY = [[0] * n for _ in range(v)]
            if which == "a":   # x_{ij+} += da e_j ; y_{ij-} = e_i - a^{-1} e_j -> +da e_j
                dX[tp][j] = 1; dY[tm][j] = 1
            else:              # x_{ij-} -> -db e_j ; y_{ij+} = e_i + b^{-1} e_j -> -db e_j
                dX[tm][j] = -1; dY[tp][j] = -1
            dM = [[dot(dX[t], Y[s]) + dot(X[t], dY[s]) for s in range(v)] for t in range(v)]
            vecs.append([int(dM[t][s]) for t in range(v) for s in range(v)])
    return vecs


# ---------------------------------------------------------------- Theorem D (global D5 normal form)
def kernel_frac(cols):
    """Basis of {c : sum_k c_k cols[k] = 0} (exact)."""
    n, k = len(cols[0]), len(cols)
    rows = [[F(cols[j][i]) for j in range(k)] for i in range(n)]
    piv, r = [], 0
    for c in range(k):
        pr = next((i for i in range(r, n) if rows[i][c] != 0), None)
        if pr is None:
            continue
        rows[r], rows[pr] = rows[pr], rows[r]
        inv = 1 / rows[r][c]
        rows[r] = [x * inv for x in rows[r]]
        for i in range(n):
            if i != r and rows[i][c] != 0:
                f = rows[i][c]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        piv.append(c); r += 1
    free = [c for c in range(k) if c not in piv]
    basis = []
    for fc in free:
        z = [F(0)] * k; z[fc] = F(1)
        for i, pc in enumerate(piv):
            z[pc] = -rows[i][fc]
        basis.append(z)
    return basis


def inverse_frac(A):
    n = len(A)
    aug = [[F(x) for x in row] + [F(int(i == j)) for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        pr = next(i for i in range(c, n) if aug[i][c] != 0)
        aug[c], aug[pr] = aug[pr], aug[c]
        inv = 1 / aug[c][c]
        aug[c] = [x * inv for x in aug[c]]
        for i in range(n):
            if i != c and aug[i][c] != 0:
                f = aug[i][c]
                aug[i] = [a - f * b for a, b in zip(aug[i], aug[c])]
    return [row[n:] for row in aug]


def d5_normal_form(M, check_pattern=True):
    """Run the construction of Theorem D on a rank-5 realisation M of D5,
    starting from M alone; assert every intermediate claim; return the
    edge-supported factors (x_t, y_t) in dual coordinates."""
    v, lines = 20, D5_LINES
    G = mat(*dn_unit(5))
    if check_pattern:
        assert all(M[t][s] == 0 for t, s in orth_pairs(G)) and all(M[t][t] != 0 for t in range(v))
    assert rank_frac(M) == 5
    # rank factorisation M = P Q^T from pivot rows R / columns C of M
    C, R = [], []
    for c in range(v):
        if rank_frac([[M[t][s] for s in C + [c]] for t in range(v)]) > len(C):
            C.append(c)
    for t in range(v):
        if rank_frac([M[r] for r in R + [t]]) > len(R):
            R.append(t)
    Pm = [[M[t][c] for c in C] for t in range(v)]
    Ainv = inverse_frac([[M[r][c] for c in C] for r in R])
    Qm = [[sum(Ainv[i][k] * M[R[k]][s] for k in range(5)) for i in range(5)] for s in range(v)]
    assert all(dot(Pm[t], Qm[s]) == M[t][s] for t in range(v) for s in range(v))
    idx = {l: k for k, l in enumerate(lines)}

    def side(Z):
        W = {e: [Z[idx[(e[0], e[1], 1)]], Z[idx[(e[0], e[1], -1)]]] for e in D5_EDGES}
        assert all(rank_frac(W[e]) == 2 for e in D5_EDGES)                       # dim W_e = 2
        for tri in itertools.combinations(range(5), 3):                            # dim W_ijk = 3
            assert rank_frac([z for e in itertools.combinations(tri, 2) for z in W[e]]) == 3
        f = []
        for a in range(5):
            at = [tuple(sorted((a, b))) for b in range(5) if b != a]
            for e1, e2 in itertools.combinations(at, 2):                           # pairwise meet in a line
                assert rank_frac(W[e1] + W[e2]) == 3
            ker = kernel_frac(W[at[0]] + [[-x for x in z] for z in W[at[1]]])
            assert len(ker) == 1
            fa = [ker[0][0] * W[at[0]][0][i] + ker[0][1] * W[at[0]][1][i] for i in range(5)]
            assert all(rank_frac(W[e] + [fa]) == 2 for e in at)                     # common line L_a
            f.append(fa)
        assert rank_frac(f) == 5                                                   # L_0..L_4 basis
        return f
    fP, gQ = side(Pm), side(Qm)
    pair = [[dot(fP[a], gQ[c]) for c in range(5)] for a in range(5)]
    assert all((pair[a][c] == 0) == (a != c) for a in range(5) for c in range(5))  # dual up to scale
    # coordinates: p_t = sum_a x_t[a] f_a, q_t = sum_a y_t[a] g_a / pair[a][a]
    Sinv = inverse_frac([[fP[a][i] for a in range(5)] for i in range(5)])
    Tinv = inverse_frac([[gQ[a][i] / pair[a][a] for a in range(5)] for i in range(5)])
    X = [[sum(Sinv[a][i] * Pm[t][i] for i in range(5)) for a in range(5)] for t in range(v)]
    Y = [[sum(Tinv[a][i] * Qm[t][i] for i in range(5)) for a in range(5)] for t in range(v)]
    for t, (i, j, s) in enumerate(lines):                                         # edge-supported
        assert all(X[t][a] == 0 and Y[t][a] == 0 for a in range(5) if a not in (i, j))
    assert all(dot(X[t], Y[u]) == M[t][u] for t in range(v) for u in range(v))
    return X, Y


def modp(x, p=P1):
    x = F(x)
    if x.denominator % p == 0:
        raise ValueError("denominator divisible by p")
    return x.numerator * pow(x.denominator, p - 2, p) % p


def tangent_upper_rational(X, Y, pairs, p=P1):
    """tangent_upper for rational X, Y (denominators prime to p: reduction
    Z_(p) -> F_p is a ring map, so rank_p <= rank_Q still holds)."""
    return tangent_upper([[modp(a, p) for a in r] for r in X], [[modp(a, p) for a in r] for r in Y], pairs, p)[0]


def scaled(M, d1, d2):
    return [[d1[t] * M[t][s] * d2[s] for s in range(len(M))] for t in range(len(M))]


def boundary_member():
    """A rank-5 realisation outside the open family chart: x_{01+} = e_0 (a_01 = 0)."""
    X, Y = d5_family(D5_POINTS["pt1"])
    idx = {l: k for k, l in enumerate(D5_LINES)}
    tp, tm = idx[(0, 1, 1)], idx[(0, 1, -1)]
    X[tp] = [F(1), F(0), F(0), F(0), F(0)]; X[tm] = [F(1), F(-1), F(0), F(0), F(0)]
    Y[tp] = [F(1), F(1), F(0), F(0), F(0)]; Y[tm] = [F(0), F(1), F(0), F(0), F(0)]
    return X, Y


# ---------------------------------------------------------------- F2 dense pairing
def dense_classes(G):
    v = len(G)
    cols = [sum((1 if (t == s or G[t][s] == 0) else 0) << t for t in range(v)) for s in range(v)]
    basis = []
    for c in cols:
        for b in basis:
            c = min(c, c ^ b)
        if c:
            basis.append(c)
    span = {0}
    for b in basis:
        span |= {x ^ b for x in span}
    return len(basis), sorted(w for w in span if w), cols


def f2_rank(rowmasks):
    basis = []
    for r in rowmasks:
        for b in basis:
            r = min(r, r ^ b)
        if r:
            basis.append(r)
    return len(basis)


def bd_block_rank(G, R, A):
    v = len(G)
    Aset = set(A)
    rows = []
    for t in R:
        m = 0
        for s in Aset:
            if t == s or G[t][s] == 0:
                m |= 1 << s
        rows.append(m)
    return f2_rank(rows)


# ---------------------------------------------------------------- main
def main(argv):
    if not __debug__:
        raise SystemExit("verify.py relies on assert for proof-relevant intermediate checks; run without -O")
    t_start = time.time()
    print("== Part A: E6 first-order rigidity at the Gram point ==")
    X6, Y6 = simple_root_unit("E", 6)
    G6 = mat(X6, Y6)
    check("E6 unit: 36 lines, T=6, Gram diagonal 2",
          len(X6) == 36 and all(G6[t][t] == 2 for t in range(36)))
    deg = {sum(1 for s in range(36) if s != t and G6[t][s] == 0) for t in range(36)}
    ap = alpha_perp(G6)
    check("E6 orthogonality: 15 orthogonal lines each, alpha_perp=4 (no 6-frame)", deg == {15} and ap == 4,
          "degrees %s alpha_perp %d" % (deg, ap))
    r = rigidity_report("E6", X6, Y6, primes=(P1, P2))
    check("E6 tangent upper bound (primes %d, %d) = 71" % (P1, P2), r["upper"] == [71, 71],
          "system rank %s over %d ordered orthogonal pairs, 432 unknowns" % (r["sysrank"], r["pairs"]))
    check("E6 scaling-orbit tangent rank >= 71 = 2v-1 (and <= 2v-1: rows-sum = cols-sum)", r["orbit"] == 71)
    Xe, _ = e6_in_e8_coordinates()
    Ge = mat(Xe, Xe)
    pe = orth_pairs(Ge)
    up_e = tangent_upper_ambient(Xe, pe, P1, 6)
    check("E6 cross-check in E8 doubled coordinates (36 lines in Z^8, rank 6): tangent upper bound 71",
          len(Xe) == 36 and len(pe) == 540 and up_e == 71 and rank_mod(orbit_tangent_vectors(Ge), 36 * 36, P1) == 71)
    print("  => dim T_G V(E6, rank<=6) = 71 = dim of the scaling orbit {D1 G D2}: G is a smooth point,"
          " locally V = scaling orbit (local rigidity, not global uniqueness)")

    print("== Part B: D5 Gram point is not rigid; explicit 16-parameter non-Gram family ==")
    X5, Y5 = dn_unit(5)
    G5 = mat(X5, Y5)
    v5 = 20
    check("D5 alpha_perp=4 (no 5-frame)", alpha_perp(G5) == 4)
    r5 = rigidity_report("D5", X5, Y5, primes=(P1, P2))
    check("D5 tangent upper bound = 55 (two primes)", r5["upper"] == [55, 55], "system rank %s" % r5["sysrank"])
    check("D5 scaling-orbit tangent = 39", r5["orbit"] == 39)
    Xg, Yg = d5_family(GRAM_PAR)
    check("D5 family at a=b=1 is the Gram matrix", mat(Xg, Yg) == [[F(x) for x in row] for row in G5])
    pairs5 = orth_pairs(G5)
    fam = family_tangent_vectors()
    check("D5 family tangent directions satisfy the pattern zeros", all(in_pattern(z, v5, pairs5) for z in fam))
    orbit5 = orbit_tangent_vectors(G5)
    low = rank_mod(fam + orbit5, v5 * v5, P1)
    check("D5 family directions + scaling orbit span 55 (prime lower bound) = tangent upper bound", low == 55)
    check("D5 family directions modulo the orbit: 55 - 39 = 16 = 20 parameters - 4 (coordinate torus)",
          low - r5["orbit"] == 16 and len(fam) == 20)
    for name, par in D5_POINTS.items():
        X, Y = d5_family(par)
        M = mat(X, Y)
        zeros = all(M[t][s] == 0 for t, s in pairs5)
        diag = all(M[t][t] != 0 for t in range(v5))
        rk = (rank_frac(X), rank_frac(Y), rank_frac(M))
        wit = nonscaling_witnesses(M, G5)
        check("D5 family %s: pattern zeros, nonzero diagonal, rank 5, %d D1 G D2 violations" % (name, wit),
              zeros and diag and rk == (5, 5, 5) and wit > 0)
    check("D5 control: Gram parameters give 0 D1 G D2 violations",
          nonscaling_witnesses(mat(Xg, Yg), G5) == 0)

    print("== Part C: the D5 dense-pairing floor 20 on the whole family ==")
    h, classes, cols = dense_classes(G5)
    check("D5 dense pairing: h=5, 31 classes", h == 5 and len(classes) == 31)
    idx = {l: k for k, l in enumerate(D5_LINES)}
    edge_classes = []
    for w in classes:
        O = {t for t in range(v5) if w >> t & 1}
        E = {(i, j) for (i, j, s) in (D5_LINES[t] for t in O)}
        closed = all(idx[(i, j, 1)] in O and idx[(i, j, -1)] in O for (i, j) in E)
        edge_classes.append((w, E, closed))
    check("every class is a union of +/- edge pairs (columns of e_i+e_j and e_i-e_j in B_d coincide)",
          all(c for _, _, c in edge_classes))
    missing = [(w, E) for w, E, _ in edge_classes if len({i for e in E for i in e}) < 5]
    check("exactly 5 classes miss a vertex; each is the axis class {lines avoiding a} (12 lines)",
          len(missing) == 5 and all(len(E) == 6 for _, E in missing))
    # Lemma S (proved in README): span{x_t : t in O} = span{e_i : i covered by E_O}
    # because x_{ij+}, x_{ij-} span <e_i, e_j> iff a+b != 0 iff M_tt != 0.
    for name, par in list(D5_POINTS.items()) + [("gram", GRAM_PAR)]:
        X, Y = d5_family(par)
        dx = [w for w in classes if rank_frac([X[t] for t in range(v5) if w >> t & 1]) < 5]
        dy = [w for w in classes if rank_frac([Y[t] for t in range(v5) if w >> t & 1]) < 5]
        ok_lemma = all(rank_frac([X[t] for t in range(v5) if w >> t & 1]) == len({i for e in E for i in e})
                       for w, E, _ in edge_classes)
        check("Lemma S exact at %s; deficient classes = the 5 axis classes on both sides" % name,
              ok_lemma and sorted(dx) == sorted(dy) == sorted(w for w, _ in missing))
    # term-rank table (Lemma 5.1 of #2277: depends only on Def(R), Def(A)); R(e_a) = lines through a
    through = {a: [t for t, (i, j, s) in enumerate(D5_LINES) if a in (i, j)] for a in range(5)}
    full = list(range(v5))
    table = {
        "matched": {bd_block_rank(G5, through[a], through[a]) for a in range(5)},
        "unmatched": {bd_block_rank(G5, through[a], through[b]) for a in range(5) for b in range(5) if a != b},
        "one-deficient": {bd_block_rank(G5, through[a], full) for a in range(5)} |
                         {bd_block_rank(G5, full, through[a]) for a in range(5)},
        "none": {bd_block_rank(G5, full, full)},
    }
    check("D5 term ranks: matched 4, unmatched 3, one deficient 4, none 5",
          table == {"matched": {4}, "unmatched": {3}, "one-deficient": {4}, "none": {5}}, str(table))
    trip = [c for c in itertools.permutations([(a, b) for a in range(5) for b in range(5) if a != b], 3)
            if all(c[i][1] == c[j][0] for i in range(3) for j in range(3) if i != j)]
    check("#2277 c1.d5core re-derived: no three pairs (a_i!=b_i) with b_i = a_j for all i != j", not trip)
    check("coordinate decoder p_a = X e_a, q_a = Y e_a attains 5*4 = 20 in every family member",
          5 * min(table["matched"]) == 20)

    print("== Part D: every rank-5 realisation of D5 is edge-supported (Theorem D, constructive replay) ==")
    d1 = [F(k + 2, 3) * (-1) ** k for k in range(v5)]
    d2 = [F(5, k + 1) for k in range(v5)]
    inst = [("pt%d scaled" % (k + 1), scaled(mat(*d5_family(par)), d1, d2)) for k, par in enumerate(D5_POINTS.values())]
    inst.append(("Gram scaled", scaled([[F(x) for x in row] for row in G5], d1, d2)))
    Xbd, Ybd = boundary_member()
    inst.append(("boundary member (x_01+ = e_0)", mat(Xbd, Ybd)))
    for name, M in inst:
        Xn, Yn = d5_normal_form(M)
        dx = [w for w in classes if rank_frac([Xn[t] for t in range(v5) if w >> t & 1]) < 5]
        dy = [w for w in classes if rank_frac([Yn[t] for t in range(v5) if w >> t & 1]) < 5]
        Rx = {a: [t for t in range(v5) if Xn[t][a] != 0] for a in range(5)}
        Ay = {a: [t for t in range(v5) if Yn[t][a] != 0] for a in range(5)}
        tab = ({bd_block_rank(G5, Rx[a], Ay[a]) for a in range(5)},
               {bd_block_rank(G5, Rx[a], Ay[b]) for a in range(5) for b in range(5) if a != b})
        check("Theorem D construction replayed on %s: W_e, triangles, L_a, dual pairing, edge-supported; "
              "deficient classes = axis classes; actual R(e_a), A(e_b) ranks matched 4 / unmatched 3" % name,
              sorted(dx) == sorted(dy) == sorted(w for w, _ in missing) and tab == ({4}, {3}), str(tab))
    ups = [tangent_upper_rational(*d5_family(par), pairs5) for par in D5_POINTS.values()]
    ups.append(tangent_upper_rational(Xbd, Ybd, pairs5))
    check("D5 tangent upper bound 55 also at pt1-3 and at the boundary member (consistent with Theorem D: "
          "smooth points of one 55-dimensional component)", ups == [55, 55, 55, 55], str(ups))

    print("== Controls (dimension changes / non-rigid units) ==")
    X4, Y4 = dn_unit(4)
    r4 = rigidity_report("D4", X4, Y4)
    f4 = rank_frac(family_tangent_vectors(4) + orbit_tangent_vectors(mat(X4, Y4)))
    e4 = tangent_exact(X4, Y4, orth_pairs(mat(X4, Y4)))
    check("D4 control (has a 4-frame): tangent 44 > orbit 23 (not rigid; exact Fraction rank); "
          "edge family + orbit spans exactly 32 (exact)",
          r4["upper"] == [44] and e4 == 44 and r4["orbit"] == 23 and f4 == 32, "family+orbit span %d" % f4)
    X6d, Y6d = dn_unit(6)
    r6 = rigidity_report("D6", X6d, Y6d)
    f6 = rank_mod(family_tangent_vectors(6) + orbit_tangent_vectors(mat(X6d, Y6d)), 900, P1)
    check("D6 control: tangent 84 = 59 + 25, all realised by the edge family (30 params - 5 torus)",
          r6["upper"] == [84] and r6["orbit"] == 59 and f6 == 84, "family+orbit span %d" % f6)
    if "--skip-e7" not in argv:
        X7, Y7 = simple_root_unit("E", 7)
        r7 = rigidity_report("E7", X7, Y7)
        check("E7 control: tangent 125 = 2v-1 (rigid at first order)", r7["upper"] == [125] and r7["orbit"] == 125,
              "%.1fs" % r7["secs"])
    if "--e8" in argv:
        X8, Y8 = simple_root_unit("E", 8)
        r8 = rigidity_report("E8", X8, Y8)
        check("E8 control: tangent 239 = 2v-1", r8["upper"] == [239] and r8["orbit"] == 239)

    print("== Negative controls (each must FAIL the corresponding acceptance test) ==")
    # Removing a single orthogonal pair leaves E6 first-order rigid (checked
    # below), so the perturbation that must break rigidity removes all 15
    # orthogonality constraints of line 0 (row and column).  (Partial removals
    # at line 0 were explored in scratch only; the outcome depends on the
    # removal order and is NOT certified here.)
    one = rigidity_report("E6-minus-one-pair", X6, Y6, drop={orth_pairs(G6)[0]})
    check("E6 robustness: one orthogonal pair removed, still 71", one["upper"] == [71])
    drop0 = {(0, s) for s in range(36) if s != 0 and G6[0][s] == 0}
    rn = rigidity_report("E6-line0-unconstrained", X6, Y6, drop=drop0)
    neg1 = rn["upper"][0] == rn["orbit"]
    # exact lower bound: orbit + free first-order moves of x_0 and y_0 (dX = E_0 u, dY = E_0 w);
    # these vectors vanish on every remaining constrained pair because no pair involves line 0.
    free0 = [[(Y6[s][a] if t == 0 else 0) for t in range(36) for s in range(36)] for a in range(6)]
    free0 += [[(X6[t][a] if s == 0 else 0) for t in range(36) for s in range(36)] for a in range(6)]
    pairs_rn = orth_pairs(G6, drop0)
    low_rn = rank_mod(orbit_tangent_vectors(G6) + free0, 36 * 36, P1)
    check("NEG E6 pattern with the 15 orthogonality constraints of line 0 removed: rigidity certificate fails; "
          "tangent exactly 81 > 71 (prime upper bound 81 matched by orbit + free line-0 moves, prime lower bound 81)",
          not neg1 and rn["upper"] == [81] and low_rn == 81 and all(in_pattern(z, 36, pairs_rn) for z in free0),
          "tangent upper %d, explicit lower %d, orbit %d" % (rn["upper"][0], low_rn, rn["orbit"]))
    rd = rigidity_report("D5-minus-one-pair", X5, Y5, drop={orth_pairs(G5)[0]})
    ed = tangent_exact(X5, Y5, orth_pairs(G5, {orth_pairs(G5)[0]}))
    check("NEG D5 pattern with one orthogonal pair removed: tangent exactly 57 != 55 (exact Fraction rank)",
          rd["upper"] == [57] and ed == 57)
    Xb, Yb = d5_family(D5_POINTS["pt1"], sign_bug=True)
    Mb = mat(Xb, Yb)
    check("NEG D5 family with sign error in y_{ij-} violates the pattern zeros",
          not all(Mb[t][s] == 0 for t, s in pairs5))
    bad = {e: (F(2), F(-2)) if e == (0, 1) else (F(1), F(1)) for e in D5_EDGES}
    Xc, Yc = d5_family(bad)
    Mc = mat(Xc, Yc)
    extra = [w for w in classes if rank_frac([Xc[t] for t in range(v5) if w >> t & 1]) < 5]
    check("NEG inadmissible a=-b on edge 01: zero diagonal entry and extra deficient classes",
          any(Mc[t][t] == 0 for t in range(v5)) and len(extra) > 5, "%d deficient classes" % len(extra))
    a_only = rank_frac(fam[0::2] + orbit5)
    check("NEG half family (b frozen, 10 a-directions) + orbit spans < 55 (exact Fraction rank): "
          "the lower bound is not automatic",
          a_only < 55, "span %d" % a_only)

    Mbad = mat(*d5_family(D5_POINTS["pt2"]))
    t1, s1 = pairs5[0]
    Xq, Yq = d5_family(D5_POINTS["pt2"])
    Yq[s1] = [y + (F(1) if i == 2 else 0) for i, y in enumerate(Yq[s1])]   # breaks M_{t1 s1} = 0 only
    Mbad = mat(Xq, Yq)
    broke = sum(1 for t, s in pairs5 if Mbad[t][s] != 0)
    try:
        d5_normal_form(Mbad, check_pattern=False)
        failed = False
    except AssertionError:
        failed = True
    check("NEG Theorem D construction on a rank-5 non-realisation (%d orthogonal zeros broken) fails" % broke,
          failed and broke > 0)
    print("ALL %d CHECKS PASSED in %.1fs" % (len(CHECKS), time.time() - t_start))


if __name__ == "__main__":
    main(sys.argv[1:])
