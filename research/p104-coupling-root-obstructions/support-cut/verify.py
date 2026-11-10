#!/usr/bin/env python3
"""Exact four-arm cut checks. @CubeJerry/OpenAI assistance, Apache-2.0."""
import argparse
from fractions import Fraction
import itertools
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def identity(n):return [[int(i==j) for j in range(n)] for i in range(n)]

def multiply(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]

def subtract(a,b):return [[x-y for x,y in zip(ar,br)] for ar,br in zip(a,b)]

def rank(rows):
    a=[[Fraction(x) for x in row] for row in rows]
    if not a:return 0
    r=0
    for j in range(len(a[0])):
        p=next((i for i in range(r,len(a)) if a[i][j]),None)
        if p is None:continue
        a[r],a[p]=a[p],a[r]
        z=a[r][j];a[r]=[x/z for x in a[r]]
        for i in range(r+1,len(a)):
            z=a[i][j]
            if z:a[i]=[x-z*y for x,y in zip(a[i],a[r])]
        r+=1
        if r==len(a):break
    return r

def arm(n,coords,u,v,left):
    result=[]
    for j,i in enumerate(coords):
        x=[0]*n;y=[0]*n;x[:2]=u;y[:2]=v
        x[i]=1;y[i]=-1 if left else 1
        for k in (coords[:j] if left else coords[j+1:]):x[k]=2
        need(sum(a*b for a,b in zip(x,y))==0,'native nilpotence')
        result.append((x,y))
    return result

def product(sequence,n,coefficient=-2):
    q=identity(n)
    for x,y in sequence:
        row=[sum(y[i]*q[i][j] for i in range(n)) for j in range(n)]
        q=[[q[i][j]+coefficient*x[i]*row[j] for j in range(n)] for i in range(n)]
    return q

def projector(n,coords,hub=None):
    p=[[0]*n for _ in range(n)]
    for i in coords:p[i][i]=1
    if hub is not None:
        for i in range(2):
            for j in range(2):p[i][j]=hub[i][j]
    need(multiply(p,p)==p,'projector idempotence')
    return p

def cross(p,q):return multiply(multiply(p,q),subtract(identity(len(q)),p))

def minor(a,rows,cols):
    b=[[a[i][j] for j in cols] for i in rows]
    return b,b[0][0]*b[1][1]-b[0][1]*b[1][0]

def pair(a,b,second=False):
    n=a+b+2;l=list(range(2,2+a));r=list(range(2+a,n))
    u,v,w=((0,1),(1,1),(-1,0)) if second else ((1,0),(1,-1),(0,1))
    sites=arm(n,l,u,v,True)+arm(n,r,w,v,False)
    return n,l,r,sites,product(sites,n)

def cut_checks(a,b,second=False,reduced=False):
    need(a>=2 if second else b>=2,'critical middle-arm length at least two')
    n,l,r,sites,q=pair(a,b,second)
    if second:
        p=projector(n,[l[0]],[[0,0],[1,1]]) if reduced else projector(n,[0,1,l[0]])
        rows=[1,l[0]] if reduced else [0,1];cols=[l[1],r[-1]]
        expected=(-8 if reduced else -4)*(-1)**a
    else:
        p=projector(n,[r[-1]],[[0,0],[-1,1]]) if reduced else projector(n,[0,1,r[-1]])
        rows=[1,r[-1]] if reduced else [0,1];cols=[l[0],r[-2]]
        expected=(8 if reduced else 4)*(-1)**(a-1)
    block=cross(p,q);small,determinant=minor(block,rows,cols)
    need(determinant==expected,'displayed cross-minor determinant')
    need(rank(block)>=2,'cross-block rank at least two')
    x,y=sites[0 if second else -1]
    need(multiply(p,[[z] for z in x])==[[z] for z in x],'support fixes query image')
    need(multiply([y],p)==[y],'support fixes query covector')
    return {'minor':small,'determinant':determinant,'cross_rank':rank(block)}

def four_arms(lengths,spectators=0):
    n=2+sum(lengths)+spectators;coords=[];cursor=2
    for size in lengths:
        coords.append(list(range(cursor,cursor+size)));cursor+=size
    data=(((1,0),(1,-1),True),((0,1),(1,-1),False),
          ((0,1),(1,1),True),((-1,0),(1,1),False))
    sites=[]
    for indices,(u,v,left) in zip(coords,data):sites+=arm(n,indices,u,v,left)
    for i,(_,y) in enumerate(sites):
        for j,(x,_) in enumerate(sites):
            need(sum(a*b for a,b in zip(y,x))==(i>j)-(i<j),'all sign-Gram entries')
    split=sum(lengths[:2]);prefix=product(sites[:split],n);suffix=product(sites[split:],n)
    p0=projector(n,[0,1,coords[1][-1]]);p1=projector(n,[0,1,coords[2][0]])
    first=minor(cross(p0,prefix),[0,1],[coords[0][0],coords[1][-2]])
    second=minor(cross(p1,suffix),[0,1],[coords[2][1],coords[3][-1]])
    need(first[1]==4*(-1)**(lengths[0]-1),'embedded prefix determinant')
    need(second[1]==-4*(-1)**lengths[2],'embedded suffix determinant')
    return n,coords,sites,{'lengths':list(lengths),'spectators':spectators,
        'prefix_minor':first[0],'suffix_minor':second[0],
        'cross_ranks':[rank(cross(p0,prefix)),rank(cross(p1,suffix))],
        'sign_gram_entries':len(sites)**2}

