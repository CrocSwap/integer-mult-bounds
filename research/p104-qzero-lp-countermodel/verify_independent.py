#!/usr/bin/env python3
"""Independently check rational duals and the exact two-hub primal.

This verifier uses only Python's standard library. It does not import the LP
generator or solver. Integer powers verify every directed rpow enclosure.
"""
import copy
import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

SCALE=10**12
BAR=F(128891,1000)

def decimal_bound(value,places,up):
    scale=10**places
    q,r=divmod(value.numerator*scale,value.denominator)
    if up and r: q+=1
    return str(q//scale)+'.'+str(q%scale).zfill(places)

def enclosure(base):
    # float is only a candidate; the integer test below proves the enclosure.
    q=int(math.pow(base,0.99)*SCALE)
    target=base**99*SCALE**100
    while q**100>target: q-=1
    while (q+1)**100<=target: q+=1
    if not (q**100<=target<(q+1)**100): raise AssertionError('rpow enclosure')
    return F(q,SCALE),F(q+1,SCALE)

def check_primal(k,r,e):
    assert sum(r.values())==2*k-2
    assert sum(d*v for d,v in r.items())==sum(a*v for a,v in e.items())
    assert e.get(1,0)>=2*k
    assert all(2<=d<=k and v>=0 for d,v in r.items())
    assert all(1<=a<=k and v>=0 for a,v in e.items())
    for ell in range(2,k+1):
        w=lambda d: k-1 if d>=ell else d-1
        left=sum(d*w(d)*v for d,v in r.items())-sum(a*w(a)*v for a,v in e.items() if a>=2)
        assert left>=2*k*(k-1),('rc2',ell,left)
        assert sum(d*v for d,v in r.items() if d>=ell)>=sum(a*v for a,v in e.items() if a>=ell),('match',ell)
    lo=sum(v*enclosure(8*d+1)[0] for d,v in r.items())-sum(v*enclosure(8*a)[1] for a,v in e.items())
    hi=sum(v*enclosure(8*d+1)[1] for d,v in r.items())-sum(v*enclosure(8*a)[0] for a,v in e.items())
    return F(104,k)*lo,F(104,k)*hi

def check_dual(cert):
    k=cert['k']; z=cert['dual_eq']; zr,zi=F(z['roles']),F(z['incidence'])
    assert set(z)=={'roles','incidence'}
    y={}
    for row in cert['dual_nonzero']:
        name=row['name']; val=F(row['weight'])
        assert name not in y and val>=0
        if name=='mains': rhs=-2*k
        else:
            prefix,number=name.rsplit('_',1); ell=int(number)
            assert prefix in ('rc2','match') and 2<=ell<=k
            assert prefix!='match' or cert['tails']
            rhs=-2*k*(k-1) if prefix=='rc2' else 0
        assert row['rhs']==rhs
        y[name]=val
    def weight(ell,d): return k-1 if d>=ell else d-1
    role_slacks=[]
    for d in range(2,k+1):
        dual=zr+d*zi
        for ell in range(2,k+1):
            dual-=d*weight(ell,d)*y.get('rc2_'+str(ell),0)
            if d>=ell: dual-=d*y.get('match_'+str(ell),0)
        role_slacks.append(dual-enclosure(8*d+1)[1])
    event_slacks=[]
    for a in range(1,k+1):
        dual=-a*zi-(y.get('mains',0) if a==1 else 0)
        for ell in range(2,k+1):
            if a>=2: dual+=a*weight(ell,a)*y.get('rc2_'+str(ell),0)
            if a>=ell: dual+=a*y.get('match_'+str(ell),0)
        event_slacks.append(dual+enclosure(8*a)[0])
    assert min(role_slacks)>=0,('role slack',min(role_slacks))
    assert min(event_slacks)>=0,('event slack',min(event_slacks))
    dualrhs=(2*k-2)*zr-2*k*y.get('mains',0)-2*k*(k-1)*sum(y.get('rc2_'+str(ell),0) for ell in range(2,k+1))
    bound=F(104,k)*dualrhs
    assert bound==F(cert['certified_bound']),('wrong dot product',bound,cert['certified_bound'])
    assert (bound<BAR)==cert['strictly_below_bar']
    return bound,min(role_slacks),min(event_slacks)

def must_reject(fn,label):
    try: fn()
    except (AssertionError,ValueError,KeyError):
        print('control rejected:',label); return
    raise AssertionError('control unexpectedly accepted: '+label)

def main():
    root=Path(__file__).resolve().parent
    for k in [71,72,73,74]:
        cert=json.loads((root/('k%d.json'%k)).read_text())
        bound,rs,es=check_dual(cert)
        r={2:2*k-4,k:2};e={1:2*k,2:2*k-4}
        low,high=check_primal(k,r,e)
        assert low<=high<=bound
        if k in (71,72,73): assert low>BAR
        if k==74: assert bound<BAR
        print('k=%d primal=[%s, %s], dual<=%s, gap<=%s, dual minus bar=%s'%(k,decimal_bound(low,12,False),decimal_bound(high,12,True),decimal_bound(bound,12,True),decimal_bound(bound-low,12,True),bound-BAR))
    cert=json.loads((root/'k72.json').read_text())
    neg=copy.deepcopy(cert);next(x for x in neg['dual_nonzero'] if x['name']=='mains')['weight']='-1'
    must_reject(lambda:check_dual(neg),'negative inequality multiplier')
    damaged=copy.deepcopy(cert);damaged['dual_eq']['roles']=str(F(damaged['dual_eq']['roles'])-1)
    must_reject(lambda:check_dual(damaged),'role-column domination')
    dot=copy.deepcopy(cert);dot['certified_bound']=str(F(dot['certified_bound'])-1)
    must_reject(lambda:check_dual(dot),'altered dual objective')
    must_reject(lambda:check_primal(72,{2:140,72:2},{1:143,2:140}),'perturbed primal incidence/mains')
    assert not (BAR<BAR)
    print('control passed: equality with bar is not strict')
    print('all independent checks passed')

if __name__=='__main__':main()
