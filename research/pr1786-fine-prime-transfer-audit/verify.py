#!/usr/bin/env python3
"""Independent audit checks for PR1786's written fine-prime transfer.

Audited text: research/fine-prime-padding/FINE-PRIME-PADDING.md at PR1786 head
c52345caa318fc6b1b6e2659c57d746317a72823 (SHA256 in README.md). Every
quantity below is re-derived from that prose and from the cited PR1673/PR1758
statements. Nothing is imported or read from PR1786's checkers or ledger.

Exact rational arithmetic decides every PASS condition except the parts marked
INFORMATIONAL (eventual thresholds, computed in floating point and reported only).
Standard library only. Claude Code (Opus) donated session; Apache-2.0.
"""
import json
import math
import sys
from decimal import Decimal, getcontext
from fractions import Fraction as F
from pathlib import Path

if not __debug__:
    raise SystemExit('assertions must be enabled')
ROOT = Path(__file__).resolve().parents[2]
getcontext().prec = 60
report = {}


def dec_ln(n):
    return Decimal(n).ln()


# Rigorous rational bounds: 3.14159 < pi < 3.1416 and 0.6931 < ln 2 < 0.6932.
PI_LO, PI_HI = F(314159, 100000), F(31416, 10000)
LN2_LO, LN2_HI = F(6931, 10000), F(6932, 10000)


def alpha_of(p):
    """alpha = ceil(sqrt((4/pi) log(16p))); refuse if the ceiling is ambiguous."""
    v = (Decimal(4) / Decimal('3.14159265358979323846264338327950288')) * dec_ln(16 * p)
    r = v.sqrt()
    a = int(r) + (0 if r == int(r) else 1)
    assert abs(r - Decimal(a)) > Decimal('1e-30') and abs(r - Decimal(a - 1)) > Decimal('1e-30')
    return a


# ---------------------------------------------------------------- section 1
# s in ((1-2eta)t, (1-eta)t], eta = 1/(4p^2); theta = t/s - 1 is decreasing in s.
def theta_range(p):
    eta = F(1, 4 * p * p)
    lo = 1 / (1 - eta) - 1          # attained at s = (1-eta)t
    hi = 1 / (1 - 2 * eta) - 1      # approached as s -> (1-2eta)t (excluded)
    return eta, lo, hi


for p in range(2, 2001):
    eta, lo, hi = theta_range(p)
    assert lo > F(1, 4 * p * p)                       # strict lower bound of section 1
    assert hi == F(1, 2 * p * p - 1) and hi <= F(1, p * p)
    # capacity: (1-2eta)^d >= 1-2d*eta > 1/2 for every d <= p (Bernoulli; d=p worst)
    assert 1 - 2 * p * eta > F(1, 2)
# exact Bernoulli spot checks, d = p
for p in (2, 3, 5, 17, 64):
    assert (1 - F(1, 2 * p * p)) ** p >= 1 - F(p, 2 * p * p) > F(1, 2)
report['section1_theta_interval'] = 'PASS: 1/(4p^2) < theta <= 1/(2p^2-1) <= 1/p^2 and S/T > 1/2 (d<=p), p=2..2000 exact'


# INFORMATIONAL: eventual threshold of the Trudgian-based count.
# Count >= eta x/log x - 2 f(x) with f(y)=0.2795 y (log y)^(-3/4) exp(-sqrt(log y/6.455))
# increasing for log y >= 2. Half the main term survives iff
#   4*0.2795*u^(1/4)*exp(-sqrt(u/6.455)) <= 1/(4p^2),  u = log x = c p^(1-eps).
def count_ok(L, c, one_minus_eps):
    lu = math.log(c) + one_minus_eps * L
    if lu > 600:   # sqrt(u/6.455) > e^299 dwarfs 2L + log(u)/4 + 3 for every L <= 1e13 tested
        return True
    u = math.exp(lu)
    if u < math.log(229):
        return False
    lhs = math.log(4 * 0.2795 * 4) + 2 * L + 0.25 * math.log(u) - math.sqrt(u / 6.455)
    return lhs <= 0


