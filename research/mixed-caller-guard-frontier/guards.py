"""Enumerate every minimal dyadic guard allocation with a proved finite cap.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from itertools import product


def need(ok,message):
    if not ok:
        raise ValueError(message)


def floor_log2(x):
    need(x>0,'Positive logarithm argument')
    k=x.numerator.bit_length()-x.denominator.bit_length()
    if Q(2)**k>x:k-=1
    return k


def exponent_bound(coefficients):
    need(coefficients and all(isinstance(a,Q) and a>0 and a.denominator & (a.denominator-1)==0 for a in coefficients),'Positive dyadic coefficients')
    d=max(a.denominator.bit_length()-1 for a in coefficients)
    b=max(0,floor_log2(2*sum(coefficients)))
    return len(coefficients)*b+(len(coefficients)-1)*d


def value(coefficients,g):
    need(len(g)==len(coefficients) and all(type(x) is int and x>=0 for x in g),'Nonnegative integer guards')
    return sum(a*Q(2)**(-x) for a,x in zip(coefficients,g))


def frontier(coefficients):
    cap=exponent_bound(coefficients);m=len(coefficients)
    lower=[max(0,floor_log2(a)+1) for a in coefficients]
    out=[]
    for prefix in product(*(range(lower[i],cap+1) for i in range(m-1))):
        rest=1-sum(a*Q(2)**(-g) for a,g in zip(coefficients,prefix))
        if rest<=0:continue
        last=max(0,floor_log2(coefficients[-1]/rest)+1)
        g=prefix+(last,)
        if last>cap:continue
        s=value(coefficients,g)
        need(s<1,'Strict feasible tuple')
        if all(x==0 or s+a*Q(2)**(-x)>=1 for a,x in zip(coefficients,g)):
            out.append(g)
    return cap,sorted(out)


def tariff_intervals(points,weights):
    need(len(weights)==4 and all(type(x) is int and x>0 for x in weights),'Positive four-class tariff')
    lines=[(weights[0]*g[0],sum(w*x for w,x in zip(weights[1:],g[1:])),g) for g in points]
    cuts={Q(0)}
    for a,b,_ in lines:
        for c,d,_ in lines:
            if b!=d:
                x=Q(c-a,b-d)
                if x>0:cuts.add(x)
    cuts=sorted(cuts)
    def best(x):
        score=min(a+b*x for a,b,_ in lines)
        return tuple(g for a,b,g in lines if a+b*x==score)
    regions=[]
    for lo,hi in zip(cuts,cuts[1:]+[None]):
        winners=best((lo+hi)/2 if hi is not None else lo+1)
        if regions and regions[-1]['guards']==winners:
            regions[-1]['hi']=hi
        else:regions.append(dict(lo=lo,hi=hi,guards=winners))
    endpoints={str(r['hi']):best(r['hi']) for r in regions if r['hi'] is not None}
    return regions,endpoints
