"""LINEAR56 glcheck.py: [C] check of the ordering lemma GL: the recursive choice (pick last index i_n so the remaining rows
are independent, recurse on the principal submatrix) yields an order with rank M[1..k-1,1..k] = k-1 for all k, and then
Lcal(M) = {L alternating : LM strictly upper} = 0.  Random invertible 8x8 and 9x9 M."""
import numpy as np
from lcore import f2rank
from lmtest import lcal_dim
rng=np.random.default_rng(5)
def gl_order(M):
    idx=list(range(len(M))); order=[]
    while idx:
        A=M[np.ix_(idx,idx)]
        for pos in range(len(idx)):
            rest=[r for r in range(len(idx)) if r!=pos]
            if f2rank(A[rest]) == len(rest): break
        else: return None
        order.insert(0,idx[pos]); idx=[idx[r] for r in rest]
    return order
bad=0
for n in (8,9):
    for it in range(300):
        while True:
            M=rng.integers(0,2,(n,n))
            if f2rank(M)==n: break
        o=gl_order(M); Mo=M[np.ix_(o,o)]
        ok1=all(f2rank(Mo[:k-1,:k])==k-1 for k in range(2,n+1))
        ok2=lcal_dim(Mo)==0
        if not (ok1 and ok2): bad+=1
print('GL failures',bad,'of 600')
