"""Outward-rounded rational enclosures for prime-power cyclic kernels."""
from fractions import Fraction as F
import math
from functools import lru_cache

BITS=1536
SCALE=1<<BITS
def hull(lo,hi):
    a=lo*SCALE;b=hi*SCALE
    return (F(a.numerator//a.denominator,SCALE),F(-((-b.numerator)//b.denominator),SCALE))
def point(x):return (F(x),F(x))
def add(a,b):return hull(a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[1],-a[0])
def sub(a,b):return add(a,neg(b))
def mul(a,b):
    v=[x*y for x in a for y in b];return hull(min(v),max(v))
def scale(a,s):return mul(a,point(s))
def cadd(a,b):return (add(a[0],b[0]),add(a[1],b[1]))
def cneg(a):return (neg(a[0]),neg(a[1]))
def cmul(a,b):return (sub(mul(a[0],b[0]),mul(a[1],b[1])),add(mul(a[0],b[1]),mul(a[1],b[0])))
ZERO=(point(0),point(0));ONE=(point(1),point(0))

def atan_inverse(q):
    # Alternating series, with an exact bound by the next omitted term.
    total=F(0);power=F(1,q);j=0
    while True:
        total+=(-1 if j%2 else 1)*power/(2*j+1)
        power/=q*q;j+=1
        remainder=power/(2*j+1)
        if remainder<F(1,1<<(BITS+16)):break
    other=total+(-1 if j%2 else 1)*remainder
    return hull(min(total,other),max(total,other))

@lru_cache(maxsize=None)
def pi_interval():return sub(scale(atan_inverse(5),16),scale(atan_inverse(239),4))

def root_interval(r,k):
    if r<3 or math.gcd(r,k)!=1 or not 0<k<r:raise ValueError('invalid primitive embedding')
    signed=k if 2*k<=r else k-r
    theta=scale(pi_interval(),F(2*signed,r))
    if max(abs(theta[0]),abs(theta[1]))>4:raise ValueError('angle bound')
    itheta=(point(0),theta)
    total=term=ONE
    # Taylor remainder for complex exp: <=exp(4)*4^(N+1)/(N+1)! <128*...
    n=0
    while True:
        n+=1;term=cmul(term,itheta);term=(scale(term[0],F(1,n)),scale(term[1],F(1,n)));total=cadd(total,term)
        remainder=F(128*4**(n+1),math.factorial(n+1))
        if remainder<F(1,1<<(BITS+16)):break
    widen=(-remainder,remainder)
    return (add(total[0],widen),add(total[1],widen))

@lru_cache(maxsize=None)
def kernel(r,k):
    z=root_interval(r,k)
    powers=[ONE]
    for _ in range(r-1):powers.append(cmul(powers[-1],z))
    # f_j=product_(s=j+1)^(r-1)(1-zeta^s), P=f/r.
    a=[ZERO]*r;a[-1]=ONE
    for j in range(r-2,-1,-1):a[j]=cmul(a[j+1],cadd(ONE,cneg(powers[j+1])))
    return [(scale(x,F(1,r)),scale(y,F(1,r))) for x,y in a]