def reject(action,reason,label,controls):
    try:action()
    except ValueError as error:
        need(reason in str(error),'wrong failure reason for '+label);controls.append(label)
    else:raise ValueError('accepted invalid control: '+label)

def run():
    counts={'original_prefix':0,'original_suffix':0,'reduced_hub_prefix':0,'reduced_hub_suffix':0}
    for a in range(1,9):
        for b in range(1,9):
            if b>=2:
                cut_checks(a,b);counts['original_prefix']+=1
                cut_checks(a,b,reduced=True);counts['reduced_hub_prefix']+=1
            if a>=2:
                cut_checks(a,b,second=True);counts['original_suffix']+=1
                cut_checks(a,b,second=True,reduced=True);counts['reduced_hub_suffix']+=1
    embedded=[four_arms((4,4,5,5),s)[3] for s in (0,2,5)]
    need(all(v==56 for v in counts.values()),'all declared length pairs completed')
    placements=0
    for gaps in itertools.combinations_with_replacement(range(19),3):
        before=sum(g<8 for g in gaps);after=sum(g>8 for g in gaps)
        need(not(before>=2 and after>=2),'three-thin cut counts impossible');placements+=1
    need(placements==1330,'all unordered three-thin gap placements')
    need(sum(g<8 for g in (0,0,18,18))==2 and sum(g>8 for g in (0,0,18,18))==2,
         'four-thin count obstruction is not a five-thin lower bound')
    controls=[]
    reject(lambda:cut_checks(1,1),'middle-arm length','R0 length one outside theorem',controls)
    reject(lambda:cut_checks(1,1,second=True),'middle-arm length','L1 length one outside theorem',controls)
    n,l,r,sites,q=pair(1,1)
    need(rank(cross(projector(n,[0,1,r[-1]]),q))==1,'short-arm cross rank really drops')
    n,l,r,sites,q=pair(2,2)
    need(rank(cross(identity(n),q))==0,'enlarged support removes cut')
    controls.append('whole-space support removes cross block')
    inverse=product(list(reversed(sites)),n,coefficient=2)
    need(multiply(inverse,q)==identity(n),'higher-rank cancellation is exact')
    reject(lambda:need(rank(subtract(inverse,identity(n)))<=1,'rank-one thin'),
           'rank-one thin','single higher-rank inverse is not a thin',controls)
    n,coords,sites,_=four_arms((2,2,2,2))
    total=product(sites,n);p=projector(n,[0,1,coords[0][0]])
    prefix=product(sites[:1],n);suffix=product(sites[1:],n)
    need(multiply(p,prefix)==multiply(prefix,p),'first prefix commutes')
    need(multiply(p,suffix)!=multiply(suffix,p),'suffix need not commute without scalar endpoint')
    reject(lambda:need(total==[[-int(i==j) for j in range(n)] for i in range(n)],'scalar endpoint'),
           'scalar endpoint','missing scalar endpoint invalidates suffix inference',controls)
    n,l,r,sites,q=pair(2,2);p=projector(n,[0,1,r[-1]])
    inverse=product(list(reversed(sites)),n,coefficient=2)
    transported=multiply(multiply(inverse,p),q)
    need(multiply(transported,transported)==transported,'transport is still an idempotent')
    reject(lambda:need(transported==p,'constant transported projector'),
           'constant transported projector','fixed support transport is S-dependent',controls)
    perturbation=[]
    for k in (0,1,2,3):
        altered=list(sites)
        for j in range(k):
            x=[int(i==j) for i in range(n)];y=[int(i==(j+1)%n) for i in range(n)]
            altered.insert(j*2,(x,y))
        change=rank(subtract(product(altered,n),q))
        need(change<=k,'rank-one insertion perturbation bound')
        perturbation.append({'insertions':k,'difference_rank':change})
    return {'claim':'At least four thins for fixed natural supports; no net-cost or kappa claim',
        'length_conditions':{'a':'>=1','b':'>=2','c':'>=2','d':'>=1'},
        'length_pair_domain':[1,8],'minor_checks':counts,'embedded_cases':embedded,
        'three_thin_placements':placements,'placement_stop_rule':'exhaust unordered placements in 19 gaps',
        'four_thin_count_only_witness':[0,0,18,18],
        'rank_perturbation_controls':perturbation,'negative_controls':controls,
        'seed':None,'all_length_proof':'PROOF.md; finite checks are corroboration'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true')
    args=parser.parse_args();result=run();path=HERE/'RESULT.json'
    if args.write:path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(json.loads(path.read_text())==result,'frozen exact result')
    print('PASS_FOUR_ARM_CUT_BOUND '+json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
