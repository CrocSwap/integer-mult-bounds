# Impl A (generalized: any d<=8, K and M include the empty set). Bound: #{t: M_t ⊆ K} <= N[|K|+8-d], N=G2 (0,1,3,6), so |K| <= d-5.
import json, sys, numpy as np
from fractions import Fraction as Fr
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}; N={0:0,1:1,2:3,3:6,4:12,5:20,6:36,7:63}
def dual(ws,NL,d):
    p=len(ws); km=d-1; Ks=[K for K in range(0,1<<p) if bin(K).count('1')<=km]; nk=len(Ks); nv=nk+p
    A=lil_matrix((1<<p,nv))
    for i,K in enumerate(Ks):
        s=K
        while True:
            A[s,i]=-1
            if s==0: break
            s=(s-1)&K
    for j in range(p):
        for M in range(1,1<<p):
            if M>>j&1: A[M,nk+j]=-1
    c=np.array([N[bin(K).count('1')+8-d] for K in Ks]+[g[w] for w in ws],float)
    r=linprog(c,A_ub=A.tocsr(),b_ub=-np.ones(1<<p),bounds=(0,None),method='highs-ds')
    cert={'K':[[K,str(Fr(r.x[i]*1.002).limit_denominator(10**6))] for i,K in enumerate(Ks) if r.x[i]>1e-12],
          'z':[str(Fr(r.x[nk+j]*1.002).limit_denominator(10**6)) for j in range(p)],'ws':ws,'NL':NL,'d':d}
    return r.fun,cert
def scen(ws,s):
    if s==7: return [('ClassI',ws,120,8)]
    L=[('beta1',ws,120,8),('alpha',ws,119,8)]
    for x in sorted(set(ws)):
        w=list(ws); w[w.index(x)]=x+1; L.append(('bump%d'%x,sorted(w,reverse=True),120,8))
    if 7 in ws:
        w=list(ws); w.remove(7); L.append(('b3B',w,120,7))
    return L
rows={579:([7]*8+[4,4,4,3],7),596:([7]*9+[4,4],7),597:([7]*9+[5,1,1,1],7),598:([7]*9+[5,2,1],7),599:([7]*9+[5,3],7),600:([7]*9+[6,1,1],7),601:([7]*9+[6,2],7),
 381:([7]*6+[6,6,5,5,5,1],6),384:([7]*7+[6,5,5,5],6),576:([7]*7+[6,5,5,5,1],7),577:([7]*7+[6,6,5,3,2],7),578:([7]*7+[6,6,5,5],7),580:([7]*8+[5,5,3,2],7),581:([7]*8+[5,5,5],7)}
out={}
for r,(ws,s) in rows.items():
    for name,w,NL,d in scen(ws,s):
        val,cert=dual(w,NL,d); out['%d:%s'%(r,name)]=cert
        print(r,name,'d',d,'Σg',sum(g[x] for x in w),'dual',round(val,3),'NL',NL,'KILL' if val<NL-1e-6 else 'FEASIBLE',flush=True)
json.dump(out,open('certs2_k7.json','w'))
