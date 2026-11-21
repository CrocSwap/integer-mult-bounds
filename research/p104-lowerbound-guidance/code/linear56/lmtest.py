"""LINEAR56 lmtest.py: for invertible M over F2 (n x n): does some simultaneous permutation P give
   Lcal(P^T M P) = {L alternating : L M' strictly upper} = 0 ?   exhaustive for small n, random for n=8."""
import sys, numpy as np, itertools
from lcore import f2rank, kernel
def lcal_dim(M):
    n=len(M); pairs=list(itertools.combinations(range(n),2))
    # unknowns L_{ab}, a<b ; constraints (LM)_{ij}=0 for j<=i
    rows=[]
    for i in range(n):
        for j in range(i+1):
            r=np.zeros(len(pairs),np.int64)
            for idx,(a,b) in enumerate(pairs):
                # L_{i c} M_{c j}: L_{ab} appears as L_{a b} (i=a,c=b) and L_{b a} (i=b,c=a)
                if a==i: r[idx]^=M[b,j]
                if b==i: r[idx]^=M[a,j]
            rows.append(r)
    return len(pairs)-f2rank(np.array(rows))
def best_order(M,tries=None,rng=None):
    n=len(M)
    perms=itertools.permutations(range(n)) if tries is None else (rng.permutation(n) for _ in range(tries))
    for p in perms:
        p=list(p)
        if lcal_dim(M[np.ix_(p,p)])==0: return p
    return None
if __name__=="__main__":
    mode=sys.argv[1]
    if mode=='small':
        for n in (2,3,4):
            bad=0; tot=0
            for bits in itertools.product([0,1],repeat=n*n):
                M=np.array(bits).reshape(n,n)
                if f2rank(M)<n: continue
                tot+=1
                if best_order(M) is None: bad+=1
            print('n',n,'invertible',tot,'no good order',bad,flush=True)
    else:
        rng=np.random.default_rng(1); hist={}
        for it in range(int(sys.argv[2])):
            while True:
                M=rng.integers(0,2,(8,8))
                if f2rank(M)==8: break
            d0=lcal_dim(M); p=best_order(M,200,rng); hist[(d0>0, p is None)]=hist.get((d0>0,p is None),0)+1
        print('(identity order bad?, no order found in 200 tries):count',hist)
