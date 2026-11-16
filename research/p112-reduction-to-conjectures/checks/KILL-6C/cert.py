# Impl A: dual (Farkas) certificates for the multiplicity-aware count LP. Solves the dual LP with HiGHS, rationalizes, writes certs.json.
# Dual: find y_K>=0 (|K|<=7), z_j>=0 with  sum_{K sup M} y_K + sum_{j in M} z_j >= 1 for all nonempty M,  and  sum y_K N[|K|] + sum z_j g_j < NL.
import json, numpy as np
from fractions import Fraction as Fr
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
KMAX=3
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}; N={1:1,2:3,3:6,4:12,5:20,6:36,7:63}
def dual(ws,NL):
    p=len(ws); Ks=[K for K in range(1,1<<p) if bin(K).count("1")<=KMAX]; nk=len(Ks); nv=nk+p
    A=lil_matrix(((1<<p)-1,nv))
    for i,K in enumerate(Ks):
        s=K
        while s: A[s-1,i]=-1; s=(s-1)&K
    for j in range(p):
        for M in range(1,1<<p):
            if M>>j&1: A[M-1,nk+j]=-1
    c=np.array([N[bin(K).count('1')] for K in Ks]+[g[w] for w in ws],float)
    r=linprog(c,A_ub=A.tocsr(),b_ub=-np.ones((1<<p)-1),bounds=(0,None),method='highs-ds')
    x=r.x
    # rationalize with a safety scale: y,z rounded up slightly so coverage stays >=1
    cert={'K':[],'z':[]}
    for i,K in enumerate(Ks):
        if x[i]>1e-12: cert['K'].append([K,str(Fr(x[i]*1.002).limit_denominator(1000000))])
    cert['z']=[str(Fr(x[nk+j]*1.002).limit_denominator(1000000)) for j in range(p)]
    return r.fun,cert
rows={303:[6]*10+[5,5],315:[7,7,7,6,6,6,6,6,5,5,5,4],400:[6]*10+[5,4,1,1],401:[6]*10+[5,4,2],402:[6]*10+[5,5,1],409:[6]*11+[5],411:[7]+[6]*9+[5,5],417:[7,7]+[6]*7+[5,5,5],425:[7,7,7]+[6]*5+[5]*4}
out={}
for r,ws in rows.items():
    sc=[('ClassI',ws,120)]
    if r==303: sc=[('beta1',ws,120),('alpha',ws,119)]+[('bump%d'%x,sorted(ws[:ws.index(x)]+[x+1]+ws[ws.index(x)+1:],reverse=True),120) for x in (5,6)]
    if r==315: sc=[('alpha',ws,119),('bump4',sorted(ws[:-1]+[5],reverse=True),120)]
    for name,w,NL in sc:
        val,cert=dual(w,NL); cert.update(ws=w,NL=NL); out['%d:%s'%(r,name)]=cert
        print(r,name,'dual min',round(val,3),'NL',NL,'#K',len(cert['K']),flush=True)
json.dump(out,open('certs.json','w'))
