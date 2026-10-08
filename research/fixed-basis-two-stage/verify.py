#!/usr/bin/env python3
"""Exact fixed-I+J two-stage construction at dimensions (47,45).

Profiles and formulas adapt icekylinx PR32; topology/assembly retain PR29/33.
Dominik Scholz, with substantial GPT-6 Astra/Codex assistance. Apache-2.0.
Rebuild complete profiles with producer.py; retain all inherited attribution.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from math import comb, factorial
import json,sys,hashlib

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'research/two-stage'),str(ROOT/'scripts'),str(ROOT/'research/two-stage-dimensions/corners')]
from two_stage_unequal import profile,prescriptions
from moment import moment_search
from assembly_parameterized import assembly
from cutoffs import js,cutoffs
import importlib.util
from difflib import unified_diff
spec=importlib.util.spec_from_file_location('dimension_predecessor',ROOT/'research/two-stage-dimensions/verify_candidate.py')
predecessor=importlib.util.module_from_spec(spec);spec.loader.exec_module(predecessor)

def lucas_lehmer(exponent):
    assert all(exponent%d for d in range(2,int(exponent**.5)+1))
    m=2**exponent-1;s=4
    for _ in range(exponent-2):s=(s*s-2)%m
    assert s==0
    return m

def tree(edges,n):
    assert len(edges)==n-1
    seen={0}
    while True:
        new=seen|{v for u,v in edges if u in seen}|{u for u,v in edges if v in seen}
        if new==seen:break
        seen=new
    assert len(seen)==n

def run():
    assert not sys.flags.optimize, 'Assertions must remain enabled'
    corner_sources=ROOT/'research/two-stage-dimensions/corners'
    corner_manifest=json.loads((corner_sources/'SOURCE.json').read_text())
    for name,digest in corner_manifest['local_sha256'].items():
        assert hashlib.sha256((corner_sources/name).read_bytes()).hexdigest()==digest,name
    prior=predecessor.run()
    manifest=json.loads((ROOT/'references/fixed32/SOURCE.json').read_text())
    for name,record in manifest['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==record['sha256'],name
    primes=[lucas_lehmer(e) for e in (61,31,19)]
    product=primes[0]*primes[1]*primes[2]
    axes=[];fixed={};bounds={}
    for h in (47,45):
        record=json.loads((ROOT/f'research/two-stage-dimensions/producer-{h}.json').read_text())
        original=record['original']
        assert original['R']==record['matched']['R'] and original['loss']==h*(h-1)
        axes.append(record['matched'])
        f=json.loads((HERE/f'profiles-{h}.json').read_text())
        assert f['h']==h and f['R']==original['R'] and f['loss']==original['loss']
        assert f['rank_sum']==sum(r*n for r,n in enumerate(f['blocks']))==h*f['R']+2*f['loss']
        assert f['crt_disagreements']==0 and f['field_prime']==primes[0]
        fixed[h]=f
        z=3*h-7;single=(4*h-2)*z+27*(h+1)
        D=3*(h+1)*(h-1)**2;B=2*(h-1)*single
        bb={r:sum(comb(h,j)*factorial(j)*B**j*D**(r-j) for j in range(r+1)) for r in (2,3,4)}
        assert bb[2]<primes[0] and bb[3]<product and bb[4]<product
        assert 3*(h+1)*(h-1)<min(primes)
        bounds[h]=dict(single_correction_numerator=single,common_denominator=D,numerator_bound=B,minor_bounds=bb)
    p=profile(*axes);a,b=47,45;m=p['m'];d=a+b-1;N=p['N'];z=Counter(p['rows'])
    M=prescriptions(a,b)
    rows=[(M[i%b][i//b],a+i%b) for i in range(d)]
    cols=[(M[i%b][i//b],a+i%b) for i in range(m-d,m)]
    tree(rows,a+b);tree(cols,a+b)
    # Keep only the universally nonzero first data run, not PR31's second run.
    z[1]-=2*N*(b-2);z[b-2]+=2*N
    for axis in axes:
        h=axis['h'];rep=N//comb(h,3)
        for r,n in enumerate(axis['histogram']):
            if 2*r>h:z[2*r-h]-=rep*n;z[1]-=rep*(h-r)*n
            else:z[1]-=rep*r*n
        for r,n in enumerate(fixed[h]['blocks']):
            if n:z[r]+=rep*n
    z={r:n for r,n in z.items() if n}
    assert min(z.values())>0 and sum(r*n for r,n in z.items())==p['s']
    exact=moment_search(m,p['W'],z,denominator=10**12)
    assert exact['saving']==Q(1663233,10**11)
    f=prior['finite_bridge']
    assert max(z)==f['bit']['maxchild'] and all(0<r<m for r in z)
    f['rows']['degree_gap']=Q(f['rows']['degree_gap']);f['semantic']['C0']=int(f['semantic']['C0'])
    k=Q(16631776,10**12);assembled=assembly(f,exact['saving'],k,beta=Q(1,20),h=Q(1,10**12))
    negatives=[]
    for name,kwargs in [('old_guard',dict(old_guard=True)),('old_exposures',dict(old_exposures=True)),('old_beta',dict(beta=Q(1,10))),('next_kappa_grid',dict(kappa=k+Q(1,10**12)))]:
        parameters=dict(beta=Q(1,20),h=Q(1,10**12),kappa=k)
        parameters.update(kwargs)
        try:assembly(f,exact['saving'],**parameters)
        except AssertionError:negatives.append(name)
        else:raise AssertionError('Negative control accepted: '+name)
    without_data=Counter(z);without_data[b-2]-=2*N;without_data[1]+=2*N*(b-2)
    assert moment_search(m,p['W'],without_data)['saving']<exact['saving']
    negatives.append('omit_data_block_lowers_saving')
    assert exact['next_moment_upper']>=1
    assert len(assembled['constraints'])==47 and len(assembled['margins'])==7
    paths=[Path(__file__),HERE/'producer.py',HERE/'rankone_profiles.cpp',HERE/'README.md',ROOT/'notes/fixed-basis-two-stage.tex',ROOT/'references/fixed32/SOURCE.json']
    return dict(status='CONDITIONAL fixed-basis two-stage witness; not formal verification',
                negative_controls=negatives,source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                profile_sha256={str(h):hashlib.sha256((HERE/f'profiles-{h}.json').read_bytes()).hexdigest() for h in (45,47)},
                basis='Both axes fixed to I+J; original envelope labels and original oriented carrier matchings',
                references=dict(PR32='0ef3aeb61f55cc0b321ce6a0ef00acee25cefe52',PR29='9d963275075fa98f1da821e27757b238dafd6b3c'),
                counts={k:p[k] for k in ('m','N','W','L','s','deficit')},rows=z,
                data_profile=dict(singletons=48,blocks=[43,1933],copies=2*N),fixed_profiles=fixed,
                exactness=dict(primes=primes,prime_product=product,bounds=bounds,tree_nullspace_restrictions=True),
                bit=exact,assembly=assembled,finite_bridge=f,eventual_bounds=cutoffs(f,assembled),
                profiler_sha256=hashlib.sha256((HERE/'rankone_profiles.cpp').read_bytes()).hexdigest())

if __name__=='__main__':
    r=run();(HERE/'certificate.json').write_text(json.dumps(js(r),indent=2,sort_keys=True)+'\n')
    original=(ROOT/'notes/two-stage-corners-47-45-note.tex').read_text()
    updated=(ROOT/'notes/fixed-basis-two-stage.tex').read_text()
    patch=''.join(unified_diff(original.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/notes/two-stage-corners-47-45-note.tex',tofile='b/notes/two-stage-corners-47-45-note.tex'))
    (ROOT/'patches/fixed-basis-two-stage.patch').write_text(patch)
    print('PASS conditional kappa',r['assembly']['parameters']['kappa'],'bit',r['bit']['saving'])
    print('moment gap',float(r['bit']['strict_gap']),'analytic gap',float(r['assembly']['absorption_gap']))
