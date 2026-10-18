#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite checks for the 2-adic corollary in the full-Borel superposition register model (see PROOF.md).

Standard library only, exact Fraction and F2 arithmetic, fixed seeds. The model (PR288 §0/§1.2(e), free group enlarged
to the lower Borel): W data registers plus auxiliary registers, each holding an element of the group algebra F2[G],
G <= GL_2m(Q), with H coordinates before D coordinates. Paid calls are I + x y^T ([n_A] - 1) with n_A = [[I, A], [0, I]],
at cost rank_Q(A). Free moves are GL_R(F2) mixing and multiplication of a register by an invertible lower-triangular
2m x 2m matrix (Levi maps on H or D, and lower-left D += K H). Only the data-to-data block of the final state matters.

pi is the F2-linear extension of reduction mod 2 on the monoid S of 2-integral matrices (inverses need not be
2-integral); rho(X) is the F2 rank of the (all H rows) x (all D columns) block of pi(X), i.e. PR288's FO functional on
Lambda/2Lambda with Y0 = D (equivalently P1's nu read through pi). Corollary (PROOF.md): sum of paid ranks >=
sum_w rank((g_w mod 2)_HD) over the data entries g_w, = mW on unit targets.

These are finite sanity checks of the lemmas, not a proof:
  1. pi is multiplicative on random products in F2[G], including free maps singular mod 2, and on forced F2
     cancellations (I + N([n_A]-1))^2 = I + N([n_2A]-1);
  2. rho = 0 on free moves (including maps singular mod 2), rho(paid) <= rank_Q A (nonzero A), rho subadditive, and
     rho(word) <= paid rank along random words with dirty auxiliaries;
  3. the data block alone has rho = mW for unit targets with permuted outputs, Levi factors and clean-ancilla
     garbage, and garbage cannot lower rho; a target factor singular mod 2 drops (g_w)_HD to rank 0;
  4. positive controls reaching the target exactly at cost mW: the direct word, its Levi conjugation, and its
     Borel conjugation with lower-left updates (K != 0);
  5. remark (m = 1, any rational data): the mod-p permutation-module functional is <= (p - 1) per paid call, zero on
     free moves, subadditive, and W (p - 1) on dyadic targets;
  6. scope controls: outside each hypothesis the invariant is undefined or weaker; among them only a free upper map
     (not natively free) reaches the target with zero paid calls. No saving with dyadic data is exhibited here.
The computed receipt must equal the committed RESULT.json (run with --out to regenerate it).
Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.
Usage: python3 -I -B verify.py [--out | --mutations]
"""

import json
import random
import sys
from fractions import Fraction
from pathlib import Path

if not __debug__:
    sys.stdout.write('FAIL_BIT_FULL_BOREL_2ADIC_FLOOR refusing to run under python -O\n')
    sys.exit(2)
HERE = Path(__file__).resolve().parent
# --mutations: each named defect is injected in-process and the run must then fail (the checks are not vacuous)
MUTATIONS = {  # mutation -> the check that must reject it
    'gamul_or': 'P^2 = paid(2A) with F2 cancellation',
    'mod2_wrong': 'pi multiplicative',
    'free_upper': 'rho(free Borel move) = 0',
    'paid_undercount': 'rho(paid call) <= rank_Q A',
    'general_double': 'the data block alone has rho = mW',
    'borel_skip': 'Borel-conjugated direct word equals l n_C l2 exactly',
    'upper_lower': "'a free upper map H += D would reach the target n_I with zero paid calls': False",
    'modp_axis': 'rho_p(free lower-triangular map) = 0',
}
MUTATION = None


class Fail(Exception):
    pass


def need(cond, what):
    if not cond:
        raise Fail(what)


class Dyadic(Exception):
    """Raised when a rational entry has an even denominator (no reduction mod 2)."""


# ---------- rational 2m x 2m matrices (tuples of tuples of Fractions) ----------

def mat(rows):
    return tuple(tuple(Fraction(x) for x in r) for r in rows)


def eye(n):
    return mat([[1 if i == j else 0 for j in range(n)] for i in range(n)])


def mul(a, b):
    n, k, p = len(a), len(b), len(b[0])
    return tuple(tuple(sum((a[i][t] * b[t][j] for t in range(k)), Fraction(0)) for j in range(p)) for i in range(n))


def block(A, B, C, D):
    """[[A, B], [C, D]] from m x m blocks."""
    return tuple(tuple(A[i]) + tuple(B[i]) for i in range(len(A))) + \
        tuple(tuple(C[i]) + tuple(D[i]) for i in range(len(C)))


def zero(m):
    return mat([[0] * m for _ in range(m)])


def shear(A):
    m = len(A)
    return block(eye(m), A, zero(m), eye(m))


def lower(X, K, Z):
    m = len(X)
    return block(X, zero(m), K, Z)


def inv(a):
    """Exact inverse of a square rational matrix (Gauss-Jordan)."""
    n = len(a)
    rows = [list(r) + [Fraction(int(i == j)) for j in range(n)] for i, r in enumerate(a)]
    for c in range(n):
        p = next(i for i in range(c, n) if rows[i][c] != 0)
        rows[c], rows[p] = rows[p], rows[c]
        piv = rows[c][c]
        rows[c] = [x / piv for x in rows[c]]
        for i in range(n):
            if i != c and rows[i][c] != 0:
                f = rows[i][c]
                rows[i] = [x - f * y for x, y in zip(rows[i], rows[c])]
    return tuple(tuple(r[n:]) for r in rows)


def qrank(a):
    rows = [list(r) for r in a]
    r = 0
    cols = len(rows[0]) if rows else 0
    for c in range(cols):
        p = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                f = rows[i][c] / rows[r][c]
                rows[i] = [x - f * y for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def mod2(x):
    if x.denominator % 2 == 0:
        raise Dyadic(str(x))
    if MUTATION == 'mod2_wrong':
        return x.denominator % 2
    return (x.numerator * x.denominator) % 2  # odd denominator is a 2-adic unit, so x = numerator mod 2


def reduce_mat(a):
    return tuple(tuple(mod2(x) for x in r) for r in a)


# ---------- group algebra F2[G] and W x W matrices over it ----------
# an element is a frozenset of group elements (coefficients in F2: multiplicity mod 2)

def ga(*gs):
    s = set()
    for g in gs:
        s ^= {g}
    return frozenset(s)


def ga_add(x, y):
    return frozenset(set(x) ^ set(y))


def ga_mul(x, y):
    s = set()
    for g in x:
        for h in y:
            if MUTATION == 'gamul_or':
                s |= {mul(g, h)}
            else:
                s ^= {mul(g, h)}
    return frozenset(s)


def M_mul(X, Y):
    W = len(X)
    out = []
    for i in range(W):
        row = []
        for j in range(W):
            acc = frozenset()
            for k in range(W):
                if X[i][k] and Y[k][j]:
                    acc = ga_add(acc, ga_mul(X[i][k], Y[k][j]))
            row.append(acc)
        out.append(row)
    return out


def M_eye(W, n):
    return [[ga(eye(n)) if i == j else frozenset() for j in range(W)] for i in range(W)]


def pi(X, n):
    """2mW x 2mW F2 matrix as a list of row bitmasks: register blocks of size n = 2m."""
    W = len(X)
    rows = [0] * (W * n)
    for i in range(W):
        for j in range(W):
            acc = [[0] * n for _ in range(n)]
            for g in X[i][j]:
                r = reduce_mat(g)
                for a in range(n):
                    for b in range(n):
                        acc[a][b] ^= r[a][b]
            for a in range(n):
                for b in range(n):
                    if acc[a][b]:
                        rows[i * n + a] |= 1 << (j * n + b)
    return rows


def f2_mul(A, B):
    out = []
    for r in A:
        acc, k = 0, 0
        while r:
            if r & 1:
                acc ^= B[k]
            r >>= 1
            k += 1
        out.append(acc)
    return out


def f2_rank(rows):
    basis = []
    for v in rows:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def rho(X, m):
    """F2 rank of the (all H rows) x (all D columns) block of pi(X)."""
    n = 2 * m
    W = len(X)
    P = pi(X, n)
    dmask = sum(1 << (j * n + m + b) for j in range(W) for b in range(m))
    return f2_rank([P[i * n + a] & dmask for i in range(W) for a in range(m)])


# ---------- moves ----------

def rand_unit(rng):
    """A 2-adic unit: odd numerator and odd denominator."""
    return Fraction(rng.choice([1, -1, 3, -3, 5]), rng.choice([1, 3, 5]))


def rand_int2(rng):
    """A 2-integral rational (odd denominator)."""
    return Fraction(rng.choice([0, 0, 1, -1, 2, 3, -2]), rng.choice([1, 1, 3, 5]))


def rand_A(m, rank, rng, nonzero=False):
    """A 2-integral m x m matrix of rational rank <= rank (sum of rank-one 2-integral outer products)."""
    if nonzero:
        while True:
            A = rand_A(m, rank, rng)
            if qrank(A):
                return A
    A = [[Fraction(0)] * m for _ in range(m)]
    for _ in range(rank):
        u = [rand_int2(rng) for _ in range(m)]
        v = [rand_int2(rng) for _ in range(m)]
        for i in range(m):
            for j in range(m):
                A[i][j] += u[i] * v[j]
    return mat(A)


def rand_lower_free(m, rng, even_diagonal=False):
    """A free map: invertible lower triangular, 2-integral. With even_diagonal, diagonal entries may be even
    (singular mod 2, inverse dyadic): the theorem needs only 2-integrality of the maps actually applied."""
    def diag():
        return rng.choice([Fraction(2), Fraction(-2), Fraction(4, 3)]) if even_diagonal and rng.randrange(3) == 0 \
            else rand_unit(rng)
    X = [[(diag() if i == j else (rand_int2(rng) if j < i else 0)) for j in range(m)] for i in range(m)]
    Z = [[(diag() if i == j else (rand_int2(rng) if j < i else 0)) for j in range(m)] for i in range(m)]
    K = [[rand_int2(rng) for _ in range(m)] for _ in range(m)]
    if MUTATION == 'free_upper':
        return block(mat(X), mat([[1 if (i, j) == (0, 0) else 0 for j in range(m)] for i in range(m)]), mat(K), mat(Z))
    return lower(mat(X), mat(K), mat(Z))


def rank_one_idempotent(W, rng):
    while True:
        x = [rng.randrange(2) for _ in range(W)]
        y = [rng.randrange(2) for _ in range(W)]
        if sum(a * b for a, b in zip(x, y)) % 2 == 1:
            return x, y


def paid(W, n, A, x, y):
    """I + N([n_A] - 1) with N = x y^T over F2."""
    g = shear(A)
    out = M_eye(W, n)
    for i in range(W):
        for j in range(W):
            if x[i] and y[j]:
                out[i][j] = ga_add(out[i][j], ga(g, eye(n)))  # adds [n_A] - 1 = [n_A] + [I] over F2
    return out


def free_register(W, n, w, l):
    out = M_eye(W, n)
    out[w][w] = ga(l)
    return out


def mixing(W, n, P):
    return [[ga(eye(n)) if P[i][j] else frozenset() for j in range(W)] for i in range(W)]


def rand_invertible_f2(W, rng):
    while True:
        P = [[rng.randrange(2) for _ in range(W)] for _ in range(W)]
        if f2_rank([sum(b << j for j, b in enumerate(r)) for r in P]) == W:
            return P


# ---------- Remark (m = 1, any rational data): the mod-p permutation module ----------

def modp(x, p):
    if x.denominator % p == 0:
        raise Fail('not p-integral at p = %d: %s' % (p, x))
    return (x.numerator * pow(x.denominator, -1, p)) % p


def psi_cols(X, p):
    """Columns of psi_p(X) on V^R, V = F2^{F_p^2}; basis index reg * p^2 + h * p + d."""
    n = p * p
    R = len(X)
    cols = [0] * (R * n)
    cache = {}
    for i in range(R):
        for j in range(R):
            for g in X[i][j]:
                if g not in cache:
                    a = [[modp(x, p) for x in row] for row in g]
                    cache[g] = [((a[0][0] * h + a[0][1] * d) % p) * p + (a[1][0] * h + a[1][1] * d) % p
                                for h in range(p) for d in range(p)]
                img = cache[g]
                for k in range(n):
                    cols[j * n + k] ^= 1 << (i * n + img[k])
    return cols, n


def rho_p(X, p):
    """F2 rank of the T' <- S' block of psi_p(X): S' = D-axis points (h = 0), T' = points with h != 0."""
    cols, n = psi_cols(X, p)
    R = len(X)
    tmask = sum(1 << (r * n + h * p + d) for r in range(R) for h in range(1, p) for d in range(p))
    if MUTATION == 'modp_axis':  # take the H axis instead of the D axis
        hmask = sum(1 << (r * n + h * p + d) for r in range(R) for h in range(p) for d in range(1, p))
        return f2_rank([cols[r * n + h * p] & hmask for r in range(R) for h in range(p)])
    return f2_rank([cols[r * n + d] & tmask for r in range(R) for d in range(p)])


def psi_mul(cx, cy):
    """Columns of psi(X) psi(Y) from the column bitmasks of psi(X) and psi(Y)."""
    out = []
    for c in cy:
        acc, i = 0, 0
        while c:
            if c & 1:
                acc ^= cx[i]
            c >>= 1
            i += 1
        out.append(acc)
    return out


def run():
    rng = random.Random(20261015)
    stats = dict(homomorphism_products=0, free_moves=0, singular_free_moves=0, paid_moves=0, words=0, word_steps=0,
                 max_terms=0, forced_cancellations=0, products_with_singular_free_map=0, square_identity=0,
                 width_one_steps=0, width_one_singular_free=0, width_one_products=0)
    # 1. pi is multiplicative (exact group-algebra products)
    for m, W in ((1, 2), (2, 2), (2, 3)):
        n = 2 * m
        for _ in range(30):
            singular = [False]

            def rand_elem():
                kind = rng.randrange(3)
                if kind == 0:
                    x, y = rank_one_idempotent(W, rng)
                    return paid(W, n, rand_A(m, 1, rng), x, y)
                if kind == 1:
                    l = rand_lower_free(m, rng, even_diagonal=True)
                    singular[0] |= any(l[i][i].numerator % 2 == 0 for i in range(n))
                    return free_register(W, n, rng.randrange(W), l)
                return mixing(W, n, rand_invertible_f2(W, rng))
            X, Y = rand_elem(), rand_elem()
            X = M_mul(X, rand_elem())
            need(pi(M_mul(X, Y), n) == f2_mul(pi(X, n), pi(Y, n)), 'pi multiplicative')
            stats['homomorphism_products'] += 1
            stats['products_with_singular_free_map'] += singular[0]
        # forced F2 cancellation: for y^T x = 1, (I + N([n_A] - 1))^2 = I + N([n_{2A}] - 1) over F2
        for _ in range(6):
            x, y = rank_one_idempotent(W, rng)
            A = rand_A(m, 1, rng, nonzero=True)
            P = paid(W, n, A, x, y)
            PP = M_mul(P, P)
            need(PP == paid(W, n, mat([[2 * v for v in r] for r in A]), x, y), 'P^2 = paid(2A) with F2 cancellation')
            need(pi(PP, n) == f2_mul(pi(P, n), pi(P, n)), 'pi multiplicative on P^2')
            stats['forced_cancellations'] += 1
    # 2-3. rho along random words, with dirty auxiliaries
    word_log = []
    for m, W, aux in ((1, 2, 0), (1, 3, 2), (2, 2, 0), (2, 2, 1), (2, 3, 1), (3, 2, 1)):
        n = 2 * m
        R = W + aux
        for trial in range(16):
            X = M_eye(R, n)
            spent, prev = 0, 0
            for step in range(9):
                kind = rng.randrange(4)
                if kind == 0:
                    a = rng.randrange(1, m + 1)
                    A = rand_A(m, a, rng, nonzero=True)
                    x, y = rank_one_idempotent(R, rng)
                    F = paid(R, n, A, x, y)
                    r = qrank(A) - (1 if MUTATION == 'paid_undercount' else 0)
                    need(rho(F, m) <= r, 'rho(paid call) <= rank_Q A')
                    spent += r
                    stats['paid_moves'] += 1
                elif kind == 1:
                    l = rand_lower_free(m, rng, even_diagonal=trial % 2 == 1)
                    F = free_register(R, n, rng.randrange(R), l)
                    need(rho(F, m) == 0, 'rho(free Borel move) = 0')
                    stats['singular_free_moves'] += any(l[i][i].numerator % 2 == 0 for i in range(n))
                    stats['free_moves'] += 1
                else:
                    F = mixing(R, n, rand_invertible_f2(R, rng))
                    need(rho(F, m) == 0, 'rho(GL_W(F2) mixing) = 0')
                    stats['free_moves'] += 1
                Xn = M_mul(F, X) if rng.randrange(2) else M_mul(X, F)
                cur = rho(Xn, m)
                need(cur <= prev + rho(F, m), 'rho subadditive along the word')
                need(cur <= spent, 'rho(word) <= paid rank so far')
                X, prev = Xn, cur
                stats['word_steps'] += 1
                stats['max_terms'] = max(stats['max_terms'], max(len(e) for row in X for e in row))
            stats['words'] += 1
            word_log.append(dict(m=m, W=W, aux=aux, paid_rank=spent, final_rho=prev))
    # target and positive control: direct word of mW rank-one shears, per data register
    direct = []
    for m, W, aux in ((1, 2, 0), (2, 2, 1), (2, 3, 0), (3, 3, 2)):
        n = 2 * m
        R = W + aux
        targets = []
        for w in range(W):
            C = [[(rand_unit(rng) if i == j else (rand_int2(rng) if j < i else 0)) for j in range(m)] for i in range(m)]
            targets.append(mat(C))
        T = M_eye(R, n)
        for w in range(W):
            T[w][w] = ga(shear(targets[w]))
        need(rho(T, m) == m * W, 'target rho = mW')
        X = M_eye(R, n)
        cost = 0
        for w in range(W):
            e = [1 if i == w else 0 for i in range(R)]
            for k in range(m):  # column decomposition C = sum_k C e_k e_k^T, each of rank one
                A = mat([[targets[w][i][j] if j == k else 0 for j in range(m)] for i in range(m)])
                X = M_mul(paid(R, n, A, e, e), X)
                cost += qrank(A)
        need(X == T, 'direct word equals the target in F2[G]')
        need(cost == m * W and rho(X, m) == m * W, 'direct word cost mW')
        direct.append(dict(m=m, W=W, aux=aux, cost=cost, target_rho=m * W))
    # Theorem 1, weakest target condition: permuted outputs, free Levi factors on targets, clean-ancilla garbage
    general = []
    for m, W, anc in ((1, 2, 1), (2, 2, 1), (2, 3, 2)):
        n = 2 * m
        R = W + anc
        Cs = [mat([[((2 if MUTATION == 'general_double' and i == 0 else 1) * rand_unit(rng) if i == j else
                     (rand_int2(rng) if j < i else 0)) for j in range(m)] for i in range(m)]) for _ in range(W)]
        perm = list(range(W))
        rng.shuffle(perm)
        X = M_eye(R, n)
        for w in range(W):
            X[w][w] = frozenset()
        for w in range(W):
            X[perm[w]][w] = ga(mul(mul(rand_lower_free(m, rng), shear(Cs[w])), rand_lower_free(m, rng)))
        for a in range(W, R):  # clean ancillas: arbitrary garbage in their rows and columns
            for j in range(R):
                X[a][j] = ga(rand_lower_free(m, rng), shear(rand_A(m, 1, rng)))
                X[j][a] = ga(shear(rand_A(m, 1, rng)))
        Xd = [[X[i][j] for j in range(W)] for i in range(W)]
        need(rho(Xd, m) == m * W, 'the data block alone has rho = mW (unit targets)')
        need(rho(X, m) >= rho(Xd, m), 'garbage and auxiliaries cannot lower rho below the data block')
        general.append(dict(m=m, W=W, clean_ancillas=anc, data_block_rho=rho(Xd, m), full_rho=rho(X, m), mW=m * W))
    # a target factor singular mod 2 makes (g_w)_HD singular: the restated bound drops accordingly (here to 0)
    m = 2
    lsing = lower(mat([[2, 0], [0, 2]]), zero(2), eye(2))
    gs = mul(lsing, shear(eye(2)))
    need(rho([[ga(gs)]], 2) == 0 and qrank(mat([[gs[i][2 + j] for j in range(2)] for i in range(2)])) == 2,
         'Levi factor singular mod 2: (g)_HD = 2I has rank 2 over Q but 0 mod 2')
    # Remark: m = 1, arbitrary rational (here dyadic) data, mod-p permutation module
    dyadic = [Fraction(1, 2), Fraction(-1, 2), Fraction(3, 4), Fraction(1, 8), Fraction(2), Fraction(-5, 2),
              Fraction(7, 4), Fraction(1), Fraction(-3)]
    width_one = []
    for p in (5, 11, 13):
        units = [x for x in dyadic if x.numerator % p]
        for W, aux in ((2, 0), (2, 1), (3, 0), (3, 2)):
            R = W + aux
            for trial in range(4):
                X = M_eye(R, 2)
                calls = prev = 0
                for step in range(8):
                    kind = rng.randrange(3)
                    if kind == 0:
                        x, y = rank_one_idempotent(R, rng)
                        F = paid(R, 2, mat([[rng.choice(units)]]), x, y)
                        need(rho_p(F, p) == p - 1, 'rho_p(paid call) = p - 1 at m = 1')
                        calls += 1
                    elif kind == 1:
                        sing = rng.randrange(4) == 0  # a free map singular mod p (diagonal divisible by p)
                        l = lower(mat([[rng.choice(units) * (p if sing else 1)]]),
                                  mat([[rng.choice(dyadic + [Fraction(0)])]]), mat([[rng.choice(units)]]))
                        F = free_register(R, 2, rng.randrange(R), l)
                        need(rho_p(F, p) == 0, 'rho_p(free lower-triangular map) = 0')
                        stats['width_one_singular_free'] += sing
                    else:
                        F = mixing(R, 2, rand_invertible_f2(R, rng))
                        need(rho_p(F, p) == 0, 'rho_p(mixing) = 0')
                    left = rng.randrange(2)
                    Xn = M_mul(F, X) if left else M_mul(X, F)
                    a_, b_ = (F, X) if left else (X, F)
                    need(psi_cols(Xn, p)[0] == psi_mul(psi_cols(a_, p)[0], psi_cols(b_, p)[0]), 'psi_p multiplicative')
                    stats['width_one_products'] += 1
                    cur = rho_p(Xn, p)
                    need(cur <= prev + rho_p(F, p), 'rho_p subadditive')
                    need(cur <= (p - 1) * calls, 'rho_p(word) <= (p - 1) * paid calls')
                    X, prev = Xn, cur
                    stats['width_one_steps'] += 1
            T = M_eye(R, 2)
            for w in range(W):
                c = rng.choice(units)
                T[w][w] = ga(mul(mul(lower(mat([[rng.choice(units)]]), mat([[Fraction(1, 2)]]),
                                           mat([[rng.choice(units)]])), shear(mat([[c]]))),
                                 lower(mat([[rng.choice(units)]]), mat([[Fraction(-3, 4)]]), mat([[rng.choice(units)]]))))
            need(rho_p(T, p) == W * (p - 1), 'width-one dyadic target has rho_p = W (p - 1)')
            width_one.append(dict(p=p, W=W, aux=aux, target_rho_p=W * (p - 1)))
    # nonabelian positive control: free Levi conjugation around the direct word reaches n_{X^-1 C Z} at cost rank C
    conj = []
    for m, W in ((2, 2), (3, 2)):
        n = 2 * m
        X = M_eye(W, n)
        T = M_eye(W, n)
        cost = 0
        for w in range(W):
            Xl = mat([[(rand_unit(rng) if i == j else (rand_int2(rng) if j < i else 0)) for j in range(m)] for i in range(m)])
            Zl = mat([[(rand_unit(rng) if i == j else (rand_int2(rng) if j < i else 0)) for j in range(m)] for i in range(m)])
            C = mat([[(rand_unit(rng) if i == j else (rand_int2(rng) if j < i else 0)) for j in range(m)] for i in range(m)])
            l = lower(Xl, zero(m), Zl)
            linv = lower(inv(Xl), zero(m), inv(Zl))
            need(mul(l, linv) == eye(n) and all(x.denominator % 2 for r in linv for x in r), '2-integral inverse')
            F = free_register(W, n, w, linv)
            X = M_mul(X, F)
            e = [1 if i == w else 0 for i in range(W)]
            for k in range(m):
                A = mat([[C[i][j] if j == k else 0 for j in range(m)] for i in range(m)])
                X = M_mul(X, paid(W, n, A, e, e))
                cost += qrank(A)
            F = free_register(W, n, w, l)
            X = M_mul(X, F)
            T[w][w] = ga(shear(mul(mul(inv(Xl), C), Zl)))  # l^-1 n_C l = n_{X^-1 C Z}
        need(X == T, 'conjugated direct word equals the target n_{X^-1 C Z}')
        need(cost == m * W and rho(X, m) == m * W, 'conjugated direct word costs mW')
        conj.append(dict(m=m, W=W, cost=cost))
    # tightness with lower-left updates (K != 0): [l] (direct word) [l'] reaches l n_C l' exactly at cost mW
    borel = []
    for m, W in ((2, 2), (3, 2)):
        n = 2 * m
        X = M_eye(W, n)
        T = M_eye(W, n)
        cost = 0
        for w in range(W):
            l, l2 = rand_lower_free(m, rng), rand_lower_free(m, rng)
            need(any(l[m + i][j] for i in range(m) for j in range(m)), 'l has a lower-left block (D += K H)')
            C = mat([[(rand_unit(rng) if i == j else (rand_int2(rng) if j < i else 0)) for j in range(m)] for i in range(m)])
            X = M_mul(X, free_register(W, n, w, l))
            e = [1 if i == w else 0 for i in range(W)]
            for k in range(m):
                A = mat([[C[i][j] if j == k else 0 for j in range(m)] for i in range(m)])
                X = M_mul(X, paid(W, n, A, e, e))
                cost += qrank(A)
            if MUTATION != 'borel_skip':
                X = M_mul(X, free_register(W, n, w, l2))
            T[w][w] = ga(mul(mul(l, shear(C)), l2))
        need(X == T, 'Borel-conjugated direct word equals l n_C l2 exactly')
        need(cost == m * W and rho(X, m) == m * W, 'Borel-conjugated direct word costs mW and has rho = mW')
        borel.append(dict(m=m, W=W, cost=cost))
    g = shear(rand_A(2, 1, rng))
    need(ga_mul(ga(eye(4), g), ga(eye(4), g)) == ga(eye(4), mul(g, g)), '(1 + [g])^2 = 1 + [g^2] in F2[G]')
    stats['square_identity'] += 1
    # scope controls: outside each hypothesis the invariant is undefined or weaker (no saving is exhibited, except
    # that a free upper map would make the target itself free)
    controls = {}
    try:
        reduce_mat(shear(mat([[Fraction(1, 2)]])))
        controls['dyadic frame: invariant undefined (no mod-2 reduction)'] = False
    except Dyadic:
        controls['dyadic frame: invariant undefined (no mod-2 reduction)'] = True
    m = 1
    d = lower(mat([[2]]), mat([[0]]), mat([[1]]))
    dinv = lower(mat([[Fraction(1, 2)]]), mat([[0]]), mat([[1]]))
    A = mat([[1]])
    comm = mul(mul(mul(d, shear(A)), dinv), shear(mat([[-1]])))
    need(comm == shear(A), 'PR288(d): the commutator d n_A d^-1 n_A^-1 equals n_A')
    try:
        reduce_mat(dinv)
        controls['PR288(d) commutator needs the dyadic inverse of d'] = False
    except Dyadic:
        controls['PR288(d) commutator needs the dyadic inverse of d'] = True
    upper = block(eye(1), mat([[1]]), zero(1), eye(1))  # H += D, if it were free
    if MUTATION == 'upper_lower':
        upper = block(eye(1), zero(1), mat([[1]]), eye(1))
    Xu = M_mul(M_eye(1, 2), free_register(1, 2, 0, upper))  # a word with one free upper move and no paid call
    controls['a free upper map H += D would reach the target n_I with zero paid calls'] = \
        Xu == [[ga(shear(mat([[1]])))]] and rho(Xu, 1) == 1
    Teven = [[ga(shear(mat([[2, 0], [1, 1]])))]]
    controls['even-diagonal target: the bound weakens to rank(C mod 2) < mW'] = rho(Teven, 2) < 2
    need(all(controls.values()), 'scope controls: %s' % controls)
    need(stats['singular_free_moves'] > 0 and stats['products_with_singular_free_map'] > 0
         and stats['width_one_singular_free'] > 0, 'free maps singular mod 2 (and mod p at m = 1) were exercised')
    return dict(stats=stats, words=word_log, direct_controls=direct, general_target_controls=general,
                width_one=width_one, conjugated_direct_controls=conj, borel_direct_controls=borel,
                scope_controls=sorted(controls))


def run_mutations():
    global MUTATION
    MUTATION = None
    run()  # the unmutated baseline must pass first
    caught = {}
    for name in MUTATIONS:
        MUTATION = name
        try:
            run()
            caught[name] = None
        except (Fail, Dyadic) as e:
            caught[name] = '%s: %s' % (type(e).__name__, e)
        finally:
            MUTATION = None
    for name, msg in caught.items():
        print('  mutation %-16s -> %s' % (name, msg or 'NOT CAUGHT'))
    wrong = [k for k, v in caught.items() if not v or MUTATIONS[k] not in v]
    need(not wrong, 'mutations not rejected by their intended check: %s' % wrong)
    print('PASS_BIT_FULL_BOREL_2ADIC_FLOOR_MUTATIONS rejected=%d/%d' % (len(caught), len(MUTATIONS)))
    return 0


def main(out=False):
    result = dict(object='full-Borel bit register model: finite checks of the 2-adic floor (PROOF.md)', **run(),
                  python=sys.version.split()[0])
    text = json.dumps({k: v for k, v in result.items() if k != 'python'}, indent=1, sort_keys=True) + '\n'
    if out:
        (HERE / 'RESULT.json').write_text(text)
    else:
        need((HERE / 'RESULT.json').read_text() == text, 'computed receipt differs from committed RESULT.json')
    s = result['stats']
    print('homomorphism products %d; random words %d (%d steps, %d free and %d paid moves, up to %d group terms per '
          'entry); direct controls %d; scope controls %d' % (
              s['homomorphism_products'], s['words'], s['word_steps'], s['free_moves'], s['paid_moves'],
              s['max_terms'], len(result['direct_controls']), len(result['scope_controls'])))
    print('PASS_BIT_FULL_BOREL_2ADIC_FLOOR_FINITE_CHECKS products=%d cancellations=%d words=%d steps=%d '
          'singular_free=%d direct=%d conjugated=%d borel=%d general_targets=%d width_one_steps=%d scope_controls=%d' % (
              s['homomorphism_products'], s['forced_cancellations'], s['words'], s['word_steps'],
              s['singular_free_moves'], len(result['direct_controls']), len(result['conjugated_direct_controls']),
              len(result['borel_direct_controls']), len(result['general_target_controls']),
              s.get('width_one_steps', 0), len(result['scope_controls'])))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(run_mutations() if '--mutations' in sys.argv[1:] else main('--out' in sys.argv[1:]))
    except (Fail, Dyadic) as e:
        sys.stdout.write('FAIL_BIT_FULL_BOREL_2ADIC_FLOOR %s: %s\n' % (type(e).__name__, e))
        sys.exit(1)
