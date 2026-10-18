# exact dual certificates: max sum m s.t. A m <= b, m>=0 ; certificate y>=0 with A^T y >= 1 => sum m <= b.y
import numpy as np, scipy.sparse as sp
from fractions import Fraction
from scipy.optimize import linprog
from lp2 import G,N,pats
def build(ws,Nv):
    a=len(ws); cap=[G[w] for w in ws]
    masks=list(range(1,1<<a)); 
    rows=[];cols=[];b=[];r=0
    for U in range(1,1<<a):
        u=bin(U).count('1'); lim=Nv[min(u,8)]
        S=U
        while S: rows.append(r);cols.append(S-1);S=(S-1)&U
        b.append(lim); r+=1
    for j in range(a):
        for m in masks:
            if m>>j&1: rows.append(r);cols.append(m-1)
        b.append(cap[j]); r+=1
    A=sp.csr_matrix((np.ones(len(rows)),(rows,cols)),shape=(r,len(masks)))
    return A,np.array(b,float)
def cert(ws,Nv):
    A,b=build(ws,Nv)
    res=linprog(-np.ones(A.shape[1]),A_ub=A,b_ub=b,bounds=(0,None),method='highs')
    y=-res.ineqlin.marginals; y=np.maximum(y,0)
    yq=np.ceil(y*1e4)/1e4
    yi=np.rint(yq*1e4).astype(np.int64)    # integer numerators over 10^4
    # exact check A^T yi >= 10^4 (integer arithmetic)
    At=A.T.tocsr().astype(np.int64)
    col=At@yi
    ok=col.min()>=10**4
    bound=Fraction(int((np.rint(b).astype(np.int64)*yi).sum()),10**4)
    return -res.fun, ok, float(bound), int(col.min())
if __name__=='__main__':
    Nsh=[0,3,6,12,20,36,63,112,112]
    for p in pats: print(p,cert(p,N),flush=True)
    print('d=7',cert([7,6,6,6,6,6,6,6,6],Nsh))
