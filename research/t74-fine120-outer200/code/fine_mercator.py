"""Finer-constant copy of the retained Mercator moment engine (engines/moment.py): identical algorithm and enclosure logic,
DYAD 2^800 outward rounding, 800 Mercator terms (tail bounded by the next term), 70 exponential terms."""
from fractions import Fraction as F
from functools import lru_cache
DYAD = 1 << 800
LOGN = 800
EXPN = 70
def floor(x): return F(x.numerator*DYAD//x.denominator, DYAD)
def ceil(x): return -floor(-x)
@lru_cache(None)
def logarithm(x):
    assert x >= 1
    k = 0
    while x >= 2: x /= 2; k += 1
    j = int(x >= F(3, 2))
    if j: x /= F(3, 2)
    def mercator(y):
        z=y-1
        assert 0 <= z <= F(1,2)
        t=z; s=F(0)
        for n in range(1, LOGN):
            s += (t if n & 1 else -t)/n
            t *= z
        return s, s+t/LOGN
    a,b=mercator(x); c,d=mercator(F(3,2)); e,f=mercator(F(4,3))
    return floor(a+(k+j)*c+k*e), ceil(b+(k+j)*d+k*f)
def exponential(l,u):
    assert 0 <= l <= u < F(1,10)
    def poly(x):
        s=t=F(1)
        for j in range(1,EXPN): t=t*x/j; s+=t
        return s,t
    lo,_=poly(l);hi,last=poly(u)
    return floor(lo),ceil(hi+last*u/EXPN/(1-u/(EXPN+1)))
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
