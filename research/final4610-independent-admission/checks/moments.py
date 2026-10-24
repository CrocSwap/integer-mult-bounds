#!/usr/bin/env python3
"""Independent directed fixed-point moment screen; stdlib only, no repository imports.

Every interval endpoint is an integer scaled by 10**70. Arithmetic rounds outwards.
Log uses range reduction plus positive atanh series with exact rational tail.
Exp uses its positive Taylor series and geometric tail, then reciprocal.
This is an arithmetic screen: no implementation or theorem admission is implied.
"""
from fractions import Fraction as F
from functools import lru_cache
import argparse,json,hashlib,platform,time
from pathlib import Path
from .outer import parameters,evaluate as outer_evaluate,encode as outer_encode
S=10**70
NLOG=90
NEXP=80

def ceilq(a,b): return -((-a)//b)
def point(q):
    q=F(q); return (q.numerator*S//q.denominator,ceilq(q.numerator*S,q.denominator))
def add(a,b): return a[0]+b[0],a[1]+b[1]
def neg(a): return -a[1],-a[0]
def sub(a,b):return add(a,neg(b))
def mul(a,b):
    v=[a[0]*b[0],a[0]*b[1],a[1]*b[0],a[1]*b[1]]
    return min(v)//S,ceilq(max(v),S)
def div(a,b):
    assert b[0]>0
    v=[F(x*S,y) for x in a for y in b]
    return min(v).__floor__(),max(v).__ceil__()
def scale(a,n):return mul(a,point(n))
def display(a):return [str(F(a[0],S)),str(F(a[1],S))]
def decimal(a):
    def dec(n):
        sign='-' if n<0 else '';n=abs(n);return sign+str(n//S)+'.'+str(n%S).zfill(70)
    return [dec(x) for x in a]

def log_reduced(q):
    assert 1<=q<=2
    z=(q-1)/(q+1); total=F(0); zp=z
    for j in range(NLOG):
        total+=2*zp/(2*j+1);zp*=z*z
    tail=2*zp/((2*NLOG+1)*(1-z*z))
    lo=point(total)[0]; hi=point(total+tail)[1]
    return lo,hi
@lru_cache(None)
def log_rank(r):
    assert isinstance(r,int) and r>0
    e=r.bit_length()-1
    return add(log_reduced(F(r,2**e)),scale(log_reduced(F(2)),e))
def exp_positive(a):
    assert 0<=a[0]<=a[1]
    if a[1]>=S:
        half=div(a,point(2));e=exp_positive(half);return mul(e,e)
    result=point(1);term=point(1)
    for j in range(1,NEXP+1):
        term=div(mul(term,a),point(j));result=add(result,term)
    nextterm=div(mul(term,a),point(NEXP+1))
    # Ratios after the next term are <= a.upper/(NEXP+2).
    bound=div(nextterm,sub(point(1),div(a,point(NEXP+2))))
    return result[0],result[1]+bound[1]
def power(r,k):
    """Enclose r**(1-k), supporting |k| log(r)<1."""
    k=F(k)
    if r==1:return point(1)
    a=scale(log_rank(r),abs(k))
    e=exp_positive(a)
    return scale(div(point(1),e) if k>=0 else e,r)
def moment(hist,k):
    a=point(0)
    for r,n in hist.items():a=add(a,scale(power(int(r),k),n))
    return a
def margin(T,P,k):return sub(moment(T,k),moment(P,k))
def dictint(d):
    out={}
    for k,v in d.items():
        assert isinstance(k,(str,int)) and not isinstance(k,bool)
        assert isinstance(v,(str,int)) and not isinstance(v,bool),'counts must be exact JSON integers or integer strings'
        r,n=int(k),int(v)
        assert str(k)==str(r) and str(v)==str(n) and r>0,'invalid exact rank or count'
        if n:out[r]=n
    return out
def derivative_interval(T,P,lo,hi):
    result=point(0)
    for hist,sign in [(P,1),(T,-1)]:
        for r,n in hist.items():
            # For all c in [lo,hi], r**(1-c) decreases with c.
            interval=(power(r,hi)[0],power(r,lo)[1])
            result=add(result,scale(mul(log_rank(r),interval),sign*n))
    return result

def strictification(T,P,k,extra):
    k=F(k);target=moment(T,k);paid=add(moment(P,k),moment(extra,k))
    alpha=div(paid,target)
    # Same model and fixed sufficient tail constants as final 4610, independent engine.
    higher=add(moment(P,k-F(1,5)),moment(extra,k-F(1,5)))
    gamma=div(higher,mul(power(20,F(4,5)),target))
    delta=div(point(sum(T.values())*21),mul(div(point(20),power(20,k)),target))
    alpha_ok=alpha[1]<point(1-F(1,10**11))[0]
    tails_ok=gamma[1]<point(F(97,100))[0] and delta[1]<point(F(97,100))[0]
    return {'alpha':decimal(alpha),'gamma':decimal(gamma),'delta':decimal(delta),'alpha_strict_gap_check':alpha_ok,'tails_below_97_over_100':tails_ok,'same_model_moment_and_tail_screen':alpha_ok and tails_ok,'funded_alpha_margin':decimal(sub(sub(target,paid),scale(target,F(1,10**11))))}

def price_quote(T,P,k,extra):
    assert all(P.get(r,0)+n>=0 for r,n in extra.items()),'paid removals exceed existing source invoice'
    m=margin(T,P,k);c=moment(extra,k)
    remaining=sub(m,c)
    status='AFFORDABLE_RAW' if remaining[0]>0 else 'UNAFFORDABLE_RAW' if remaining[1]<=0 else 'UNRESOLVED'
    return {'k':str(F(k)),'extra_paid':extra,'raw_margin':decimal(m),'extra_cost':decimal(c),'remaining':decimal(remaining),'status':status,'strictification':strictification(T,P,k,extra),'funding_status':'conditional arithmetic screen; implementation costs and compiler/outer/native closure remain required'}
def root(T,P,lo,hi,steps=40):
    lo=F(lo);hi=F(hi)
    assert margin(T,P,lo)[0]>0 and margin(T,P,hi)[1]<0
    for _ in range(steps):
        mid=(lo+hi)/2;m=margin(T,P,mid)
        if m[0]>0:lo=mid
        elif m[1]<0:hi=mid
        else:break
    return [str(lo),str(hi)]
def reconstruct(controller,local,helpers):
    from collections import Counter
    T=Counter();P=Counter();counts=Counter()
    for event in controller['physical_events']:
        counts[event[0]]+=1
        if event[0]=='LOCAL':T.update(helpers);P.update(local)
        elif event[0]=='QUERY_SHEAR':P[1]+=112
        elif event[0]=='IDLE':P[8*len(event[2])]+=224
        elif event[0] in ('ADD','SIGNED_SWAP'):pass  # fixed nonrecursive operations, not recursive child calls
        else:raise AssertionError('unknown controller event')
    for term in controller['diagonal']:T[1+8*sum(term[1:])]+=112
    assert counts=={'LOCAL':18,'QUERY_SHEAR':15,'IDLE':15,'ADD':90,'SIGNED_SWAP':16}
    return dict(T),dict(P)
def price_planes(T,P,k):
    k=F(k);target=moment(T,k)
    raw=margin(T,P,k)
    alpha_budget=sub(raw,scale(target,F(1,10**11)))
    higher=moment(P,k-F(1,5))
    gamma_budget=sub(scale(mul(power(20,F(4,5)),target),F(97,100)),higher)
    return {'k':str(k),'raw_budget':decimal(raw),'alpha_reserved_budget':decimal(alpha_budget),'gamma_budget':decimal(gamma_budget),'coefficients':{str(r):{'raw_and_alpha':decimal(power(r,k)),'gamma':decimal(power(r,k-F(1,5)))} for r in [1,2,3,4,8,16,32,64,128]},'interpretation':'Each extra paid histogram must satisfy both linear planes; negative coordinates are explicit paid-call removals requiring implementation witnesses. These planes are necessary conditional arithmetic checks; they do not admit an implementation.'}

