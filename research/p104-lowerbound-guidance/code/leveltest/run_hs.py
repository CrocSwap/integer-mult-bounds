# half-spin 64 (h=8) quarter decoder from dangersets/s7_hsdesign.py: terms (u,u) over the D8 orthoframe; rational weights (P_i.u)(P_j.u)/8, common factor dropped.
import sys,numpy as np; sys.path.insert(0,'../dangersets')
from ds_lib import *
from lt import f2rank_rows,toint,rankp
L=e8_lines(); P=halfspin(L); n=len(P); Q=Qmat(P).astype(np.int64)
fr=[]
for i in range(0,8,2):
    for s in (1,-1):
        r=np.zeros(8,dtype=np.int64); r[i]=2; r[i+1]=2*s; fr.append(r)
Qi=[toint(Q[i]) for i in range(n)]
rows=[];Ws=[];Vs=[]
for u in fr:
    g=P@u; Ws.append(g); Vs.append(g)  # deposit col = P.u, gather row = P.w (w=u), u.w=8 constant
    S=[i for i in range(n) if g[i]!=0]; D=S
    da=f2rank_rows([Qi[i] for i in S]); mask=sum(1<<i for i in S); pr=f2rank_rows([Qi[i]&mask for i in D]); rows.append((da,pr,len(S)))
print('rows (dim a, price, |S|):',rows,'D=',sum(r[1] for r in rows))
W=np.array(Ws).T; V=np.array(Vs).T
tot=0;lev=[]
h=max(r[0] for r in rows)
for l in range(1,h+1):
    R=[k for k,(da,pr,_) in enumerate(rows) if da-pr<l<=da]
    rk=rankp(W[:,R]@V[:,R].T) if R else 0; lev.append(rk); tot+=rk
print('levels',lev,'S =',tot)
