"""MERGEROWS m7: adversarial SA over HS64 Gram decoders U (8 rows): minimise NF-S1 (constructive NF + gauge climb).
Objective low = candidate counter-decoder to 'NF => alpha+beta >= 38'."""
import sys,pickle,numpy as np,sympy
from m5 import *
L=std_set(sys.argv[1]); Q=Q_std(L); thr=int(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3])); N=int(sys.argv[4])
U=pickle.load(open('delta_U.pkl','rb')) if sys.argv[1]=='HS64' else sympy.eye(8)
def score(U):
    rows=gram_rows_B(L,np.eye(8,dtype=int),U,8)
    if check_decoder(rows,Q)!=0: return None
    nfr,ds=nf_all(rows,Q)
    return gauge_max(nfr,Q,300,0)['gmax_sum'],sum(prices(rows,Q)),sum(prices(nfr,Q)),rows
cur=score(U); best=cur[0]
for it in range(N):
    E=sympy.eye(8); i,j=rng.choice(8,2,replace=False); E[i,j]=int(rng.choice([-1,1,2,-2]))
    U2=E*U if rng.random()<0.5 else U*E
    s=score(U2)
    if s is None: continue
    if s[0]<=cur[0] or rng.random()<0.15:
        U,cur=U2,s
        if s[0]<best: best=s[0]
    print(it,'NF-S1',s[0],'C',s[1],'NF C',s[2],'cur',cur[0],'best',best,flush=True)
    if s[0]<thr: pickle.dump((U2,s[3]),open('m7_low_%s_%d.pkl'%(sys.argv[3],it),'wb'))
