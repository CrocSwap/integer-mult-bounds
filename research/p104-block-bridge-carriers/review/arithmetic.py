"""Rational arithmetic retained from concurrent independent reviewer A.
Jerry Chen / @CubeJerry; substantial OpenAI GPT-6 Astra Pro assistance.
Apache-2.0. This predates and is independent of the carrier author arithmetic.
"""
from fractions import Fraction as Q
from functools import lru_cache

def need(ok, message):
    if not ok:
        raise ValueError(message)

def log_unit(u):
    need(Q(1)<=u<=Q(2), 'Logarithm range reduction')
    z = (u-1)/(u+1)
    total, power, m = Q(0), z, 48
    for j in range(m):
        total += power/(2*j+1)
        power *= z*z
    lo = 2*total
    return lo, lo+2*power/((2*m+1)*(1-z*z))

@lru_cache(maxsize=None)
def log_bounds(r):
    need(type(r) is int and r>=1, 'Positive integer logarithm')
    k = r.bit_length()-1
    a,b = log_unit(Q(2))
    c,d = log_unit(Q(r,2**k))
    return k*a+c,k*b+d

def exp_polynomial(a, degree):
    need(Q(0)<=a<=Q(1), 'Alternating exponential range')
    total = term = Q(1)
    for j in range(1,degree+1):
        term *= -a/j
        total += term
    return total

@lru_cache(maxsize=None)
def power_bounds(r,kappa):
    need(Q(0)<=kappa<=Q(1), 'Exponent domain')
    if r==1 or kappa==0:
        return Q(r),Q(r)
    lo,hi = log_bounds(r)
    # exp(-a) decreases: odd-degree Taylor at the upper a is a lower bound;
    # even-degree Taylor at the lower a is an upper bound, by alternating terms.
    lower = r*exp_polynomial(kappa*hi,11)
    upper = r*exp_polynomial(kappa*lo,12)
    need(0<lower<=upper<=r, 'Positive ordered power enclosure')
    return lower,upper

def interval_sum(coefficients,kappa):
    lo=hi=Q(0)
    for r,c in sorted(coefficients.items()):
        a,b = power_bounds(r,kappa)
        lo += c*(a if c>=0 else b)
        hi += c*(b if c>=0 else a)
    return lo,hi

def enclosure(bounds, places=14):
    scale = 10**places
    low = bounds[0].numerator*scale//bounds[0].denominator
    high = -((-bounds[1].numerator*scale)//bounds[1].denominator)
    def text(value):
        sign = '-' if value<0 else ''
        value=abs(value)
        return sign+str(value//scale)+'.'+str(value%scale).zfill(places)
    return [text(low),text(high)]
