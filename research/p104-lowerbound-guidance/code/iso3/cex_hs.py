"""ISO3 cex_hs: exact data for the S1 (isotropic-pair, digit-0) counterexample on HS64. Proof of S1<=30 in ISO3.md sec 3."""
import pickle, numpy as np
from gmax import *
rows=pickle.load(open('hs_kind1.pkl','rb')); L=std_set('HS64'); Q=Q_std(L); n=len(Q)
assert check_decoder(rows,Q)==0
VW,VU=vals(rows,n); six=[0,1,4,5,6,7]
pr=[]
for k in range(8):
    D=[t for t in range(n) if VW[t,k]<BIG]; S=[t for t in range(n) if VU[t,k]<BIG]; pr.append(rk2(Q[np.ix_(D,S)]))
for k in six: assert (VW[:,k]==1).all() and (VU[:,k]==-5).all() and pr[k]==8
for k in (2,3):
    fw=VW[:,k][VW[:,k]<BIG]; fu=VU[:,k][VU[:,k]<BIG]
    assert set(fw.tolist())<={2,3} and set(fu.tolist())=={-4}
print('valid; prices',pr,'C',sum(pr),'r2+r3',pr[2]+pr[3],'=> S1 <= 16 + r2 + r3 =',16+pr[2]+pr[3])
best=max(gauge_max(rows,Q,1500,sd)['gmax_sum'] for sd in range(4)); print('hill-climb S1 max (4x1500):',best); assert best<=16+pr[2]+pr[3]
