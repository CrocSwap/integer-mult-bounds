"""Exact finite evidence for sparse-completion rank additivity.
SPDX-License-Identifier: Apache-2.0; woklerx with substantial Codex assistance.
"""
from itertools import combinations,product
from collections import Counter
from pathlib import Path
import argparse,json
HERE=Path(__file__).resolve().parent
def need(x,s):
    if not x:raise ValueError(s)
def rankmod(matrix,p=65521):
    a=[[x%p for x in row] for row in matrix];n=len(a);r=0
    for j in range(len(a[0]) if a else 0):
        k=next((k for k in range(r,n) if a[k][j]),None)
        if k is None:continue
        a[r],a[k]=a[k],a[r];v=pow(a[r][j],-1,p);a[r]=[(x*v)%p for x in a[r]]
        for k in range(r+1,n):
            if a[k][j]:
                v=a[k][j];a[k]=[(x-v*y)%p for x,y in zip(a[k],a[r])]
        r+=1
        if r==n:break
    return r
def run():
    need(all(65521%d for d in range(2,256)),'modulus is prime')
    roots=set()
    for i,j in combinations(range(8),2):
        for a,b in product((-2,2),repeat=2):
            r=[0]*8;r[i],r[j]=a,b;roots.add(max(tuple(r),tuple(-x for x in r)))
    for r in product((-1,1),repeat=8):
        if sum(x<0 for x in r)%2==0:roots.add(max(r,tuple(-x for x in r)))
    roots=sorted(roots);need(len(roots)==120,'120roots')
    f=[]
    for i in range(0,8,2):
        for sign in (-1,1):
            r=[0]*8;r[i]=2;r[i+1]=2*sign;f.append(tuple(r))
    live=[r for r in roots if r not in f];need(len(live)==112,'P112')
    dot=lambda a,b:sum(x*y for x,y in zip(a,b))
    supports=[[i for i,r in enumerate(live) if dot(r,a)] for a in roots]
    histogram=Counter(map(len,supports));need(histogram=={53:112,56:8},'root-normal support minimum53')
    gram=[[dot(r,s) for s in live] for r in live];need(rankmod(gram)==8,'baseline rank8')
    # Matrices use twice the conventional masked target, avoiding fractions.
    examples=[]
    for k in (1,2,8,16,52):
        edges=[];used=set()
        for i in range(k):
            j=next(j for j in range(112) if j not in used and abs(gram[i][j])==4)
            used.add(j);edges.append((i,j))
        changed=[r[:] for r in gram]
        for i,j in edges:changed[i][j]+=1
        measured=rankmod(changed);need(measured==8+k,'rank8+k matching example')
        # The explicit factorization bounds the rational rank above by8+k;
        # a nonzero modular minor proves the matching lower bound.
        examples.append(dict(k=k,odd_edges=edges,modular_rank=measured,rational_rank_upper=8+k))
    # Four nonzero odd entries can form rank1, not rank4.
    rectangle=None
    for i,j in combinations(range(112),2):
        cols=[k for k in range(112) if abs(gram[i][k])==abs(gram[j][k])==4]
        if len(cols)>=2:rectangle=([i,j],cols[:2]);break
    a,b=rectangle;changed=[r[:] for r in gram]
    for i in a:
        for j in b:changed[i][j]+=1
    need(rankmod(changed)==9,'rank-one odd rectangle')
    # Exact53-support boundary: a root-linear vector lies in the spike span.
    alpha=next(a for a,s in zip(roots,supports) if len(s)==53)
    c=[dot(r,alpha) for r in live];active=[i for i,v in enumerate(c) if v]
    sharp=[[8*gram[i][j]-c[i]*c[j] for j in range(112)] for i in range(112)]
    need(len(active)==53 and rankmod(sharp)==7,'53support projection cancellation')
    remaining=[live[i] for i in range(112) if not c[i]]
    need(rankmod(remaining)==7,'53deletion complement rank7')
    # Restoring any removed row repairs the code/spike independence.
    need(all(rankmod(remaining+[live[i]])==8 for i in active),'all53restorations')
    # Positive rank upper7 comes from I-alpha alpha^t/8, whose nullspace is alpha.
    need(sum(x*x for x in alpha)==8,'projection identity')
    return dict(status='PASS_P112_SPARSE_COMPLETION_RANK',root_support_histogram={str(k):v for k,v in sorted(histogram.items())},minimum_code_support=53,inherited_premise='PR968 E8 real hyperplane-flat classification: E7 has63lines; every other type has at most42.',matching_examples=examples,odd_rectangle=dict(rows=a,columns=b,nonzero_entries=4,correction_rank=1,completion_rank=9),boundary_control=dict(support=active,normal=alpha,correction_rank=1,completion_rank=7,all_single_restorations=53,masked=False),controls=['nonzero-entry-count is not correction rank','53support code/spike dependence invalidates additivity','all53one-row restorations restore independence'])
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();x=json.loads(json.dumps(run()));p=HERE/'CERTIFICATE.json'
    if a.write:p.write_text(json.dumps(x,indent=2)+'\n')
    else:need(x==json.loads(p.read_text()),'complete receipt')
    print('PASS_P112_SPARSE_COMPLETION_RANK support=53 matching_sizes=1,2,8,16,52 boundary_rank=7 controls=3')
