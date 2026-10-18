#!/usr/bin/env python3
"""Exact discovery-only endpoint refinement; final inherited checks still run.

Derived from PR2863 review/moment_core.py (SHA256
22290074f138fa9b902e5f6f6e8a0ec366d6f812992adb6df9b617ce952fb852).
Credit its Codex-assisted reviewer and retained ancestry; Apache-2.0.
All arithmetic below is outward-directed integer arithmetic at 512 bits.
The conservative surcharge is exactly the retained moment.py charge, converted
to an extra rank-one multiplicity after scaling every count and W by 10^16.
"""
from fractions import Fraction as Q
from functools import lru_cache

S = 1 << 512
LOG_TERMS = 220
EXP_TERMS = 114

def ceildiv(a,b): return -((-a)//b)
def down(q): return q.numerator*S//q.denominator
def up(q): return ceildiv(q.numerator*S,q.denominator)

def log_ratio(a,b):
    assert 1 <= Q(a,b) <= 2
    z=Q(a-b,a+b); zl=down(z); zu=up(z)
    z2l=zl*zl//S; z2u=ceildiv(zu*zu,S)
    vl,vu=zl,zu; lo=hi=0
    for j in range(LOG_TERMS):
        lo += vl//(2*j+1); hi += ceildiv(vu,2*j+1)
        vl=vl*z2l//S; vu=ceildiv(vu*z2u,S)
    # Positive tail: 2*z^(2J+1)/((2J+1)*(1-z^2)), z<=1/3.
    tail=ceildiv(9*vu,4*(2*LOG_TERMS+1))
    return 2*lo,2*hi+tail

@lru_cache(None)
def log_int(n):
    assert type(n) is int and n>=1
    if n==1: return 0,0
    k=n.bit_length()-1; l,u=log_ratio(2,1); a,b=log_ratio(n,1<<k)
    return k*l+a,k*u+b

def exp_positive(t):
    assert 0<=t<=S//2
    vl=vu=S;lo=hi=S
    for j in range(1,EXP_TERMS+1):
        vl=vl*t//(S*j);vu=ceildiv(vu*t,S*j);lo+=vl;hi+=vu
    return lo,hi+2*ceildiv(vu*t,S*(EXP_TERMS+1))

def power(n,alpha):
    l,u=log_int(n)
    el,_=exp_positive(down(alpha*Q(l,S)))
    _,eu=exp_positive(up(alpha*Q(u,S)))
    return n*(S*S//eu),n*ceildiv(S*S,el)

def moment(H,m,W,a,bad=False):
    assert 0<a<Q(1,100) and all(type(r) is int and 0<r<m and type(n) is int and n>0 for r,n in H.items())
    # Normalize: sum H_r*r^(1-a) / (W*m^(1-a)); add retained surcharge
    # 32*m*sum(H)/(10^16*W) * exp(a log m).
    prof=dict(H)
    if bad:
        prof={r:n*10**16 for r,n in H.items()}
        prof[1]=prof.get(1,0)+32*m*m*sum(H.values())
        W*=10**16
    lo=hi=0
    for r,n in prof.items():
        l,u=power(r,a);lo+=n*l;hi+=n*u
    l,u=power(m,a)
    return lo-W*u,hi-W*l

def refine(H,m,W,coarse,bad=False,digits=40):
    """Refine a separately certified 24-digit coarse bracket.

    This generator establishes a fine signed bracket. It is no replacement for
    final check_moment: retained coarse AND both fine engines must recheck it.
    """
    assert __debug__ and 24<=digits<=70
    coarse=Q(coarse); scale=10**digits
    assert (coarse*scale).denominator==1
    lo=int(coarse*scale);hi=lo+10**(digits-24)
    assert moment(H,m,W,Q(lo,scale),bad)[1]<0
    assert moment(H,m,W,Q(hi,scale),bad)[0]>0
    while hi-lo>1:
        mid=(lo+hi)//2;l,u=moment(H,m,W,Q(mid,scale),bad)
        if u<0:lo=mid
        elif l>0:hi=mid
        else:raise AssertionError('512-bit enclosure insufficient')
    assert moment(H,m,W,Q(lo,scale),bad)[1]<0
    assert moment(H,m,W,Q(hi,scale),bad)[0]>0
    return Q(lo,scale)
