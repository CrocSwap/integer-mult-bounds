"""Finer-constant copy of the retained Mercator moment engine (engines/moment.py): same algorithm and enclosure logic, evaluated in directed-rounding
integer fixed point on the 2^-33436 grid instead of exact rationals (same enclosure semantics, far faster).
33436 (even) Mercator terms (tail bounded by the next term), 5042 exponential terms.

Soundness of the integer evaluation: every quantity is non-negative and every operation is monotone, so flooring every intermediate gives a lower
bound and ceiling every intermediate gives an upper bound; the alternating Mercator sum tracks separate lower/upper term bounds and subtracts
upper terms from the lower sum (and lower terms from the upper sum). The enclosure is then outward-rounded to the 2^-33436 grid."""
from fractions import Fraction as F
from functools import lru_cache
from math import factorial
DYAD = 1 << 33436
LOGN = 33437   # the loop sums n = 1..LOGN-1 = 33436 terms: an EVEN alternating partial sum lies BELOW log(1+z), as the retained engine (n = 1..224) does
EXPN = 5042
def floor(x): return F(x.numerator*DYAD//x.denominator, DYAD)
def ceil(x): return -floor(-x)
@lru_cache(None)
def mercator(y):
    """Enclosure [s, s + next term] of log(y) for 1 <= y <= 3/2 by the alternating Mercator series in z = y-1."""
    z=y-1
    assert 0 <= z <= F(1,2)
    assert (LOGN - 1) % 2 == 0, 'an even number of terms is required: an odd partial sum lies above the log'
    p,q=z.numerator,z.denominator
    tl=tu=DYAD; sl=su=0
    for n in range(1, LOGN):
        tl=tl*p//q; tu=-((-tu*p)//q)          # z^n bounds
        lo=tl//n; hi=-((-tu)//n)
        if n & 1: sl+=lo; su+=hi
        else: sl-=hi; su-=lo
    tu=-((-tu*p)//q)                           # z^LOGN upper bound
    su+=-((-tu)//LOGN)
    return F(sl,DYAD), F(su,DYAD)

@lru_cache(None)
def logarithm(x):
    assert x >= 1
    k = 0
    while x >= 2: x /= 2; k += 1
    j = int(x >= F(3, 2))
    if j: x /= F(3, 2)
    a,b=mercator(x); c,d=mercator(F(3,2)); e,f=mercator(F(4,3))
    return floor(a+(k+j)*c+k*e), ceil(b+(k+j)*d+k*f)

def exponential(l,u):
    """Outward enclosure of exp on [l,u] (0 <= l <= u < 1/10) on the 2^-33436 grid: lower = partial sum through x^(EXPN-1)/(EXPN-1)!
    (all terms positive), upper = partial sum at u plus 2*u^EXPN/EXPN! (the tail is at most u^EXPN/EXPN! / (1 - u/(EXPN+1)) <= 2 u^EXPN/EXPN!)."""
    assert 0 <= l <= u < F(1,10)
    xl=l.numerator*DYAD//l.denominator; xu=-((-u.numerator*DYAD)//u.denominator)
    # lower: Taylor sum through x^(EXPN-1)/(EXPN-1)! with every term floored; upper: same with ceilings plus the tail 2*x^EXPN/EXPN!
    # (nested floors/ceilings: floor(floor(v/2^k)/j) = floor(v/(j 2^k)), so the shift form is the same rounding)
    tl=sl=DYAD; th=sh=DYAD
    for j in range(1, EXPN):
        tl=((xl*tl)>>33436)//j; sl+=tl
        c=-((-xu*th)>>33436); th=-((-c)//j); sh+=th
    c=-((-xu*th)>>33436); tn=-((-c)//EXPN)
    sh+=2*tn+2
    return F(sl,DYAD), F(sh,DYAD)

def moment(H,m,W,a,bad=False):
    lo=hi=F(0)
    for r,n in H.items():
        assert 0 < r < m and n > 0
        l,u=logarithm(F(m,r)); e,f=exponential(a*l,a*u)
        p=F(r*n,m*W);lo+=p*e;hi+=p*f
    if bad:
        l,u=logarithm(F(m));e,f=exponential(a*l,a*u)
        p=F(32*m*sum(H.values()),10**16*W)
        lo+=p*e;hi+=p*f
    return floor(lo),ceil(hi)
