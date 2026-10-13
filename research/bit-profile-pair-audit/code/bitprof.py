"""Exact paid-profile arithmetic for bitE8 bit words.

Two facts are used.

(1) The certified saving c of a bit supplier with modulus m, live port-register count W and paid
    profile n (n_r = number of elementary paid climbs of rank r) is the unique root a > 0 of

        Psi(a) := sum_r n_r * r * ((m/r)^a - 1)  =  D,     D := m*W - sum_r r*n_r .

    Equivalently, since Psi(a) = m^a * G(a) - M with G(a) = sum_r n_r r^(1-a) and M = sum_r r n_r,
    and both m^a and G are strictly increasing in a, for ANY fixed a0 the certified saving is a
    strictly decreasing function of the single weighted count  G(a0) = sum_r n_r r^(1-a0).
    Rank-profile search is therefore a linear-objective problem, and a candidate word can be priced
    exactly in O(#gates) with no root finding.

(2) G decomposes over registers: a register's contribution depends only on the gates that touch it,
    so the objective delta of a gate transport is the sum of the deltas of the two registers it
    touches, and a k-move improvement requires the moves to share registers.

The root of (1) is certified here with exact rational interval arithmetic (own ln/exp bounds):
no floating point and no dependence on the repository's moment engine is used.
"""
from fractions import Fraction as F
from collections import Counter

# ---------------------------------------------------------------- rigorous rational ln / exp
def _atanh_ln_bounds(z, terms=60):
    """1 <= z < 3/2 -> rational interval for ln z via 2*atanh(t), t=(z-1)/(z+1) <= 1/5."""
    t = (z - 1) / (z + 1)
    s = F(0); term = t
    for n in range(terms):
        s += term / (2 * n + 1)
        term *= t * t
    rem = 2 * term / ((2 * terms + 1) * (1 - t * t))
    return 2 * s, 2 * (s + rem)

def ln_bounds(x, terms=60):
    """x rational >= 1 -> (lo,hi) with lo <= ln x <= hi."""
    assert x >= 1
    k = 0
    while x >= 2:
        x /= 2; k += 1
    j = 0
    if x >= F(3, 2):
        x /= F(3, 2); j = 1
    lo, hi = _atanh_ln_bounds(x, terms)
    l32 = _atanh_ln_bounds(F(3, 2), terms)
    l43 = _atanh_ln_bounds(F(4, 3), terms)
    ln2_lo, ln2_hi = l32[0] + l43[0], l32[1] + l43[1]
    return k * ln2_lo + j * l32[0] + lo, k * ln2_hi + j * l32[1] + hi

def exp_bounds(y, terms=60):
    """0 <= y <= 1 -> (lo,hi) with lo <= exp(y) <= hi."""
    assert 0 <= y <= 1
    s = F(0); term = F(1)
    for n in range(terms):
        s += term
        term *= y / (n + 1)
    return s, s + term / (1 - y / (terms + 1))

def pow_bounds(base, a, terms=60):
    """base rational >= 1, a rational in [0,1] -> (lo,hi) with lo <= base**a <= hi."""
    assert base >= 1 and 0 <= a <= 1
    llo, lhi = ln_bounds(base, terms)
    return exp_bounds(a * llo, terms)[0], exp_bounds(a * lhi, terms)[1]

# ---------------------------------------------------------------- the fee functional
def ln_table(ranks, m, terms=34):
    """ln bounds for each distinct base m/r; computed once, reused for every a."""
    return {r: ln_bounds(F(m, r) if F(m, r) >= 1 else 1 / F(m, r), terms) for r in ranks}

def fee_bounds(n, m, a, lnb, terms=34):
    """rational interval for Psi(a) = sum_r n_r * r * ((m/r)^a - 1) using precomputed ln bounds"""
    lo = F(0); hi = F(0)
    for r, c in n.items():
        if not c: continue
        llo, lhi = lnb[r]
        if F(m, r) >= 1:
            plo = exp_bounds(a * llo, terms)[0]; phi = exp_bounds(a * lhi, terms)[1]
        else:
            u = exp_bounds(a * llo, terms)[1]; v = exp_bounds(a * lhi, terms)[0]
            plo, phi = 1 / u, 1 / v
        w = c * r
        lo += w * (plo - 1); hi += w * (phi - 1)
    return lo, hi

