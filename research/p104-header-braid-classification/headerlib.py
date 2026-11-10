"""Exact helpers for the saturated-header classification (Python 3.12, standard library only).

Conventions.  A unit is U = I - 2 x y with y x = 0 (x a column, y a row).  A tuple (U_0,...,U_n) acts with U_0 first:
J = U_n ... U_0.  Gram G_ij = y_i x_j.  Matrices are lists of rows of int or Fraction.
"""
from fractions import Fraction as Q


def sgn(a):
    return (a > 0) - (a < 0)


def eye(n):
    return [[Q(int(i == j)) for j in range(n)] for i in range(n)]


def mul(A, B):
    Bt = list(zip(*B))
    return [[sum(p * q for p, q in zip(r, c) if p and q) for c in Bt] for r in A]


def mv(A, v):
    return [sum(p * q for p, q in zip(r, v) if p and q) for r in A]


def vm(v, A):
    return [sum(v[i] * A[i][j] for i in range(len(v)) if v[i]) for j in range(len(A[0]))]


def dot(a, b):
    return sum(p * q for p, q in zip(a, b))


def transpose(A):
    return [list(r) for r in zip(*A)]


def unit(x, y, c=-2):
    n = len(x)
    return [[Q(int(i == j)) + c * x[i] * y[j] for j in range(n)] for i in range(n)]


def product(tuples):
    """J = U_n ... U_0 for tuples [(x,y),...] listed from the first-acting unit."""
    n = len(tuples[0][0])
    J = eye(n)
    for x, y in tuples:
        J = mul(unit(x, y), J)
    return J


def is_scalar(M, c):
    n = len(M)
    return all(M[i][j] == (c if i == j else 0) for i in range(n) for j in range(n))


def gram(tuples):
    return [[dot(yi, xj) for (xj, _) in tuples] for (_, yi) in tuples]


def sign_gram(N):
    return [[sgn(i - j) for j in range(N)] for i in range(N)]


def is_header(tuples):
    """Saturated header: n+1 units on F^n, y_t x_t = 0, product -I."""
    n = len(tuples[0][0])
    return (len(tuples) == n + 1 and all(dot(y, x) == 0 for x, y in tuples)
            and is_scalar(product(tuples), -1))


def is_normalised(tuples):
    return is_header(tuples) and gram(tuples) == sign_gram(len(tuples))


