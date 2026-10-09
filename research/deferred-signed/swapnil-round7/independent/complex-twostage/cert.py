"""Certified complex saving a_c from a residual histogram {rank r: count n_r}, exact rationals only.

Moment condition (PR #10 batched recursion, sigma = 1 - a):  sum_r n_r r^sigma / (W m^sigma) < 1.
Write it as  M(a) = sum_r w_r (m/r)^a,  w_r = r n_r / (W m)  (so sum_r w_r = s/(W m) < 1).
We bound (m/r)^a <= exp(a U_r) with a rational U_r >= ln(m/r), and exp(x) <= 1 + x + x^2/2 + x^3/(6(1 - x/4))
for 0 <= x < 4 (the Taylor tail sum_{j>=3} x^j/j! is dominated by the geometric series x^3/6 sum (x/4)^i).
ln upper bounds: ln y = k ln 2 + ln(y/2^k), y/2^k in [1, 2); ln z = 2 atanh((z-1)/(z+1)), atanh truncated after
K odd terms with the tail bounded by u^(2K+1) / ((2K+1)(1-u^2)); every term is exact, rounded up to 10^-40.
a_c = largest grid point a with M(a) < 1 (binary search; M is increasing in a).
Usage: imported by run.py (cert(hist, W, m) -> (a_c, 1 - M(a_c)))."""
from fractions import Fraction as Q

PREC = 10 ** 40

def up(x): return Q(-((-x.numerator * PREC) // x.denominator), PREC)          # round up to the 10^-40 grid

def atanh_up(u, K=40):
    s = Q(0); p = u
    for k in range(K): s += p / (2 * k + 1); p *= u * u
    return s + p / ((2 * K + 1) * (1 - u * u))                                    # p = u^(2K+1)

LN2 = up(2 * atanh_up(Q(1, 3)))

def ln_up(y):
    y = Q(y); assert y >= 1
    k = 0
    while y >= 2: y /= 2; k += 1
    return up(k * LN2 + 2 * atanh_up((y - 1) / (y + 1)))

def exp_up(x):
    assert 0 <= x < 4
    return 1 + x + x * x / 2 + x ** 3 / (6 * (1 - x / 4))

def moment(ws, a): return sum(w * exp_up(a * U) for w, U in ws)

def cert(hist, W, m, grid=10 ** 12):
    ws = [(Q(r * n, W * m), ln_up(Q(m, r))) for r, n in hist.items()]
    lo, hi = 0, grid // 1000                    # a < 10^-3 (far above any saving here)
    assert moment(ws, Q(hi, grid)) > 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if moment(ws, Q(mid, grid)) < 1: lo = mid
        else: hi = mid
    a = Q(lo, grid); return a, 1 - moment(ws, a)
