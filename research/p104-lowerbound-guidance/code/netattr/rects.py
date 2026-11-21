# enumerate maximal rectangles (D,S) restricted to readers x gathers, with price r; and covers with sum price <= B
from common import *
def max_rects(h,labs,readers,gathers,Rmax):
    subs=subspaces(h)
    best={}
    for V in subs:
        Sset=frozenset(p for p in gathers if labs[p] in V)
        if not Sset: continue
        for K in subs:
            if not K<=V: continue
            r=dimof(V)-dimof(K)
            if r<1 or r>Rmax: continue
            Kp=perp(K,h)
            Dset=frozenset(t for t in readers if labs[t] in Kp)
            if not Dset: continue
            pr=price([labs[t] for t in Dset],[labs[p] for p in Sset])
            if pr<1: continue
            key=(Dset,Sset)
            if key not in best or best[key]>pr: best[key]=pr
    items=list(best.items())
    # remove dominated: (D,S) subset of (D',S') with price' <= price
    keep=[]
    for (D,S),pr in items:
        dom=False
        for (D2,S2),pr2 in items:
            if pr2<=pr and D<=D2 and S<=S2 and (D,S)!=(D2,S2): dom=True;break
        if not dom: keep.append((D,S,pr))
    return keep
def covers(rects,cells,B):
    cells=frozenset(cells); out=[]
    pass
    def cov(R): return frozenset((t,p) for (t,p) in cells if t in R[0] and p in R[1])
    cv=[cov(R) for R in rects]
    def rec(start,chosen,covered,budget):
        if covered==cells: out.append(list(chosen))
        # pick an uncovered cell, branch on rects covering it (index >= any) -> use cell-based branching
        if covered==cells: return
        c=min(cells-covered)
        for i,R in enumerate(rects):
            if R[2]<=budget and c in cv[i] and i not in chosen:
                rec(0,chosen+[i],covered|cv[i],budget-R[2])
    rec(0,[],frozenset(),B)
    # dedupe as sets
    s=set(frozenset(x) for x in out)
    return [sorted(x) for x in s]
