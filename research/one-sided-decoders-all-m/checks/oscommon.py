# OS-SPARSE common: P112/P104 Gram lines, labels (9-bit), term cost rank B[R,A(y)] = dim U_R - dim(U_R ∩ K_A).
import sys, pickle
from common2 import *
import numpy as np
def load(unit='P112'):
    from frames_data import load_frames
    F0,F1=load_frames()
    rem=set(F0) if unit=='P112' else set(F0)|set(F1)
    L=[E8[i] for i in range(120) if i not in rem]; v=len(L); Br=B0rows(L)
    ech=[];bidx=[]
    for t in range(v):
        x=Br[t];c=0
        for (pv,pc,hb) in ech:
            if x>>hb&1: x^=pv; c^=pc
        if x: hb=x.bit_length()-1; ech.append((x,c|(1<<len(bidx)),hb)); bidx.append(t)
    def solve(r):
        x=r;c=0
        for (pv,pc,hb) in ech:
            if x>>hb&1: x^=pv; c^=pc
        assert x==0; return c
    lab=[solve(Br[t]) for t in range(v)]
    h=len(bidx)
    rowu={}
    for u in range(1,1<<h):
        r=0
        for i in range(h):
            if u>>i&1: r^=Br[bidx[i]]
        rowu[u]=r
    return dict(L=L,v=v,Br=Br,lab=lab,h=h,rowu=rowu,F0=[E8[i] for i in F0],F1=[E8[i] for i in F1],rem=rem)
def KA(D,y):
    A=sum(1<<s for s in range(D['v']) if dot(D['L'][s],y)!=0)
    return [u for u,r in D['rowu'].items() if r&A==0]
def span_basis(vs):
    bs=[]
    for x in vs:
        for b in bs: x=min(x,x^b)
        if x: bs.append(x)
    return bs
def in_span(bs,x):
    for b in bs: x=min(x,x^b)
    return x==0
def term_cost(D,R,K):
    # R: iterable of line indices; K: list of u (kernel of A)
    bs=span_basis([D['lab'][t] for t in R])
    d=len(bs)
    ks=[u for u in K if in_span(bs,u)]
    return d-len(span_basis(ks))
