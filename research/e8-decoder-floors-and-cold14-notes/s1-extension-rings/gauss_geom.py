"""Gaussian E8: the 60 Q(i)-lines (J-orbits of E8 roots).  Exact integer arithmetic.
A Q(i)-line through root r is the real plane <r, Jr>; complex rank of a line set = real rank / 2."""
import sys, itertools, numpy as np
sys.path.insert(0,'/Users/joelpulikkan/imb-main/research/format-limits/scripts')
from e8units import standard_e8, rank_q

def gaussian_e8():
    L,G=standard_e8()
    roots=np.vstack([L,-L])
    J=np.zeros((8,8),dtype=np.int64)
    for a in range(4):
        J[2*a+1,2*a]=1; J[2*a,2*a+1]=-1
    assert (J@J==-np.eye(8,dtype=np.int64)).all()
    S=set(map(tuple,roots)); assert all(tuple(J@r) in S for r in roots)
    seen=set(); lines=[]
    for r in roots:
        if tuple(r) in seen: continue
        for o in (r,J@r,-r,-(J@r)): seen.add(tuple(o))
        lines.append(r)
    lines=np.array(lines)
    assert len(lines)==60
    return lines,J

def nonorth(lines,J):
    R=lines@lines.T
    I=lines@J@lines.T
    M=(R!=0)|(I!=0); np.fill_diagonal(M,False); return M

def crank(lines,J,idx):
    rows=[]
    for i in idx: rows+= [list(lines[i]), list(J@lines[i])]
    r=rank_q(rows) if rows else 0
    assert r%2==0; return r//2

def flats(lines,J,maxrank=3):
    v=len(lines); out={1:{frozenset([i]) for i in range(v)}}
    def closure(idx):
        r=crank(lines,J,idx)
        return frozenset(j for j in range(v) if j in idx or crank(lines,J,list(idx)+[j])==r), r
    for r in range(2,maxrank+1):
        out[r]=set()
        for Fl in out[r-1]:
            base=list(Fl)
            # pick an independent basis of size r-1 from Fl
            bas=[]
            for i in base:
                if crank(lines,J,bas+[i])>len(bas): bas.append(i)
                if len(bas)==r-1: break
            for j in range(v):
                if j in Fl: continue
                C,rr=closure(bas+[j]); assert rr==r
                out[r].add(C)
    return out
