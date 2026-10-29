# N_j = max #E8 root lines in a j-dim subspace (char 0). Exhaustive over root-spanned subspaces, j<=J.
# r in span(B) (B independent) iff Gram det(B+r)=0; Gram from the E8 Cartan form (pos. def.), entries small ints -> rounding exact.
import numpy as np, sys
from e8 import lines, C
L=np.array(lines,dtype=np.int64); n=len(L); Gm=L@C@L.T   # 120x120 Gram
def contained(B):
    k=len(B); idx=np.array(B)
    GB=Gm[np.ix_(idx,idx)]
    # det of bordered matrices for all r at once
    M=np.zeros((n,k+1,k+1)); M[:,:k,:k]=GB; M[:,:k,k]=Gm[idx,:].T; M[:,k,:k]=Gm[idx,:].T; M[:,k,k]=Gm.diagonal()
    dets=np.rint(np.linalg.det(M)).astype(np.int64)
    return frozenset(np.nonzero(dets==0)[0].tolist())
J=int(sys.argv[1])
level={(frozenset([i]),(i,)) for i in range(n)}
for j in range(2,J+1):
    seen={}
    for S,B in level:
        for i in range(n):
            if i in S: continue
            T=contained(list(B)+[i])
            if T not in seen: seen[T]=tuple(B)+(i,)
    level=set(seen.items())
    print('j=%d: #root-spanned subspaces %d, max lines %d'%(j,len(level),max(len(s) for s,_ in level)),flush=True)
