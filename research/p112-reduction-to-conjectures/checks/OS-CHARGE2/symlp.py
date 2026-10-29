# Independent symmetric LP (OS-CHARGE2). For a multiset of piece weights (counts n_w), max #lines coverable:
# vars x_s (per-subset value, s = type vector), constraints:
#  (a) for each nonzero type u: sum_{0<s<=u} prod C(u_w,s_w) x_s <= Nq(|u|)
#  (b) for each weight w present: sum_{s_w>=1} C(n_w-1,s_w-1) prod_{w'!=w} C(n_w',s_w') x_s <= g(w)
# objective sum_s prod C(n_w,s_w) x_s.  Symmetrisation is exact (LP invariant under prod Sym(n_w)).
# Returns LP value and an EXACT rational upper bound from a repaired dual certificate.
import itertools, numpy as np
from math import comb, prod
from fractions import Fraction
from scipy.optimize import linprog
import scipy.sparse as sp
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}
NE8=[0,1,3,6,12,20,36,63,120]
def Nq(u,codim,NL):
    k=u+codim
    return NL if k>=8 else min(NE8[k],NL)
def lp(counts,codim=0,NL=112,exact=True):
    ws=[w for w in sorted(counts) if counts[w]>0]; n=[counts[w] for w in ws]
    types=[t for t in itertools.product(*[range(c+1) for c in n]) if any(t)]
    idx={t:i for i,t in enumerate(types)}
    obj=np.array([prod(comb(n[i],t[i]) for i in range(len(n))) for t in types],float)
    rows=[];cols=[];vals=[];b=[];R=0
    subs={}
    for u in types:
        su=sum(u)
        for s in itertools.product(*[range(x+1) for x in u]):
            if not any(s): continue
            rows.append(R);cols.append(idx[s]);vals.append(prod(comb(u[i],s[i]) for i in range(len(n))))
        b.append(Nq(su,codim,NL)); R+=1
    for i,w in enumerate(ws):
        for s in types:
            if s[i]>=1:
                rows.append(R);cols.append(idx[s]);vals.append(comb(n[i]-1,s[i]-1)*prod(comb(n[k],s[k]) for k in range(len(n)) if k!=i))
        b.append(g[w]); R+=1
    A=sp.csr_matrix((vals,(rows,cols)),shape=(R,len(types)))
    res=linprog(-obj,A_ub=A,b_ub=b,bounds=(0,None),method='highs')
    val=-res.fun
    if not exact: return val,None
    y=np.maximum(-res.ineqlin.marginals,0)
    yq=[Fraction(int(np.ceil(x*1e7)),10**7) for x in y]
    # exact column check, repair with the full-type constraint (row index of types[-1] = all n, coef = obj)
    Acoo=A.tocoo(); colsum=[Fraction(0)]*len(types)
    for r,c,vv in zip(Acoo.row,Acoo.col,Acoo.data): colsum[c]+=yq[r]*int(round(vv))
    full=idx[tuple(n)]
    tfix=max([Fraction(0)]+[(int(obj[c])-colsum[c])/int(obj[c]) for c in range(len(types))])
    yq[full]+=tfix
    bound=sum(yq[r]*b[r] for r in range(R))
    return val,bound
if __name__=='__main__':
    from collections import Counter
    for p in [[7]+[6]*9,[7]+[6]*9+[1],[7,7]+[6]*8,[7]+[6]*9+[1,1],[7]+[6]*9+[2],[7,7]+[6]*8+[1],[7,7,7]+[6]*7]:
        print(p,lp(Counter(p)))
    print('d7',lp(Counter([7]+[6]*8),codim=1))
    print('CONTROL [8]^8 d=8:',lp(Counter([8]*8)))
    print('CONTROL [8]^8 d=7 (need 111):',lp(Counter([8]*8),codim=1))
