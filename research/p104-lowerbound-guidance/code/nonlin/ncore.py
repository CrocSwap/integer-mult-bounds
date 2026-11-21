"""NONLIN ncore.py (own code). Geometry for P104 in homogeneous F2^9 coords h=(1,c), beta=1(+)B."""
import sys, numpy as np, itertools
sys.path.insert(0,'../linear56')
from lcore import C120,G,Bm,Q,Binv,f2rank,rref,kernel,solve2
n=104
C=C120[:104].astype(np.int64); Cb=C%2
Z=C120[104:].astype(np.int64); Zb=Z%2
H=np.concatenate([np.ones((104,1),np.int64),Cb],1)          # labels in F2^9
Beta=np.zeros((9,9),np.int64); Beta[0,0]=1; Beta[1:,1:]=Bm
def beta(x,y): return int(np.asarray(x)@Beta@np.asarray(y)%2)
assert ((H@Beta@H.T)%2==Q).all()
e=np.zeros(9,np.int64); e[0]=1
def ctil(t): v=np.zeros(9,np.int64); v[1:]=Cb[t]; return v
def span_dim(rows): return f2rank(np.array(rows)) if len(rows) else 0
