"""Small exact repricer for explicitly supplied local histogram/demand deltas.

No physical admission is performed. Automatic packing only adjusts pure bins
when exact divisibility permits it; otherwise an explicit pattern witness is needed.
"""
from fractions import Fraction as F
from collections import Counter
import baseline_arithmetic as old
import packing

def pure_retile(demand_delta):
    original=packing.calculate()['stage_certificate']
    patterns=[dict(widths=row['widths'][:],count=row['count'])for row in original['patterns']]
    for rank,change in demand_delta.items():
        if not change:continue
        if 120%rank:raise ValueError('Explicit packing witness needed for non-divisor rank '+str(rank))
        blocks=120//rank
        row=next((row for row in patterns if row['widths']==[rank]*blocks),None)
        initial=0 if row is None else row['count']*blocks
        revised=initial+60*change
        if revised<0 or revised%blocks:
            raise ValueError('Explicit mixed-pattern packing witness needed for rank '+str(rank))
        if row is None:patterns.append(dict(widths=[rank]*blocks,count=revised//blocks))
        else:row['count']=revised//blocks
    return [row for row in patterns if row['count']]

def moment_root(H,W):
    scale=10**18;lo=0;hi=scale//100
    if not old.moment(H,120,W,F(0))[1]<1:raise ValueError('Moment does not contract at a=0')
    assert old.moment(H,120,W,F(hi,scale))[0]>1
    while hi-lo>1:
        mid=(lo+hi)//2;L,U=old.moment(H,120,W,F(mid,scale))
        if U<1:lo=mid
        elif L>1:hi=mid
        else:raise ArithmeticError('More interval precision required')
    c=F(lo,scale);upper=F(hi,scale)
    return c,upper,old.moment(H,120,W,c),old.moment(H,120,W,upper)

def reprice(local_histogram_delta,role_rank_count_delta,patterns=None):
    if any(type(r)is not int or type(n)is not int or r<=0 or r>=120 for D in (local_histogram_delta,role_rank_count_delta)for r,n in D.items()):
        raise ValueError('Deltas require positive integer ranks and integer counts')
    old.source_integrity();H,_=old.final_histogram()
    H.update({r:5*n for r,n in local_histogram_delta.items()})
    if any(n<0 for n in H.values()):raise ValueError('Negative child count')
    H=Counter({r:n for r,n in H.items()if n})
    original=packing.calculate()['stage_certificate'];demand=original['demand'].copy()
    for r,n in role_rank_count_delta.items():demand[r]=demand.get(r,0)+60*n
    if any(n<0 for n in demand.values()):raise ValueError('Negative residual demand')
    demand={r:n for r,n in demand.items()if n}
    if patterns is None:patterns=pure_retile(role_rank_count_delta)
    witness=packing.verify(120,demand,patterns)
    stock=422400+5*witness['feasible_bins'];W=F(stock,60)
    c,upper,L,U=moment_root(H,W);b=F(754736418878859,10**18)
    chain=[F(384599,10**10)]
    for i in range(3):chain.append((1-c)*c+c*chain[-1])
    eta=F(1,10**12);beta=F(1,10**9)
    if not chain[-1]<(1-beta)*b:
        raise ValueError('Complex side now binds: this narrow repricer needs a revised bootstrap/backoff policy')
    q=chain[-1]*(1-2*eta);G=(1-eta)*q/(1+q);ticks=G*10**18
    k=F((ticks.numerator-1)//ticks.denominator,10**18)
    assembly=old.assembly(c,b,k)
    return dict(status='CONDITIONAL_ARITHMETIC_ONLY',physical_admission=False,
       local_histogram_delta=local_histogram_delta,role_rank_count_delta=role_rank_count_delta,
       histogram=dict(sorted(H.items())),calls=sum(H.values()),rank_mass=old.rank(H),
       literal_stock=stock,unreplicated_stock=W,deficit=120*W-old.rank(H),
       packing=witness,root_bracket=[c,upper],moment_interval=L,adjacent_moment_interval=U,
       kappa=k,kappa_decimal=old.ex.dec(k),assembly=assembly)
