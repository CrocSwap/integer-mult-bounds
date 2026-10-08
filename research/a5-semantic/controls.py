#!/usr/bin/env python3
"""Exact retained-basis A5 controls by Rohan Arun with OpenAI Codex assistance.

The basis prescriptions are icekylinx's PR18; source-frame composition is
Zhihao Chen's PR21. Finite controls supplement the new written block proof.
"""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import json,random


def line(n,rng):
    p=[Q(rng.randrange(1,100)) for _ in range(n)]
    xi=[Q(rng.randrange(1,100)) for _ in range(n)]
    d=sum(x*y for x,y in zip(p,xi))
    return p,[x/d for x in xi]


def corner(p,xi,v,nu,wrong_boundary=False):
    R=list(range(25))+list(range(7))+list(range(25))*2
    C=list(range(25))*2+list(range(7))+list(range(25))
    if wrong_boundary:
        C[58],C[80]=C[80],C[58]
    out=[]
    for i in range(47):
        beta=i%23;a=R[i]
        out.append([int(beta==(528+j)%23)*p[a]*xi[C[35+j]]
                    +int(a==C[35+j])*v[beta]*nu[(528+j)%23]
                    -p[a]*xi[C[35+j]]*v[beta]*nu[(528+j)%23]
                    for j in range(47)])
    return out


def ordered_pivots(matrix):
    a=[row[:] for row in matrix];active=set(range(len(a[0])));out=[]
    for i in range(len(a)):
        nz=[j for j in active if a[i][j]]
        if not nz:continue
        j=max(nz);active.remove(j);out.append((i,j))
        for k in range(i+1,len(a)):
            q=a[k][j]/a[i][j]
            if q:a[k]=[x-q*y for x,y in zip(a[k],a[i])]
    return out


def run():
    expected=[(i,i+24) for i in range(1,22)]
    records=[]
    for seed in (210101,210102,210103,210104):
        rng=random.Random(seed);p,xi=line(25,rng);v,nu=line(23,rng)
        assert sum(x*y for x,y in zip(p,xi))==sum(x*y for x,y in zip(v,nu))==1
        q=corner(p,xi,v,nu);pivots=ordered_pivots(q)
        assert len(pivots)==47 and pivots[1:22]==expected
        assert ordered_pivots([[-x for x in row] for row in q])==pivots
        assert q[0][46]==-p[0]*xi[24]*v[0]*nu[22]
        for i in range(1,22):
            for j in range(25,46):
                schur=q[i][j]-q[i][46]*q[0][j]/q[0][46]
                formula=int(i==j-24)*p[i]*xi[j-22]+int(i==j-22)*v[i]*nu[j-24]
                assert schur==formula
                if j>i+24:assert schur==0
                if j==i+24:assert schur==p[i]*xi[i+2] and schur!=0
        # The raw corner has upper-right entries; the first pivot cancellation
        # is necessary. An incorrect retained-boundary substitution also fails.
        assert q[1][45]!=0
        wrong=ordered_pivots(corner(p,xi,v,nu,wrong_boundary=True))
        assert wrong[1:22]!=expected
        records.append(dict(seed=seed,field='Q',corner_rank=47,
                            block_rows=[1,21],block_corner_columns=[25,45],
                            block_physical_inner_columns=[553,573],
                            exact_schur_formula_checked=True,
                            negative_controls=['omit_first_pivot_cancellation','wrong_inverse_column_boundary']))
    here=Path(__file__).resolve().parent;root=here.parents[1]
    files=[Path(__file__).resolve(),here/'a5-block.tex']
    return dict(status='EXACT FINITE A5 BLOCK CONTROLS; NOT FORMAL THEOREM VERIFICATION',
                cases=records,conservative_profile=dict(singletons=26,blocks=[21,481],rank_sum=528),
                source_sha256={str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in files})


if __name__=='__main__':
    result=run();Path(__file__).with_name('a5-controls.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS four exact-Q A5 corners; contiguous21 block; two negative controls per case')
