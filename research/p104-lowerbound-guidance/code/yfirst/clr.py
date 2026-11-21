import sys; sys.path.insert(0,'../fewstops')
from load import *
from fractions import Fraction as Q
N=n+W['owned_fields']; rows=[{r:Q(1)} if r<n else {} for r in range(N)]
nz=0;tot=0
for e in P:
    op,r=e[0],e[1]
    if op=='INIT': rows[r]={}
    elif op=='CLEAR':
        tot+=1; nz+=bool(rows[r]); rows[r]={}
    elif op=='SCALE':
        q=Q(e[2]); rows[r]={k:v*q for k,v in rows[r].items()}
    elif op in('ADD','COPY'):
        s=e[2];q=Q(e[3]);R=rows[r]
        for k,v in rows[s].items():
            nv=R.get(k,0)+q*v
            if nv: R[k]=nv
            else: R.pop(k,None)
print('clears',tot,'nonzero at clear',nz)
