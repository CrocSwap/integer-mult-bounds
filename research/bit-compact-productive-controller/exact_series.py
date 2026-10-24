"""Independent positive-series rational intervals, no external numeric library."""
from fractions import Fraction as F
from functools import lru_cache
S=10**40
def need(c,m):
    if not c:raise ValueError(m)
def floor(q):return q.numerator//q.denominator
def ceil(q):return -((-q.numerator)//q.denominator)
def grid(lo,hi):return F(floor(lo*S),S),F(ceil(hi*S),S)
def logratio(z,n=60):
    need(0<=z<=F(1,3),'Reduced log domain');s=F(0);p=z
    for j in range(n):s+=2*p/(2*j+1);p*=z*z
    return s,s+2*p/((2*n+1)*(1-z*z))
LN2=logratio(F(1,3))
@lru_cache(None)
def logbound(x):
    if x==1:return F(0),F(0)
    k=x.bit_length()-1;a,b=logratio(F(x-2**k,x+2**k));return grid(a+k*LN2[0],b+k*LN2[1])
@lru_cache(None)
def expbound(y):
    need(0<=y<7,'Bounded exp');s=p=F(1);n=90
    for j in range(1,n+1):p=p*y/j;s+=p
    return grid(s,s+(p*y/(n+1))/(1-y/(n+2)))
@lru_cache(None)
def power(x,t):
    if x==1:return F(1),F(1)
    a,b=logbound(x);a,b=grid(t*a,t*b);return expbound(a)[0],expbound(b)[1]
def moment(profile,t):
    vv=[(n,power(k,t))for k,n in profile.items()];return sum(n*v[0]for n,v in vv),sum(n*v[1]for n,v in vv)
def mul(a,b):return a[0]*b[0],a[1]*b[1]
def div(a,b):return a[0]/b[1],a[1]/b[0]
def interval(a):return {'lower':str(a[0]),'upper':str(a[1]),'display':float(sum(a)/2)}
