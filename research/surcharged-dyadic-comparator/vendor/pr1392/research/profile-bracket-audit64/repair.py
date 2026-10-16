"""Endpoint-certified grid bisection with explicit undecided status.

@woklerx, substantial OpenAI Codex assistance. Apache-2.0.
The interval oracle remains flemhhh's frozen PR1048 implementation.
"""
from fractions import Fraction as F

def need(ok,msg):
    if not ok:raise ValueError(msg)

def classify(lo,hi):
    need(lo<=hi,'invalid enclosure')
    return -1 if hi<0 else 1 if lo>0 else 0

def bracket(oracle,digits=24,initial_terms=34,max_terms=136):
    """For a strictly increasing function with a root in(0,1/10).

    Oracle returns a rigorous rational enclosure for the function. Success
    certifies BOTH strict endpoint signs; unresolved returns the retained wider
    certified bracket (or no bracket if initial endpoint signs are unresolved).
    No floating-point nomination is used.
    """
    need(type(digits) is int and 1<=digits<=200,'digits1..200')
    need(type(initial_terms) is int and initial_terms>=1 and type(max_terms) is int and max_terms>=initial_terms,'term budget')
    scale=10**digits;trace=[]
    def sign(q):
        terms=initial_terms
        while True:
            lo,hi=oracle(F(q,scale),terms);s=classify(lo,hi)
            trace.append([q,terms,s])
            if s or terms==max_terms:return s,terms
            terms=min(terms*2,max_terms)
    low,high=0,scale//10;slo,tlo=sign(low);shi,thi=sign(high)
    if (slo,shi)!=(-1,1):
        return dict(status='UNRESOLVED_INITIAL_ENDPOINTS',trace=trace,certified_bracket=None)
    while high-low>1:
        mid=(low+high)//2;sm,tm=sign(mid)
        if sm<0:low,tlo=mid,tm
        elif sm>0:high,thi=mid,tm
        else:
            return dict(status='UNRESOLVED_INTERIOR_SIGN',trace=trace,certified_bracket=[str(F(low,scale)),str(F(high,scale))],endpoint_terms=[tlo,thi])
    return dict(status='CERTIFIED',trace=trace,certified_bracket=[str(F(low,scale)),str(F(high,scale))],endpoint_terms=[tlo,thi])

def profile_oracle(original,n,m,W,surcharge=False):
    need(type(m) is int and m>=2 and type(W) is int and W>0,'integer m,W')
    need(n and all(type(r) is int and 1<=r<=m and type(c) is int and c>0 for r,c in n.items()),'positive supported rank profile')
    need(any(r<m for r in n) or surcharge,'strictly increasing fee required')
    D=m*W-sum(r*c for r,c in n.items());need(D>0,'positive deficit')
    cache={}
    def oracle(a,terms):
        need(F(0)<=a<=F(1,10),'exponent interval')
        if terms not in cache:
            table=original.ln_table(set(n),m,terms)
            if surcharge:table['_m']=original.ln_bounds(F(m),terms)
            cache[terms]=table
        table=cache[terms]
        need(all(a*hi<=1 for lo,hi in table.values()),'original exponential oracle envelope')
        lo,hi=(original.fee_bounds_bad if surcharge else original.fee_bounds)(n,m,a,table,terms)
        return lo-D,hi-D
    return oracle
