"""PR65/PR100 exact moment enclosures reused in Round15; no numerical floats.

Exact-moment and independent-moment formulas retain the earlier rational
degree8/degree12 bounds. Credits: Rohan Arun, Dominik Scholz, icekylinx,
Zhihao Chen, RaD, Chafik Boukhalfa and the preserved predecessor sources.
The immutable PR108 binary_frame_math supplies the byte-identical base2 log.
"""
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
from math import factorial
from pathlib import Path
import sys

if not __debug__:raise SystemExit('Assertions required')
LOG_SOURCE='1f96e8aafc8ae89f8eeec5d03800131d93d58e01bf8a7fca8feb03702d1740d0'


def configure(repo):
    global arithmetic
    p=Path(repo)/'scripts/experiments/binary_frame_math.py'
    assert sha256(p.read_bytes()).hexdigest()==LOG_SOURCE
    spec=importlib.util.spec_from_file_location('round15_arithmetic',p)
    arithmetic=importlib.util.module_from_spec(spec);spec.loader.exec_module(arithmetic)


def floor_scaled(x,denominator):
    return (x*denominator).numerator//(x*denominator).denominator


def ceiling_scaled(x,denominator):
    return -floor_scaled(-x,denominator)


def exact_moment(m,width,rows,saving,degree=8,rounding=10**40):
    assert type(saving) is Q and 0<saving<1 and degree>=1
    lo,hi=Q(),Q();terms={}
    for t,count in sorted(rows.items()):
        assert type(t) is int and type(count) is int and 0<t<m and count>0
        loglo,loghi=arithmetic.logs(Q(m,t));u,v=saving*loglo,saving*loghi
        assert 0<=u<=v<1
        lower=sum((u**j/factorial(j) for j in range(degree+1)),Q())
        upper=sum((v**j/factorial(j) for j in range(degree+1)),Q())
        upper+=v**(degree+1)/factorial(degree+1)/(1-v/Q(degree+2))
        lower=Q(floor_scaled(lower,rounding),rounding)
        upper=Q(ceiling_scaled(upper,rounding),rounding)
        weight=Q(t*count,m*width);lo+=weight*lower;hi+=weight*upper
        terms[t]=dict(weight=weight,log_lower=loglo,log_upper=loghi,exp_lower=lower,exp_upper=upper)
    return dict(saving=saving,lower=lo,upper=hi,strict_gap=1-hi,degree=degree,
                rounding_denominator=rounding,terms=terms)


def log_interval(x):
    assert x>=1
    k=0
    while x>Q(3,2):x/=Q(3,2);k+=1
    def small(y):
        z=(y-1)/(y+1);power,total=z,Q()
        for j in range(60):total+=power/Q(2*j+1);power*=z*z
        return 2*total,2*total+2*power/(121*(1-z*z))
    lo,hi=small(x);blo,bhi=small(Q(3,2))
    return lo+k*blo,hi+k*bhi


def independent_moment(profile,saving,recorded_terms):
    low,high=Q(),Q()
    rows={int(t):n for t,n in profile['child_multiplicities'].items()}
    for t,n in sorted(rows.items()):
        lo,hi=log_interval(Q(profile['m'],t));recorded=recorded_terms[str(t)]
        assert Q(recorded['log_lower'])<=lo<=hi<=Q(recorded['log_upper'])
        u,v=lo*saving,hi*saving;assert 0<u<=v<Q(1,1000)
        u=Q(floor_scaled(u,10**40),10**40);v=Q(ceiling_scaled(v,10**40),10**40)
        tlo,thi=Q(1),Q(1);elo,ehi=Q(1),Q(1)
        for j in range(1,13):tlo,thi=tlo*u/j,thi*v/j;elo,ehi=elo+tlo,ehi+thi
        ehi+=2*thi*v/13;weight=Q(t*n,profile['m']*profile['W'])
        low+=weight*Q(floor_scaled(elo,10**40),10**40)
        high+=weight*Q(ceiling_scaled(ehi,10**40),10**40)
    return low,high