def fee_float(n, m, a):
    import math
    return sum(c * r * (math.exp(a * math.log(m / r)) - 1) for r, c in n.items() if c)

def profile_deficit(n, m, W):
    return m * W - sum(r * c for r, c in n.items())

def certify_c(n, m, W, digits=24, terms=34):
    """exact rational bracket [q/10^digits, (q+1)/10^digits] for the certified saving c."""
    D = profile_deficit(n, m, W)
    assert D > 0, 'non-positive deficit'
    lnb = ln_table(set(n), m, terms)
    lo, hi = F(0), F(1, 10)
    assert fee_bounds(n, m, hi, lnb, terms)[0] > D > fee_bounds(n, m, lo, lnb, terms)[1]
    # coarse float narrowing, then exact rational bisection on the grid q/10^digits
    piv = sorted(n); lo_f, hi_f = 0.0, 0.1
    for _ in range(80):
        mid = (lo_f + hi_f) / 2
        if fee_float(n, m, mid) < D: lo_f = mid
        else: hi_f = mid
    scale = 10 ** digits
    span = 10 ** (digits - 6)
    qlo = max(0, int(lo_f * scale) - span); qhi = min(scale // 10, int(hi_f * scale) + span)
    assert qlo < qhi
    while qhi - qlo > 1:
        mid = (qlo + qhi) // 2
        if fee_bounds(n, m, F(mid, scale), lnb, terms)[1] < D: qlo = mid
        else: qhi = mid
    return F(qlo, scale), F(qhi, scale), D

def weighted_count(n, a0):
    """G(a0) = sum_r n_r r^(1-a0) as a float (for search ordering)"""
    return sum(c * (r ** (1.0 - a0)) for r, c in n.items())

# ---------------------------------------------------------------- the shipped (surcharged) pricer
SURCHARGE_DEN = 10 ** 16      # 32*m^2 rank-one fallback calls per paid child, charged at rank one

def surcharge_num(n, m):
    return 32 * m * m * sum(n.values())

def fee_bounds_bad(n, m, a, lnb, terms=34):
    lo, hi = fee_bounds(n, m, a, lnb, terms)
    llo, lhi = lnb['_m']
    v = exp_bounds(a * llo, terms)[0]; u = exp_bounds(a * lhi, terms)[1]
    K = F(surcharge_num(n, m), SURCHARGE_DEN)
    return lo + K * v, hi + K * u

def certify_c_bad(n, m, W, digits=24, terms=34):
    """exact rational bracket for the shipped certified saving c, including the inherited
    bad-envelope rank-one fallback surcharge:  Psi(a) + 32 m^2 (sum_r n_r) m^a / 10^16 = D."""
    D = profile_deficit(n, m, W)
    lnb = ln_table(set(n), m, terms); lnb['_m'] = ln_bounds(F(m), terms)
    assert fee_bounds_bad(n, m, F(1, 10), lnb, terms)[0] > D > fee_bounds_bad(n, m, F(0), lnb, terms)[1]
    K = surcharge_num(n, m)
    lo_f, hi_f = 0.0, 0.1
    for _ in range(100):
        mid = (lo_f + hi_f) / 2
        if fee_float(n, m, mid) + K * (m ** mid) / SURCHARGE_DEN < D: lo_f = mid
        else: hi_f = mid
    scale = 10 ** digits; span = 10 ** (digits - 6)
    qlo = max(0, int(lo_f * scale) - span); qhi = min(scale // 10, int(hi_f * scale) + span)
    assert qlo < qhi
    while qhi - qlo > 1:
        mid = (qlo + qhi) // 2
        if fee_bounds_bad(n, m, F(mid, scale), lnb, terms)[1] < D: qlo = mid
        else: qhi = mid
    return F(qlo, scale), F(qhi, scale), D
