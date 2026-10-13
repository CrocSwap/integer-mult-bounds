#!/usr/bin/env python3
"""Copied retained centers with reversed23/25 corner and balanced assembly.

Credits: icekylinx PR36 copied-center schedule, James Chang PR34 reversed
corner/balanced parameters, Zhihao Chen PR23/29 semantic assembly,
RaD/hipotures transfer, Aurel Prosz (Paureel) two-stage/copied-stream topology,
Rohan Arun PR31 corner method, Dominik Scholz PR33 dimension refinement,
and Swapnil Jain and earlier contributors. Finite arithmetic is separate
from written simultaneous-basis, stream-scheduling and tape proof obligations.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from math import comb
from pathlib import Path
import argparse, importlib.util, json, sys
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
def load_local(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
inherited=load_local("copied_reversed_inherited_network",ROOT/"scripts/copied_centers_network.py")
balanced=load_local("copied_reversed_balanced_assembly",HERE/"balanced_assembly.py")
assembly,cutoffs,ceil=balanced.assembly,balanced.cutoffs,balanced.ceil
AB=Q(962729831,25000000000000)
AC=Q(717,10**7)
KAPPA=Q(3850771033,10**14)
PR36_COMMIT='11817ccacb564bb7f98789c20dc11d3fece207e3'
def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [js(v) for v in x]
    return x

def read(path):
    return json.loads(path.read_text(),parse_float=lambda s: (_ for _ in ()).throw(ValueError('Floating scientific input: '+s)))

@lru_cache(None)
def logs(value):
    value=Q(value);assert value>=1;power=0
    while value>2:value/=2;power+=1
    def series(x):
        z=(x-1)/(x+1);lower=2*sum((z**(2*j+1)/Q(2*j+1) for j in range(24)),Q())
        return lower,lower+2*z**49/(49*(1-z*z))
    lo,hi=series(value);l2,h2=series(Q(2));lo+=power*l2;hi+=power*h2
    return Q((lo*10**24).numerator//(lo*10**24).denominator,10**24),Q(ceil(hi*10**12),10**12)

def moment(m,W,rows,saving):
    lower=Q();upper=Q();enclosures={}
    for t,n in sorted(rows.items()):
        assert 0<t<m and n>=0
        lo,hi=logs(Q(m,t));u,v=saving*lo,saving*hi;assert 0<=u<=v<1
        weight=Q(n*t,m*W)
        lower+=weight*(1+u+u*u/2+u*u*u/6)
        upper+=weight*(1+v+v*v/(2*(1-v/3)))
        enclosures[t]=dict(lower=lo,upper=hi)
    return dict(saving=saving,lower=lower,upper=upper,strict_gap=1-upper,logarithms=enclosures)

def inputs():
    def get(name):return read(ROOT/'certificates'/('copied-centers-'+name+'.json'))
    return get('bit-axes'),get('complex-input'),get('corner-25-23')

def counts(rows, reversed_corner=True):
    a,b=(r['h'] for r in rows);m=a*b;N=rows[0]['v']*rows[1]['v']
    assert (a,b)==((23,25) if reversed_corner else (25,23))
    for r in rows:assert r['v']==comb(r['h'],3)
    banks={r['h']:N//r['v']*r['R'] for r in rows}
    W=2*N+sum(banks.values());L=sum(N//r['v']*r['loss'] for r in rows)
    parts={};physical=[]
    for row in rows:
        h=row['h'];hist=inherited.physical_histogram(row);physical.append(dict(h=h,**hist))
        internal=Counter()
        for r,n in enumerate(hist['histogram']):
            n*=N//row['v']
            if 2*r>h:internal[2*r-h]+=n;internal[1]+=(h-r)*n
            else:internal[1]+=r*n
        parts[f'internal_{h}']=+internal
        parts[f'exterior_{h}']=Counter({h:banks[h],m-2*h:banks[h]})
        parts[f'growth_{h}']=Counter({1:2*N,h-2:2*N})
    widths=(21,17) if reversed_corner else (21,15)
    singles=(a+b-1)-sum(widths)
    assert singles==(9 if reversed_corner else 11)
    parts['data']=Counter({1:singles*2*N,widths[0]:2*N,widths[1]:2*N,m-2*(a+b-1):2*N})
    parts['paid_correction']=Counter({1:N})
    hist=sum(parts.values(),Counter());s=W*m-N+L
    assert all(0<t<m and n>0 for t,n in hist.items())
    assert sum(t*n for t,n in hist.items())==s
    return dict(dimensions=[a,b],m=m,N=N,B1=banks[a],B2=banks[b],W=W,L=L,total_rank=s,
        deficit=N-L,maxchild=max(hist),child_multiplicities=dict(sorted(hist.items())),
        parts=parts,physical=physical,data_profile=dict(singletons=singles,blocks=[*widths,m-2*(a+b-1)]))

def verify_sources():
    manifest=read(HERE/"SOURCE.json")
    assert manifest["inherited_commit"]==PR36_COMMIT
    for name,digest in manifest["files"].items():
        assert sha256((HERE/name).read_bytes()).hexdigest()==digest, "Source pin mismatch: "+name
    return manifest

def run():
    assert not sys.flags.optimize
    verify_sources()
    # Full upstream arithmetic replay; no producer execution or tracked writes.
    baseline=inherited.certificate()
    axes,phase_row,old_corner=inputs()
    old=counts(axes,False);original=inherited.profile(axes,old_corner)
    assert old['child_multiplicities']==original['child_multiplicities']
    bit=counts(list(reversed(axes)));phase=inherited.profile([phase_row,phase_row])
    for key in ['m','N','W','L','total_rank','deficit','maxchild']:
        assert bit[key]==old[key]
    exact=moment(bit['m'],bit['W'],bit['child_multiplicities'],AB)
    assert exact['upper']<1
    old_at_new=moment(old['m'],old['W'],old['child_multiplicities'],AB)
    assert old_at_new['lower']>1
    next_bit=moment(bit['m'],bit['W'],bit['child_multiplicities'],AB+Q(1,10**14))
    assert next_bit['upper']>=1
    complex_moment=inherited.moment(phase['m'],phase['W'],phase['child_multiplicities'],AC,True)
    f=inherited.finite_bridge(bit,phase,[phase_row,phase_row])
    assert js(f)==js(baseline['finite_bridge'])
    final=assembly(f,AB,KAPPA,a_complex=AC)
    eventual=cutoffs(f,final)
    controls=[]
    for name,kwargs in [('old_guard',dict(old_guard=True)),('old_exposures',dict(old_exposures=True)),('original_prefix',dict(original_prefix=True)),('next_kappa_grid',dict(kappa=KAPPA+Q(1,10**14)))]:
        try:assembly(f,AB,kwargs.pop('kappa',KAPPA),a_complex=AC,**kwargs)
        except AssertionError:controls.append(name)
        else:raise AssertionError('Negative control accepted: '+name)
    altered=json.loads(json.dumps(js(f))); altered['semantic']['E']=64*(f['complex']['W']+f['complex']['m']+1)**3
    try:assembly(altered,AB,KAPPA,a_complex=AC)
    except AssertionError:controls.append('old_semantic_E_without_G')
    else:raise AssertionError('Stale semantic constant accepted')
    paths=[HERE/'witness.py',HERE/'balanced_assembly.py']
    sources=dict(baseline['source_sha256'])
    sources.update({str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths})
    return dict(status='Conditional copied-center reversed-corner witness; finite arithmetic checked, written geometry and tape hypotheses retained',
        inherited_commit=PR36_COMMIT,bit=dict(counts=bit,**exact),complex=dict(counts=phase,**complex_moment),
        finite_bridge=f,assembly=final,eventual_bounds=eventual,negative_controls=controls,
        prior=dict(kappa=baseline['kappa'],bit=baseline['bit']['saving'],profile_at_new_bit_lower=old_at_new['lower']),
        ratio_to_PR36=KAPPA/baseline['kappa'],next_bit_grid=dict(lower=next_bit['lower'],upper=next_bit['upper'],actual_exclusion=next_bit['lower']>1,
        scope='Only the tested grid/enclosure; no global optimality claim'),source_sha256=sources,
        inherited_scope=baseline['scope'],scope='PR36 copied-center physical profile retained. Reversed23/25 data residual replaces21+15+11 by21+17+9 at equal rank mass. PR34 balanced parameters use PR36 enlarged E including scalar G. All47 constraints and7 margins are arithmetic; general basis/scheduling proofs are separate dependencies.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);args=p.parse_args();result=run()
    if args.output:args.output.write_text(json.dumps(js(result),sort_keys=True,indent=2)+'\n')
    print('PASS bit='+str(AB)+'; kappa='+str(KAPPA)+';47 strict constraints;7 margins;stock'+str(result['finite_bridge']['rows']['degree']))