def rank(M):
    A = [[Q(v) for v in r] for r in M]
    r = 0
    for c in range(len(A[0]) if A else 0):
        p = next((i for i in range(r, len(A)) if A[i][c]), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        f = A[r][c]
        A[r] = [v / f for v in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c]:
                g = A[i][c]
                A[i] = [u - g * v for u, v in zip(A[i], A[r])]
        r += 1
    return r


def solve(A, B):
    """Solve A X = B exactly (A square invertible); returns X."""
    n = len(A)
    M = [[Q(v) for v in A[i]] + [Q(v) for v in B[i]] for i in range(n)]
    for c in range(n):
        p = next(i for i in range(c, n) if M[i][c])
        M[c], M[p] = M[p], M[c]
        f = M[c][c]
        M[c] = [v / f for v in M[c]]
        for i in range(n):
            if i != c and M[i][c]:
                g = M[i][c]
                M[i] = [u - g * v for u, v in zip(M[i], M[c])]
    return [r[n:] for r in M]


def inverse(A):
    return solve(A, eye(len(A)))


# ---- the frame S_n and the canonical root -------------------------------------------------------------------
def S_matrix(n):
    return [[sgn(j - i) for j in range(n)] for i in range(n)]


def canonical(n):
    """Saturated normalised header in the frame Omega = S_n (y_t = x_t^T S_n).

    Path basis d_s = e_s - e_{s+1} (s < n-1), d_{n-1} = e_{n-1}; x_0 = sum of d_s over odd s; x_{t+1} = x_t - d_t.
    """
    assert n % 2 == 0 and n >= 2
    d = []
    for s in range(n):
        v = [0] * n
        v[s] = 1
        if s < n - 1:
            v[s + 1] = -1
        d.append(v)
    x = [sum((d[s][i] for s in range(1, n, 2)), 0) for i in range(n)]
    S = S_matrix(n)
    out = []
    for t in range(n + 1):
        out.append(([Q(v) for v in x], [Q(v) for v in vm(x, S)]))
        if t < n:
            x = [x[i] - d[t][i] for i in range(n)]
    return out[::-1]


# ---- Hurwitz moves on normalised integer tuples ------------------------------------------------------------
def move(T, i, s):
    """Hurwitz move on a normalised tuple of integer (x, y) pairs, positions i, i+1; s = +1 or -1.

    s=+1: (U_i, U_{i+1}) -> (U_{i+1}, U_{i+1} U_i U_{i+1}^-1);  s=-1: -> (U_i^-1 U_{i+1} U_i, U_i); the product is unchanged.
    Signs of (x,y) are chosen so that the Gram stays the sign matrix (valid on normalised tuples)."""
    (xi, yi), (xj, yj) = T[i], T[i + 1]
    if s == 1:
        a = (list(xj), list(yj))
        b = ([2 * q - p for p, q in zip(xi, xj)], [2 * q - p for p, q in zip(yi, yj)])
    else:
        a = ([2 * p - q for p, q in zip(xi, xj)], [2 * p - q for p, q in zip(yi, yj)])
        b = (list(xi), list(yi))
    return T[:i] + [a, b] + T[i + 2:]


def key(T, m=None):
    """Gauge-free key: the matrices x y of the units (reduced mod m if given)."""
    out = []
    for x, y in T:
        out.append(tuple((p * q) % m if m else p * q for p in x for q in y))
    return tuple(out)


def int_canonical(n):
    return [([int(v) for v in x], [int(v) for v in y]) for x, y in canonical(n)]


def orbit_size_mod(T, m, limit=10**7):
    """Size of the orbit of the unit tuple T (integer normalised tuple) under all Hurwitz moves, units reduced mod m."""
    start = [([v % m for v in x], [v % m for v in y]) for x, y in T]
    k0 = key(start, m)
    seen = {k0}
    frontier = [start]
    while frontier:
        nxt = []
        for S in frontier:
            for i in range(len(S) - 1):
                for s in (1, -1):
                    S2 = move(S, i, s)
                    S2 = [([v % m for v in x], [v % m for v in y]) for x, y in S2]
                    k = key(S2, m)
                    if k not in seen:
                        seen.add(k)
                        nxt.append(S2)
                        if len(seen) > limit:
                            raise ValueError('orbit limit')
        frontier = nxt
    return len(seen)


# ---- chain-nested roots (a|b) --------------------------------------------------------------------------------
def chain_root(a, b):
    """Chain (a|b): fields A=0, f_0..f_{a-1}, h_0..h_{b-1}, one empty field E when 1+a+b is odd.
    Left unit i: x = A + f_i + 2 sum_{j<i} f_j, y = A* - f_i*.  Right unit m: x = -A + h_m + 2 sum_{l>m} h_l, y = A* + h_m*.
    Between them the 'thin' units (closed forms below).  Returned as integer (x,y) pairs in word order."""
    nf = 1 + a + b
    e = nf % 2
    n = nf + e
    A = 0
    f = list(range(1, 1 + a))
    h = list(range(1 + a, 1 + a + b))
    E = nf if e else None

    def vec():
        return [0] * n

    out = []
    for i in range(a):
        x, y = vec(), vec()
        x[A] = 1
        x[f[i]] = 1
        for j in range(i):
            x[f[j]] = 2
        y[A] = 1
        y[f[i]] = -1
        out.append((x, y))

    def thin(al, u, p=0, q=0):
        x, y = vec(), vec()
        x[A], y[A] = al, u
        for i, j in enumerate(f):
            x[j], y[j] = al + 1, (1 - u) * (-1) ** i
        for r, j in enumerate(reversed(h)):
            x[j], y[j] = 1 - al, (u - 1) * (-1) ** r
        if E is not None:
            x[E], y[E] = q, p
        return x, y

    pa, pb = a % 2, b % 2
    if pa and pb:
        th = [thin(0, 1, 0, 1), thin(-1, 2, 1, 0), thin(-1, 3, 1, -1)]
    elif not pa and not pb:
        th = [thin(0, 1, 0, 1), thin(-1, 0, 1, 0), thin(-1, -1, 1, -1)]
    elif pa:
        th = [thin(0, 1), thin(-1, 0)]
    else:
        th = [thin(0, 1), thin(1, 2)]
    out += th
    for m in range(b):
        x, y = vec(), vec()
        x[A] = -1
        x[h[m]] = 1
        for l in range(m + 1, b):
            x[h[l]] = 2
        y[A] = 1
        y[h[m]] = 1
        out.append((x, y))
    return out


def qt(T):
    return [([Q(v) for v in x], [Q(v) for v in y]) for x, y in T]


def sixsix_root(path):
    """The 8-field, 9-query root of the #6726 caller from its ROOT.json; units are I - 2 R with R the stored query."""
    import json
    d = json.load(open(path))
    n = d['fields'] if isinstance(d['fields'], int) else len(d['fields'])
    T = []
    for R in d['queries']:
        R = [[Q(v) for v in r] for r in R]
        i = next(i for i in range(n) if any(R[i]))
        j = next(j for j in range(n) if R[i][j])
        y = [R[i][k] for k in range(n)]
        x = [R[k][j] / R[i][j] for k in range(n)]
        T.append((x, y))
    N = len(T)
    G = [[dot(T[i][1], T[j][0]) for j in range(N)] for i in range(N)]
    e = [1] * N
    for j in range(1, N):
        e[j] = -G[0][j] * e[0]
    if not all(e[i] * e[j] * G[i][j] == sgn(i - j) for i in range(N) for j in range(N)):
        raise ValueError('not a sign-Gram header after unit signs')
    out = []
    for t in range(N):
        x = [e[t] * v for v in T[t][0]]
        y = [e[t] * v for v in T[t][1]]
        if any(v.denominator != 1 for v in x + y):
            raise ValueError('not integral')
        out.append(([int(v) for v in x], [int(v) for v in y]))
    return out


# ---- frames and literal words --------------------------------------------------------------------------------
def omega_of(T):
    """The skew form Omega with y_t = x_t^T Omega (exists and is unique for a normalised header)."""
    n = len(T[0][0])
    X = [[Q(v) for v in T[t][0]] for t in range(n)]
    Y = [[Q(v) for v in T[t][1]] for t in range(n)]
    Om = solve(X, Y)
    if not all(Om[a][b] == -Om[b][a] for a in range(n) for b in range(n)):
        raise ValueError('Omega not skew')
    xn, yn = T[n]
    if vm([Q(v) for v in xn], Om) != [Q(v) for v in yn]:
        raise ValueError('last unit inconsistent with Omega')
    return Om


def s_frames(T):
    """All signed relabelings of the fields (one per choice of first field) that bring Omega to S_n; returns tuples."""
    n = len(T[0][0])
    Om = omega_of(T)
    S = S_matrix(n)
    out = []
    for a in range(n):
        if any(abs(Om[a][b]) != 1 for b in range(n) if b != a):
            return []
        e = [Om[a][b] if b != a else 1 for b in range(n)]
        Op = [[e[i] * e[j] * Om[i][j] for j in range(n)] for i in range(n)]
        order = sorted(range(n), key=lambda b: (b != a, -sum(1 for c in range(n) if c != b and Op[b][c] == 1)))
        if all(Op[order[i]][order[j]] == S[i][j] for i in range(n) for j in range(n)):
            out.append([([int(e[order[k]] * x[order[k]]) for k in range(n)],
                         [int(e[order[k]] * y[order[k]]) for k in range(n)]) for x, y in T])
    return out


def mod2_multiset(T):
    return sorted(tuple(v % 2 for v in x) for x, _ in T)


def apply_word(T, word):
    for i, s in word:
        T = move(T, i, s)
    return T


def shortest_word(T1, T2, max_len=12):
    """Shortest Hurwitz word T1 -> T2 (list of (position, +-1)) by growing breadth-first balls around both ends.

    The length is exact: a word of length L exists iff balls of radii ceil(L/2) and floor(L/2) meet, and the balls are
    grown one radius at a time, so when they first meet the length is minimal.  None if nothing within max_len."""
    ka, kb = key(T1), key(T2)
    if ka == kb:
        return 0, []
    A, B = {ka: []}, {kb: []}
    fa, fb = {ka: T1}, {kb: T2}
    ra = rb = 0
    while ra + rb < max_len:
        grow_a = len(fa) <= len(fb)
        S, O, F = (A, B, fa) if grow_a else (B, A, fb)
        nxt = {}
        for k, S1 in F.items():
            for i in range(len(S1) - 1):
                for s in (1, -1):
                    S2 = move(S1, i, s)
                    k2 = key(S2)
                    if k2 in S:
                        continue
                    S[k2] = S[k] + [(i, s)]
                    nxt[k2] = S2
        if grow_a:
            fa, ra = nxt, ra + 1
        else:
            fb, rb = nxt, rb + 1
        hit = [k for k in nxt if k in O]
        if hit:
            k = min(hit)
            w = A[k] + [(i, -s) for (i, s) in reversed(B[k])]
            return len(w), w
    return None
