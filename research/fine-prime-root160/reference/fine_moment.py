"""Higher-precision independent base-two moment enclosure (same algorithm as base_two_moment.py, finer constants)."""
from fractions import Fraction as Q
GRID = 10**100
LOG_TERMS = 110
EXP_TERMS = 40
def require(c, msg):
    if not c: raise ValueError(msg)
def log_unit(x):
    require(1 <= x <= 2, "logarithm range")
    z = (x-1)/(x+1)
    lo = 2*sum((z**(2*j+1)/(2*j+1) for j in range(LOG_TERMS)), Q(0))
    return lo, lo+2*z**(2*LOG_TERMS+1)/((2*LOG_TERMS+1)*(1-z*z))
def log_bounds(x):
    k = 0
    while x > 2:
        x /= 2; k += 1
    lo, hi = log_unit(x)
    l2, u2 = log_unit(Q(2))
    lo, hi = lo+k*l2, hi+k*u2
    return Q((lo*GRID).__floor__(), GRID), Q((hi*GRID).__ceil__(), GRID)
def exp_bounds(x):
    require(0 <= x < 1, "exponential range")
    term = total = Q(1)
    for j in range(1, EXP_TERMS):
        term *= x/j; total += term
    tail = term*x/EXP_TERMS/(1-x/(EXP_TERMS+1))
    return total, total+tail
def moment(m, W, entries, saving):
    lo = hi = Q(0)
    for t, count in entries:
        t, count = int(t), int(count)
        require(0 < t < m and count > 0, "improper child")
        l, u = log_bounds(Q(m, t))
        lo += Q(t*count, m*W)*exp_bounds(saving*l)[0]
        hi += Q(t*count, m*W)*exp_bounds(saving*u)[1]
    return Q((lo*GRID).__floor__(), GRID), Q((hi*GRID).__ceil__(), GRID)
