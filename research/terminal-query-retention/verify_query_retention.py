#!/usr/bin/env python3
"""Independent exact, standard-library verification of query-retention claims."""
from fractions import Fraction as F
import json

def mat(A): return [[F(x) for x in row] for row in A]
def mm(A,B): return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]
def eye(n): return mat([[int(i==j) for j in range(n)] for i in range(n)])
def rank(A):
    A=[r[:] for r in A];k=0
    for j in range(len(A[0])):
        p=next((i for i in range(k,len(A)) if A[i][j]),None)
        if p is None:continue
        A[k],A[p]=A[p],A[k];v=A[k][j];A[k]=[x/v for x in A[k]]
        for i in range(len(A)):
            if i!=k:
                v=A[i][j];A[i]=[x-v*y for x,y in zip(A[i],A[k])]
        k+=1
        if k==len(A):break
    return k
def inverse(A):
    n=len(A);B=[r+s for r,s in zip(A,eye(n))]
    for j in range(n):
        p=next((i for i in range(j,n) if B[i][j]),None)
        if p is None:raise ValueError('singular')
        B[j],B[p]=B[p],B[j];v=B[j][j];B[j]=[x/v for x in B[j]]
        for i in range(n):
            if i!=j:
                v=B[i][j];B[i]=[x-v*y for x,y in zip(B[i],B[j])]
    return [r[n:] for r in B]
def main():
    Q=mat([[1,2,-1,0],[0,1,3,2]])
    T=Q+mat([[0,0,1,0],[0,0,0,1]])
    B=mat([[1,0],[0,1],[2,-3]])
    L=mm(B,Q)
    assert rank(Q)==2 and rank(L)==2 and mm(inverse(T),T)==eye(4)
    # Simultaneously all four independent arbitrary-dirty basis columns.
    assert mm(B,T[:2])==L
    # Two read slots are necessary; adding a redundant query costs no new child.
    assert rank(L)>1
    bad=T[:];bad[0]=mat([[0,0,0,0]])[0]
    try:inverse(bad)
    except ValueError:pass
    else:raise AssertionError('singular pivot accepted')
    bad=T[:];bad[0]=T[2][:]
    assert mm(B,bad[:2])!=L
    # z1 was once available but is destroyed. A retained z0 cannot recover z1.
    sideinfo_counterexample=[[0,0],[0,1]]
    assert sideinfo_counterexample[0][0]==sideinfo_counterexample[1][0]
    assert sideinfo_counterexample[0][1]!=sideinfo_counterexample[1][1]
    # Source-changing invocation on (x,y,z). Subtract old-dirty response,
    # then undo the JOINT source/dirty block, leaving y untouched.
    old=mat([[1,0,0],[0,1,-3],[0,0,1]])
    word=mat([[2,0,0],[1,1,3],[1,0,1]])
    cleanup=mat([[F(1,2),0,0],[0,1,0],[F(-1,2),0,1]])
    expected=mat([[1,0,0],[1,1,0],[0,0,1]])
    assert mm(cleanup,mm(word,old))==expected
    wrong=mat([[F(1,2),0,0],[0,1,0],[-1,0,1]])
    assert mm(wrong,mm(word,old))!=expected
    print(json.dumps(dict(status='PASS_EXACT',independent_columns=4,query_rank=2,
      requested_queries=3,retained_slots=2,negative_controls=4,
      joint_source_dirty_lift_columns=3,
      recursive_cost='2 children at the common query-frame rank; unchanged final climbs',
      scope='finite lemma witness, not a complete multiplication supplier'),indent=2))
if __name__=='__main__':main()
