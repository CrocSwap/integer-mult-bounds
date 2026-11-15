"""Dylan Crow, with Anthropic Claude assistance; Apache-2.0. Root-spanned rational subspaces of Q^8, represented by the bitmask of E8 root lines they contain."""
import e8lib as E
from fractions import Fraction as Fr
V=E.V
L=E.LINES
_cache={}
def _basis(idx):
    rows=[]
    piv=[]
    for i in idx:
        v=[Fr(a) for a in L[i]]
        for (p,b) in zip(piv,rows):
            if v[p]!=0:
                f=v[p]/b[p]; v=[x-f*y for x,y in zip(v,b)]
        nz=[k for k in range(8) if v[k]!=0]
        if nz:
            rows.append(v); piv.append(nz[0])
    return rows,piv
def _inspan(v,rows,piv):
    v=[Fr(a) for a in v]
    for (p,b) in zip(piv,rows):
        if v[p]!=0:
            f=v[p]/b[p]; v=[x-f*y for x,y in zip(v,b)]
    return all(x==0 for x in v)
def closure(mask):
    """mask of all root lines in the rational span of the lines in mask; returns (closed_mask, dim)"""
    r=_cache.get(mask)
    if r is not None: return r
    idx=[i for i in range(V) if mask>>i&1]
    rows,piv=_basis(idx)
    cm=0
    for i in range(V):
        if mask>>i&1 or _inspan(L[i],rows,piv): cm|=1<<i
    r=(cm,len(rows))
    _cache[mask]=r; _cache[cm]=r
    return r
def dim(mask): return closure(mask)[1]
FULL=(1<<V)-1
ZERO=0
HYP=[sum(1<<s for s in E.ORTH[t]) for t in range(V)]
LINE=[1<<s for s in range(V)]
def join(a,b): return closure(a|b)[0]
def inside(a,b): return a&~b==0   # for closed masks
for t in range(V): assert closure(HYP[t])==(HYP[t],7)
assert closure(FULL)==(FULL,8)
