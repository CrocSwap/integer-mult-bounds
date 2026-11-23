"""Exact directed Hall witnesses and positive separating combinations."""
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json

from directed import UNIT, power

P = 183312


def qstr(x):
    return str(Q(x))


def cut_ok(rank, cut, target):
    return cut is None or (4 * rank >= 5 * cut if target else rank >= cut)


def scales(t0, p0):
    return (t0, Counter({2*r:n for r,n in t0.items()})), (p0, Counter({2*r:n for r,n in p0.items()}))


def split_paid(p0, n0, n1):
    p = [Counter(p0), Counter({2*r:n for r,n in p0.items()})]
    if not (0 <= n0 <= P and 0 <= n1 <= P):
        raise ValueError('split count exceeds actual rank-one port inventory')
    p[0][Q(1)] -= n0
    p[0][Q(1, 2)] += 2*n0
    p[1][Q(2)] -= n1
    p[1][Q(1)] += 2*n1
    return p


def margin(target, paid, cut, c, lower):
    # Conservative lower capacity minus upper demand, or optimistic upper.
    return (sum(n*power(r,c)[0 if lower else 1] for r,n in target.items() if cut_ok(r,cut,True))
            - sum(n*power(r,c)[1 if lower else 0] for r,n in paid.items() if cut_ok(r,cut,False)))


def split_row(t0,p0,cut,c,lower):
    targets, paid = scales(t0,p0)
    a = margin(targets[0],paid[0],cut,c,lower)
    b = margin(targets[1],paid[1],cut,c,lower)
    idx = 1 if lower else 0
    def charged(r):return power(r,c)[idx] if cut_ok(r,cut,False) else 0
    u = P*(charged(Q(1))-2*charged(Q(1,2)))
    v = P*(charged(Q(2))-2*charged(Q(1)))
    return tuple(map(Q,(a,b,u,v)))


def all_cuts(paid):
    return [None, *sorted({Q(r) for pp in paid for r,n in pp.items() if n > 0})]


def ratio_witness(t0,p0,c,n0,n1):
    targets,_ = scales(t0,p0)
    paid=split_paid(p0,n0,n1)
    low=Q(0); high=None; named=[]
    for cut in all_cuts(paid):
        a=Q(margin(targets[0],paid[0],cut,c,True))
        b=Q(margin(targets[1],paid[1],cut,c,True))
        named.append((cut,a,b))
        if b>0: low=max(low,-a/b)
        elif b<0: high=a/(-b) if high is None else min(high,a/(-b))
        elif a<0: raise ArithmeticError(('negative zero-slope cut',cut))
    if high is None or not low < high:
        raise ArithmeticError(('ratio interval empty',float(low),None if high is None else float(high)))
    x=(low+high)/2
    values=[(cut,a+b*x) for cut,a,b in named]
    if not all(v>0 for _,v in values):
        raise ArithmeticError('missing strict Hall margin')
    return x,values,(low,high)


def fractional_witness(t0,p0,c):
    total=split_row(t0,p0,None,c,True)
    one=split_row(t0,p0,Q(1),c,True)
    two=split_row(t0,p0,Q(2),c,True)
    a,b,u,_=total; a1,b1,u1,_=one; a2,b2,u2,_=two
    assert u<0 and u1>0 and u2==0 and b2<0
    denominator=b-u*b1/u1
    assert denominator>0
    lo=-(a-u*a1/u1)/denominator
    hi=-a2/b2
    assert 0<lo<hi
    x=(lo+hi)/2
    nlow=-(a1+b1*x)*P/u1
    nhigh=-(a+b*x)*P/u
    assert 0<nlow<nhigh<P
    n=(nlow+nhigh)/2
    paid=split_paid(p0,n,0)
    targets,_=scales(t0,p0)
    margins=[(cut,Q(margin(targets[0],paid[0],cut,c,True))+x*Q(margin(targets[1],paid[1],cut,c,True))) for cut in all_cuts(paid)]
    assert all(v>0 for _,v in margins)
    return x,n,margins,(lo,hi)


