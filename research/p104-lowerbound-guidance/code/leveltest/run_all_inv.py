import numpy as np
def inv4(P):
    m=P.shape[0]; A=np.concatenate([P%4,np.eye(m,dtype=np.int64)],1)
    for c in range(m):
        p=next((i for i in range(c,m) if A[i,c]%2),None)
        if p is None: return None
        A[[c,p]]=A[[p,c]]; A[c]=(A[c]*(1 if A[c,c]%4==1 else 3))%4
        for i in range(m):
            if i!=c: A[i]=(A[i]-A[i,c]*A[c])%4
    return A[:,m:]