def threshold(c, one_minus_eps):
    lo, hi = 1.0, 1e13
    assert count_ok(hi, c, one_minus_eps)
    for _ in range(200):
        mid = (lo + hi) / 2
        if count_ok(mid, c, one_minus_eps):
            hi = mid
        else:
            lo = mid
    # condition is monotone past the threshold: spot-check a geometric grid above it
    assert all(count_ok(hi * k, c, one_minus_eps) for k in (1.0001, 1.5, 3, 10, 100))
    return hi


report['section1_eventual_threshold_INFORMATIONAL'] = {
    'meaning': 'smallest log(p) (natural) from which the cited Trudgian bound leaves half the main term, if log x = c p^(1-eps), eps = 9999999/10000000',
    **{f'c={c}': f'{threshold(c, 1e-7):.4g}' for c in (0.01, 1, 100)},
}

# ---------------------------------------------------------------- section 2
# LOG-A-PHASE-SCHUR-AUDIT s1: ||N-I||_inf <= exp(-2a theta) + 5 exp(-2a), any theta>0.
# Claim: theta >= 1/(4p^2), a >= 4 log(16p) => row gap >= 1/(8p^2).
# Proof used here: x = 2a theta >= a/(2p^2); if x<=1 then 1-e^-x >= x/2 >= a/(4p^2)
# >= log(16p)/p^2 >= 2/p^2 ... (16p >= e^2 for p >= 1); if x>1, 1-e^-x > 1/2.
# And 5 e^(-2a) <= 5 (16p)^(-8). Check gap >= 1/(8p^2) exactly using ln(16p) >= 2.
for p in range(1, 5001):
    lower_first = min(F(1, 2), F(2, p * p))            # uses log(16p) >= log 16 > 2
    assert lower_first - F(5, (16 * p) ** 8) >= F(1, 8 * p * p)
report['section2_row_gap'] = 'PASS: gap >= 1/(8p^2) for p=1..5000 (exact; the argument is uniform in p)'

# Control: PR1673's old numeric margin 1/(8p) cannot be reused at the new theta.
# At theta = 1/(2p^2-1) (largest new theta) and a <= 5 log(16p)+pi+2 sqrt(4 pi log 16p),
# 1 - e^{-2a theta} <= 2a theta < 1/(8p) once p is large: exhibit it exactly at p=2^20.
p = 2 ** 20
a_hi = PI_HI * alpha_of(p) ** 2
assert 2 * a_hi * F(1, 2 * p * p - 1) < F(1, 8 * p)
report['control_old_row_margin_1_over_8p_fails'] = f'PASS (rejects): at p=2^20 the new-theta gap is below 1/(8p)'

# Column analogue (not written in LOG-A s1): for column j and source offset i=j-h with
# G=q_j-q_i, the exponent is (rho h+beta_i)^2-beta_j^2 = G(G+2beta_j). In-cell neighbours give
# 1+2beta_j >= 2theta and 1-2beta_j > 2theta, summing to 2, and |G|>=2 gives >= G^2/2, so
# ||N-I||_1 <= e^{-2a theta} + e^{-2a(1-theta)} + 4e^{-2a}: the same polynomial gap as rows.
# Finite fixture: build N on 3000 source points (several cells) at p=8, theta just above
# 1/(4p^2), a = pi*alpha^2, |h|<=8, and compare row and column off-diagonal sums (Decimal).
def n_fixture(p, npts=3000, hmax=8):
    theta = Decimal(1) / Decimal(4 * p * p) * Decimal('1.0001')
    rho = 1 + theta
    a = Decimal('3.14159265358979323846264338327950288') * alpha_of(p) ** 2
    qv = [int((rho * j + Decimal('0.5')).to_integral_value(rounding='ROUND_FLOOR')) for j in range(npts)]
    bv = [rho * j - qv[j] for j in range(npts)]
    assert all(Decimal('-0.5') <= x < Decimal('0.5') for x in bv)
    rows = [Decimal(0)] * npts
    cols = [Decimal(0)] * npts
    for i in range(npts):
        for h in range(-hmax, hmax + 1):
            k = i + h
            if h == 0 or not 0 <= k < npts:
                continue
            e = (-a * ((rho * h + bv[i]) ** 2 - bv[k] ** 2)).exp()
            rows[i] += e
            cols[k] += e
    inner = range(hmax, npts - hmax)
    return theta, a, max(rows[i] for i in inner), max(cols[i] for i in inner), sum(1 for j in range(1, npts) if qv[j] - qv[j - 1] == 2)


