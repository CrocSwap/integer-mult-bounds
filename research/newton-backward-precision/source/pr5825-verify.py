#!/usr/bin/env python3
"""Check the exact residual, shared bank, cost census and scoped lower bound."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from math import comb
import argparse
import copy
import hashlib
import json
import random
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))


def source_checks():
    origins=json.loads((ROOT/'ORIGINS.json').read_text())
    for item in origins:
        data=(ROOT/item['local']).read_bytes()
        for b,expect in ((data,True),(data+b'!',False)):
            good=hashlib.sha256(b).hexdigest()==item['sha256'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==item['git_blob']
            if good!=expect:raise ValueError('Frozen source authentication')
    return len(origins)


def polynomial_oracle(x,n,a,R):
    # Evaluate g(W) by falling factorials, without a Walsh transform or pruning.
    N=1<<n
    w_additions=0
    def W(v):
        nonlocal w_additions
        result=[]
        for r in range(N):
            z=(n*v[r][0],n*v[r][1])
            for bit in range(n):
                z=G.add(z,G.neg(v[r^(1<<bit)]));w_additions+=1
            result.append((F(z[0],2),F(z[1],2)))
        return result
    v=list(x);bulk=list(x)
    for h in range(1,R+1):
        u=W(v)
        v=[((z[0]-(a+h-1)*old[0])/h,(z[1]-(a+h-1)*old[1])/h) for z,old in zip(u,v)]
        coefficient=G.phase(G.pi_power(h),h)
        bulk=[G.add(z,G.mul(coefficient,w)) for z,w in zip(bulk,v)]
    bulk=[G.phase(z,a) for z in bulk]
    raw=G.raw_tensor(x,n);scale=G.pi_power(n)
    answer=[G.add(y,G.neg(G.mul(scale,z))) for y,z in zip(raw,bulk)]
    G.need(all(F(v).denominator==1 for z in answer for v in z),'Integral correction numerator')
    G.need(w_additions==R*n*N,'Literal Newton-W bulk graph')
    return [tuple(int(v) for v in z) for z in answer]


def expect_failure(call):
    try:call()
    except ValueError:return
    raise ValueError('Invalid source/precision/lifetime accepted')


def run():
    corruptions=source_checks()
    global C,G
    import compiler as C
    G=C.G
    rng=random.Random(581531);cases=0;plans_count=0;empty=0;uniform_mass=0;pruned_mass=0
    receipts=[];fingerprint=hashlib.sha256()
    for n in range(1,8):
        x=[tuple(rng.randrange(-31,32) for _ in range(2)) for _ in range(1<<n)]
        for R in range(n):
            for a in range(n-R+1):
                oracle=polynomial_oracle(x,n,a,R)
                for p in (0,1,3):
                    plan=C.prepare(n,a,R,p);bank=C.gather(x,[plan]);out,bill=C.deliver(bank,plan,x)
                    expected=[G.residue(z,p+n) for z in oracle]
                    G.need(out==expected,'Complete polynomial/tensor residual endpoint')
                    nodes=C.profile(n,plan['demands'])
                    mass=dict(bank.invoice)['ADD_MASS'];pruned_mass+=mass
                    T={r:plan['Q'] for r in range(1<<n) if not a<=r.bit_count()<=a+R}
                    unodes=C.profile(n,T);old=sum(((1<<n)>>d)*q for (d,v),q in unodes.items() if d)
                    G.need(mass<=old,'Actual coefficient pruning never exceeds interval mask')
                    uniform_mass+=old;empty+=not bool(nodes);plans_count+=1;cases+=1
                    fingerprint.update(json.dumps([n,a,R,p,out,bill],sort_keys=True).encode())
                    C.close(bank);expect_failure(lambda:C.deliver(bank,plan,x))
    # Every basis column at low widths uses a separately generated source.
    basis=0
    for n in range(1,5):
        for R in range(n):
            a=(n-R)//2;plan=C.prepare(n,a,R,1)
            for s in range(1<<n):
                x=[G.ONE if r==s else G.ZERO for r in range(1<<n)]
                bank=C.gather(x,[plan]);out,_=C.deliver(bank,plan,x)
                G.need(out==[G.residue(z,n+1) for z in polynomial_oracle(x,n,a,R)],'Complete basis residual')
                C.close(bank);basis+=1
    # Different spectral responses share one actual immutable source.
    n=8;x=[tuple(rng.randrange(-100,101) for _ in range(2)) for _ in range(1<<n)]
    plans=[C.prepare(n,a,R,p) for a,R,p in ((0,2,1),(2,3,2),(4,2,3),(1,5,1))]
    shared=C.gather(x,plans);single_mass=0;shared_outputs=[];delivery_bills=[]
    for plan in plans:
        single=C.gather(x,[plan]);out,bill=C.deliver(shared,plan,x);other,_=C.deliver(single,plan,x)
        G.need(out==other==[G.residue(z,plan['p']+n) for z in polynomial_oracle(x,n,plan['a'],plan['R'])],'Every shared response')
        single_mass+=dict(single.invoice)['ADD_MASS'];C.close(single);shared_outputs.append(out);delivery_bills.append(bill)
    shared_mass=dict(shared.invoice)['ADD_MASS']
    G.need(shared_mass<single_mass,'Strict shared gather saving')
    bad=list(x);bad[0]=G.add(bad[0],G.ONE)
    expect_failure(lambda:C.deliver(shared,plans[0],bad))
    low=C.gather(x,[C.prepare(n,0,2,0)])
    expect_failure(lambda:C.deliver(low,C.prepare(n,0,2,20),x));C.close(low)
    retirement=C.close(shared);expect_failure(lambda:C.deliver(shared,plans[0],x))
    delivery_mass=sum(b.get('ADD_MASS',0)+b.get('MULT_ADD_MASS',0) for b in delivery_bills)
    shared_report=dict(separate_add_mass=single_mass+delivery_mass,shared_add_mass=shared_mass+delivery_mass,parameters=[[p[k] for k in ('n','a','R','p')] for p in plans],
        separate_gather_mass=single_mass,shared_gather_mass=shared_mass,
        delivery_bills=delivery_bills,preparation=[p['preparation'] for p in plans],retirement=retirement,
        output_sha256=hashlib.sha256(json.dumps(shared_outputs).encode()).hexdigest())
    # R=0 has full prefixes through depth n-1, even after exact coefficient pruning.
    r0=0
    for n in range(2,11):
        for a in range(n+1):
            for p in (0,1,n):
                plan=C.prepare(n,a,0,p);nodes=C.profile(n,plan['demands']);Q=p+2*n-1
                G.need(all(nodes[d,v]==Q for d in range(n) for v in range(1<<d)),'Every proper R0 prefix has full precision')
                mass=sum(((1<<n)>>d)*q for (d,v),q in nodes.items() if d)
                G.need(mass==C.r0_gather_mass(n,a,p),'Closed exact R0 gather formula')
                G.need(mass>=(1<<n)*(n-1)*Q,'R0 all-width lower bound')
                r0+=1
    # Positive-degree literal bulk has at least one complete W pass at >=p digits.
    lower_bounds=[]
    for n in range(4,257):
        p=n
        bulk=(1<<n)*n*p//2
        residual=(1<<n)*(n-1)*(p+2*n-1)
        G.need(residual>=bulk,'Uniform all-interval conservative lower bound')
        if n in (4,8,16,32,64,128,256):lower_bounds.append(dict(n=n,p=p,all_intervals_add_mass_lower=bulk))
    # Omitting correction fails on a literal basis input.
    x=[G.ONE]+[G.ZERO]*7;oracle=polynomial_oracle(x,3,1,1)
    G.need(any(G.residue(z,4)!=G.ZERO for z in oracle),'Exceptional bank is required')
    plan=C.prepare(3,1,1,1);bank=C.gather(x,[plan]);correct,_=C.deliver(bank,plan,x)
    wrong=copy.deepcopy(plan);wrong['m']=0;damaged,_=C.deliver(bank,wrong,x)
    G.need(damaged!=correct,'Wrong normalization quotient fails')
    wrong=copy.deepcopy(plan)
    for coefficient in wrong['coefficients']:
        if coefficient['q']:
            coefficient['unit']=G.neg(coefficient['unit']);break
    damaged,_=C.deliver(bank,wrong,x)
    G.need(damaged!=correct,'Wrong coefficient sign fails')
    C.close(bank)

    return dict(schema_version=1,source_corruptions=corruptions,parameter_cases=plans_count,
        polynomial_endpoint_cases=cases,basis_columns=basis,empty_corrections=empty,
        uniform_gather_mass=uniform_mass,valuation_gather_mass=pruned_mass,
        exact_R0_profiles=r0,lower_bound_samples=lower_bounds,shared=shared_report,
        complete_stream_sha256=fingerprint.hexdigest(),
        controls=['changed source version','insufficient creation precision','retired bank',
                  'omitted exceptional correction','wrong normalization quotient','wrong coefficient sign'],
        scope='Exact ordinary residual and scoped standalone circuit-cost obstruction; no new kappa.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write-receipt',action='store_true');args=p.parse_args()
    result=run();path=ROOT/'RESULT.json'
    if args.write_receipt:
        with path.open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    else:
        if json.dumps(json.loads(path.read_text()),sort_keys=True)!=json.dumps(result,sort_keys=True):raise ValueError('Exact typed receipt')
    print('PASS_GAUSSIAN_SPECTRAL_EXECUTION',json.dumps({k:v for k,v in result.items() if k not in ('shared','lower_bound_samples')},sort_keys=True))
