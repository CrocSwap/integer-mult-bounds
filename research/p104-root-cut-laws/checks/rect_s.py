"""Rectangle law, the packing of 72 odd rectangles, and Theorem S (THEOREM.md section 3).
Exact integer and rational arithmetic, standard library only. Prints 'ok   ' lines and the marker PASS_RECT_S."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import random
from fractions import Fraction as Fr
from math import lcm
from collections import Counter
from common import req, finish, load, fr_matrix

P = 1000003


# ---------- 2 x 2 matrices over F_p
def mm(A, B, p=P):
    return [[(A[i][0] * B[0][j] + A[i][1] * B[1][j]) % p for j in (0, 1)] for i in (0, 1)]


def rk2(M, p=P):
    if (M[0][0] * M[1][1] - M[0][1] * M[1][0]) % p:
        return 2
    return 1 if any(v % p for r in M for v in r) else 0


def cell(A, B, s, p=P):
    M = mm(A, B, p)
    return rk2([[M[0][0] - s, M[0][1]], [M[1][0], M[1][1] - s]], p)


def inv2(g, p=P):
    det = (g[0][0] * g[1][1] - g[0][1] * g[1][0]) % p
    iv = pow(det, -1, p)
    return [[g[1][1] * iv % p, -g[0][1] * iv % p], [-g[1][0] * iv % p, g[0][0] * iv % p]]


def conj(g, M, p=P):
    return mm(mm(g, M, p), inv2(g, p), p)


def rectangle_draws():
    rnd = random.Random(2026)
    cells = ((1, 2), (3, 2), (3, 4), (1, 4))              # (row, col): rows 1,3 against columns 2,4
    sg = lambda r, c: 1 if r > c else -1
    assert sg(1, 2) * sg(3, 2) * sg(3, 4) * sg(1, 4) == -1
    viol = tight = draws = 0
    for _ in range(40000):
        mode = rnd.randrange(3)
        if mode == 0:     # fully random 2 x 2 matrices
            A = {r: [[rnd.randrange(P), rnd.randrange(P)], [rnd.randrange(P), rnd.randrange(P)]] for r in (1, 3)}
            B = {c: [[rnd.randrange(P), rnd.randrange(P)], [rnd.randrange(P), rnd.randrange(P)]] for c in (2, 4)}
        else:             # simultaneously conjugated sign-diagonal gains, half of them with one column conjugated again
            g = [[rnd.randrange(1, 50), rnd.randrange(50)], [rnd.randrange(50), rnd.randrange(1, 50)]]
            if (g[0][0] * g[1][1] - g[0][1] * g[1][0]) % P == 0:
                continue
            dg = lambda: [[rnd.choice((1, -1)) % P, 0], [0, rnd.choice((1, -1)) % P]]
            A = {r: conj(g, dg()) for r in (1, 3)}
            B = {c: conj(g, dg()) for c in (2, 4)}
            if mode == 2:
                g2 = [[1, rnd.randrange(9)], [rnd.randrange(9), 1 + rnd.randrange(1, 9)]]
                if (g2[0][0] * g2[1][1] - g2[0][1] * g2[1][0]) % P:
                    B[rnd.choice((2, 4))] = conj(g2, [[1, 0], [0, P - 1]])
        tot = sum(cell(A[r], B[c], sg(r, c)) for r, c in cells)
        draws += 1
        viol += tot < 2
        tight += tot == 2
    return draws, viol, tight


def rectangle_scalar_exhaustive(p):
    """rho = 1: all A_d, A_e, B_c, B_f in F_p, signs of odd product; the sum of the four cell ranks is >= 1."""
    sgn = (1, 1, 1, -1)
    worst = 4
    for a in range(p):
        for e in range(p):
            for b in range(p):
                for f in range(p):
                    t = sum((1 if (x * y - s) % p else 0) for (x, y, s) in ((a, b, sgn[0]), (e, b, sgn[1]), (e, f, sgn[2]), (a, f, sgn[3])))
                    worst = min(worst, t)
    return worst


def packing():
    m = 9
    rects = []
    for i in range(1, m + 1):
        for j in range(i + 1, m + 1):
            rects.append(((i, j), (i + m, j), (i + m, j + m), (i, j + m)))
            rects.append(((j, i), (j + m, i), (j + m, i + m), (j, i + m)))
    sg = lambda r, c: 1 if r > c else -1
    odd = all(sg(*q[0]) * sg(*q[1]) * sg(*q[2]) * sg(*q[3]) == -1 for q in rects)
    cnt = Counter(c for q in rects for c in q)
    offdiag = all(r != c and 1 <= r <= 2 * m and 1 <= c <= 2 * m for r, c in cnt)
    # each rectangle has distinct rows d != e and distinct columns c != f
    shape = all(q[0][0] != q[1][0] and q[0][1] != q[3][1] and q[0][0] == q[3][0] and q[1][0] == q[2][0] and q[0][1] == q[1][1] and q[2][1] == q[3][1] for q in rects)
    allcells = {(r, c) for r in range(1, 2 * m + 1) for c in range(1, 2 * m + 1) if r != c}
    unused = sorted(allcells - set(cnt))
    return len(rects), odd, max(cnt.values()), len(cnt), offdiag, shape, unused


# ---------- Theorem S on data
def det2(M):
    return M[0][0] * M[1][1] - M[0][1] * M[1][0]


def inv2q(M):
    d = det2(M)
    return [[M[1][1] / d, -M[0][1] / d], [-M[1][0] / d, M[0][0] / d]]


def mmq(A, B):
    return [[A[i][0] * B[0][j] + A[i][1] * B[1][j] for j in (0, 1)] for i in (0, 1)]


def load_blocks(name):
    R = load(name)
    n, N = R['n'], R['N']
    X, Y = fr_matrix(R['X']), fr_matrix(R['Y'])
    if len(X) == n and len(X[0]) == N:
        X = [list(c) for c in zip(*X)]
        Y = [list(c) for c in zip(*Y)]
    units = [s['units'] for s in R['stages']]
    L = len(units)
    # the units of stage d precede the units of stage c when d < c (so the sign of a cell is sgn(d - c))
    order_ok = all(max(units[d]) < min(units[c]) for d in range(L) for c in range(d + 1, L))
    G = {}
    for d in range(L):
        for c in range(L):
            if d != c:
                G[d, c] = [[sum(Y[u][k] * X[v][k] for k in range(n)) for v in units[c]] for u in units[d]]
    return n, X, Y, units, L, G, order_ok


def factor_form(G, L, sign):
    """Find invertible Xi_d, H_c with sign(d,c) * G[d,c] = Xi_d H_c for all d != c, or return None."""
    S = {(d, c): [[sign(d, c) * v for v in row] for row in G[d, c]] for (d, c) in G}
    if det2(S[0, 1]) == 0:
        return None
    Xi = {0: [[Fr(1), Fr(0)], [Fr(0), Fr(1)]]}
    for d in range(1, L):
        c0 = next(c for c in range(L) if c not in (0, d))
        if det2(S[0, c0]) == 0:
            return None
        Xi[d] = mmq(S[d, c0], inv2q(S[0, c0]))
    H = {c: S[0, c] for c in range(1, L)}
    H[0] = mmq(inv2q(Xi[1]), S[1, 0])
    for d in range(L):
        for c in range(L):
            if d != c and mmq(Xi[d], H[c]) != S[d, c]:
                return None
    if any(det2(Xi[d]) == 0 for d in range(L)) or any(det2(H[c]) == 0 for c in range(L)):
        return None
    return Xi, H


def residual_sums(n, X, Y, units, L, G):
    """For every pair of hub coordinates {a, b}: sum over stage pairs d != c of the rank of the cell with the two hub coordinates removed."""
    den_x = lcm(*[v.denominator for r in X for v in r])
    den_y = lcm(*[v.denominator for r in Y for v in r])
    Xi_ = [[int(v * den_x) for v in r] for r in X]
    Yi_ = [[int(v * den_y) for v in r] for r in Y]
    Gi = {k: [[int(v * den_x * den_y) for v in row] for row in blk] for k, blk in G.items()}
    out = {}
    for a in range(n):
        for b in range(a + 1, n):
            tot, hist = 0, Counter()
            for (d, c), blk in Gi.items():
                M = [[blk[i][j] - Yi_[units[d][i]][a] * Xi_[units[c][j]][a] - Yi_[units[d][i]][b] * Xi_[units[c][j]][b] for j in (0, 1)] for i in (0, 1)]
                if M[0][0] * M[1][1] - M[0][1] * M[1][0] != 0:
                    r = 2
                elif any(v != 0 for row in M for v in row):
                    r = 1
                else:
                    r = 0
                tot += r
                hist[r] += 1
            out[a, b] = (tot, dict(hist))
    return out


def main():
    # ---- rectangle law
    draws, viol, tight = rectangle_draws()
    req(viol == 0 and tight > 1000, 'rectangle law (rho = 2) on %d draws over F_%d: 0 violations, %d tight (sum = 2)' % (draws, P, tight))
    for p in (3, 5, 7, 11):
        req(rectangle_scalar_exhaustive(p) == 1, 'rectangle law (rho = 1) exhaustive over F_%d: the minimum of the four-cell sum is 1' % p)
    # controls: an even quadruple has no law; characteristic 2 has none; both reach 0
    I2 = [[1, 0], [0, 1]]
    req(sum(cell(I2, I2, 1) for _ in range(4)) == 0, 'control: an even sign quadruple (all +1) with A = B = I reaches sum 0')
    req(sum(cell(I2, I2, 1 % 2, 2) for _ in range(4)) == 0, 'control: in characteristic 2 the odd quadruple reaches sum 0 (2 is not a unit)')
    # the proof step: three exact cells force the fourth to be 2 s I
    rnd = random.Random(5)
    forced = 0
    for _ in range(300):
        g = [[rnd.randrange(1, 90), rnd.randrange(90)], [rnd.randrange(90), rnd.randrange(1, 90)]]
        if det2(g) % P == 0:
            continue
        s = [rnd.choice((1, -1)) for _ in range(3)]
        s.append(-s[0] * s[1] * s[2])                     # odd product
        Ad = [[s[0] * x % P for x in r] for r in inv2(g)]  # A_d B_c = s_dc with B_c = g
        Ae = [[s[1] * x % P for x in r] for r in inv2(g)]
        Bc = g
        Bf = [[s[2] * x % P for x in r] for r in inv2(Ae)]  # A_e B_f = s_ef
        M = mm(Ad, Bf)
        fourth = [[(s[3] * (1 if i == j else 0) - M[i][j]) % P for j in (0, 1)] for i in (0, 1)]
        forced += fourth == [[2 * s[3] % P, 0], [0, 2 * s[3] % P]]
    req(forced > 250, 'proof step: with three exact cells the fourth residual is exactly 2 s I (%d random instances)' % forced)
    # ---- packing
    nr, odd, mx, ncell, offd, shape, unused = packing()
    req(nr == 72 and odd and shape, 'packing: 72 rectangles, each with two rows and two columns, all of odd sign product')
    req(mx == 1 and ncell == 288 and offd, 'packing: every cell used at most once (288 distinct off-diagonal cells)')
    req(unused == sorted([(i + 9, i) for i in range(1, 10)] + [(i, i + 9) for i in range(1, 10)]), 'packing: the 18 unused off-diagonal cells are (i+9, i) and (i, i+9)')
    # ---- Theorem S on the two roots
    results = {}
    for name in ('root_h.json', 'root_t0_dsum.json'):
        n, X, Y, units, L, G, order_ok = load_blocks(name)
        req(order_ok and L == 18, '%s: 18 stages of two LOCAL units, stage units in word order (cell sign sgn(d - c))' % name)
        ff = factor_form(G, L, lambda d, c: 1 if d > c else -1)
        req(ff is not None, '%s: hypothesis of Theorem S: sgn(d-c) * Gamma_dc = Xi_d H_c for all 306 cells d != c, Xi_d and H_c invertible' % name)
        wrong = factor_form(G, L, lambda d, c: 1)
        req(wrong is None, '%s: control: with every sign +1 the factorisation fails' % name)
        sums = residual_sums(n, X, Y, units, L, G)
        mn = min(v[0] for v in sums.values())
        argmin = sorted(k for k, v in sums.items() if v[0] == mn)
        req(len(sums) == n * (n - 1) // 2 and mn >= 144, '%s: Theorem S, all %d hub pairs: the sum over cells of the residual rank is at least 144 (minimum %d)' % (name, len(sums), mn))
        results[name] = (mn, argmin, sums)
    mn, argmin, sums = results['root_h.json']
    req(mn == 144 and argmin == [(0, 1)], 'root_h: the bound 144 is attained at the hub pair (0, 1) only; histogram there %s' % sums[0, 1][1])
    ordered = sorted(v[0] for v in sums.values())
    req(ordered[1] > 144, 'root_h: every other hub pair gives more (next smallest sum %d, largest %d)' % (ordered[1], ordered[-1]))
    mn0, argmin0, sums0 = results['root_t0_dsum.json']
    req(mn0 == 144 and argmin0 == [(0, 20)], 'root_t0: the bound 144 is attained at the hub pair (0, 20) only')
    # control: the same residual count on a synthetic family that satisfies the factorisation with all signs +1 reaches 0
    nn, Xs, Ys = 2, [[Fr(int(i == j)) for j in range(2)] for i in range(2)], None
    units = [[0, 1]] * 3
    Gs = {(d, c): [[Fr(1), Fr(0)], [Fr(0), Fr(1)]] for d in range(3) for c in range(3) if d != c}
    resid0 = all(Gs[k][i][j] - Fr(int(i == j)) == 0 for k in Gs for i in (0, 1) for j in (0, 1))
    req(resid0 and factor_form(Gs, 3, lambda d, c: 1) is not None and factor_form(Gs, 3, lambda d, c: 1 if d > c else -1) is None,
        'control: a family with Gamma = +Xi H (no sign pattern) is not of the form sgn(d-c) Xi H, and its hub residual is 0, below the bound')
    finish('PASS_RECT_S')


if __name__ == '__main__':
    main()
