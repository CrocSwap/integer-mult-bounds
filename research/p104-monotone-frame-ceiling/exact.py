"""Enclose rank powers with integer arithmetic and explicit series tails.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from functools import cache

BITS = 160
UNIT = 1 << BITS


def ceil_div(a, b):
    return -(-a // b)


def log_unit(a, b):
    """Enclose log(a/b), for 1 <= a/b <= 2, in units of 2^-BITS."""
    if not b <= a <= 2*b:
        raise ValueError('The logarithm argument is outside [1,2]')
    z = Fraction(a-b, a+b)
    power = z
    lower = upper = 0
    for j in range(80):
        term = 2*power/(2*j+1)
        lower += term.numerator*UNIT // term.denominator
        upper += ceil_div(term.numerator*UNIT, term.denominator)
        power *= z*z
    tail = 2*power/(161*(1-z*z))
    upper += ceil_div(tail.numerator*UNIT, tail.denominator)
    return lower, upper


@cache
def log_rank(r):
    if not isinstance(r, int) or r < 1:
        raise ValueError('The rank must be a positive integer')
    b = r.bit_length()-1
    lo, hi = log_unit(r, 1 << b)
    two_lo, two_hi = log_unit(2, 1)
    return lo+b*two_lo, hi+b*two_hi


def exp_small(lo, hi):
    """Enclose exp(x), where 0 <= lo/UNIT <= x <= hi/UNIT <= 1."""
    if not 0 <= lo <= hi <= UNIT:
        raise ValueError('The exponential argument is outside [0,1]')
    lower = upper = term_lo = term_hi = UNIT
    for j in range(1, 49):
        term_lo = term_lo*lo // (UNIT*j)
        term_hi = ceil_div(term_hi*hi, UNIT*j)
        lower += term_lo
        upper += term_hi
    next_hi = ceil_div(term_hi*hi, UNIT*49)
    return lower, upper+2*next_hi


@cache
def power(r, kappa):
    """Return integer bounds for r^(1-kappa) times UNIT."""
    if r == 0:
        return 0, 0
    if not 0 <= kappa < 1:
        raise ValueError('The saving must be in [0,1)')
    lo, hi = log_rank(r)
    xlo = lo*kappa.numerator // kappa.denominator
    xhi = ceil_div(hi*kappa.numerator, kappa.denominator)
    elo, ehi = exp_small(xlo, xhi)
    return r*UNIT*UNIT//ehi, ceil_div(r*UNIT*UNIT, elo)
