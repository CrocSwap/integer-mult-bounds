#!/usr/bin/env python3
"""Exact checks for outer/ACCRETIVE-SCALE.md (scale qualification of GAUGEFREE-INTERIORS Theorem 4.1, per the PR1758 review
https://github.com/CrocSwap/integer-mult-bounds/pull/1758#issuecomment-6203527654). Fractions and SymPy only, no floats.

 A  the review's counterexample N = 2, H = tI: Lambda/mu = 1 for every t, but max(||H||, ||H^-1||) = max(t, 1/t) is unbounded,
    while the absolute-scale guard 2 + Lambda + 1/mu dominates it.
 B  unit diagonal (Lambda >= 1, mu <= 1): 2 Lambda/mu - Lambda - 1/mu >= 0 (polynomial with nonnegative coefficients).
 C  descendants (Lambda' = Lambda + Lambda^2/mu, inverse 1/mu, shears Lambda/mu) on unit diagonal:
    Lambda' + 1/mu <= 3 (Lambda/mu)^2 and 2 + Lambda' + 1/mu <= 4 (2 + Lambda/mu)^2.
 D  near-unit diagonal fallback (|h0 - 1| <= 1/2, so |h0| >= 1/2, Re h0 <= 3/2): Lambda + 1/mu <= (7/2) Lambda/mu.
 E  the applied kernels have diagonal exactly one: G'_s(0) = 1 and the narrow N_ii = 1 symbolically; on exact rational
    truncated/rounded Toeplitz sections (diagonal 1, as the circuit applies them) e0* H e0 = 1 (so mu <= 1) and
    ||H e0||^2 >= 1 (so Lambda >= 1), and the Hermitian part is positive definite by exact LDL^T.
"""
from fractions import Fraction as Q
import sympy as sp

checks = 0
def ok(c, why):
    global checks
    if not c: raise SystemExit('FAIL: ' + why)
    checks += 1

# A. counterexample
for k in range(-40, 41, 5):
    t = Q(2) ** k
    Lam, mu = t, t                      # H = tI: ||H|| = t, Hermitian part = tI
    ok(Lam / mu == 1, 'A ratio')
    worst = max(t, 1 / t)               # max(||H||, ||H^-1||)
    ok(2 + Lam + 1 / mu >= worst, 'A absolute guard dominates')
ok(max(Q(2) ** 40, Q(2) ** -40) == Q(2) ** 40, 'A unbounded at fixed ratio')

# B, C, D symbolic: Lambda = L0 (1 + a), mu = m0 / (1 + b), a, b >= 0
a, b = sp.symbols('a b', nonnegative=True)
def nonneg_poly(expr, why):
    num, den = sp.fraction(sp.together(sp.expand(expr)))
    pn, pd = sp.Poly(sp.expand(num), a, b), sp.Poly(sp.expand(den), a, b)
    ok(all(c >= 0 for c in pn.coeffs()) and all(c >= 0 for c in pd.coeffs()), why)
Lam, mu = 1 + a, 1 / (1 + b)
r = Lam / mu
nonneg_poly(2 * r - Lam - 1 / mu, 'B unit diagonal: Lambda + 1/mu <= 2 Lambda/mu')
Lp = Lam + Lam ** 2 / mu
nonneg_poly(3 * r ** 2 - Lp - 1 / mu, 'C descendant: Lambda prime + 1/mu <= 3 (Lambda/mu)^2')
nonneg_poly(4 * (2 + r) ** 2 - (2 + Lp + 1 / mu), 'C descendant log form')
nonneg_poly(r - Lam / 1, 'C shear Lambda/mu >= Lambda')   # shears <= Lambda/mu, inverse 1/mu <= Lambda/mu
nonneg_poly(r - 1 / mu, 'C inverse 1/mu <= Lambda/mu')
LamD, muD = sp.Rational(1, 2) * (1 + a), sp.Rational(3, 2) / (1 + b)
nonneg_poly(sp.Rational(7, 2) * LamD / muD - LamD - 1 / muD, 'D near-unit diagonal: Lambda + 1/mu <= 7/2 Lambda/mu')

# E. the applied kernels
g, s, u, aa, b0, th, t = sp.symbols('gamma s u a beta0 theta t', real=True)
Gp = sp.exp(-g * u ** 2 + 2 * g * s * u)
ok(sp.simplify(Gp.subs(u, 0) - 1) == 0, "E G'_s(0) = 1")
ok(sp.simplify(sp.exp(g * s ** 2) * sp.exp(-g * (u - s) ** 2) - Gp) == 0, "E G'_s normalisation identity")
# narrow block N_{i,i+h} = exp(-a[(rho h + beta_i)^2 - beta_{i+h}^2]) at h = 0
h = sp.symbols('h', real=True)
bi = b0 + th * t
N = sp.exp(-aa * ((1 + th) * h + bi) ** 2 + aa * (bi + th * h) ** 2)
ok(sp.simplify(N.subs(h, 0) - 1) == 0, 'E narrow N_ii = 1')

def ldl_pd(M):
    n = len(M); A = [row[:] for row in M]
    for k in range(n):
        if A[k][k] <= 0: return False
        for i in range(k + 1, n):
            f = A[i][k] / A[k][k]
            for j in range(k, n): A[i][j] -= f * A[k][j]
    return True

def kernel(gq, sq, n, W, bits):
    # truncated at band W, entries rounded to `bits` bits with exact diagonal 1; G'_s(u) = exp(-gamma u^2 + 2 gamma s u) real
    ent = {}
    for d in range(-W, W + 1):
        v = sp.exp(-gq * d * d + 2 * gq * sq * d)
        ent[d] = Q(1) if d == 0 else Q(int(sp.floor(v * 2 ** bits + sp.Rational(1, 2)))) / 2 ** bits
    return [[ent.get(j - i, Q(0)) if abs(j - i) <= W else Q(0) for j in range(n)] for i in range(n)]

for gq in (sp.Rational(1, 2), sp.Integer(2), sp.Integer(20)):
    for sq in (sp.Integer(0), sp.Rational(1, 4), sp.Rational(499, 1000), sp.Rational(-499, 1000)):
        for n in (2, 4, 8):
            H = kernel(gq, sq, n, min(n - 1, 6), 40)
            ok(all(H[i][i] == 1 for i in range(n)), 'E diagonal exactly one after truncation/rounding')
            ok(H[0][0] == 1, 'E e0* H e0 = 1, so mu <= 1')
            ok(sum(H[i][0] ** 2 for i in range(n)) >= 1, 'E ||H e0||^2 >= 1, so Lambda >= 1')
            Hs = [[(H[i][j] + H[j][i]) / 2 for j in range(n)] for i in range(n)]
            ok(ldl_pd(Hs), 'E Hermitian part positive definite (accretive) gamma=%s s=%s n=%d' % (gq, sq, n))
print('PASS_ACCRETIVE_SCALE', checks, 'exact checks')
