# leftover tables: for parabolic J (h generic in J^perp), Off=Phi\Phi_J (lines). min over pairs of 7-flats of |Off \ (A u B)|.
# for J=E7 (root r): also min with r in A u B.  Impl A: python ints + numpy popcount.
import sys; import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'g777'))
from carrier_lib import *
import numpy as np, itertools
Z=[0]*512
for a in range(1,512):
    m=0
    for t in range(n):
        if not par(a&lab[t]): m|=1<<t
    Z[a]=m
masks=set()
for a in range(1,512):
    for b in range(a+1,512):
        masks.add(Z[a]&Z[b])
masks=sorted(masks); print('7-flat masks',len(masks),flush=True)
def pc(x): return bin(x).count('1')
def dot(u,v): return sum(x*y for x,y in zip(u,v))
def parab(J):
    S=[simple[j] for j in J]
    # lines in span of S: lines orthogonal to all w with w perp S ... use rank test
    import sympy
    M=sympy.Matrix(S) if S else None
    out=set()
    for t in range(n):
        if not S: continue
        if sympy.Matrix(S+[lines[t]]).rank()==len(S): out.add(t)
    return out
def best_pair(T,need=None):
    """max |(A|B)&T| over pairs of 7-flats; if need: require bit need in A|B. returns max"""
    A=sorted({m&T for m in masks},key=pc,reverse=True)
    best=0
    sizes=[pc(x) for x in A]
    for i,x in enumerate(A):
        if sizes[i]+sizes[0]<=best: break
        for j in range(i,len(A)):
            if sizes[i]+sizes[j]<=best: break
            u=x|A[j]
            if need is not None and not (u>>need)&1: continue
            c=pc(u)
            if c>best: best=c
    return best
if __name__=='__main__':
    import sympy
    full=(1<<n)-1
    seen={}
    for r in range(7,-1,-1):
        for J in itertools.combinations(range(8),r):
            PJ=parab(J); T=full
            for t in PJ: T&=~(1<<t)
            if pc(T)>94: continue
            key=len(PJ)
            b=best_pair(T); 
            print('J',J,'|Phi_J|',len(PJ),'|Off|',pc(T),'max7flat',max(pc(m&T) for m in masks),'max2flats',b,'minleft',pc(T)-b,flush=True)
    # root r0 = line 0 ; Off_E(r0)
    r0=lines[0]; T=sum(1<<t for t in range(n) if dot(r0,lines[t])!=0)
    b=best_pair(T,need=0); print('root: |Off|',pc(T),'max2flats with r covered',b,'minleft(r covered)',pc(T)-b)
