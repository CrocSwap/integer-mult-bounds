"""DOUBLE56 rho.py (own code): exact-ish master maxima rho_B = max_y rank sum diag(y_k)Q diag(b_k), rho_A likewise.
rho_B = transversal rank of the subspace family R_t = span{b_k o Q_t : t in D_k} (Rado). Computed as the rank over GF(2^16) of a
random combination (always <= rho_B; equal w.h.p.), plus an F2 Rado certificate (upper bound) via greedy J search."""
import numpy as np
PR=0x1100B  # x^16+x^12+x^3+x+1 primitive
EXP=np.zeros(2*65536,dtype=np.int64); LOG=np.zeros(65536,dtype=np.int64)
x=1
for i in range(65535):
    EXP[i]=x; LOG[x]=i; x<<=1
    if x&0x10000: x^=PR
EXP[65535:2*65535]=EXP[:65535]
def gmul_vec(c,v):
    out=np.zeros_like(v); nz=v!=0
    if c==0: return out
    out[nz]=EXP[LOG[c]+LOG[v[nz]]]; return out
def ginv(c): return int(EXP[(65535-LOG[c])%65535])
def grank(M):
    M=M.copy(); n,m=M.shape; r=0
    for col in range(m):
        piv=None
        for i in range(r,n):
            if M[i,col]: piv=i;break
        if piv is None: continue
        M[[r,piv]]=M[[piv,r]]
        inv=ginv(int(M[r,col])); M[r]=gmul_vec(inv,M[r])
        for i in range(n):
            if i!=r and M[i,col]: M[i]^=gmul_vec(int(M[i,col]),M[r])
        r+=1
        if r==n: break
    return r
def f2basis(vecs):
    """vecs: iterable of python ints; returns reduced basis list"""
    piv={}
    for x in vecs:
        while x:
            h=x.bit_length()-1
            if h in piv: x^=piv[h]
            else: piv[h]=x; break
    return list(piv.values())
def f2rank(vecs): return len(f2basis(vecs))
def toint(v): return int(''.join(str(int(c)%2) for c in v),2) if len(v) else 0
def spaces_B(W,V,Q):
    """R_t for t in ports: basis (ints over n bits) of span{b_k o Q_t : t in D_k}"""
    W=W%4; V=V%4; n,m=W.shape; b=V%2
    bq=[[toint(b[:,k]*Q[t]) for k in range(m)] for t in range(n)]
    return [f2basis([bq[t][k] for k in range(m) if W[t,k]]) for t in range(n)]
def spaces_A(W,V,Q): return spaces_B(V,W,Q.T)
def trank(R,n,trials=3,seed=1):
    rng=np.random.default_rng(seed); best=0
    for _ in range(trials):
        M=np.zeros((len(R),n),dtype=np.int64)
        for t,B in enumerate(R):
            for x in B:
                lam=int(rng.integers(1,65536))
                bits=np.array([(x>>(n-1-s))&1 for s in range(n)],dtype=bool)
                M[t,bits]^=lam
        best=max(best,grank(M))
    return best
def rado_ub(R,n,iters=1):
    """greedy: start J=all, drop port whose removal lowers dim V_J + n-|J| most (or keeps it); returns best value and J"""
    J=set(t for t in range(len(R)) if R[t]); best=f2rank([x for t in J for x in R[t]])+len(R)-len(J); bestJ=set(J)
    improved=True
    while improved and J:
        improved=False; cur=f2rank([x for t in J for x in R[t]])+len(R)-len(J)
        cand=None
        for t in list(J):
            J2=J-{t}; val=f2rank([x for u in J2 for x in R[u]])+len(R)-len(J2)
            if val<cur or (cand is None and val==cur):
                if val<cur: cand=(val,t); cur=val
                elif cand is None: cand=(val,t)
        if cand and cand[0]<=cur:
            J.discard(cand[1]); improved=True
            v=f2rank([x for t in J for x in R[t]])+len(R)-len(J)
            if v<best: best=v; bestJ=set(J)
            if v>best+3: break
    return best,bestJ
def rhos(W,V,Q,trials=3):
    n=W.shape[0]
    RB=spaces_B(W,V,Q); RA=spaces_A(W,V,Q)
    return trank(RB,n,trials),trank(RA,n,trials),RB,RA
def check_decoder(W,V,Q):
    W=W%4; V=V%4; n=W.shape[0]
    return not (((W@V.T-2*np.eye(n,dtype=np.int64))%4)*Q).any()
def cost(W,V,Q):
    W=W%4; V=V%4; C=0
    for k in range(W.shape[1]):
        D=np.nonzero(W[:,k])[0]; S=np.nonzero(V[:,k])[0]
        if len(D) and len(S): C+=f2rank([toint(Q[t,S]) for t in D])
    return C
