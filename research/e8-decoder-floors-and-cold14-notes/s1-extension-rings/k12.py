"""Coxeter-Todd K12 = {x in Z[w]^6 : x_i = x_j mod theta, sum x_i = 0 mod 3}; 756 minimal vectors (norm 6) = 126 lines (G34).
Units of Z[w]: +-w^a.  Exact enumeration of the minimal vectors."""
import sys, itertools; sys.path.insert(0,sys.path[0])
import numpy as np
from klines import *
UNITS=[(1,0),(0,1),(-1,-1),(-1,0),(0,-1),(1,1)]          # 1, w, w^2, -1, -w, -w^2
def mul(x,y):
    a,b=x; c,d=y; return (a*c-b*d, a*d+b*c-b*d)
THETA=(1,2)            # theta = w - w^2 = w - (-1-w) = 1 + 2w  (norm 3)
def norm(x): a,b=x; return a*a-a*b+b*b
def k12_min():
    out=set()
    # type 1: theta*u1 at i, theta*u2 at j with u1 = -u2 mod theta (opposite sign classes)
    for i,j in itertools.combinations(range(6),2):
        for a in range(6):
            for b in range(6):
                if (a<3)==(b<3): continue
                x=[(0,0)]*6; x[i]=mul(THETA,UNITS[a]); x[j]=mul(THETA,UNITS[b]); out.add(tuple(x))
    # type 2: eps * w^{a_i}, sum w^{a_i} = 0 mod 3
    for eps in (1,-1):
        for e in itertools.product(range(3),repeat=6):
            n=[e.count(0),e.count(1),e.count(2)]
            if not (n[0]%3==n[1]%3==n[2]%3): continue
            out.add(tuple(UNITS[k if eps==1 else k+3] for k in e))
    out=sorted(out)
    assert len(out)==756 and all(sum(norm(c) for c in x)==6 for x in out)
    return out
def k12_system():
    vs=k12_min()
    S=eis_system('K12', vs, 6)
    reps=dedup_lines(S.V, S.basis)
    return System('G34(K12)', reps, S.Q, S.basis)
if __name__=='__main__':
    S=k12_system(); print(S.name,'v',S.v,'w',S.w,'nonorth deg',set(S.NO.sum(1)))
    a,K=S.alpha(); print('alpha',a,'rank of clique',S.rank(K))
