"""Fixed 12-candidate diagnostic; no solver, no unbounded search.

Build an exact 18-Y-label subsystem with one regular block. Test whether
each remaining Y label can even be added individually. Negative results
apply only to the saved concrete candidates.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import json
import random
import time
from local_support_elimination import ADJ,CLIQUE,TRIPLES,classes
from local_rank_test import Y,line_graph
from mixed_rank_search import coordinate_supports
from noncovariant_search import multiply,inverse
from covariant_block_test import rank

EXCEPTIONS=tuple(range(1,7))
FIXED=sorted(i for j in CLIQUE[0] for i in classes()[j][1])
REMAINING=sorted(set(Y)-set(FIXED))


def nullspace(rows,width):
    a=[[Q(x) for x in row] for row in rows];pivots=[];r=0
    for c in range(width):
        p=next((i for i in range(r,len(a)) if a[i][c]),None)
        if p is None:continue
        a[p],a[r]=a[r],a[p];value=a[r][c];a[r]=[x/value for x in a[r]]
        for i in range(len(a)):
            if i!=r and a[i][c]:
                value=a[i][c];a[i]=[x-value*y for x,y in zip(a[i],a[r])]
        pivots.append(c);r+=1
    basis=[]
    for c in range(width):
        if c in pivots:continue
        v=[Q(0)]*width;v[c]=1
        for i,p in enumerate(pivots):v[p]=-a[i][c]
        basis.append(v)
    return basis


def exact_rank(rows):return rank(rows) if rows and rows[0] else 0


def build(seed):
    rng=random.Random(seed);colors=line_graph(0)['colors'];factors={};recipe=[]
    angles=[Q(1),Q(2),Q(1,2),Q(-1)]
    for point in CLIQUE[0]:
        private=[2*k+c for k,line in enumerate(CLIQUE) if point in line and k!=0 for c in (0,1)]
        if seed:rng.shuffle(private)
        transform=[[Q(i==j) for j in range(4)] for i in range(4)]
        if seed:
            for _ in range(4):
                i,j=rng.sample(range(4),2);s=rng.choice([-1,1])
                transform[i]=[x+s*y for x,y in zip(transform[i],transform[j])]
        inv=inverse(transform);used_angles=[]
        for outside in (7,8):
            clique=[i for i in classes()[point][1] if outside in TRIPLES[i]]
            singleton=next(i for i in clique if set(TRIPLES[i])-{outside}<=set(CLIQUE[0]))
            others=sorted(set(clique)-{singleton});color=colors[str(singleton)]
            t=angles[(seed+point+outside)%len(angles)] if seed else Q(1);used_angles.append(str(t))
            p0,p1,p2,p3=private
            specifications=[(singleton,{color:Q(1)},{color:Q(1)},p0),
                            (others[0],{1-color:Q(1),p1:t},{1-color:1/(1+t*t),p1:t/(1+t*t)},p2),
                            (others[1],{1-color:t,p1:Q(-1)},{1-color:t/(1+t*t),p1:-1/(1+t*t)},p3)]
            for i,first,dual,second in specifications:
                a=[[Q(0),Q(0)] for _ in range(14)];b=[[Q(0)]*14 for _ in range(2)]
                for c,x in first.items():a[c][0]=x
                for c,x in dual.items():b[0][c]=x
                a[second][1]=b[1][second]=Q(1)
                aa=multiply(transform,[a[c] for c in private])
                bb=multiply([[row[c] for c in private] for row in b],inv)
                for u,c in enumerate(private):
                    a[c]=aa[u]
                    for k in range(2):b[k][c]=bb[k][u]
                factors[i]=(a,b)
        recipe.append({'point':point,'private_coordinates':private,'angles':used_angles,
                       'private_transform':[[str(x) for x in row] for row in transform]})
    verify_partial(factors)
    return factors,recipe


def verify_partial(factors):
    supports,forced=coordinate_supports(EXCEPTIONS);assert set(factors)==set(FIXED)
    for i,(a,b) in factors.items():
        assert len(a)==14 and len(b)==2 and all(len(row)==2 for row in a) and all(len(row)==14 for row in b)
        assert multiply(b,a)==[[1,0],[0,1]]
        for c in range(14):
            if c not in supports[i]:assert a[c]==[0,0] and b[0][c]==b[1][c]==0
            if c in forced[i]:assert any(a[c]) and any(b[k][c] for k in range(2))
    for i,j in combinations(FIXED,2):
        if ADJ[i]>>j&1:
            assert multiply(factors[i][1],factors[j][0])==[[0,0],[0,0]]
            assert multiply(factors[j][1],factors[i][0])==[[0,0],[0,0]]
    return True


def extension_constraints(factors,target):
    supports,_=coordinate_supports(EXCEPTIONS);coords=sorted(supports[target])
    neighbors=[i for i in FIXED if ADJ[i]>>target&1]
    ca=[[factors[i][1][k][c] for c in coords] for i in neighbors for k in range(2)]
    cb=[[factors[i][0][c][k] for c in coords] for i in neighbors for k in range(2)]
    return coords,ca,cb


def extension_test(factors,target):
    coords,ca,cb=extension_constraints(factors,target)
    na=nullspace(ca,len(coords));nb=nullspace(cb,len(coords))
    pairing=[[sum(x*y for x,y in zip(b,a)) for a in na] for b in nb]
    return {'target':target,'triple':list(TRIPLES[target]),'coordinates':coords,
            'A_kernel_basis':[[str(x) for x in row] for row in na],
            'B_kernel_basis':[[str(x) for x in row] for row in nb],
            'normalization_pairing_rank':exact_rank(pairing),
            'individually_attachable':exact_rank(pairing)>=2}


def verify_extension(factors,result):
    coords,ca,cb=extension_constraints(factors,result['target']);assert coords==result['coordinates']
    na=[[Q(x) for x in row] for row in result['A_kernel_basis']]
    nb=[[Q(x) for x in row] for row in result['B_kernel_basis']]
    for matrix,basis in [(ca,na),(cb,nb)]:
        assert all(len(v)==len(coords) for v in basis)
        assert all(sum(x*y for x,y in zip(row,v))==0 for row in matrix for v in basis)
        # Independent rank replay certifies that the displayed kernel is complete.
        assert exact_rank(basis)==len(basis)
        assert exact_rank(matrix)+len(basis)==len(coords)
    pairing=[[sum(x*y for x,y in zip(b,a)) for a in na] for b in nb]
    r=exact_rank(pairing)
    assert r==result['normalization_pairing_rank']
    assert result['individually_attachable']==(r>=2)
    return True


def audit():
    start=time.monotonic();candidates=[]
    for seed in range(12):
        factors,recipe=build(seed);tests=[extension_test(factors,i) for i in REMAINING]
        for result in tests:verify_extension(factors,result)
        candidates.append({'seed':seed,'recipe':recipe,
                           'partial_factors':[{'vertex':i,'A':[[str(x) for x in row] for row in a],
                                               'B':[[str(x) for x in row] for row in b]} for i,(a,b) in sorted(factors.items())],
                           'extension_tests':tests,
                           'individually_attachable_labels':sum(t['individually_attachable'] for t in tests)})
    return {'status':'BOUNDED CONCRETE-CANDIDATE DIAGNOSTIC; NO NEW KAPPA',
            'fixed_budget':'12 deterministic candidates, 24 individual extension checks each; no adaptive expansion.',
            'regular_block':0,'partial_labels':18,'remaining_Y_labels':24,
            'candidates':candidates,'seconds':time.monotonic()-start,
            'scope':'The concrete 18-label partial constructions and their individual Y extensions only. No general impossibility theorem, full 42-Y certificate, X labels or multiplication witness.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=audit();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'seconds':result['seconds'],
                     'attachable_labels_by_candidate':[c['individually_attachable_labels'] for c in result['candidates']]},indent=2))
