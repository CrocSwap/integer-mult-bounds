import numpy as np
from lt import *
n=104
rng=np.random.default_rng(0)
def f2solve(A,c):
    A=A%2; c=c%2; r,m=A.shape; M=np.concatenate([A,c[:,None]],1).astype(np.int64); piv=[]; row=0
    for col in range(m):
        p=next((i for i in range(row,r) if M[i,col]),None)
        if p is None: continue
        M[[row,p]]=M[[p,row]]
        for i in range(r):
            if i!=row and M[i,col]: M[i]^=M[row]
        piv.append(col); row+=1
    if M[row:,m].any(): return None
    free=[j for j in range(m) if j not in piv]; x=np.zeros(m,np.int64)
    x[free]=rng.integers(0,2,len(free))
    for i,col in enumerate(piv): x[col]=(M[i,m]+M[i,free]@x[free])%2
    return x
def kernel_f2(A):
    A=A%2; r,m=A.shape; M=A.copy().astype(np.int64); piv=[]; row=0
    for col in range(m):
        p=next((i for i in range(row,r) if M[i,col]),None)
        if p is None: continue
        M[[row,p]]=M[[p,row]]
        for i in range(r):
            if i!=row and M[i,col]: M[i]^=M[row]
        piv.append(col); row+=1
    free=[j for j in range(m) if j not in piv]; out=[]
    for f in free:
        x=np.zeros(m,np.int64); x[f]=1
        for i,col in enumerate(piv): x[col]=M[i,f]
        out.append(x)
    return out
def resample(W,V,t,side):
    if side=='V': V,W=W,V
    P=np.nonzero(Q104[t])[0]; A=V[P]%4; c=np.array([2 if p==t else 0 for p in P])
    K=kernel_f2(A); w0=np.zeros(A.shape[1],np.int64)
    for kv in K:
        if rng.random()<0.5: w0=(w0+kv)%2
    w1=f2solve(A,((c-A@w0)%4)//2)
    if w1 is not None: W=W.copy(); W[t]=(w0+2*w1)%4
    if side=='V': W,V=V,W
    return W,V
def check(W,V): return not ((((W@V.T)-2*np.eye(n,dtype=np.int64))%4)*Q104).any()
