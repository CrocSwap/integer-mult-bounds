import sys,pickle,collections,numpy as np
from gmax import *
rows=pickle.load(open(sys.argv[1],'rb'))
L=std_set(sys.argv[2]); Q=Q_std(L); n=len(Q)
VW,VU=vals(rows,n)
for k in range(len(rows)):
    D=[t for t in range(n) if VW[t,k]<BIG]; S=[t for t in range(n) if VU[t,k]<BIG]
    print(k,'r',rk2(Q[np.ix_(D,S)]),'VW',dict(collections.Counter(VW[:,k].tolist())),'VU',dict(collections.Counter(VU[:,k].tolist())))
