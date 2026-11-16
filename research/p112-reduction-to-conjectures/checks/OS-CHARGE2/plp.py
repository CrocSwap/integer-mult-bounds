# Profile LP (OS-CHARGE2). Pieces in classes c (count n_c, profile P_c[u] = max #lines of the piece lying in a
# real u-dim subspace, P_c[8+] = size). For every class c and every sub-multiset U containing a piece of c:
#   #{t in R_j : M(t) ⊆ U, j ∈ M(t)} <= P_c(|U|+codim).   Plus (a) N-constraints.  Exact repaired dual bound.
import itertools, numpy as np
from math import comb, prod
from fractions import Fraction
from scipy.optimize import linprog
import scipy.sparse as sp
NE8=[0,1,3,6,12,20,36,63,120]
def lp(classes,codim=0,NL=112):
    n=[c for c,_ in classes]; P=[p for _,p in classes]; K=len(n)
    def cap(c,u): k=u+codim; return P[c][min(k,8)]
    def Nq(u): k=u+codim; return NL if k>=8 else min(NE8[k],NL)
    types=[t for t in itertools.product(*[range(x+1) for x in n]) if any(t)]
    idx={t:i for i,t in enumerate(types)}
    obj=np.array([prod(comb(n[i],t[i]) for i in range(K)) for t in types],float)
    rows=[];cols=[];vals=[];b=[];R=0
    for u in types:
        su=sum(u); subs=[s for s in itertools.product(*[range(x+1) for x in u]) if any(s)]
        for s in subs:
            rows.append(R);cols.append(idx[s]);vals.append(prod(comb(u[i],s[i]) for i in range(K)))
        b.append(Nq(su)); R+=1
        for c in range(K):
            if u[c]==0: continue
            cp=cap(c,su)
            for s in subs:
                if s[c]>=1:
                    rows.append(R);cols.append(idx[s]);vals.append(comb(u[c]-1,s[c]-1)*prod(comb(u[k],s[k]) for k in range(K) if k!=c))
            b.append(cp); R+=1
    A=sp.csr_matrix((vals,(rows,cols)),shape=(R,len(types)))
    res=linprog(-obj,A_ub=A,b_ub=b,bounds=(0,None),method='highs')
    val=-res.fun
    y=np.maximum(-res.ineqlin.marginals,0)
    yq=[Fraction(int(np.ceil(x*1e7)),10**7) for x in y]
    Acoo=A.tocoo(); colsum=[Fraction(0)]*len(types)
    for r,c,vv in zip(Acoo.row,Acoo.col,Acoo.data): colsum[c]+=yq[r]*int(round(vv))
    full=idx[tuple(n)]  # first row emitted for type u=full is the (a)-row
    rowfull=[r for r in range(R)]  # find (a)-row of full type
    # (a)-rows are emitted first for each u; locate by recomputation
    r=0; rf=None
    for u in types:
        if u==tuple(n): rf=r
        r+=1+sum(1 for c in range(K) if u[c])
    tfix=max([Fraction(0)]+[(int(obj[c])-colsum[c])/int(obj[c]) for c in range(len(types))])
    yq[rf]+=tfix
    bound=sum(yq[r]*b[r] for r in range(R))
    return val,bound
def gen(w):  # generic profile for weight w: min(N_u, g(w))
    g={1:1,2:2,3:4,4:8,5:12,6:20,7:36}[w]
    return {u:min(NE8[u],g) for u in range(1,8)}|{8:g}
