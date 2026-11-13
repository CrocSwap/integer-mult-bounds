#!/usr/bin/env python3
"""Price seeds use Decimal; every bound is certified by integer powers only."""
from decimal import Decimal,localcontext
from fractions import Fraction as Q
from functools import lru_cache
D=10**24
DP=pow(D,5000)
CERTIFICATES={}
def need(ok,label):
    if not ok:raise ValueError(label)
@lru_cache(None)
def price(r):
    need(isinstance(r,int) and 0<=r<=137,'price domain')
    if r==0:return Q(0),Q(0)
    N=pow(r,4981)*DP
    with localcontext() as ctx:
        ctx.prec=85
        a=int((Decimal(r)**(Decimal(4981)/Decimal(5000)))*Decimal(D))
    while pow(a,5000)>N:a-=1
    while pow(a+1,5000)<=N:a+=1
    low=pow(a,5000);high=pow(a+1,5000)
    need(low<=N<high,'exact integer power bracket')
    b=a if low==N else a+1
    CERTIFICATES[r]=dict(rank=r,lower_numerator=a,upper_numerator=b,denominator=D,
        lower_power_le_scaled_target=True,upper_power_ge_scaled_target=True,target_bits=N.bit_length())
    return Q(a,D),Q(b,D)
def moment(profile):
    lo=hi=Q(0)
    for r,c in profile.items():
        if not c:continue
        a,b=price(int(r));lo+=c*(a if c>=0 else b);hi+=c*(b if c>=0 else a)
    return lo,hi
def display(interval):
    with localcontext() as ctx:
        ctx.prec=45
        dec=[str(Decimal(q.numerator)/Decimal(q.denominator)) for q in interval]
    return dict(exact=list(map(str,interval)),decimal_display_only=dec)
