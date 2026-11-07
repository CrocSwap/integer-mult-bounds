#!/usr/bin/env python3
"""Exact checks for the root hub forcing theorem.  Python 3.12, standard library only (Fractions, own Laurent polynomials).

Run:  python3 -I -B research/p104-root-hub-forcing/check.py
Marker: PASS_P104_ROOT_HUB_FORCING

Conventions: the word is S_N T_N ... S_1 T_1 with later events on the LEFT; a stage's scaling piece sits after its shear.
The chain data below are the shear vectors (x_k, y_k) and masks of the 1|1 and 2|2 chain-nested roots (the family of the root of #6833,
shortest two members); thin shears have mask None.  Everything else is recomputed here.
"""
import itertools
import random
import sys
from fractions import Fraction as F

# ------------------------------------------------------------------ Laurent polynomials: dict {exponent tuple: Fraction}
def pc(c, nv):
    return {(0,) * nv: F(c)} if c else {}

def pv(i, nv, e=1):
    k = [0] * nv
    k[i] = e
    return {tuple(k): F(1)}

def padd(a, b):
    r = dict(a)
    for k, v in b.items():
        s = r.get(k, 0) + v
        if s:
            r[k] = s
        else:
            r.pop(k, None)
    return r

def pmul(a, b):
    r = {}
    for ka, va in a.items():
        for kb, vb in b.items():
            k = tuple(x + y for x, y in zip(ka, kb))
            s = r.get(k, 0) + va * vb
            if s:
                r[k] = s
            else:
                r.pop(k, None)
    return r

def pscale(a, c):
    return {k: v * c for k, v in a.items()} if c else {}

def pinv_mono(a):
    require(len(a) == 1, "not a monomial")
    (k, v), = a.items()
    return {tuple(-x for x in k): 1 / v}

def peval(a, pt):
    tot = F(0)
    for k, v in a.items():
        t = v
        for x, e in zip(pt, k):
            t *= F(x) ** e
        tot += t
    return tot

def require(ok, msg):
    if not ok:
        raise ValueError(msg)

# ------------------------------------------------------------------ matrices of polynomials (list of rows)
def mlift(A, nv):
    return [[pc(x, nv) for x in row] for row in A]

def mzero(r, c):
    return [[{} for _ in range(c)] for _ in range(r)]

def meye(n, nv):
    return [[pc(1 if i == j else 0, nv) for j in range(n)] for i in range(n)]

def mmul(A, B):
    r, k, c = len(A), len(B), len(B[0])
    out = mzero(r, c)
    for i in range(r):
        for l in range(k):
            if not A[i][l]:
                continue
            for j in range(c):
                if B[l][j]:
                    out[i][j] = padd(out[i][j], pmul(A[i][l], B[l][j]))
    return out

