"""DEN4 gf.py (own code): GF(2^16) arithmetic + rank; used to evaluate F2[x]-matrix ranks at random points (gives a LOWER estimate of the F2(x)-rank)."""
import numpy as np
POLY=0x1100B
EXP=np.zeros(2*65535,dtype=np.int64); LOG=np.zeros(65536,dtype=np.int64)
x=1
for i in range(65535):
    EXP[i]=x; LOG[x]=i; x<<=1
    if x&0x10000: x^=POLY
EXP[65535:]=EXP[:65535]
def gmul(a,b):
    if a==0 or b==0: return 0
    return int(EXP[LOG[a]+LOG[b]])
def gpow(a,k):
    if k==0: return 1
    if a==0: return 0
    return int(EXP[(LOG[a]*k)%65535])
def grank(M):
    M=[list(map(int,r)) for r in M]; R=len(M); Cc=len(M[0]) if R else 0; r=0
    for c in range(Cc):
        p=next((i for i in range(r,R) if M[i][c]),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]; inv=int(EXP[(65535-LOG[M[r][c]])%65535])
        M[r]=[gmul(inv,v) for v in M[r]]
        for i in range(R):
            if i!=r and M[i][c]:
                f=M[i][c]; M[i]=[a^gmul(f,b) for a,b in zip(M[i],M[r])]
        r+=1
        if r==R: break
    return r
def polyrank(coeffs,trials=2,seed=0):
    """coeffs: list of F2 matrices P_0..P_d; returns max over random t in GF(2^16) of rank sum P_l t^l."""
    rng=np.random.default_rng(seed); best=0
    for _ in range(trials):
        t=int(rng.integers(2,65535)); n,m=coeffs[0].shape
        A=np.zeros((n,m),dtype=np.int64)
        for l,P in enumerate(coeffs):
            tl=gpow(t,l)
            A^=(np.asarray(P)%2)*tl
        best=max(best,grank(A))
    return best
