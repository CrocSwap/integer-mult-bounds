# Full subset LP: n_M = #lines with membership set M (lines t whose piece-set is M).
# Constraints (from Circuit Lemma line form, d=8 => V=R^8): sum n_M = NL; for |K|<=7: sum_{M sub K} n_M <= N[|K|]; per piece j: sum_{M ni j} n_M <= g(w_j).
import itertools, sys, numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}; N={0:0,1:1,2:3,3:6,4:12,5:20,6:36,7:63}
def lp(ws,NL=120,kmax=7):
    p=len(ws); Ms=list(range(1,1<<p)); nv=len(Ms)
    Ks=[K for K in range(1,1<<p) if bin(K).count('1')<=kmax]
    A=lil_matrix((len(Ks)+p,nv)); b=[]
    for i,K in enumerate(Ks):
        # submasks of K
        s=K
        while s:
            A[i,s-1]=1; s=(s-1)&K
        b.append(N[bin(K).count('1')])
    for j in range(p):
        for M in Ms:
            if M>>j&1: A[len(Ks)+j,M-1]=1
        b.append(g[ws[j]])
    res=linprog(np.zeros(nv),A_ub=A.tocsr(),b_ub=b,A_eq=np.ones((1,nv)),b_eq=[NL],bounds=(0,None),method='highs')
    return res.status  # 0 feasible, 2 infeasible
rows={303:[6]*10+[5,5],315:[7,7,7,6,6,6,6,6,5,5,5,4],400:[6]*10+[5,4,1,1],401:[6]*10+[5,4,2],402:[6]*10+[5,5,1],409:[6]*11+[5],411:[7]+[6]*9+[5,5],417:[7,7]+[6]*7+[5,5,5],425:[7,7,7]+[6]*5+[5]*4}
for r,ws in rows.items():
    out=['ClassI:%s'%('INFEAS' if lp(ws)==2 else 'feas')]
    if r in (303,315):
        out.append('alpha:%s'%('INFEAS' if lp(ws,119)==2 else 'feas'))
        for x in sorted(set(ws)):
            w=list(ws); w[w.index(x)]=x+1; out.append('bump%d:%s'%(x,'INFEAS' if lp(w)==2 else 'feas'))
    print(r,' '.join(out),flush=True)