def witness_flow(t0,p0,c,x,n0,n1):
    targets,_=scales(t0,p0); paid=split_paid(p0,n0,n1)
    capacity=Counter(); demand=Counter()
    for weight,th,ph in zip((Q(1),x),targets,paid,strict=True):
        for k,n in th.items():capacity[k]+=weight*n*power(k,c)[0]
        for r,n in ph.items():demand[r]+=weight*n*power(r,c)[1]
    flows=[]
    for r in sorted((r for r in demand if demand[r]>0),reverse=True):
        left=demand[r]
        for k in sorted(capacity,reverse=True):
            if not cut_ok(k,r,True): continue
            amount=min(left,capacity[k])
            if amount>0:
                capacity[k]-=amount; left-=amount
                flows.append((r,k,amount))
            if left==0: break
        if left:raise ArithmeticError(('unfunded paid rank',r,left))
    assert all(v>=0 for v in capacity.values())
    assert all(4*k>=5*r for r,k,_ in flows)
    return flows,capacity


def addmul(rows,weights):
    return tuple(sum(w*row[j] for w,row in zip(weights,rows,strict=True)) for j in range(4))


def continuous_dual(t0,p0,c):
    total=split_row(t0,p0,None,c,False)
    one=split_row(t0,p0,Q(1),c,False)
    two=split_row(t0,p0,Q(2),c,False)
    # All rows are optimistic necessary margins in units 2^-224. u and v
    # are the frequency-weighted split fractions, and v>=0 is exact.
    assert total[2]<0 and one[2]>0 and two[2]==0 and two[1]<0
    lam1=-total[2]/one[2]
    lam2=-(total[1]+lam1*one[1])/two[1]
    lamv=-(total[3]+lam1*one[3]+lam2*two[3])
    rows=[total,one,two,(Q(0),Q(0),Q(0),Q(1))]
    weights=[Q(1),lam1,lam2,lamv]
    comb=addmul(rows,weights)
    assert all(v>0 for v in weights) and comb[1:]==(0,0,0) and comb[0]<0
    return rows,weights,comb


def integer_dual(t0,p0,c,side):
    two=split_row(t0,p0,Q(2),c,False)
    if side=='at-most-1005':
        primary=split_row(t0,p0,Q(1),c,False)
        constraint=(Q(1005),Q(0),Q(-P),Q(0))
        assert primary[2]>0
    elif side=='at-least-1006':
        primary=split_row(t0,p0,None,c,False)
        constraint=(Q(-1006),Q(0),Q(P),Q(0))
        assert primary[2]<0
    else:raise ValueError(side)
    assert two[1]<0 and two[2]==0 and primary[1]>0
    lam2=-primary[1]/two[1]
    lamn=-primary[2]/constraint[2]
    lamv=-(primary[3]+lam2*two[3])
    rows=[primary,two,constraint,(Q(0),Q(0),Q(0),Q(1))]
    weights=[Q(1),lam2,lamn,lamv]
    comb=addmul(rows,weights)
    assert all(v>0 for v in weights) and comb[1:]==(0,0,0) and comb[0]<0
    return rows,weights,comb


def dual_record(rows,weights,comb):
    return {'rows':[[qstr(x) for x in row] for row in rows],
            'positive_multipliers':[qstr(x) for x in weights],
            'weighted_result':[qstr(x) for x in comb],
            'constant_divided_by_unit':qstr(comb[0]/UNIT)}


def flow_record(flows):
    return [[qstr(r),qstr(k),qstr(amount/UNIT)] for r,k,amount in flows]


def hist_digest(t0,p0):
    d={'target':{str(r):n for r,n in sorted(t0.items())},'paid':{str(r):n for r,n in sorted(p0.items())}}
    return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
