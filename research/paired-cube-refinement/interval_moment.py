"""Independent exact interval moments; no floating point or producer execution.

Retained from PR163/164 research/paired-cube-balanced-161/arithmetic/
interval_moment.py, prepared for chafreaky with OpenAI Codex assistance.
Apache-2.0. Arithmetic body unchanged.

Positive atanh series, range reduction by 4/3, explicit geometric tails,
80 logarithm terms and degree-12 exponential enclosures. The final rounding
is outward on the 10^-45 grid. Prepared with OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from functools import lru_cache
from math import factorial
GRID = 10**45
LOG_TERMS = 80
EXP_DEGREE = 12

def require(ok, reason):
    if not ok: raise ValueError(reason)

def lower(x):return Q((x*GRID).numerator//(x*GRID).denominator,GRID)
def upper(x):
    y=x*GRID
    return Q(-((-y.numerator)//y.denominator),GRID)

@lru_cache(None)
def log_interval(x):
    x=Q(x);require(x>=1,'log interval domain')
    base=Q(4,3);k=0
    while x>base:x/=base;k+=1
    def short(y):
        z=(y-1)/(y+1);power=z;s=Q(0)
        for j in range(LOG_TERMS):s+=power/Q(2*j+1);power*=z*z
        lo=2*s;tail=2*power/(Q(2*LOG_TERMS+1)*(1-z*z))
        return lo,lo+tail
    lo,hi=short(x);blo,bhi=short(base)
    return lower(k*blo+lo),upper(k*bhi+hi)

def exp_interval(lo,hi):
    require(0<=lo<=hi<Q(1,4),'exp enclosure domain')
    def poly(x):
        value=term=Q(1)
        for j in range(1,EXP_DEGREE+1):term=term*x/j;value+=term
        return value
    low=poly(lo);high=poly(hi)
    tail=hi**(EXP_DEGREE+1)/factorial(EXP_DEGREE+1)/(1-hi/Q(EXP_DEGREE+2))
    return lower(low),upper(high+tail)

def prepare(profile):
    m,W=profile['m'],profile['W'];require(type(m) is int and type(W) is int and m>1 and W>0,'profile dimensions')
    raw=profile['child_multiplicities'];hist={int(t):n for t,n in raw.items()}
    require(len(hist)==len(raw),'aliased histogram keys')
    require(all(0<t<m and type(n) is int and n>0 for t,n in hist.items()),'invalid child or multiplicity')
    mass=sum(t*n for t,n in hist.items());require(mass==profile['total_rank']==W*m-profile['N']+profile['L'],'rank mass')
    require(max(hist)==profile['maxchild'],'maximum child')
    require(0<mass<W*m,'rank-moment contraction')
    return [(t,n,*log_interval(Q(m,t))) for t,n in sorted(hist.items())]

def moment(profile,a,details=False):
    a=Q(a);require(a>=0,'nonnegative saving');lo=hi=Q(0);rows=[]
    for t,n,L,U in prepare(profile):
        E,F=exp_interval(a*L,a*U);w=Q(t*n,profile['m']*profile['W']);lo+=w*E;hi+=w*F
        if details:rows.append(dict(child=t,multiplicity=n,log_lower=L,log_upper=U,exp_lower=E,exp_upper=F,contribution_lower=w*E,contribution_upper=w*F))
    result=dict(saving=a,lower=lo,upper=hi,strict_gap_lower=1-hi)
    if details:result['terms']=rows
    return result

def saving_grid(profile,denominator=10**24):
    require(type(denominator) is int and denominator>0,'positive saving grid')
    prepare(profile);lo=0;hi=denominator//32;iterations=0
    require(moment(profile,Q(lo,denominator))['upper']<1,'initial contraction')
    require(moment(profile,Q(hi,denominator))['lower']>1,'initial exclusion')
    while hi-lo>1:
        mid=(hi+lo)//2;m=moment(profile,Q(mid,denominator));iterations+=1
        if m['upper']<1:lo=mid
        elif m['lower']>1:hi=mid
        else:raise ValueError('Moment interval overlaps one; increase enclosure precision')
    accepted=moment(profile,Q(lo,denominator),True);rejected=moment(profile,Q(hi,denominator),True)
    require(accepted['upper']<1<rejected['lower'],'adjacent saving proof failed')
    return dict(accepted=accepted,rejected=rejected,denominator=denominator,iterations=iterations,method=dict(log_base='4/3',log_terms=LOG_TERMS,exp_degree=EXP_DEGREE,outward_grid=GRID))
