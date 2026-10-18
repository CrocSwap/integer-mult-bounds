"""Exact surcharged ties; large integer counts denote profiles, not circuits."""
from fractions import Fraction as Q
from math import gcd,lcm


def tie(quadratic=False):
    m=64;c=Q(32*m*m,10**16);p,q=c.numerator,c.denominator
    u,v=1025,1024
    # t=u/v, or t^2=u/v. Both imply 0<log2(t)<1/10.
    rank,degree=(4,3) if quadratic else (2,6)
    na,nb=rank*v*q+p*u,u*(q+p)
    scale=m*q*v**degree
    a,b={1:na*scale},{rank:nb*scale}
    W=na*u**degree*(q+p)
    factor=gcd(gcd(next(iter(a.values())),next(iter(b.values()))),W)
    return {r:n//factor for r,n in a.items()},{r:n//factor for r,n in b.items()},m,W//factor,Q(u,v)


def negative_factor():
    # Same negative root -3, distinct positive roots close to one. Coefficients
    # are scaled into integer dyadic profiles with the actual m=8 surcharge.
    m=8;c=Q(32*m*m,10**16)
    C,D=Q(4)+Q(1,256),Q(4)+Q(1,128)
    polys=[[-3*C*D,D*(9-C),6*D,D],[-3*C*D,C*(9-D),6*C,C]]
    profiles=[]
    for poly in polys:
        n2,n4=poly[2]/2,poly[1]/4
        n1=(poly[3]-c*(n2+n4))/(1+c)
        profiles.append({1:n1,2:n2,4:n4})
    W=3*C*D/8
    scale=lcm(W.denominator,*(n.denominator for profile in profiles for n in profile.values()))
    return [{r:int(n*scale) for r,n in profile.items()} for profile in profiles],m,int(W*scale)