def madd(A, B):
    return [[padd(a, b) for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]

def mscal(A, p):
    return [[pmul(a, p) for a in row] for row in A]

def mequal(A, B):
    return all(a == b for ra, rb in zip(A, B) for a, b in zip(ra, rb))

def cmat(A):  # constant matrix of Fractions -> Fractions
    return [[F(x) for x in row] for row in A]

def cmul(A, B):
    return [[sum(A[i][l] * B[l][j] for l in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]

def ctr(A):
    return [list(r) for r in zip(*A)]

def cid(n):
    return [[F(1 if i == j else 0) for j in range(n)] for i in range(n)]

def cinv(A):
    n = len(A)
    M = [[F(x) for x in row] + [F(1 if i == j else 0) for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None:
            raise ZeroDivisionError("singular")
        M[c], M[p] = M[p], M[c]
        pv_ = M[c][c]
        M[c] = [x / pv_ for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [row[n:] for row in M]

def crank(A):
    M = [list(map(F, r)) for r in A]
    rk = 0
    cols = len(M[0]) if M else 0
    for c in range(cols):
        p = next((r for r in range(rk, len(M)) if M[r][c] != 0), None)
        if p is None:
            continue
        M[rk], M[p] = M[p], M[rk]
        for r in range(len(M)):
            if r != rk and M[r][c] != 0:
                f = M[r][c] / M[rk][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[rk])]
        rk += 1
    return rk

def pdet(A):
    """determinant of a polynomial matrix by DP over column subsets (small n)"""
    n = len(A)
    memo = {0: None}
    def rec(row, cols):  # cols: frozenset of remaining columns, row index = n-len(cols)
        if row == n:
            return {(): F(1)}
        if (row, cols) in memo:
            return memo[(row, cols)]
        tot = {}
        for pos, c in enumerate(sorted(cols)):
            if not A[row][c]:
                continue
            sub = rec(row + 1, cols - {c})
            term = {}
            for k, v in A[row][c].items():
                for k2, v2 in sub.items():
                    kk = tuple(x + y for x, y in zip(k, k2)) if k2 != () else k
                    term[kk] = term.get(kk, 0) + v * v2
            if pos % 2:
                term = {k: -v for k, v in term.items()}
            tot = padd(tot, {k: v for k, v in term.items() if v})
        memo[(row, cols)] = tot
        return tot
    return rec(0, frozenset(range(n)))

# ------------------------------------------------------------------ chain data: (x, y, mask or None) for shears 1..N
CHAIN = {
    (1, 1): (4, [
        ([1, 1, 0, 0], [1, -1, 0, 0], [0, 1]),
        ([0, 1, 1, 1], [1, 0, 0, 0], None),
        ([-1, 0, 2, 0], [2, -1, 1, 1], None),
        ([-1, 0, 2, -1], [3, -2, 2, 1], None),
        ([-1, 0, 1, 0], [1, 0, 1, 0], [0, 2]),
    ]),
    (2, 2): (6, [
        ([1, 1, 0, 0, 0, 0], [1, -1, 0, 0, 0, 0], [0, 1]),
        ([1, 2, 1, 0, 0, 0], [1, 0, -1, 0, 0, 0], [0, 1, 2]),
        ([0, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0], None),
        ([-1, 0, 0, 2, 2, 0], [0, 1, -1, 1, -1, 1], None),
        ([-1, 0, 0, 2, 2, -1], [-1, 2, -2, 2, -2, 1], None),
        ([-1, 0, 0, 1, 2, 0], [1, 0, 0, 1, 0, 0], [0, 3, 4]),
        ([-1, 0, 0, 0, 1, 0], [1, 0, 0, 0, 1, 0], [0, 4]),
    ]),
}
# determinant of the matrix M(D) built in Lemma M (normalisation M(1) = I), a monomial unit; exponents indexed by shear position
DET_EXPECT = {(1, 1): (F(1), (2, 0, 0, 0, 0)), (2, 2): (F(1), (4, 3, 0, 0, 0, 0, 0))}


def chain_checks(key):
    n, Q = CHAIN[key]
    N = len(Q)
    require(N == n + 1, "saturation N = n+1")
    X = [q[0] for q in Q]
    Y = [q[1] for q in Q]
    masks = [set(q[2]) if q[2] is not None else None for q in Q]
    thick = [k for k in range(N) if masks[k] is not None]
    for k in range(N):
        require(sum(a * b for a, b in zip(Y[k], X[k])) == 0, "y_k x_k = 0")
        if masks[k] is not None:  # atomic LOCAL: x_k, y_k live on the mask
            require(all(X[k][f] == 0 and Y[k][f] == 0 for f in range(n) if f not in masks[k]), "x,y inside mask")
    nv = N
    def lam_exp(j, i, f):  # exponent vector of the diagonal entry f of Lam_(j,i) = product of the scalings in gaps j..i-1
        e = [0] * nv
        for k in range(j, i):
            if masks[k] is not None and f in masks[k]:
                e[k] += 1
        return tuple(e)
    def Dm(k):
        return [[(pv(k, nv) if (masks[k] is not None and i == j and i in masks[k]) else pc(1 if i == j else 0, nv)) if i == j else {}
                 for j in range(n)] for i in range(n)]
    T = [[[(F(1 if i == j else 0) - 2 * X[k][i] * Y[k][j]) for j in range(n)] for i in range(n)] for k in range(N)]
    # replay: W(D) = -D^w at Q=-1, W(+1) = D^w
    W = meye(n, nv)
    W1 = meye(n, nv)
    for k in range(N):
        W = mmul(Dm(k), mmul(mlift(T[k], nv), W))
        W1 = mmul(Dm(k), W1)
    tgt = []
    for f in range(n):
        e = [0] * nv
        for k in thick:
            if f in masks[k]:
                e[k] = 1
        tgt.append(tuple(e))
    ok_minus = all(W[i][j] == ({tgt[i]: F(-1)} if i == j else {}) for i in range(n) for j in range(n))
    ok_plus = all(W1[i][j] == ({tgt[i]: F(1)} if i == j else {}) for i in range(n) for j in range(n))
    require(ok_minus and ok_plus, "replay W(-1) = -D^w, W(+1) = D^w")
    # monomial Gram, g_ij g_ji = -1, additivity, beta pattern
    def g(i, j):   # y_i Lam(j,i) x_j  (i>j)
        r = {}
        for f in range(n):
            c = F(Y[i][f] * X[j][f])
            if c:
                r = padd(r, {lam_exp(j, i, f): c})
        return r
    def gi(j, i):  # y_j Lam(j,i)^-1 x_i
        r = {}
        for f in range(n):
            c = F(Y[j][f] * X[i][f])
            if c:
                r = padd(r, {tuple(-x for x in lam_exp(j, i, f)): c})
        return r
    mono = True
    prod_ok = True
    for i in range(N):
        for j in range(i):
            a, b = g(i, j), gi(j, i)
            mono &= len(a) == 1
            prod_ok &= pmul(a, b) == pc(-1, nv)
    require(mono, "every g_ij (i>j) is a monomial")
    require(prod_ok, "g_ij g_ji = -1")
    expo = {(i, j): next(iter(g(i, j))) for i in range(N) for j in range(i)}
    add_ok = all(
        tuple(sum(expo[(k + 1, k)][t] for k in range(j, i)) for t in range(nv)) == expo[(i, j)]
        for i in range(N) for j in range(i))
    require(add_ok, "exponents additive")
    sgn = {(i, j): next(iter(g(i, j).values())) for i in range(N) for j in range(i)}
    beta_ok = all(expo[(i, j)][m] == (1 if j <= m < i else 0) for i in range(N) for j in range(i) for m in thick)
    require(beta_ok, "beta^m_ij = [j <= p_m < i]")
    # top coefficient and common carrier
    Sin = [k for k in thick if k <= N - 2]
    top = tuple(1 if k in Sin else 0 for k in range(nv))
    gN1 = g(N - 1, 0)
    require(list(gN1) == [top], "g_N1 = c prod_{S_in} D_m")
    c = gN1[top]
    inter = set(range(n))
    for k in Sin:
        inter &= masks[k]
    carrier = {f for f in inter if Y[N - 1][f] * X[0][f] != 0}
    cform = sum(F(Y[N - 1][f] * X[0][f]) for f in inter)
    allmask = set(range(n))
    for k in thick:
        allmask &= masks[k]
    require(c != 0 and c == cform, "top coefficient = sum over common coordinates of y_N x_1")
    require(carrier and carrier <= allmask, "carrier lies in every mask")
    # beta^{m(N)}_{N1} = 0 directly: y_N = y_N E_loc, so y_N F = 0 for the other pieces of m(N); here m(N) is single-piece
    require(N - 1 in thick and (N - 1) not in Sin, "m(N) is outside S_in")
    print("chain (%d|%d) n=%d N=%d: replay ok; all %d Gram entries monomial, g_ij g_ji=-1, additive, beta pattern; "
          "g_N1 = %s * prod D_m (m in %s), carrier %s, every-mask set %s"
          % (key[0], key[1], n, N, N * (N - 1) // 2, c, ["D%d" % k for k in Sin], sorted(carrier), sorted(allmask)))
    return n, N, X, Y, masks, thick, T, lam_exp, g, gi


def lemma_M(key):
    n, N, X, Y, masks, thick, T, lam_exp, g, gi = chain_checks(key)
    nv = N
    def lam_diag(k):  # Lam_<k as list of monomial polys
        return [{lam_exp(0, k, f): F(1)} for f in range(n)]
    Tp = []
    for k in range(N):
        L = lam_diag(k)
        Tp.append([[pmul(pmul(pinv_mono(L[a]), pc(T[k][a][b], nv)), L[b]) if T[k][a][b] != 0 else {} for b in range(n)] for a in range(n)])
    P = meye(n, nv)
    for k in range(N):
        P = mmul(Tp[k], P)
    require(mequal(P, [[pc(-1 if i == j else 0, nv) for j in range(n)] for i in range(n)]), "master identity prod T' = -I")
    # primed Gram
    xp = [[pmul(pinv_mono(lam_diag(k)[f]), pc(X[k][f], nv)) if X[k][f] != 0 else {} for f in range(n)] for k in range(N)]
    yp = [[pmul(lam_diag(k)[f], pc(Y[k][f], nv)) if Y[k][f] != 0 else {} for f in range(n)] for k in range(N)]
    def gram(Xs, Ys):
        G = mzero(N, N)
        for i in range(N):
            for j in range(N):
                s = {}
                for f in range(n):
                    if Ys[i][f] and Xs[j][f]:
                        s = padd(s, pmul(Ys[i][f], Xs[j][f]))
                G[i][j] = s
        return G
    G0 = gram([[pc(v, nv) for v in x] for x in X], [[pc(v, nv) for v in y] for y in Y])
    Gp = gram(xp, yp)
    def Zof(G):
        return [[padd(pc(1 if i == j else 0, nv), padd(pscale(G[i][j], 2) if i > j else {}, {k: -v for k, v in G[i][j].items()}))
                 for j in range(N)] for i in range(N)]
    Z0, Zp = Zof(G0), Zof(Gp)
    def rank1(Z):
        return all(padd(pmul(Z[i][j], Z[k][l]), {kk: -v for kk, v in pmul(Z[i][l], Z[k][j]).items()}) == {}
                   for i in range(N) for k in range(i + 1, N) for j in range(N) for l in range(j + 1, N))
    require(rank1(Z0) and rank1(Zp), "Z has rank one")
    d = []
    for i in range(N):
        z0 = Z0[i][0][(0,) * nv]
        require(len(Zp[i][0]) == 1, "Z'_i0 monomial")
        (k, v), = Zp[i][0].items()
        d.append({k: v / z0})
    Delta_inv = [pinv_mono(x) for x in d]
    conj = all(Gp[i][j] == pmul(pmul(d[i], G0[i][j]), Delta_inv[j]) for i in range(N) for j in range(N))
    require(conj, "G' = Delta G Delta^-1")
    # M from the factorisation: Xt = Xp Delta = M X
    Xm = [[F(X[k][f]) for k in range(N)] for f in range(n)]
    Ym = [[F(Y[k][f]) for f in range(n)] for k in range(N)]
    Cc = cmul(ctr(Xm), cinv(cmul(Xm, ctr(Xm))))
    Xt = [[pmul(xp[k][f], d[k]) for k in range(N)] for f in range(n)]
    Mm = mmul(Xt, mlift(Cc, nv))
    require(mequal(mmul(Mm, mlift(Xm, nv)), Xt), "Xt = M X")
    Yt = [[pmul(Delta_inv[k], yp[k][f]) if yp[k][f] else {} for f in range(n)] for k in range(N)]
    require(mequal(mmul(Yt, Mm), mlift(Ym, nv)), "Yt M = Y  (Yt = Y M^-1)")
    require(all(mequal(mmul(Tp[k], Mm), mmul(Mm, mlift(T[k], nv))) for k in range(N)), "T'_j M = M T_j for all j")
    det = pdet(Mm)
    require(len(det) == 1, "det M monomial")
    (dk, dv), = det.items()
    require((dv, dk) == DET_EXPECT[key], "det M pinned value")
    one = [[peval(Mm[i][j], [1] * nv) for j in range(n)] for i in range(n)]
    s = one[0][0]
    require(all(one[i][j] == (s if i == j else 0) for i in range(n) for j in range(n)) and s == 1, "M(1) = I")
    # uniqueness (generic): at a random rational point the solution space of T'_j M = M T_j is already 1-dimensional,
    # and the generic dimension is at most the specialised one
    rng = random.Random(3)
    pt = [F(rng.randint(2, 9), rng.randint(2, 9)) for _ in range(nv)]
    rows = []
    for k in range(N):
        Tn = [[peval(Tp[k][a][b], pt) for b in range(n)] for a in range(n)]
        for a in range(n):
            for b in range(n):
                row = [F(0)] * (n * n)
                for c_ in range(n):
                    row[c_ * n + b] += Tn[a][c_]
                    row[a * n + c_] -= F(T[k][c_][b])
                rows.append(row)
    dim = n * n - crank(rows)
    require(dim == 1, "solution space one-dimensional")
    print("Lemma M chain (%d|%d): Z rank 1, G'=Delta G Delta^-1, M with T'_j=M T_j M^-1 for all j (%d shears), det M = %s D^%s, M(1)=%s I, solution space dim %d"
          % (key[0], key[1], N, dv, dk, s, dim))


# ------------------------------------------------------------------ multilinear top coefficient formula
rng = random.Random(20261107)

def rand_invertible(n, lo=-3, hi=3):
    while True:
        B = [[F(rng.randint(lo, hi)) for _ in range(n)] for _ in range(n)]
        try:
            return B, cinv(B)
        except ZeroDivisionError:
            pass

def piece(B, Bi, cols):  # sum_c B[:,c] Bi[c,:]
    n = len(B)
    return [[sum(B[i][c] * Bi[c][j] for c in cols) for j in range(n)] for i in range(n)]

def window_poly(n, events, nv):
    L = meye(n, nv)
    for m, E in events:
        step = madd(meye(n, nv), [[pscale(pv(m, nv), E[i][j]) if E[i][j] else {} for j in range(n)] for i in range(n)])
        L = mmul(step, L)
    return L

def bil(y, A, x):
    n = len(A)
    return sum(y[i] * A[i][j] * x[j] for i in range(n) for j in range(n))

def top_coeff(events, Sin, y, x, n):
    nv = len(Sin)
    L = window_poly(n, events, nv)
    g = {}
    for i in range(n):
        for j in range(n):
            if y[i] and x[j] and L[i][j]:
                g = padd(g, pscale(L[i][j], y[i] * x[j]))
    return g.get(tuple([1] * nv), F(0))

def formula_c(events, Sin, y, x, n):
    by = {m: [i for i, (mm, _) in enumerate(events) if mm == m] for m in Sin}
    tot = F(0)
    for ch in itertools.product(*[by[m] for m in Sin]):
        tau = cid(n)
        for i in sorted(ch):
            tau = cmul(events[i][1], tau)
        tot += bil(y, tau, x)
    return tot

def check_formula():
    res = []
    for n in (4, 5):
        for _ in range(3):
            events = []
            for m, k in enumerate((2, 2, 3)):
                B, Bi = rand_invertible(n)
                cols = list(range(n))
                rng.shuffle(cols)
                for c in cols[:k]:
                    events.append((m, piece(B, Bi, [c])))
            rng.shuffle(events)
            y = [F(rng.randint(-3, 3)) for _ in range(n)]
            x = [F(rng.randint(-3, 3)) for _ in range(n)]
            c1 = top_coeff(events, [0, 1, 2], y, x, n)
            c2 = formula_c(events, [0, 1, 2], y, x, n)
            res.append(c1 == c2)
            noncomm = any(cmul(a[1], b[1]) != cmul(b[1], a[1]) for a in events for b in events if a[0] != b[0])
            require(noncomm, "random pieces do not commute")
    require(all(res), "top coefficient formula")
    print("multilinear formula: top coefficient == sum over one-piece-per-stage choices of y tau x, %d random non-commuting cases (n=4,5; stages with 2,2,3 pieces): all True" % len(res))

def proj(n, S):
    return [[F(1 if (i == j and i in S) else 0) for j in range(n)] for i in range(n)]

def check_h6a():
    def commuting(n, blocks, masks, split):
        while True:
            Rm = cid(n)
            for b in blocks:
                for i, fi in enumerate(b):
                    for j, fj in enumerate(b):
                        Rm[fi][fj] = F(rng.randint(-2, 2) + (3 if i == j else 0))
            try:
                Ri = cinv(Rm)
                break
            except ZeroDivisionError:
                pass
        ev = {}
        for m, parts in split.items():
            ev[m] = [cmul(Rm, cmul(proj(n, set(p)), Ri)) for p in parts]
            tot = [[sum(E[i][j] for E in ev[m]) for j in range(n)] for i in range(n)]
            require(tot == proj(n, masks[m]), "pieces of a stage sum to the coordinate mask projector")
            for a, A in enumerate(ev[m]):
                require(cmul(A, A) == A, "idempotent")
                for B in ev[m][a + 1:]:
                    require(cmul(A, B) == [[F(0)] * n for _ in range(n)], "orthogonal")
        return ev
    def run(name, n, blocks, masks, split, Sin, mN, expect_hubfree):
        ev = commuting(n, blocks, masks, split)
        events = [(m, E) for m in Sin for E in ev[m]]
        rng.shuffle(events)
        for a in events:  # H6a holds by construction
            for b in events:
                require(cmul(a[1], b[1]) == cmul(b[1], a[1]), "H6a")
        Mcap = cid(n)
        for m in Sin:
            Mcap = cmul(Mcap, proj(n, masks[m]))
        by = {m: [E for mm, E in events if mm == m] for m in Sin}
        # tau = Mcap tau Mcap for every choice, in the time order of the events
        for ch in itertools.product(*[[i for i, (mm, _) in enumerate(events) if mm == m] for m in Sin]):
            tau = cid(n)
            for i in sorted(ch):
                tau = cmul(events[i][1], tau)
            require(tau == cmul(Mcap, cmul(tau, Mcap)), "tau = Mcap tau Mcap under H6a")
        common = set.intersection(*[masks[m] for m in Sin + [mN]])
        nz = 0
        for _ in range(6):
            y = [F(rng.randint(-3, 3)) if i in masks[mN] else F(0) for i in range(n)]
            x = [F(rng.randint(-3, 3)) for _ in range(n)]
            c = top_coeff(events, Sin, y, x, n)
            if c != 0:
                nz += 1
                require(any(y[f] != 0 for f in common), "c != 0 forces a common coordinate with y_N(f) != 0")
        if expect_hubfree:
            require(not common and nz == 0, "hub-free commuting config has c = 0")
        else:
            require(common and nz > 0, "sensitivity: with a hub the top coefficient is nonzero")
        print("H6a %s n=%d: pieces commute, tau = Mcap tau Mcap for every choice; top coefficient nonzero in %d/6 draws; common coordinates %s" % (name, n, nz, sorted(common)))
    run("hub-free", 4, [[0, 1]], {0: {0, 1, 2}, 1: {0, 1, 3}, 2: {2, 3}},
        {0: [[0], [1, 2]], 1: [[1], [0, 3]], 2: [[2], [3]]}, [0, 1], 2, True)
    run("hub-free (three split stages)", 5, [[0, 1], [2, 3]], {0: {0, 1, 2, 3}, 1: {0, 1, 4}, 2: {2, 3, 4}, 3: {0, 1, 2, 3}},
        {0: [[0], [1, 2], [3]], 1: [[0], [1, 4]], 2: [[2], [3, 4]], 3: [[0, 1], [2, 3]]}, [0, 1, 2], 3, True)
    run("with hub", 4, [[0, 1]], {0: {0, 1, 2}, 1: {0, 1, 3}, 2: {0, 1}},
        {0: [[0], [1, 2]], 1: [[1], [0, 3]], 2: [[0], [1]]}, [0, 1], 2, False)

def check_h6a_violation():
    n = 4
    masks = {0: {0, 1, 2}, 1: {1, 2, 3}, 2: {0, 3}}
    common_all = set.intersection(*masks.values())
    require(not common_all, "masks hub-free")
    def pieces(S):
        idx = sorted(S)
        k = len(idx)
        B, Bi = rand_invertible(k, -2, 2)
        def emb(Mk):
            Z = [[F(0)] * n for _ in range(n)]
            for i, fi in enumerate(idx):
                for j, fj in enumerate(idx):
                    Z[fi][fj] = Mk[i][j]
            return Z
        return [emb(piece(B, Bi, [0])), emb(piece(B, Bi, [1, 2]))]
    for attempt in range(200):
        ev0, ev1 = pieces(masks[0]), pieces(masks[1])
        if all(cmul(a, b) == cmul(b, a) for a in ev0 for b in ev1):
            continue
        events = [(0, ev0[0]), (1, ev1[0]), (0, ev0[1]), (1, ev1[1])]
        y = [F(rng.randint(1, 4)) if i in masks[2] else F(0) for i in range(n)]
        x = [F(rng.randint(1, 4)) for _ in range(n)]
        c = top_coeff(events, [0, 1], y, x, n)
        if c == 0:
            continue
        Mcap = proj(n, masks[0] & masks[1])
        bad = 0
        for ch in itertools.product([0, 2], [1, 3]):
            tau = cid(n)
            for i in sorted(ch):
                tau = cmul(events[i][1], tau)
            if tau != cmul(Mcap, cmul(tau, Mcap)):
                bad += 1
        require(bad > 0, "some tau escapes Mcap")
        print("H6a violated control (n=4, masks %s hub-free): cross-stage pieces do not commute, top coefficient c = %s != 0, %d of 4 choices have tau != Mcap tau Mcap "
              "(the formula alone then forces no hub; not a counterexample, the master identity is not imposed)" % ([sorted(v) for v in masks.values()], c, bad))
        return
    raise ValueError("no violating control found")

def check_small_lemmas():
    # L2: the ab-coefficient of (I+aE2)(I+bM)(I+aE1) is E2 M + M E1 (later on the left); equals (E1+E2) M iff [M,E1]=0 when [M,E1+E2]=0
    k = 4
    E1 = [[F(rng.randint(-3, 3)) for _ in range(k)] for _ in range(k)]
    E2 = [[F(rng.randint(-3, 3)) for _ in range(k)] for _ in range(k)]
    M = [[F(rng.randint(-3, 3)) for _ in range(k)] for _ in range(k)]
    # polynomial in (a,b): coefficient extraction
    nv = 2
    def step(v, E):
        return madd(meye(k, nv), [[pscale(pv(v, nv), E[i][j]) if E[i][j] else {} for j in range(k)] for i in range(k)])
    Wm = mmul(step(0, E2), mmul(step(1, M), step(0, E1)))
    ab = [[Wm[i][j].get((1, 1), F(0)) for j in range(k)] for i in range(k)]
    expect = [[cmul(E2, M)[i][j] + cmul(M, E1)[i][j] for j in range(k)] for i in range(k)]
    require(ab == expect, "ab coefficient = E2 M + M E1")
    # L2 consequence (triangle, n=4): E1 supported on M_P={a,b,d}={0,1,3} commuting with M_R=diag(1,0,1,0) is block diag {0}+{1,3}; then y_R E1 x_Q = 0
    ok = True
    for _ in range(20):
        E = [[F(0)] * 4 for _ in range(4)]
        E[0][0] = F(rng.randint(-3, 3))
        for i in (1, 3):
            for j in (1, 3):
                E[i][j] = F(rng.randint(-3, 3))
        MR = proj(4, {0, 2})
        require(cmul(E, MR) == cmul(MR, E), "E commutes with M_R")
        yR = [F(rng.randint(-3, 3)), F(0), F(rng.randint(-3, 3)), F(0)]
        xQ = [F(0), F(rng.randint(-3, 3)), F(rng.randint(-3, 3)), F(0)]
        ok &= bil(yR, E, xQ) == 0
    require(ok, "triangle: y_R E1 x_Q = 0")
    # beta^{m(N)}_{N1} = 0 directly: y_N E_loc = y_N and the other pieces F of m(N) are orthogonal to E_loc, so y_N (I + a F) = y_N exactly
    n = 5
    B, Bi = rand_invertible(n, -2, 2)
    pcs = [piece(B, Bi, [i]) for i in range(3)]          # E_loc, E_2, E_3 orthogonal idempotents
    yN = Bi[0]
    require([sum(yN[i] * pcs[0][i][j] for i in range(n)) for j in range(n)] == list(yN), "y_N E_loc = y_N")
    nv = 1
    Wn = mmul(step_one(pcs[2], n, nv), step_one(pcs[1], n, nv))
    res = [sum((yN[i] * Wn[i][j].get(kk, F(0)) for i in range(n)), F(0)) for j in range(n) for kk in [(0,), (1,), (2,)]]
    row0 = [sum((yN[i] * Wn[i][j].get((0,), F(0)) for i in range(n)), F(0)) for j in range(n)]
    rowhi = [sum((yN[i] * Wn[i][j].get((e,), F(0)) for i in range(n)), F(0)) for j in range(n) for e in (1, 2)]
    require(row0 == list(yN) and all(v == 0 for v in rowhi), "y_N times the window pieces of m(N) equals y_N")
    print("small lemmas: L2 ab-coefficient identity; triangle y_R E1 x_Q = 0 under commutation; y_N F = 0 so beta^{m(N)}_{N1} = 0 directly")

def step_one(E, n, nv):
    return madd(meye(n, nv), [[pscale(pv(0, nv), E[i][j]) if E[i][j] else {} for j in range(n)] for i in range(n)])


def main():
    check_small_lemmas()
    check_formula()
    check_h6a()
    check_h6a_violation()
    lemma_M((1, 1))
    lemma_M((2, 2))
    print("PASS_P104_ROOT_HUB_FORCING")


if __name__ == "__main__":
    sys.exit(main())
