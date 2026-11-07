"""Independent boundary controls for the six-full-block obstruction.
No author code is imported. Universal argument: SIX-FULL-REVIEW.md.
"""
from itertools import combinations
from pathlib import Path
import json

def need(ok,msg):
    if not ok:raise ValueError(msg)
def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def gf2_rank(a):
    rows=[sum((x&1)<<i for i,x in enumerate(r)) for r in a];basis={}
    for x in rows:
        while x:
            p=x.bit_length()-1
            if p in basis:x^=basis[p]
            else:basis[p]=x;break
    return len(basis)
def matching(edges):
    if not edges:return 0
    a,b=next(iter(edges));rest=edges-{(a,b)}
    return max(matching(rest),1+matching({e for e in rest if a not in e and b not in e}))

def main():
    S=[[(i>j)-(i<j) for j in range(6)] for i in range(6)]
    inv=[[(-1)**(i+j)*((i>j)-(i<j)) for j in range(6)] for i in range(6)]
    need(mm(S,inv)==[[int(i==j) for j in range(6)] for i in range(6)],'integer inverse S6')
    A={0,1,2,3};B={0,1,4,5};common=A&B
    witnesses=extensions=0
    for raw in combinations(range(7),4):
        C=set(raw)
        if len(A&C)<2 or len(B&C)<2 or common<=C:continue
        witnesses+=1;T=A|B|C
        need(len(T)<=7 and len(A&B&C)<2,'non-common-pair witness')
        for rawD in combinations(range(9),4):
            D=set(rawD)
            if min(len(A&D),len(B&D),len(C&D))<2:continue
            extensions+=1;need(len(D-T)<=1,'extension adds at most one vertex')
    family=[A,B,{0,2,4,6},{0,2,4,7},{0,2,4,8},{0,2,4,9}]
    need(all(len(x&y)>=2 for x,y in combinations(family,2)) and
         len(set.intersection(*family))==1 and len(set.union(*family))==10,
         'sharp non-common-pair fixture')
    edges={(2,3),(2,4),(2,5),(6,7),(6,8),(6,9)}
    need(matching(edges)==2 and len(set.union(*(set(e) for e in edges)))==8,'two outside stars')
    sunflower=[{0,1,2+2*i,3+2*i} for i in range(6)]
    need(len(set.union(*sunflower))==14 and all(len(x&y)==2 for x,y in combinations(sunflower,2)),
         'intersection condition alone does not bound union by ten')
    X=[[0]*12 for _ in range(14)];Y=[[0]*14 for _ in range(12)]
    for i in range(6):
        for c in range(2):
            X[c][2*i+c]=1;X[2+2*i+c][2*i+c]=1
            Y[2*i+c][c]=1;Y[2*i+c][2+2*i+c]=1
    G=mm(Y,X)
    need(all(G[2*i+a][2*j+b]%2==int(i!=j and a==b)
             for i in range(6) for j in range(6) for a in range(2) for b in range(2)),
         'characteristic-two sunflower Gram')
    need(gf2_rank(G)==12 and all(G[i][i]==2 for i in range(12)),
         'char2 rank12 control fails square-zero in characteristic zero')
    result={'verdict':'PASS_INDEPENDENT_SIX_FULL_BOUNDARY_CONTROLS',
            'canonical_noncommon_witnesses':witnesses,'compatible_extensions':extensions,
            'noncommon_union':10,'common_pair_outside_matching':2,'common_pair_union':10,
            'unrestricted_sunflower_union':14,'characteristic_two_gram_rank':12,
            'scope':'Finite independent controls; universal proof in SIX-FULL-REVIEW.md.'}
    expected=json.loads(Path(__file__).with_name('SIX-FULL-RESULT.json').read_text())
    need(result==expected,'independent report matches retained result')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
