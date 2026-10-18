#!/usr/bin/env python3
"""Exact F2[Q8] arithmetic for the bounded three-register word search."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PACKAGE=Path(__file__).resolve().parent
SEED='189ad74f7eb7b99d43830c0ed0f15958'
# Element id u+4*sign: u=0,1,2,3 means 1,i,j,k; sign 0 is positive.
UNIT_PRODUCT=(
 ((1,0),(1,1),(1,2),(1,3)),
 ((1,1),(-1,0),(1,3),(-1,2)),
 ((1,2),(-1,3),(-1,0),(1,1)),
 ((1,3),(1,2),(-1,1),(-1,0)),
)
GROUP=tuple(range(8))
NONIDENTITY=tuple(range(1,8))

def need(ok,why):
    if not ok: raise ValueError(why)

def qmul(a,b):
    sa,ua=divmod(a,4); sb,ub=divmod(b,4)
    sign,unit=UNIT_PRODUCT[ua][ub]
    neg=(sa^sb^(sign<0))
    return unit+4*int(bool(neg))

def ga_mul(a,b):
    out=0
    for i in range(8):
        if (a>>i)&1:
            for j in range(8):
                if (b>>j)&1: out^=1<<qmul(i,j)
    return out

def dot(a,b): return (a&b).bit_count()&1

def load_pins():
    import hashlib
    manifest=json.loads((PACKAGE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage']!='input': continue
        path=ROOT/row['path']
        need(path.is_file(),'missing pinned input: '+row['path'])
        need(hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'],
             'input hash mismatch: '+row['path'])

def idempotents():
    result=[]
    for x in range(1,8):
        for y in range(8):
            if dot(x,y):
                result.append((x,y,tuple(((x>>r)&1)*((y>>c)&1)
                                         for r in range(3) for c in range(3))))
    need(len(result)==28,'rank-one idempotent count')
    return result

def validate_idempotent(N):
    need(len(N)==9 and all(v in (0,1) for v in N),'3x3 binary matrix')
    for r in range(3):
        for c in range(3):
            value=0
            for k in range(3): value^=N[3*r+k]&N[3*k+c]
            need(value==N[3*r+c],'matrix is not idempotent')
    need(sum(N)!=0 and rank_binary(N)==1,'matrix is not rank one')

def rank_binary(flat):
    rows=[sum(flat[3*r+c]<<c for c in range(3)) for r in range(3)]
    rank=0
    for c in range(3):
        p=next((r for r in range(rank,3) if (rows[r]>>c)&1),None)
        if p is None: continue
        rows[rank],rows[p]=rows[p],rows[rank]
        for r in range(3):
            if r!=rank and ((rows[r]>>c)&1): rows[r]^=rows[rank]
        rank+=1
    return rank

def factor(N,g):
    ge=(1<<g)^1
    return tuple(((1<<(0)) if r==c else 0) ^ (ge if N[3*r+c] else 0)
                 for r in range(3) for c in range(3))

def mat_mul(A,B):
    C=[]
    for r in range(3):
        for c in range(3):
            z=0
            for k in range(3): z^=ga_mul(A[3*r+k],B[3*k+c])
            C.append(z)
    return tuple(C)

def target(i=1,j=2,k=3):
    return (1<<i,0,0,0,1<<j,0,0,0,1<<k)

def direct_three():
    E1=(1,0,0,0,0,0,0,0,0)
    E2=(0,0,0,0,1,0,0,0,0)
    E3=(0,0,0,0,0,0,0,0,1)
    return mat_mul(mat_mul(factor(E1,1),factor(E2,2)),factor(E3,3))

def enumerate_two_call():
    ns=idempotents(); digest=hashlib.sha256(); histogram={}; nearest=73; hits=0; count=0
    tgt=target()
    for ni,(x,y,N) in enumerate(ns):
        A_by_g=[factor(N,g) for g in NONIDENTITY]
        for g,A in zip(NONIDENTITY,A_by_g):
            for mi,(u,v,M) in enumerate(ns):
                for h in NONIDENTITY:
                    out=mat_mul(A,factor(M,h)); distance=sum((a^b).bit_count() for a,b in zip(out,tgt))
                    histogram[distance]=histogram.get(distance,0)+1
                    nearest=min(nearest,distance); hits+=distance==0; count+=1
                    digest.update(bytes((ni,g,mi,h)))
                    digest.update(bytes(out))
    return {'alphabet_words':count,'idempotents':len(ns),'nonidentity_group_labels':len(NONIDENTITY),
            'target_hits':hits,'minimum_coefficient_hamming_distance':nearest,
            'distance_histogram':{str(k):histogram[k] for k in sorted(histogram)},
            'ordered_word_output_sha256':digest.hexdigest()}

def enumerate_one_call():
    ns=idempotents(); digest=hashlib.sha256(); histogram={}; hits=0; count=0
    tgt=target()
    for ni,(x,y,N) in enumerate(ns):
        for g in NONIDENTITY:
            out=factor(N,g)
            distance=sum((a^b).bit_count() for a,b in zip(out,tgt))
            histogram[distance]=histogram.get(distance,0)+1
            hits+=distance==0; count+=1
            digest.update(bytes((ni,g)))
            digest.update(bytes(out))
    return {'alphabet_words':count,'idempotents':len(ns),
            'nonidentity_group_labels':len(NONIDENTITY),'target_hits':hits,
            'minimum_coefficient_hamming_distance':min(histogram),
            'distance_histogram':{str(k):histogram[k] for k in sorted(histogram)},
            'ordered_word_output_sha256':digest.hexdigest()}