getcontext().prec = 40
th, a8, rmax, cmax, cuts = n_fixture(8)
bound = (-2 * a8 * th).exp() + (-2 * a8 * (1 - th)).exp() + 4 * (-2 * a8).exp()
assert cuts >= 3 and rmax <= bound and cmax <= bound and 1 - cmax >= Decimal(1) / (8 * 64)
getcontext().prec = 60
report['section2_column_gap_fixture'] = (f'PASS: p=8, {cuts} cell cuts, max row off-diag {float(rmax):.6f}, '
                                         f'max column off-diag {float(cmax):.6f}, both <= {float(bound):.6f}; column gap >= 1/(8p^2)')

# FORWARD-SMALL-A-AUDIT s1-2: ||K^-1|| <= alpha e^{3b/4} c_b^{-4} (1-e^{-b rho theta})^{-2},
# c_b^{-4} <= e^{a rho/3}, (1-e^{-x})^{-1} <= 2/x for 0<x<=1, x = pi theta/(alpha^2 rho).
# Explicit in theta for 0<theta<=1, so theta >= 1/(4p^2) gives a polynomial bound.
# INFORMATIONAL eventual thresholds used by section 2's "eventually".
def first_p(pred, lo=2, hi=2**200):
    assert pred(hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if pred(mid) else (mid, hi)
    return hi


def a_upper_continuous(p):
    l = float(dec_ln(16 * p))
    return 4 * l + 2 * math.sqrt(4 * math.pi * l) + math.pi


p_a5 = first_p(lambda p: a_upper_continuous(p) <= 5 * float(dec_ln(16 * p)))
p_exp = first_p(lambda p: (5 / 3) * (1 + 1 / p**2) * float(dec_ln(16 * p)) <= 2 * float(dec_ln(p)))
report['section2_eventual_thresholds_INFORMATIONAL'] = {
    'a<=5log(16p) (continuous alpha bound)': f'p >= {p_a5:.4g}',
    'exp(a rho/3)<=p^2 given a<=5log(16p)': f'p >= {p_exp:.4g}',
}

# ---------------------------------------------------------------- section 3
# Claim: a <= 16 L_p eventually, L_p = ceil(log2 p); then with P_setup = Cp + 64 p^2 L_p,
# 2^-P_setup e^{a/(4 theta)} < 2^-Cp because a/(4theta) < a p^2 <= 16 p^2 L_p and
# e^X < 2^{2X}. Exact alpha for p <= 4096, continuous alpha bound beyond (monotone gap).
first_ok = None
for p in range(2, 4097):
    a_hi_p = PI_HI * alpha_of(p) ** 2
    L = (p - 1).bit_length()
    ok = a_hi_p <= 16 * L
    if ok and first_ok is None:
        first_ok = p
    if not ok:
        first_ok = None
    if first_ok is not None:
        # precision inequality, exact: need 64 p^2 L > (a p^2)/ln 2, i.e. a < 64 L ln 2
        assert a_hi_p < 64 * L * LN2_LO
assert first_ok is not None
# beyond 4096: for 2^(k-1) < p <= 2^k, L_p = k and a <= a_upper_continuous(p) <= a_upper_continuous(2^k),
# so checking a_upper_continuous(2^k) < 16k covers every such p (and 16 log2 p outgrows 4 ln p beyond 2^400)
for k in range(12, 400):
    p = 2 ** k
    assert a_upper_continuous(p) + 1e-9 < 16 * k
report['section3_setup_precision'] = f'PASS: a <= 16 L_p for all p >= {first_ok} (exact alpha to 4096, continuous bound to 2^400); setup inequality holds with factor 64 ln2/16 = {float(64*LN2_LO/16):.3f} slack'

# Control: the old O(p)-bit absolute weight precision underflows for every p >= 32:
# the narrow weight nearest beta=0 has -log w >= a(1/4 - theta^2)/theta > C p log 2 with C=128.
for p in range(32, 4097):
    theta_hi = F(1, 2 * p * p - 1)
    a_lo = 4 * F(int(dec_ln(16 * p) * 10**6), 10**6)
    assert a_lo * (F(1, 4) - theta_hi ** 2) / theta_hi > 128 * p * LN2_HI
report['control_old_Cp_weight_precision_underflows'] = 'PASS (rejects): C=128, every p in 32..4096'

# ---------------------------------------------------------------- section 5
# Generic locality: Q = I - sigma H^T H, sigma = p^-20. Exact identity
#   H^-1 - sigma sum_{j<J} Q^j H^T = Q^J H^-1,
# so the error is <= (1-p^-40)^J p^10 <= p^10 e^{-p^2} (the PR's constant is sharp
# for this identity; a cruder geometric-series bound would give p^30).
# The approximant has bandwidth <= 2W(J-1)+W. Check both exactly on a banded 9x9.
def mat(n, f):
    return [[F(f(i, j)) for j in range(n)] for i in range(n)]


def mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def add(A, B, s=1):
    return [[A[i][j] + s * B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def inv(A):
    n = len(A)
    M = [row[:] + [F(int(i == j)) for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        r = next(r for r in range(c, n) if M[r][c] != 0)
        M[c], M[r] = M[r], M[c]
        pv = M[c][c]
        M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [row[n:] for row in M]


def bandwidth(A):
    return max((abs(i - j) for i, row in enumerate(A) for j, x in enumerate(row) if x != 0), default=0)


n, W, J = 9, 1, 3
H = mat(n, lambda i, j: (4 if i == j else (1 if j == i + 1 else (-2 if j == i - 1 else 0))))
Ht = [list(r) for r in zip(*H)]
sigma = F(1, 64)
I = mat(n, lambda i, j: int(i == j))
Q = add(I, [[sigma * x for x in row] for row in mul(Ht, H)], -1)
S, Qj = [[F(0)] * n for _ in range(n)], I
for _ in range(J):
    S = add(S, mul(Qj, Ht))
    Qj = mul(Qj, Q)
approx = [[sigma * x for x in row] for row in S]
Hinv = inv(H)
assert add(Hinv, approx, -1) == mul(Qj, Hinv)
assert bandwidth(H) == W and bandwidth(approx) <= 2 * W * (J - 1) + W
assert bandwidth(approx) == 2 * W * (J - 1) + W
# exponents: sigma=p^-20 needs ||H||<=p^10; gap p^-40; J=p^42 gives (1-p^-40)^J<=e^{-p^2};
# radius 2W(J-1)+W < 3 p^43 for W<p; halo p^48 > radius, core p^128 > halo; gA/L -> 0 iff 128-48-beta>0.
norm_pow, scale_pow = 10, 20
gap_pow = 2 * scale_pow
iter_pow = gap_pow + 2
radius_pow = iter_pow + 1
assert (gap_pow, iter_pow, radius_pow) == (40, 42, 43) and 48 > radius_pow and 128 - 48 - 1 > 0
report['section5_neumann_locality'] = 'PASS: exact tail identity and bandwidth 2W(J-1)+W on a banded fixture; exponents 40/42/43 < halo 48 < core 128'
# Control: a halo of p^40 would not cover the radius p^43.
assert not 40 > radius_pow
report['control_halo_p40_rejected'] = 'PASS (rejects)'

# ---------------------------------------------------------------- section 7
# Re-derive the nine paid rows from the prose table (not from LEDGER.json).
b_cert = F(335950991225108904267, 200000000000000000000000)
b = b_cert - F(1, 10**64)
q = b - F(1, 10**64)
a_eff = (q + b) / 2
r0, s = F(1, 10**64), F(1, 10**64)
eps, beta, delta = F(9999999, 10**7), F(9999997, 10**7), F(1, 10**7)
c = (3 - F(45, 16)) / 2
xi = eps * (1 + q) - F(3, 32) + s
assert 7**16 < 2**45 and c == F(3, 32)


def savings(eps, beta, xi, q, a_eff):
    return {
        'main_transforms': eps * q,
        'global_coordinate_router': a_eff,
        'fused_gaussian_groups': 1 - eps + q * beta,
        'group_bit_router': 1 - eps + a_eff * beta,
        'group_scans': 1 - eps + beta,
        'strassen_boundary': c + xi - eps,
        'radix_union_movement': xi + F(1, 2) - eps,
        'polynomial_products': eps,
        'core_face_corrections': 1 - (eps + beta + 48 - 128 + 2),
    }


sv = savings(eps, beta, xi, q, a_eff)
kmin = min(sv.values())
assert kmin == sv['main_transforms'] == eps * q
assert sv['strassen_boundary'] == eps * q + s
assert sv['fused_gaussian_groups'] - eps * q == delta * (1 - 2 * q) > 0
headline = F('0.001679754788150048')
assert headline < kmin
side = {
    '1-beta': 1 - beta, '1-beta-2(1-eps)': 1 - beta - 2 * (1 - eps), 'eps-beta': eps - beta,
    '1-eps-r0': 1 - eps - r0, 'chirp guard 1-(2xi-2)-r0-beta': 1 - (2 * xi - 2) - r0 - beta,
    'xi-1/2': xi - F(1, 2), 'eps-xi': eps - xi, '2-xi': 2 - xi, '128-48-beta': 128 - 48 - beta,
}
assert all(v > 0 for v in side.values())
g_ = side['chirp guard 1-(2xi-2)-r0-beta']
assert F('0.184140990423') < g_ < F('0.184140990424')
assert side['1-beta-2(1-eps)'] == delta
pr1758 = F('0.001679745508802299051546533685199973672313473419790800679752457380932784242972585600630181672224983')
assert headline - pr1758 > F('9.2793e-9')
selected = F(json.loads((ROOT / 'certificates/selected-result.json').read_text())['kappa'])
assert headline > selected
# Control: the old chirp guard (theta ~ 1/d, exponent beta+2xi-eps) fails at this point.
assert 1 - (2 * xi - eps) - r0 - beta < 0
# Control: theta ~ 1/p (theta power 1) would also fail the guard at this point.
assert 1 - (2 * xi - 1) - r0 - beta < 0
# Control: a group size beta = 1 - delta/2 breaks the membership row 1-beta-2(1-eps).
assert 1 - (1 - delta / 2) - 2 * (1 - eps) < 0
# Control: eps = 1 removes the superpolynomial source axis (1-eps-r0 < 0).
assert 1 - 1 - r0 < 0
report['section7_ledger'] = {
    'status': 'PASS: nine rows re-derived; minimum is eps*q; boundary = main + 1e-64; all side conditions positive',
    'kappa_headline': '0.001679754788150048',
    'eps_q_decimal': f'{Decimal(kmin.numerator) / Decimal(kmin.denominator):.30f}',
    'chirp_guard': f'{Decimal(g_.numerator) / Decimal(g_.denominator):.15f}',
    'gain_over_pr1758': f'{float(headline - pr1758):.6e}',
    'controls': 'old theta~1/d guard, theta~1/p guard, beta=1-delta/2 and eps=1 all fail (rejects)',
}

# Saturation: along the whole one-parameter family delta -> 0 (eps=1-delta, beta=1-3delta,
# xi=eps(1+q)-3/32+s) the minimum row is eps*q < q. So no outer-only reparametrization of
# this ledger, on this supplier, can reach q; the remaining outer headroom is (1-eps) q.
for k in range(4, 40, 3):
    d = F(1, 10**k)
    e_, be_ = 1 - d, 1 - 3 * d
    x_ = e_ * (1 + q) - F(3, 32) + s
    sv_ = savings(e_, be_, x_, q, a_eff)
    assert min(sv_.values()) == e_ * q < q
    assert 1 - (2 * x_ - 2) - r0 - be_ > 0 and x_ < e_ and x_ > F(1, 2)
headroom = q - headline
report['saturation'] = {
    'status': 'PASS: for delta=1e-4..1e-37 the binding row stays eps*q < q',
    'b_cert_PR1699': f'{Decimal(b_cert.numerator) / Decimal(b_cert.denominator):.24f}',
    'q': 'b_cert - 2e-64',
    'headroom_q_minus_headline': f'{float(headroom):.6e}',
    'meaning': 'outer-only changes to this ledger on the PR1699 supplier can add at most this much; larger gains need a better certified complex supplier endpoint',
}

report['status'] = 'PASS_PR1786_TRANSFER_AUDIT_SCOPED'
report['scope'] = ('Explicit inequalities of FINE-PRIME-PADDING.md sections 1-3, 5, 7 and the theta-dependence '
                   'of the cited PR1673/PR1758 bounds. Not checked: SHALLOW-TOEPLITZ circuit theorem, union '
                   'schedule, layout/cost-row derivations, supplier admission, all-size compiler.')
print(json.dumps(report, indent=2))
