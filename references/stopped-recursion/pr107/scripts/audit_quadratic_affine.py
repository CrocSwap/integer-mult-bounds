#!/usr/bin/env python3
"""Exact rank witnesses for real and Gaussian quadratic-phase labels."""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import json

from certify import require,verify_sources
from prepare_layers import serializable
from experiments.quadratic_affine import family,vector,rank_witness
from audit_joint_frames import matrix,rank

ROOT=Path(__file__).resolve().parents[1]


def span_control(t,parity):
    f=family(t,False,parity);D=f['D'];selected=[]
    if parity in (None,0):selected=[vector(f,i) for i in range(D)]
    else:
        for i,(support,linear,quadratic) in enumerate(f['blocks']):
            if support.bit_count()!=2 or not support&1:continue
            offset=f['ends'][i-1] if i else 0
            selected.append(vector(f,offset))
            if support==3:selected.append(vector(f,offset+1))
    rows=[[0 if not s>>j&1 else (-1 if hi>>j&1 else 1) for j in range(D)]
          for s,lo,hi in selected]
    require(rank(matrix(rows))==D,'Real rational dimension is not certified')
    return dict(t=t,parity=parity,spanning_vectors=len(rows),exact_rank=D)


def certificate():
    fixtures=json.loads((ROOT/'scripts/experiments/quadratic_affine_witnesses.json').read_text())
    require(len(fixtures)==12,'Missing phase-family cases')
    cases=[]
    for w in fixtures:
        r=rank_witness(**w)
        require(r['positive_deficit_excluded'],'An unexcluded candidate needs further work')
        cases.append(r)
    controls=[span_control(t,p) for t in (3,4,5) for p in (0,1,None)]
    for t in (3,4,5):
        f=family(t,True);D=f['D']
        require(all(vector(f,i)==(1<<i,0,0) for i in range(D)),
                'Missing complex coordinate basis')
    sources=('scripts/audit_quadratic_affine.py','scripts/experiments/quadratic_affine.py',
             'scripts/experiments/quadratic_affine_witnesses.json',
             'docs/research/quadratic-affine-vectors.md')
    return dict(status='TWELVE SPECIFIED CENTRAL MATRICES REJECTED; NO NEW KAPPA',
                upstream_commit=verify_sources(),retained_kappa=Q(1,2**31),cases=cases,
                rational_span_controls=controls,
                scope='Full orthogonality central matrices on exactly the declared real/Gaussian families; not arbitrary supported matrices or subfamilies.',
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/quadratic-affine-vectors.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS: twelve exact quadratic-affine core rejections, including Gaussian rank-two labels.')
