"""Check original-header sectors against independent full residual matrices.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Source factor construction and full invariant oracles retain their credit.
"""
import argparse
from copy import deepcopy
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from header import profile, central_from_header, kernel_bases
from central import representative
from block_source import eye, zero, add, mul, rref, rank, kernel, inverse, complete_factor, schur
from upstream_verify import rank_columns, signature, jordan


def need(value,message):
    if not value:raise ValueError(message)


def reject(call):
    try:call()
    except ValueError:return
    raise ValueError('invalid case accepted')


def rank_factor(a,q):
    d=len(a);pivots=rref(a,q)[1];k=len(pivots)
    x=tuple(tuple(row[j] for j in pivots) for row in a)
    if not k:return x,()
    reduced,_=rref(tuple(u+v for u,v in zip(x,a)),q,k)
    y=tuple(row[k:] for row in reduced[:k])
    need(mul(x,y,q)==a,'rank factor product')
    return x,y


def factors_for(h,q,variant=0,padding=(0,0,0)):
    d=len(h);w=add(eye(d),h,q,-1)
    x,y=rank_factor(tuple(tuple(-v%q for v in row) for row in w),q)
    if variant:
        # Two unused product channels can change either factor rank.
        x=tuple(row+(int(variant in (2,4) and i==0),0) for i,row in enumerate(x))
        y=y+((0,)*d,tuple(int(variant in (3,4) and j==d-1) for j in range(d)))
    factors=[(x,y)]
    for a,pad in zip((w,w,h),padding):
        x,y=complete_factor(a,q)
        factors.append((tuple(row+(0,)*pad for row in x),y+zero(pad,d)))
    return factors


def change_sector_bases(factors,q):
    result=[]
    for sector,(x,y) in enumerate(factors):
        r=len(y)
        if r<2:result.append((x,y));continue
        g=[list(row) for row in eye(r)]
        for j in range(r-1):g[j][j+1]=(sector+j+1)%q
        g=tuple(map(tuple,g));result.append((mul(x,inverse(g,q),q),mul(g,y,q)))
    return result


def inspect(h,q,variant=0,padding=(0,0,0),change=False,central=True):
    factors=factors_for(h,q,variant,padding)
    if change:factors=change_sector_bases(factors,q)
    d=len(h);sizes=tuple(len(y) for x,y in factors);n=sum(sizes)
    x=tuple(sum((a[i] for a,b in factors),()) for i in range(d));y=sum((b for a,b in factors),())
    need(mul(x,y,q)==eye(d),'literal split')
    residual_basis=kernel(x,q)
    frame=tuple(a+b for a,b in zip(y,residual_basis));frame_inverse=inverse(frame,q)
    labels=sum(((j,)*r for j,r in enumerate(sizes)),())
    p0=tuple(tuple(int(i==j and labels[i] in (1,3)) for j in range(n)) for i in range(n))
    q0=tuple(tuple(int(i==j and labels[i] in (2,3)) for j in range(n)) for i in range(n))
    p=mul(mul(frame_inverse,p0,q),frame,q);t=mul(mul(frame_inverse,q0,q),frame,q)
    need(mul(p,p,q)==p and mul(t,t,q)==t and mul(p,t,q)==mul(t,p,q),'commuting projectors')
    need(tuple(row[:d] for row in p[:d])==eye(d) and tuple(row[:d] for row in t[:d])==eye(d),'common identity pivot')
    need(tuple(row[:d] for row in mul(p,t,q)[:d])==h,'prescribed H')
    s,u=schur(p,d,q),schur(t,d,q);m=n-d
    comm=add(mul(s,u,q),mul(u,s,q),q,-1)
    need(rank_columns(comm,q)==2*d,'literal sharpness')
    expected=profile(d,sizes)
    bases=kernel_bases(factors,q)
    actual=[];all_columns=[]
    for index,((a,b),columns) in enumerate(zip(((0,0),(1,0),(0,1),(1,1)),bases)):
        actual.append(m-rank_columns(add(s,eye(m),q,-a)+add(u,eye(m),q,-b),q))
        need(len(columns)==expected[index]==actual[-1],'joint-sector dimension')
        if columns:
            matrix=tuple(zip(*columns))
            need(rank_columns(matrix,q)==len(columns),'independent basis columns')
            need(mul(x,matrix,q)==zero(d,len(columns)),'basis lies in original residual space')
            coordinates=mul(frame_inverse,matrix,q)
            need(coordinates[:d]==zero(d,len(columns)),'zero pivot coordinates')
            coordinates=coordinates[d:]
            need(mul(s,coordinates,q)==tuple(tuple(a*v%q for v in row) for row in coordinates),'S sector action')
            need(mul(u,coordinates,q)==tuple(tuple(b*v%q for v in row) for row in coordinates),'T sector action')
            all_columns+=list(zip(*coordinates))
    need(rank_columns(tuple(zip(*all_columns)),q)==m-2*d,'complete commutator kernel basis')
    need(expected[1]+expected[2]==rank_columns(p,q)+rank_columns(t,q)-2*rank_columns(mul(p,t,q),q)-2*d,
         'original-rank shortcut')
    prediction=central_from_header(h,sizes,q)
    if central:
        difference=add(s,u,q,-1);z=mul(difference,difference,q)
        need(signature(z,q)==signature(representative(prediction,q),q),'complete central class')
    return dict(q=q,h=[list(row) for row in h],sizes=list(sizes),kernel_sectors=list(expected),
                ranks00=[rank(factors[0][0],q),rank(factors[0][1],q)] if sizes[0] else [0,0],
                prediction=prediction)


