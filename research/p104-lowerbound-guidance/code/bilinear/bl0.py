# BILINEAR bl0 (float sanity): zero-block-sum (kernel) gauge.  G' = E(x)I - 2 diag(Lam_t^{-1}); Ghat_st = lam_s^T G'_st kap_t.
# Claims checked: Ghat block row/col sums 0; Ghat_st = 1/4 eps_st alpha_s beta_t (s!=t), alpha_s=Q_s^{-1}-Q_{s-1}^{-1}, beta_t=Q_t-Q_{t-1}, Q_t=(-1)^t A_t..A_1.
import os
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np
rng=np.random.default_rng(2);I=np.eye(2)
for k in (3,4,6,9):
    As=[rng.normal(size=(2,2)) for _ in range(k-1)];P=I.copy()
    for a in As:P=a@P
    As.append((-1)**(k+1)*np.linalg.inv(P))
    Gp=np.zeros((2*k,2*k))
    for s in range(k):
        for t in range(k):Gp[2*s:2*s+2,2*t:2*t+2]=(1 if s<=t else -1)*I-(2*np.linalg.inv(As[t]+I) if s==t else 0)
    Q=[I];[Q.append(-As[t]@Q[-1]) for t in range(k)]
    kap=[0.5*(As[t]+I)@((-1)**t*np.linalg.multi_dot([I,I]+[As[j] for j in range(t-1,-1,-1)]) if t else I) for t in range(k)]
    # use recursion form: S_1=I, S_{t+1}=-A_t S_t, kap_t=1/2 Lam_t S_t ; T_k=I, T_{t-1}=-T_t A_t, lam_t^T=1/2 T_t Lam_t
    S=[I];[S.append(-As[t]@S[-1]) for t in range(k)];kap=[0.5*(As[t]+I)@S[t] for t in range(k)]
    T=[None]*k;T[k-1]=I
    for t in range(k-1,0,-1):T[t-1]=-T[t]@As[t]
    lamT=[0.5*T[t]@(As[t]+I) for t in range(k)]
    K=np.vstack(kap);L=np.hstack(lamT)
    Gh=np.zeros_like(Gp);err=0
    for s in range(k):
        for t in range(k):
            Gh[2*s:2*s+2,2*t:2*t+2]=lamT[s]@Gp[2*s:2*s+2,2*t:2*t+2]@kap[t]
            if s!=t:
                al=np.linalg.inv(Q[s+1])-np.linalg.inv(Q[s]);be=Q[t+1]-Q[t]
                err=max(err,abs(Gh[2*s:2*s+2,2*t:2*t+2]-0.25*(1 if s<=t else -1)*al@be).max())
    rs=max(abs(sum(Gh[2*s:2*s+2,2*t:2*t+2] for t in range(k))).max() for s in range(k))
    cs=max(abs(sum(Gh[2*s:2*s+2,2*t:2*t+2] for s in range(k))).max() for t in range(k))
    print(k,'|G kap|',f'{abs(Gp@K).max():.1e}','|lam G|',f'{abs(L@Gp).max():.1e}','rowsum',f'{rs:.1e}','colsum',f'{cs:.1e}','formula',f'{err:.1e}','rank',np.linalg.matrix_rank(Gh,1e-9))
