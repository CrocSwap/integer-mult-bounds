# Lattice frames for an LP line: span(S) and Phi(A); exact checks.
import sys, itertools
sys.path.insert(0,'/home/claude/work/agentB/tools')
from frames import *
def line_blocks(key):
    return sorted(X for (k2,X) in DBM if k2==key)
def targets_of(key,Z):
    x,y=key
    out=[]
    for z in (2*Z,2*Z+1):
        for (a,b) in ((x,y^1),(x^1,y)):
            out.append(idx[tuple(sorted((a,b,z)))])
    return out
def span_rows(key,S):
    rows=[]
    for X in S:
        rows+= [chi(i) for i in items(DBM[(key,X)])]
    return rows
def phi_ann(key,A):
    ann=[]
    for Z in A: ann+=[ann_vec_of_target(t) for t in targets_of(key,Z)]
    return ann
if __name__=='__main__':
    key=(2,5); Xs=line_blocks(key); print(Xs)
    import random
    bad=0; tot=0
    for k in range(1,10):
        for S in itertools.combinations(Xs,k):
            rows=span_rows(key,S); M=sp.Matrix(rows); r=M.rank()
            # basis
            B=[list(M.row(i)) for i in range(M.rows)]
            Bb=sp.Matrix(B).T.columnspace()
            Bl=[list(c) for c in Bb]
            nd=nondeg(Bl); tot+=1
            if not nd or r!=2*k+1: bad+=1; print('span',S,r,nd)
    print('span frames checked',tot,'bad',bad)
    bad=0; tot=0
    for k in range(1,10):
        for A in itertools.combinations(Xs,k):
            K=kernel_rows(phi_ann(key,A)); nd=nondeg(K); tot+=1
            if not nd or len(K)!=23-2*k: bad+=1; print('phi',A,len(K),nd)
    print('phi frames checked',tot,'bad',bad)
