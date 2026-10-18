#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact audit by woklerx with substantial OpenAI Codex assistance."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product, permutations
from math import isqrt
import json, hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def require(ok, message):
    if not ok: raise ValueError(message)
def source_check():
    for row in json.loads((HERE/'EXTERNAL-SOURCES.json').read_text()):
        b=(HERE/row['local']).read_bytes()
        require(hashlib.sha256(b).hexdigest()==row['sha256'],'external source bytes')
        require(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'external Git blob')
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            require(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'live source bytes')
source_check()

def mm(A,B):
    out=[]
    for a in A:
        row=0
        for j,b in enumerate(B):
            if (a>>j)&1:row^=b
        out.append(row)
    return tuple(out)
def rank(A):
    piv={}
    for a in A:
        while a:
            k=a.bit_length()-1
            if k in piv:a^=piv[k]
            else:piv[k]=a;break
    return len(piv)
def inv(A):
    n=len(A);rows=[a|((1<<i)<<n) for i,a in enumerate(A)]
    for i in range(n):
        p=next((j for j in range(i,n) if (rows[j]>>i)&1),None)
        if p is None:return None
        rows[i],rows[p]=rows[p],rows[i]
        for j in range(n):
            if j!=i and (rows[j]>>i)&1:rows[j]^=rows[i]
    return tuple(a>>n for a in rows)
I=(1,2,4);allG=list(product(range(8),repeat=3));GL=[g for g in allG if inv(g) is not None]
require(len(GL)==168,'GL3 cardinality')
rows=[];zeroJexample=None
for r in (1,2):
    admitted=jinvertible=0;pairs=set()
    for G in GL:
        Delta=tuple(a^b for a,b in zip(G,I));ds={i for i,a in enumerate(Delta) if a}
        Gi=inv(G);require(ds=={i for i,a in enumerate(Gi) if a!=I[i]},'inverse changed-row support')
        for L in product(range(8),repeat=r):
            R=mm(L,G);difference=tuple(a^b for a,b in zip(R,L))
            if rank(difference)!=r:continue
            require(rank(Delta)>=r,'source rank floor')
            for K in product(range(1,1<<r),repeat=3):
                KR=mm(K,R);J=tuple(a^b for a,b in zip(I,KR));H=mm(J,Delta)
                hs={i for i,a in enumerate(H) if a}
                require(ds|hs=={0,1,2},'endpoint support cover')
                require(rank(mm(R,Delta))==r,'surjective query change')
                admitted+=1
                if inv(J) is not None:
                    require(rank(H)>=r and len(hs)>=r,'target rank floor requires invertible J')
                    jinvertible+=1;pairs.add((len(ds),len(hs)))
                elif rank(H)<r and zeroJexample is None:zeroJexample={'r':r,'L':L,'R':R,'K':K,'G':G,'H':H}
    rows.append({'query_rank':r,'full_query_cases':admitted,'invertible_J_cases':jinvertible,'endpoint_support_pairs':sorted(map(list,pairs))})
require(zeroJexample is not None,'missing J invertibility control')
# Complete search for independent premise-removal controls in n=3,r=1.
controls={}
for G in allG:
    for l in range(8):
        R=mm((l,),G);Delta=tuple(a^b for a,b in zip(G,I))
        for K in product((0,1),repeat=3):
            J=tuple(a^b for a,b in zip(I,mm(K,R)))
            if inv(J) is None:continue
            H=mm(J,Delta);covered=all(d or h for d,h in zip(Delta,H))
            if covered or not l or not R[0] or not any(K):continue
            premises={'invertible_G':inv(G) is not None,'full_rank_difference':R[0]!=l,'nonzero_K_rows':all(K)}
            failures=[k for k,v in premises.items() if not v]
            if len(failures)==1 and failures[0] not in controls:controls[failures[0]]={'G':G,'L':[l],'R':R,'K':K,'Delta':Delta,'H':H}
    if len(controls)==3:break
require(len(controls)==3,'all three premise-removal controls')
# Rational sharp toy, independently multiplied over Q (not a field-reduction inference).
def qmm(A,B):return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]
def qsub(A,B):return [[a-b for a,b in zip(x,y)] for x,y in zip(A,B)]
QI=[[F(int(i==j)) for j in range(3)] for i in range(3)]
G=[[F(1),F(1),F(0)],[F(0),F(1),F(0)],[F(0),F(0),F(1)]];L=[[F(1),F(0),F(0)]];K=[[F(1)]]*3
R=qmm(L,G);D=qsub(G,QI);J=qsub(QI,qmm(K,R));H=qmm(J,D)
require(D==[[0,1,0],[0,0,0],[0,0,0]] and H==[[0,0,0],[0,-1,0],[0,-1,0]],'sharp rational toy')
require(qmm(R,K)==[[2]],'J inverse premise in rational toy: RK=2 not 1')
receipt=json.loads(json.dumps({'status':'PASS_SOURCE_QUERY_FINITE_FIELD_AUDIT','GL3':len(GL),'exhaustive_rows':rows,'missing_J_control':zeroJexample,'premise_controls':controls,'rational_sharp_support':[1,2],'scope':'GF2 exhaustive stress test plus separately proved field-independent cover; no finite-field inference about physical frames','no_new_kappa':True},sort_keys=True))
require(receipt==json.loads((HERE/'RESULT.json').read_text()),'committed audit receipt differs from recomputation')
print(json.dumps(receipt,sort_keys=True))
