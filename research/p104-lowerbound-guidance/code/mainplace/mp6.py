"""MAINPLACE mp6: all-orders k8 sweep of the nested-chain argmax under TWO-HUB SIGN FLATNESS.
Shape forced by RELAY-HALL [P]: hubs (X|Xc),(Y|Yc); D4 on X,Xc,Y,Yc with pair pieces; chords = pair pieces.
Test (scout): exists U_s,W_t in GL2, rank-1 N_R with I+sum_{R>=st}N_R = eps_st U_s W_t on all non-chord pairs (s!=t).
Stage 1 exact GF(2) prefilter: within a cell U_s = +-U_cell (proved), so eps_st u_s w_t must depend only on (cell s, cell t).
Stage 2 numeric LM on survivors. Dihedral dedupe."""
import itertools,sys,numpy as np
from scipy.optimize import least_squares
k=8;A=frozenset(range(k))
def pairings(S):
    S=sorted(S);a=S[0]
    for b in S[1:]:
        yield (frozenset({a,b}),frozenset(x for x in S if x not in(a,b)))
def dih(perm_sets):
    pass
def canon(X,Y,P):
    best=None
    for r in range(k):
        for f in (1,-1):
            m=lambda s:(f*s+r)%k
            Xs=frozenset(map(m,X));Ys=frozenset(map(m,Y))
            h1=min(tuple(sorted(Xs)),tuple(sorted(A-Xs)));h2=min(tuple(sorted(Ys)),tuple(sorted(A-Ys)))
            hs=tuple(sorted([h1,h2]))
            ps=tuple(sorted(tuple(sorted(map(m,p))) for p in P))
            key=(hs,ps)
            if best is None or key<best:best=key
    return best
def eps(s,t):return 1 if s<t else -1
def gf2(cell,chords):
    # unknowns u_s,w_t,tau(ci,cj) in GF2; eq: e_st + u_s + w_t + tau = 0
    idx={};rows=[]
    def v(n):
        if n not in idx:idx[n]=len(idx)
        return idx[n]
    for s in range(k):
        for t in range(k):
            if s==t or frozenset({s,t}) in chords:continue
            rows.append(([v(('u',s)),v(('w',t)),v(('T',cell[s],cell[t]))],0 if eps(s,t)==1 else 1))
    n=len(idx);M=np.zeros((len(rows),n+1),np.uint8)
    for i,(c,b) in enumerate(rows):
        for j in c:M[i,j]^=1
        M[i,n]=b
    r=0
    for c in range(n):
        p=next((i for i in range(r,len(M)) if M[i,c]),None)
        if p is None:continue
        M[[r,p]]=M[[p,r]]
        for i in range(len(M)):
            if i!=r and M[i,c]:M[i]^=M[r]
        r+=1
    return not any(M[i,:n].sum()==0 and M[i,n] for i in range(len(M)))
def numeric(masks,chords,tries=8,seed=0):
    rng=np.random.default_rng(seed)
    prs=[(s,t) for s in range(k) for t in range(k) if s!=t and frozenset({s,t}) not in chords]
    cov={(s,t):[i for i,Mk in enumerate(masks) if s in Mk and t in Mk] for s,t in prs}
    def res(z):
        U=z[:32].reshape(8,2,2);W=z[32:64].reshape(8,2,2);V=z[64:72].reshape(4,2);Vp=z[72:80].reshape(4,2)
        out=[]
        for s,t in prs:
            M=np.eye(2)+sum(np.outer(V[i],Vp[i]) for i in cov[(s,t)]) if cov[(s,t)] else np.eye(2)
            out.append((M-eps(s,t)*U[s]@W[t]).ravel())
        out.append([1/(1e-3+abs(np.linalg.det(U[s])))*1e-3 for s in range(8)])
        return np.concatenate(out)
    best=9
    for _ in range(tries):
        r=least_squares(res,rng.normal(size=80),xtol=1e-14,ftol=1e-14,gtol=1e-14,max_nfev=300)
        f=np.abs(res(r.x)[:-8]).max()
        U=r.x[:32].reshape(8,2,2);d=min(abs(np.linalg.det(u)) for u in U)
        if d>1e-3:best=min(best,f)
        if best<1e-10:break
    return best
if __name__=='__main__':
    seen=set();tot=g=0;surv=[]
    splits=[frozenset(c) for c in itertools.combinations(range(k),4) if 0 in c]
    for X in splits:
        for Y in splits:
            if Y==X or Y==A-X:continue   # aligned hubs: CELL-RANK dead (order-free)
            for P in itertools.product(*[list(pairings(S)) for S in (X,A-X,Y,A-Y)]):
                pcs=[p for pp in P for p in pp];key=canon(X,Y,pcs)
                if key in seen:continue
                seen.add(key);tot+=1
                cell={s:(s in X)*2+(s in Y) for s in range(k)}
                chords=set(pcs)
                if not gf2(cell,chords):continue
                g+=1;surv.append((X,Y,pcs))
    print('classes',tot,'pass GF2',g,flush=True)
    nb=0
    for X,Y,pcs in surv:
        f=numeric([X,A-X,Y,A-Y],set(pcs))
        tag='SOLVES' if f<1e-9 else 'stall'
        if f<1e-9:nb+=1
        print(tag,'%.2e'%f,sorted(X),sorted(Y),[tuple(sorted(p)) for p in pcs],flush=True)
    print('END numeric solves',nb,'of',g,flush=True)
