"""Exact and independent moment functions extracted without body changes from PR65.
Source snapshots and hashes are retained in arithmetic-sources/.
Credits: Rohan Arun, Dominik Scholz, icekylinx, Zhihao Chen, RaD and prior authors.
"""
import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'arithmetic-sources'))
import binary_frame_math as arithmetic
refine=sys.modules[__name__]

def floor_scaled(x, denominator):
    return (x * denominator).numerator // (x * denominator).denominator

def ceiling_scaled(x, denominator):
    return -floor_scaled(-x, denominator)

def exact_moment(m, width, rows, saving, degree=8, rounding=10**40):
    """Bound sum n*t/(mW)*exp(saving*log(m/t)) entirely in Q.

    At 0 <= u <= v < 1, S_d(u) is a lower bound for exp(u).
    The tail at v has first term v^(d+1)/(d+1)!; successive ratios
    are at most v/(d+2). Thus S_d(v)+first/(1-v/(d+2)) is upper.
    Directed rounding per exp bound preserves both inequalities.
    The inherited logarithm helper encloses log(m/t) rationally.
    """
    assert type(saving) is Q and 0 < saving < 1 and degree >= 1
    lo, hi = Q(), Q()
    terms = {}
    for t, count in sorted(rows.items()):
        assert type(t) is int and type(count) is int and 0 < t < m and count > 0
        loglo, loghi = arithmetic.logs(Q(m, t))
        u, v = saving*loglo, saving*loghi
        assert 0 <= u <= v < 1
        lower = sum((u**j / factorial(j) for j in range(degree+1)), Q())
        upper = sum((v**j / factorial(j) for j in range(degree+1)), Q())
        upper += v**(degree+1)/factorial(degree+1)/(1-v/Q(degree+2))
        lower = Q(floor_scaled(lower, rounding), rounding)
        upper = Q(ceiling_scaled(upper, rounding), rounding)
        weight = Q(t*count, m*width)
        lo += weight*lower
        hi += weight*upper
        terms[t] = dict(weight=weight, log_lower=loglo, log_upper=loghi,
                        exp_lower=lower, exp_upper=upper)
    return dict(saving=saving, lower=lo, upper=hi, strict_gap=1-hi,
                degree=degree, rounding_denominator=rounding, terms=terms)

def log_interval(x):
    """Atanh expansion with independent 3/2 reduction and 60 exact terms."""
    assert x >= 1
    k = 0
    while x > Q(3, 2):
        x /= Q(3, 2)
        k += 1
    def small(y):
        z = (y-1)/(y+1)
        power, total = z, Q()
        for j in range(60):
            total += power/Q(2*j+1)
            power *= z*z
        return 2*total, 2*total+2*power/(121*(1-z*z))
    lo, hi = small(x)
    blo, bhi = small(Q(3, 2))
    return lo+k*blo, hi+k*bhi

def independent_moment(profile, saving, recorded_terms):
    low, high = Q(), Q()
    rows = {int(t): n for t, n in profile['child_multiplicities'].items()}
    for t, n in sorted(rows.items()):
        lo, hi = log_interval(Q(profile['m'], t))
        recorded = recorded_terms[str(t)]
        assert Q(recorded['log_lower']) <= lo <= hi <= Q(recorded['log_upper'])
        u, v = lo*saving, hi*saving
        assert 0 < u <= v < Q(1, 1000)
        # Directed rounding of input logs bounds rational denominator sizes.
        u = Q(refine.floor_scaled(u, 10**40), 10**40)
        v = Q(refine.ceiling_scaled(v, 10**40), 10**40)
        tlo, thi = Q(1), Q(1)
        elo, ehi = Q(1), Q(1)
        for j in range(1, 13):
            tlo, thi = tlo*u/j, thi*v/j
            elo, ehi = elo+tlo, ehi+thi
        # First omitted term is degree13; subsequent ratios <1/2.
        ehi += 2*thi*v/13
        weight = Q(t*n, profile['m']*profile['W'])
        low += weight*Q(refine.floor_scaled(elo, 10**40), 10**40)
        high += weight*Q(refine.ceiling_scaled(ehi, 10**40), 10**40)
    return low, high
