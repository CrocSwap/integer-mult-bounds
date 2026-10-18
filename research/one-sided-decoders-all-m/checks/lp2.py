import numpy as np, scipy.sparse as sp
from scipy.optimize import linprog
G={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}
N=[0,1,3,6,12,20,36,63,120]
def feas(ws,nlines=112,Nv=N,maxk=8):
    a=len(ws); cap=[G[w] for w in ws]
    masks=[m for m in range(1,1<<a) if bin(m).count('1')<=maxk]
    idx={m:i for i,m in enumerate(masks)}
    rows=[];cols=[];vals=[];b=[]
    r=0
    for U in range(1,1<<a):
        u=bin(U).count('1'); lim=Nv[min(u,8)]
        # subsets S of U
        S=U
        while S:
            if S in idx: rows.append(r);cols.append(idx[S]);vals.append(1)
            S=(S-1)&U
        b.append(lim); r+=1
    for j in range(a):
        for m in masks:
            if m>>j&1: rows.append(r);cols.append(idx[m]);vals.append(1)
        b.append(cap[j]); r+=1
    A=sp.csr_matrix((vals,(rows,cols)),shape=(r,len(masks)))
    Aeq=sp.csr_matrix(np.ones((1,len(masks))))
    # objective: maximise covered lines with sum<=112 => check max sum of m
    res=linprog(-np.ones(len(masks)),A_ub=A,b_ub=b,bounds=(0,None),method='highs')
    return -res.fun
pats=[[7,6,6,6,6,6,6,6,6,6],[7,6,6,6,6,6,6,6,6,6,1],[7,7,6,6,6,6,6,6,6,6],[7,6,6,6,6,6,6,6,6,6,1,1],[7,6,6,6,6,6,6,6,6,6,2],[7,7,6,6,6,6,6,6,6,6,1],[7,7,7,6,6,6,6,6,6,6]]
if __name__=='__main__':
    for p in pats: print(p, 'max coverable lines (need 112):', round(feas(p),2),flush=True)