def run(small):
    for row in json.loads((ROOT/'SOURCES.json').read_text())['files']:
        if row['path'].startswith('research/schur-header-kernel-sectors/'):
            need(hashlib.sha256((ROOT.parents[1]/row['path']).read_bytes()).hexdigest()==row['sha256'],'source bytes')
    domains=[];digest=hashlib.sha256();count=0
    for q,d in ([(2,1),(2,2)] if small else [(2,1),(2,2),(2,3),(3,1),(3,2),(5,1),(5,2)]):
        size=0
        for data in product(range(q),repeat=d*d):
            h=tuple(tuple(data[i*d:(i+1)*d]) for i in range(d))
            r=inspect(h,q);digest.update(json.dumps(r,sort_keys=True).encode());count+=1;size+=1
        domains.append(dict(q=q,d=d,count=size))
    examples=[]
    for q in (2,3,5,7):
        for d in (1,2,3):
            for lam in (0,1):
                for variant in (1,2,3,4):
                    examples.append(inspect(jordan(d,lam,q),q,variant,(1,0,1),change=True))
    h=((0,0,0,1),(1,0,0,0),(0,1,0,1),(0,0,1,0))
    examples.append(inspect(h,2,4,(0,1,0),True))
    examples.append(inspect(((0,0,0,2),(1,0,0,0),(0,1,0,1),(0,0,1,0)),3,4,(1,0,0),True))
    empty=inspect(((1,),),2)
    need(empty['sizes'][0]==0 and empty['kernel_sectors']==[0,1,1,0],'empty 00 boundary')
    controls=0
    reject(lambda:profile(1,(1,0,1,1)));controls+=1
    reject(lambda:profile(1,(True,1,1,1)));controls+=1
    bad=[(((0,),),((0,),)),(((0,),),((0,),)),(((0,),),((0,),)),(((1,),),((1,),))]
    reject(lambda:kernel_bases(bad,2));controls+=1
    bad=deepcopy(factors_for(((0,),),2));bad[3]=(((1,0),),((1,),(0,)))
    reject(lambda:kernel_bases(bad,2));controls+=1
    base=inspect(((0,),),3)
    need(base['kernel_sectors'][0]!=0,'00 projection differs from ker pi within V00');controls+=1
    # Same H and residual dimension, with opposite or equal sector padding.
    a=inspect(((0,),),2,1,(0,0,0));b=inspect(((0,),),2,0,(1,1,0))
    need(a['prediction']['dimension']==b['prediction']['dimension'] and a['prediction']!=b['prediction'],'original profile matters');controls+=1
    return dict(status='PASS',domains=domains,complete_H_count=count,additional_cases=len(examples),
                domain_digest=digest.hexdigest(),examples=examples,empty00=empty,controls=controls)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--small',action='store_true');ap.add_argument('--write-result',action='store_true');a=ap.parse_args();r=run(a.small)
    if not a.small:
        if a.write_result:(ROOT/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
        else:need(r==json.loads((ROOT/'RESULT.json').read_text()),'receipt differs')
    print(json.dumps({k:v for k,v in r.items() if k!='examples'},sort_keys=True));print('PASS_SCHUR_HEADER_KERNEL_SECTORS')


if __name__=='__main__':main()
