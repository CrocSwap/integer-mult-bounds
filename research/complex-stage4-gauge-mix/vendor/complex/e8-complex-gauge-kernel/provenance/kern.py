from cxlab import *
import numpy as np, itertools, sys
def subspaces(F):
    """all nonzero subspaces of span(F) as canonical bases, any rank"""
    F=list(F);k=len(F);out=set()
    vecs=[]
    for mask in range(1,1<<k):
        x=0
        for i in range(k):
            if mask>>i&1:x^=F[i]
        vecs.append(x)
    # enumerate subspaces by generating from subsets of vectors up to rank k
    seen=set()
    def rec(cur,start):
        for i in range(start,len(vecs)):
            b=basis(list(cur)+[vecs[i]])
            if len(b)==len(cur)+1 and b not in seen:
                seen.add(b);rec(b,i+1)
    rec((),0)
    return seen
def setup(w):
    A,B=w['A'],w['B'];n=240+w['report']['R'];R=w['report']['R']
    M=ident(n)
    for e in A+w['cut']+B:apply(e,M)
    dirty=[{} for r in range(n)]
    for r in range(v,2*v):dirty[r]={j:x for j,x in M[r].items() if j>=2*v}
    for e in w['precondition']:apply(e,dirty)
    col=[dict() for _ in range(R)]
    for r in range(v,2*v):
        for j,x in dirty[r].items():col[j-2*v][r-v]=x
    first={}
    for seq in (A,B):
        for e in seq:
            F=basis(e[-1])
            for r in ([e[1]]+([e[2]] if e[0]=='add' else [])):
                if r>=2*v:first.setdefault(r-2*v,F)
    return col,first
if __name__=='__main__':
    w=load();col,first=setup(w);R=len(col)
    cand={}
    for h,F in first.items():
        for E in subspaces(F):cand.setdefault(E,[]).append(h)
    print('first-frame subspaces',len(cand),Counter(len(E) for E in cand))
    C=np.zeros((v,R))
    for h in range(R):
        for t,x in col[h].items():C[t,h]=float(x)
    pot=[]
    for E,G in cand.items():
        if len(G)<2:continue
        rk=np.linalg.matrix_rank(C[:,G]);pot.append((len(E)*(len(G)-rk),E,len(G),rk))
    pot.sort(reverse=True)
    print('E with positive potential',sum(1 for p in pot if p[0]>0),Counter((len(p[1]),p[2]-p[3]) for p in pot if p[0]>0))
    print(pot[:5])
