"""Tangent-CR2: is there a first-order deformation (X,Y) of the char-2 configuration phi(C) (support-compatible) with
  phi p(t).Y(s) + X(t).phi q(s) = 0 for every incidence (t,s) in E, and  phi p(t).Y(t) + X(t).phi q(t) != 0 for all t in H?
If yes (and C is no-wild), N(eps) = B o (phiP+eps X)(phiQ+eps Y)^T has rank v for every B with supp in E: cost >= v."""
import random
from gr import mul, inv, Q as FQ
def nullspace(rows, n):
    """rows: list of dict col->val over GF(2^16). returns basis of nullspace as list of lists."""
    M=[dict(r) for r in rows]; piv={}  # pivot col -> row
    R=[]
    for r in M:
        for c,pr in piv.items():
            if c in r and r[c]:
                f=r[c]
                for cc,vv in pr.items(): r[cc]=r.get(cc,0)^mul(f,vv)
        r={c:x for c,x in r.items() if x}
        if not r: continue
        c=min(r); iv=inv(r[c]); r={cc:mul(iv,x) for cc,x in r.items()}
        for c2,pr in piv.items():
            if c in pr and pr[c]:
                f=pr[c]
                for cc,vv in r.items(): pr[cc]=pr.get(cc,0)^mul(f,vv)
                piv[c2]={cc:x for cc,x in pr.items() if x}
        piv[c]=r
    free=[c for c in range(n) if c not in piv]
    basis=[]
    for f in free:
        vec=[0]*n; vec[f]=1
        for c,pr in piv.items(): vec[c]=pr.get(f,0)  # char 2: -x = x
        basis.append(vec)
    return basis
def tangent_cr2(Pt,Qt,pi,sig,E,H):
    v=len(Pt); idx={}
    for t in range(v):
        for j in sorted(pi[t]): idx[('X',t,j)]=len(idx)
    for s in range(v):
        for j in sorted(sig[s]): idx[('Y',s,j)]=len(idx)
    def lin(t,s):
        r={}
        for j in sig[s]:
            if Pt[t][j]: r[idx[('Y',s,j)]]=r.get(idx[('Y',s,j)],0)^Pt[t][j]
        for j in pi[t]:
            if Qt[s][j]: r[idx[('X',t,j)]]=r.get(idx[('X',t,j)],0)^Qt[s][j]
        return {c:x for c,x in r.items() if x}
    basis=nullspace([lin(t,s) for (t,s) in E], len(idx))
    res={}
    for t in H:
        f=lin(t,t)
        res[t]=any(sum(1 for _ in [0]) and (lambda b: (lambda acc: acc)( __import__('functools').reduce(lambda a,cx: a^mul(cx[1],b[cx[0]]), f.items(), 0)))(b) for b in basis)
    return res, len(basis)
