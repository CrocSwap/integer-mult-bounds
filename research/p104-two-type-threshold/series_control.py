"""Independent rational atanh/log and exponential-series spot checks."""
from fractions import Fraction as Q
from functools import cache
from directed import UNIT, power

G = 1 << 176

def grid(lo,hi):
    return Q((lo*G).__floor__(),G),Q((hi*G).__ceil__(),G)

@cache
def log_ratio(z):
    assert 0<=z<=Q(1,3)
    total=Q(0); term=z; z2=z*z
    for j in range(64):
        total += term/(2*j+1)
        term *= z2
    return grid(2*total,2*(total+term/(129*(1-z2))))

@cache
def log_rank(r):
    assert isinstance(r,int) and r>=1
    k=r.bit_length()-1; radix=1<<k
    lo,hi=log_ratio(Q(r-radix,r+radix)); a,b=log_ratio(Q(1,3))
    return lo+k*a,hi+k*b


def exp_small(x):
    assert 0<=x<=1
    total=term=Q(1)
    for j in range(1,40):
        term=term*x/j;total+=term
    nxt=term*x/40
    return grid(total,total+nxt/(1-x/41))

@cache
def rank_price(r,t):
    a,b=log_rank(r)
    lo,_=exp_small(a*t/16);_,hi=exp_small(b*t/16)
    return grid(lo**16,hi**16)


def check(c):
    t=1-c
    for rank in (Q(1,2),Q(1),Q(2),Q(5),Q(129),Q(258)):
        lo,hi=power(rank,c)
        if rank==Q(1,2):
            a,b=rank_price(2,t); independent=(1/b,1/a)
        else:independent=rank_price(rank.numerator,t)
        assert Q(lo,UNIT)<=independent[1] and independent[0]<=Q(hi,UNIT),str(rank)
