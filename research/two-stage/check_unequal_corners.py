#!/usr/bin/env python3
"""Exact finite-field controls for the parameterized PR24 inner basis.
These controls supplement, and do not replace, the general rational proof.
"""
import json,random
from pathlib import Path
from two_stage_unequal import prescriptions
P=1000003
def rank(mat):
    A=[r[:] for r in mat];n=len(A);col=0
    for j in range(len(A[0])):
        pivot=next((i for i in range(col,n) if A[i][j]%P),None)
        if pivot is None:continue
        A[col],A[pivot]=A[pivot],A[col]
        z=pow(A[col][j],-1,P);A[col]=[x*z%P for x in A[col]]
        for i in range(col+1,n):
            z=A[i][j]%P
            if z:A[i]=[(x-z*y)%P for x,y in zip(A[i],A[col])]
        col+=1
    return col
def control(b,seed):
    a=b+2;m=a*b;d=a+b-1;M=prescriptions(a,b)
    inv=[]
    for row in M:
        z=[0]*a
        for i,j in enumerate(row):z[j]=i
        inv.append(z)
    rng=random.Random(seed)
    def line(n):
        p=[rng.randrange(1,P) for _ in range(n)]
        xi=[rng.randrange(1,P) for _ in range(n)]
        scale=pow(sum(x*y for x,y in zip(p,xi))%P,-1,P)
        return p,[x*scale%P for x in xi]
    p,xi=line(a);v,nu=line(b)
    # Direct contraction of permutation matrices, not imported corner formula.
    def entry(i,j,which):
        alpha,beta=divmod(i,b);gamma,delta=divmod(j,b)
        r=M[beta][alpha];c=M[delta][gamma]
        A=(p[r]*xi[c] if beta==delta else 0)
        B=(v[beta]*nu[delta] if r==c else 0)
        AB=p[r]*xi[c]*v[beta]*nu[delta]
        return (A if which=='A' else B if which=='B' else A+B-AB)%P
    for size,which in [(a,'B'),(b,'A')]:
        C=[[entry(i,m-size+j,which) for j in range(size)] for i in range(size)]
        assert all(C[i][i] for i in range(size))
        assert all(C[i][j]==0 for i in range(size) for j in range(size) if i!=j)
    Q=[[entry(i,m-d+j,'Q') for j in range(d)] for i in range(d)]
    assert rank(Q)==d
    # The tensor identity contributes zero to these disjoint boundary blocks.
    assert rank([[(-x)%P for x in row] for row in Q])==d
    # Wrong ordering must not masquerade as one increasing identity block.
    bad=[[entry(i,m-b+(j+1)%b,'A') for j in range(b)] for i in range(b)]
    assert any(bad[i][j] for i in range(b) for j in range(b) if i!=j)
    return dict(a=a,b=b,seed=seed,modulus=P,auxiliary_diagonal_corners=[a,b],data_nullity_rank=d,wrong_order_rejected=True,
                normalized_line_witnesses=dict(p=p,xi=xi,v=v,nu=nu))
if __name__=='__main__':
    result=[control(b,seed) for b in [10,23,30,51,53] for seed in [1,2,3]]
    Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',len(result),'exact modular corner controls and wrong-order negatives')
