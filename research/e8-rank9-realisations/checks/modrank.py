# rank over GF(p) of a rational matrix (lower bound for the rank over Q); p large prime
P=2**61-1
def rkp(rows,p=P):
    A=[[ (x.numerator*pow(x.denominator,-1,p))%p for x in r] for r in rows]
    r=0; n=len(A[0]) if A else 0
    for c in range(n):
        piv=next((i for i in range(r,len(A)) if A[i][c]),None)
        if piv is None: continue
        A[r],A[piv]=A[piv],A[r]; inv=pow(A[r][c],-1,p)
        A[r]=[x*inv%p for x in A[r]]
        for i in range(len(A)):
            if i!=r and A[i][c]:
                f=A[i][c]; A[i]=[(x-f*y)%p for x,y in zip(A[i],A[r])]
        r+=1
    return r
