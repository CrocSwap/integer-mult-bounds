#!/usr/bin/env python3
"""Independent unbundled root invoice and scalar majorant; no author imports."""
import argparse, hashlib, json
from pathlib import Path
from fractions import Fraction as F
from collections import Counter

def audit(rp, cp):
    R=json.loads(Path(rp).read_bytes()); raw=Path(cp).read_bytes(); C=json.loads(raw)
    n=R['n']; L=len(R['stages']); assert C['roles']==n and C['stages']==L
    assert C['masks']==[sum(1<<k for k,s in enumerate(R['stages']) if i in s['mask']) for i in range(n)]
    counts=Counter(e[0] for e in C['events']); idles=Counter(); hosts=Counter(); scalars=[]
    mass=[F(1)]*n; height=[0]*n; maxmass=F(1); maxheight=0
    for e in C['events']:
        op=e[0]; r=e[1]; assert 0<=r<n
        if op in ['ADD','SCALE']:
            a=F(e[-1]); scalars.append(a); den=a.denominator; assert den&(den-1)==0
            h=den.bit_length()-1
            if op=='ADD':
                s=e[2]; assert r!=s and 0<=s<n
                mass[r]+=abs(a)*mass[s]; height[r]=max(height[r],height[s]+h)
            else:
                assert a
                mass[r]*=abs(a); height[r]+=h
        elif op=='SWAP':
            s=e[2]; assert 0<=s<n and r!=s
            mass[r],mass[s]=mass[s],mass[r]; height[r],height[s]=height[s],height[r]
        elif op=='QUERY':
            s=e[2]; assert 0<=s<n and r!=s and e[3] in [-1,1]
            mass[r]+=mass[s]; height[r]=max(height[r],height[s])
        elif op=='LAMBDA':
            assert e[2] in [-1,1]
            mass[r]*=2; height[r]+=1
        elif op=='IDLE_ONE':
            assert len(e[2])==1 and 0<=e[2][0]<L
            idles.update(e[2])
        elif op=='HOST':
            s,k=e[2:4]; assert 0<=s<n and r!=s and 0<=k<L
            assert list(map(F,e[4:]))==[F(1),F(-1)]
            hosts[k]+=1; m,h=mass[r],height[r]
            mass[r]+=mass[s]; height[r]=max(height[r],height[s]); mass[s]=m; height[s]=h
        else: raise AssertionError(op)
        maxmass=max(maxmass,*mass); maxheight=max(maxheight,*height)
    assert hosts==Counter({k:1 for k in range(L)})
    assert idles==Counter({k:len(s['mask'])-2 for k,s in enumerate(R['stages'])})
    assert counts['QUERY']==R['N']-2*L
    T=Counter(1+8*mask.bit_count() for mask in C['masks'])
    P=Counter({1:counts['QUERY'],8:counts['IDLE_ONE']})
    bits=0
    while F(2)**bits<=maxmass: bits+=1
    return dict(status='PASS',root_sha256=hashlib.sha256(Path(rp).read_bytes()).hexdigest(),
        caller_sha256=hashlib.sha256(raw).hexdigest(),events=len(C['events']),
        event_census=dict(sorted(counts.items())),scalar_census=dict(sorted(Counter(map(str,scalars)).items())),
        scalar_denominators=dict(Counter(x.denominator for x in scalars)),
        scalar_max_abs=str(max(map(abs,scalars))),coefficient_l1_majorant=str(maxmass),
        coefficient_l1_strict_power_2_bound=bits,dyadic_denominator_height_bound=maxheight,
        root_target_per_port=dict(sorted(T.items())),unbundled_outer_paid_per_port=dict(sorted(P.items())),
        native_calls=L,supplier_substitution=dict(T='p*Troot + 18*Thelp',P='p*(181 H8 + 3 H1) + 18*Pnative',
            p='simultaneous root ports in one supplier call',general_surplus='323*p - 18*sum_r r*(Pnative[r]-Thelp[r])',
            conditional_example='if supplier signed rank flux is 16*p, surplus is 35*p'),
        scope='Algebraic interface and scalar census only. Supplier, full ordinary price, compiler and outer admission remain open.')

if __name__=='__main__':
    if not __debug__: raise RuntimeError('Assertions required')
    p=argparse.ArgumentParser(); p.add_argument('--root',required=True); p.add_argument('--caller',required=True); p.add_argument('--out',required=True)
    a=p.parse_args(); r=audit(a.root,a.caller); s=json.dumps(r,indent=2)+'\n'; Path(a.out).write_text(s); print(s)
