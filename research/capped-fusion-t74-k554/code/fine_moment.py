"""Higher-precision independent base-two moment enclosure (same algorithm as base_two_moment.py, finer constants), evaluated in directed-rounding
integer fixed point on the 2^-33493 grid (lower bounds: floor every non-negative intermediate; upper bounds: ceil every intermediate), which is
monotone and therefore sound; same enclosure semantics as the exact-rational original, far faster."""
from fractions import Fraction as Q
from functools import lru_cache
GRID = 1 << 33493
LOG_TERMS = 10562
EXP_TERMS = 5042
def require(c, msg):
    if not c: raise ValueError(msg)
def _cd(a, b): return -((-a)//b)
SH = 33493
@lru_cache(None)
def log_unit(x):
    require(1 <= x <= 2, "logarithm range")
    z = (x-1)/(x+1)
    p, q = z.numerator, z.denominator
    p2, q2 = p*p, q*q
    pl = GRID*p//q; ph = _cd(GRID*p, q)            # z^1 bounds
    sl = sh = 0
    for j in range(LOG_TERMS):
        sl += pl//(2*j+1); sh += _cd(ph, 2*j+1)
        pl = pl*p2//q2; ph = _cd(ph*p2, q2)        # z^(2j+3)
    # tail 2 z^(2N+1) / ((2N+1)(1-z^2)), rounded up; ph = z^(2N+1) upper bound
    tail = _cd(2*ph*q2, (2*LOG_TERMS+1)*(q2-p2))
    return Q(2*sl, GRID), Q(2*sh+tail, GRID)
def log_bounds(x):
    require(x >= 1, "logarithm range")
    k = 0
    while x > 2:
        x /= 2; k += 1
    lo, hi = log_unit(x)
    l2, u2 = log_unit(Q(2))
    lo, hi = lo+k*l2, hi+k*u2
    return Q((lo*GRID).__floor__(), GRID), Q((hi*GRID).__ceil__(), GRID)
def exp_bounds(x):
    """Outward enclosure of exp(x), 0 <= x < 1, on the 1/GRID grid: lower = partial sum through x^(EXP_TERMS-1)/(EXP_TERMS-1)! (positive terms),
    upper = partial sum + 2*x^EXP_TERMS/EXP_TERMS! (tail <= that for x < 1)."""
    require(0 <= x < 1, "exponential range")
    xl = x.numerator*GRID//x.denominator; xu = _cd(x.numerator*GRID, x.denominator)
    tl = th = GRID; sl = sh = GRID
    for j in range(1, EXP_TERMS):
        tl = ((tl*xl) >> SH)//j; th = _cd(-((-th*xu) >> SH), j)
        sl += tl; sh += th
    tn = _cd(-((-th*xu) >> SH), EXP_TERMS)
    return Q(sl, GRID), Q(sh+2*tn+2, GRID)
def moment(m, W, entries, saving):
    lo = hi = Q(0)
    for t, count in entries:
        t, count = int(t), int(count)
        require(0 < t < m and count > 0, "improper child")
        l, u = log_bounds(Q(m, t))
        lo += Q(t*count, m*W)*exp_bounds(saving*l)[0]
        hi += Q(t*count, m*W)*exp_bounds(saving*u)[1]
    return Q((lo*GRID).__floor__(), GRID), Q((hi*GRID).__ceil__(), GRID)
