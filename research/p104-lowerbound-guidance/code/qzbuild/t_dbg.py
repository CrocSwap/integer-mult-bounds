import numpy as np
from qzword import *
rng=np.random.default_rng(0)
C=rng.normal(size=(4,4)).tolist()
ops=elem_ops(C,0.0,1.0)
X=np.eye(4)
for op in ops:
    M=np.eye(4)
    if op[0]=='ADD': M[op[1],op[2]]+=op[3]
    else: M[op[1],op[1]]=op[2]
    X=M@X
print('elem err',np.abs(X-np.array(C)).max())
v=[rng.normal(size=4) for _ in range(2)]
# biorth w
Vm=np.array(v).T; A=np.linalg.pinv(Vm); w=[A[0],A[1]]
P=np.array(prefix([(0,v[0],w[0]),(1,v[1],w[1])],4,0.0,1.0))
print('prefix', P@v[0], P@v[1], P[0]-w[0])
