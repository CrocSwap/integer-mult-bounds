import numpy as np
from qzword import *
rng=np.random.default_rng(1)
for trial in range(5):
    C=rng.normal(size=(4,4)); C[0,0]=0
    ops=elem_ops(C.tolist(),0.0,1.0)
    X=np.eye(4)
    for op in ops:
        M=np.eye(4)
        if op[0]=='ADD': M[op[1],op[2]]+=op[3]
        else: M[op[1],op[1]]=op[2]
        X=M@X
    print('elem err',np.abs(X-C).max())
