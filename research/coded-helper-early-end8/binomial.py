"""Independent integer-enclosed binomial powers, with a positive geometric tail.

No logarithms, exponentials, floating point or predecessor power engine.
"""
from functools import lru_cache
from fractions import Fraction

INTERNAL = 10**44
SCALE = 10**30
TERMS = 7000


def require(ok, message):
    if not ok:
        raise ValueError(message)


def ceiling(numerator, denominator):
    return -(-numerator // denominator)


@lru_cache(None)
def power_bounds(rank, saving):
    """Outward bounds on SCALE*r^(1-saving), for 0<saving<1 and r>=0.

For z=1-1/r, (1-z)^saving = 1-sum_{k>=1} c_k, c_k>0.
c_1=saving*z and c_(k+1)=c_k*z*(k-saving)/(k+1).
Every ratio is <z, so the omitted positive tail is at most
c_(N+1)/(1-z). Each recurrence rounds integer intervals outward.
"""
    require(type(rank) is int and 0 <= rank <= 73 and isinstance(saving, Fraction) and
            0 < saving < 1, 'Power domain')
    if rank in (0, 1):
        return rank*SCALE, rank*SCALE
    p, q = saving.numerator, saving.denominator
    numerator, denominator = p*(rank-1)*INTERNAL, q*rank
    lo, hi = numerator//denominator, ceiling(numerator, denominator)
    total_lo = total_hi = 0
    for k in range(1, TERMS+1):
        total_lo += lo
        total_hi += hi
        multiplier = (rank-1)*(k*q-p)
        divisor = rank*(k+1)*q
        lo = lo*multiplier//divisor
        hi = ceiling(hi*multiplier, divisor)
    lower = rank*(INTERNAL-total_hi-rank*hi)
    upper = rank*(INTERNAL-total_lo)
    divisor = INTERNAL//SCALE
    require(0 < lower <= upper, 'Binomial interval')
    return lower//divisor, ceiling(upper, divisor)
