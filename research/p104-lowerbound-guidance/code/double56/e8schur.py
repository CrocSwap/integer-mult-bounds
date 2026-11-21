import sys,numpy as np; sys.path.insert(0,'../orbitlp')
from geo import Q, LAB
from rho import *
W=np.load('../orbitlp/e8W.npy')%4; V=np.load('../orbitlp/e8V.npy')%4; n=104
a=W%2;b=V%2
L=np.array([[(x>>(8-i))&1 for i in range(9)] for x in LAB])
print('rank L',f2rank([toint(r) for r in L]), 'Q==LL^T',((L@L.T)%2==Q).all())
Cg=[L[:,i] for i in range(9)]
def dimspan(vs): return f2rank([toint(v%2) for v in vs])
A=[a[:,k] for k in range(8)]; B=[b[:,k] for k in range(8)]
print('dimA',dimspan(A),'dimB',dimspan(B),'dim A*C',dimspan([x*c for x in A for c in Cg]),'dim B*C',dimspan([x*c for x in B for c in Cg]))
print('dim C*C',dimspan([c*d for c in Cg for d in Cg]),'dim A+C',dimspan(A+Cg))
print('|D_k|',a.sum(0),'|S_k|',b.sum(0), 'is 1 in C?', dimspan(Cg+[np.ones(n,int)])==dimspan(Cg))
print('A in C?', dimspan(Cg+A), 'B in C?',dimspan(Cg+B))
