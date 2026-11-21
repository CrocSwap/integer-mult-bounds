# SCHERK sk0: numeric sanity of the signed-Gram normal form (float; the proof is in SK.md).
# Normal form: G = Etil*diag(A_t+I) - 2I (Etil_st = +I if s<=t else -I), with A_k...A_1 = (-1)^(k+1) I_2.
# Then rank G = 2k-2 and ANY rank factorisation G = B^T A gives prod_{t=k..1}(I + A_t B_t^T) = -I_n, V_t|U_t ~ A_t.
import os
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np
rng=np.random.default_rng(1)
def Gmat(As):
    k=len(As);G=np.zeros((2*k,2*k))
    for s in range(k):
        for t in range(k):
            G[2*s:2*s+2,2*t:2*t+2]=(1 if s<=t else -1)*(As[t]+np.eye(2))
    return G-2*np.eye(2*k)
for k in (3,4,5,7,10):
    n=2*k-2;As=[rng.normal(size=(2,2)) for _ in range(k-1)]
    P=np.eye(2)
    for a in As:P=a@P
    As.append((-1)**(k+1)*np.linalg.inv(P))
    G=Gmat(As);U,S,Vt=np.linalg.svd(G);r=(S>1e-8*S[0]).sum()
    Bt=U[:,:n]*S[:n];A=Vt[:n];B=Bt.T
    R=np.eye(n);ev=[]
    for t in range(k):
        V=np.eye(n)+A[:,2*t:2*t+2]@B[:,2*t:2*t+2].T;R=V@R
        ev.append(np.sort_complex(np.linalg.eigvals(B[:,2*t:2*t+2].T@A[:,2*t:2*t+2]+np.eye(2)))-np.sort_complex(np.linalg.eigvals(As[t])))
    print(k,'rankG',r,'|prod+I|',f"{np.abs(R+np.eye(n)).max():.1e}",'eig match',f"{max(abs(e).max() for e in ev):.1e}")
