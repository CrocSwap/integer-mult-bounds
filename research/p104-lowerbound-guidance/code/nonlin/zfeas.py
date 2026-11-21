"""feasibility table: FE[t,A]=True iff some minimal support K in F[t] has K subset A (A = allowed rows mask)."""
import pickle,numpy as np
F=pickle.load(open('ztight_F.pkl','rb')); m=16; n=104
FE=np.zeros((n,1<<m),bool)
for t in range(n):
    f=np.zeros(1<<m,bool)
    for K in F[t]: f[K]=True
    # upward closure: superset-sum
    for k in range(m):
        idx=np.arange(1<<m); sel=(idx>>k)&1==1
        f[sel]|=f[idx[sel]^(1<<k)]
    FE[t]=f
np.save('zfeas.npy',FE)
print('done',FE.sum(1).min(),FE.sum(1).max())
