"""Positive generalized-binomial interval engine, integer-only fixed point.

For 0<=b<1, y in[1,2], z=1-1/y, y**b=sum (b)_j*z**j/j!.
After N terms, successive term ratios <= z, so tail<=next/(1-z).
Each term is bounded outward at 2**256, then combined by interval products.
No logarithm, exponential, floating arithmetic or predecessor numeric engine.
OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
S=1<<256
N=256
def need(ok,msg):
    if not ok:raise ValueError(msg)
def floor(q):return q.numerator//q.denominator
def ceil(q):return -((-q.numerator)//q.denominator)
def mul(a,b):return a[0]*b[0]//S,-((-a[1]*b[1])//S)
def unit(y,b):
    need(1<=y<=2 and 0<=b<1,'binomial domain')
    z=1-1/y;lo=hi=total_lo=total_hi=S
    for j in range(1,N+1):
        ratio=(b+j-1)*z/j
        lo=floor(lo*ratio);hi=ceil(hi*ratio)
        total_lo+=lo;total_hi+=hi
    ratio=(b+N)*z/(N+1)
    tail=ceil(hi*ratio/(1-z))
    return total_lo,total_hi+tail
def power(y,b):
    need(y>=1,'power domain');k=0
    while y>2:y/=2;k+=1
    a=unit(y,b);two=unit(Q(2),b)
    for _ in range(k):a=mul(a,two)
    return a
def moment(profile,b,W):
    need(type(W)is int and W>0 and 0<=b<1,'moment domain')
    lo=hi=0
    for r,n in profile.items():
        need(type(r)is int and type(n)is int and 0<r<73 and n>0,'paid child')
        a,z=power(Q(73,r),b);lo+=n*r*a;hi+=n*r*z
    return Q(lo,S*73*W),Q(hi,S*73*W)
