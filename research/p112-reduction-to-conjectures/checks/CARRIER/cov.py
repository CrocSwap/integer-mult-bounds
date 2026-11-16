# Circuit-kill covering tests.  Off set (list of P112 line indices) must be covered by flats of dims ds plus s free lines.
from lib import *
import pickle, itertools, sys, time
from functools import lru_cache
Pl=P
labP=[lab[t] for t in P]
Pidx={t:i for i,t in enumerate(P)}
def rref_basis(vs):
    b=[]
    for x in vs:
        for y in b: x=min(x,x^y)
        if x: b.append(x)
    # canonical: fully reduce
    b.sort(reverse=True)
    for i in range(len(b)):
        for j in range(len(b)):
            if i!=j and (b[j]^b[i])<b[j] and (b[j]>>(b[i].bit_length()-1))&1: b[j]^=b[i]
    return tuple(sorted(b,reverse=True))
def inspan(x,basis):
    for y in basis: x=min(x,x^y)
    return x==0
def subspaces_containing(labs, x0, w):
    """all spans of <=w independent vectors drawn from labs containing labs[x0] ; returns set of canonical bases (dim exactly min(w, achievable))."""
    start=rref_basis([labs[x0]])
    level={start}; res=set()
    for dim in range(1,w):
        nxt=set()
        for B in level:
            ext=False
            for v in labs:
                if not inspan(v,B):
                    nxt.add(rref_basis(list(B)+[v])); ext=True
            if not ext: res.add(B)
        level=nxt
        if not level: break
    res|=level
    return res
def remove_cover(labs,w,s):
    # can we delete <= s lines so that the rest has rank <= w ?
    if len(rref_basis(list(labs)))>w+s: return False
    basis=[]; chosen=[]
    for i,v in enumerate(labs):
        if not inspan(v,basis):
            basis=list(rref_basis(basis+[v])); chosen.append(i)
            if len(chosen)==w+1: break
    if len(chosen)<=w: return True
    if s==0: return False
    for i in chosen:
        if remove_cover(labs[:i]+labs[i+1:],w,s-1): return True
    return False
def can_cover(labs, ds, s, memo=None):
    """labs: tuple of label ints (lines to cover, distinct line identities by position); ds: sorted tuple dims; s free lines"""
    if memo is None: memo={}
    key=(labs,ds,s)
    if key in memo: return memo[key]
    if not labs: memo[key]=True; return True
    if not ds:
        r=len(labs)<=s; memo[key]=r; return r
    if len(ds)==1:
        r=remove_cover(labs,ds[0],s); memo[key]=r; return r
    # quick: total capacity
    r=False
    x0=0
    if s>0 and can_cover(labs[1:],ds,s-1,memo): r=True
    if not r:
        for w in sorted(set(ds)):
            ds2=list(ds); ds2.remove(w); ds2=tuple(ds2)
            for B in subspaces_containing(labs,x0,w):
                rest=tuple(v for v in labs if not inspan(v,B))
                if len(rest)==len(labs): continue
                if can_cover(rest,ds2,s,memo): r=True; break
            if r: break
    memo[key]=r; return r
