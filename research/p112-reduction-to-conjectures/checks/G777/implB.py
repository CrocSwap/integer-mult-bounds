# Independent implementation B: own E8 construction (Bourbaki coords, half-integers x2), labels via Bourbaki simple roots,
# 7-flats via membership matrix (numpy), pair coverage via integer matrix products (no bitmasks).
import numpy as np, itertools
from fractions import Fraction
R=[]
for i,j in itertools.combinations(range(8),2):
    for a in (1,-1):
        for b in (1,-1):
            v=[0]*8; v[i]=2*a; v[j]=2*b; R.append(v)
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: R.append(list(s))
R=np.array(R); 
# one rep per line
L=[]; seen=set()
for v in R:
    k=tuple(v); m=tuple(-v)
    if m in seen: continue
    seen.add(k); L.append(v)
L=np.array(L); n=len(L); assert n==120
# Bourbaki simple roots (x2): a1=1/2(1,-1,..,-1,1), a2=e1+e2, a3=e2-e1, a4=e3-e2,...,a8=e7-e6
S=np.array([[1,-1,-1,-1,-1,-1,-1,1],[2,2,0,0,0,0,0,0],[-2,2,0,0,0,0,0,0],[0,-2,2,0,0,0,0,0],[0,0,-2,2,0,0,0,0],[0,0,0,-2,2,0,0,0],[0,0,0,0,-2,2,0,0],[0,0,0,0,0,-2,2,0]])
X=np.linalg.solve(S.T.astype(float),L.T.astype(float)).T
Xi=np.rint(X).astype(int); assert np.abs(X-Xi).max()<1e-9
lab=np.concatenate([np.ones((n,1),int),Xi%2],axis=1)  # n x 9
F=np.array([[(k>>i)&1 for i in range(9)] for k in range(1,512)])  # functionals
P=(F@lab.T)%2   # 511 x 120 : 1 = functional nonzero on label
inK=(P==0)
# 7-flats = pairs of independent functionals (distinct nonzero) ; dedupe membership rows
rows={}
for a in range(511):
    for b in range(a+1,511):
        m=inK[a]&inK[b]; rows[m.tobytes()]=m
M=np.array(list(rows.values()),dtype=np.int32); print('B: 7-flat membership rows',len(M),'max lines',M.sum(1).max())
G=(L@L.T)//4
def offset(h): return (L@h)!=0
def maxcover(T,need_idx=None,thr_left=99):
    """returns max |T & (A|B)| over pairs, and (if need_idx) restricted to pairs covering need_idx; via matrix products"""
    Tm=M[:,T]; s=Tm.sum(1)
    keep=np.nonzero(s>=max(0,T.sum()-thr_left-s.max()))[0]
    Tk=Tm[keep]; sk=s[keep]
    best=0; bestn=0
    for c0 in range(0,len(keep),2000):
        I=Tk[c0:c0+2000]@Tk.T
        U=sk[c0:c0+2000,None]+sk[None,:]-I
        best=max(best,U.max())
        if need_idx is not None:
            j=list(np.nonzero(T)[0]).index(need_idx)
            cov=(Tk[c0:c0+2000,j][:,None]+Tk[:,j][None,:])>0
            bestn=max(bestn,np.where(cov,U,0).max())
    return best,bestn,keep,Tk
# directions: generic h in J^perp for J subsets of simple roots; Off = lines not in span(J)
res={}
for r in range(8,5,-1):
    for J in itertools.combinations(range(8),r):
        if r==8: continue
        A=S[list(J)].astype(float)
        inspan=np.array([np.linalg.matrix_rank(np.vstack([A,l]))==r for l in L])
        T=~inspan
        if T.sum()>94: continue
        b,_,_,_=maxcover(T)
        print('B: |Phi_J|',inspan.sum(),'|Off|',T.sum(),'min leftover',T.sum()-b,flush=True)
# root
ri=0; T=offset(L[ri])
b,bn,keep,Tk=maxcover(T,need_idx=ri,thr_left=11)
print('B: root |Off|',T.sum(),'min leftover',T.sum()-b,'min leftover with r covered',T.sum()-bn)
# enumerate all leftovers of size<=11 with r covered
idxT=np.nonzero(T)[0]; jr=list(idxT).index(ri)
sk=Tk.sum(1); lefts=set()
for c0 in range(0,len(Tk),2000):
    blk=Tk[c0:c0+2000]
    I=blk@Tk.T; U=sk[c0:c0+2000,None]+sk[None,:]-I
    cov=(blk[:,jr][:,None]+Tk[:,jr][None,:])>0
    ii,jj=np.nonzero((U>=T.sum()-11)&cov)
    for a,b in zip(ii,jj):
        u=(blk[a]|Tk[b]); lefts.add(tuple(idxT[u==0]))
mins=[e for e in lefts if not any(set(f)<set(e) for f in lefts)]
from collections import Counter
print('B: minimal leftovers <=11 (r covered):',len(mins),Counter(len(e) for e in mins))
rk=Counter(np.linalg.matrix_rank(((lab[list(e)])%2).astype(float)) for e in mins)  # real rank of 0/1 rows ~ not F2; recompute F2 rank:
def f2rank(A):
    A=A.copy()%2; r=0
    for c in range(A.shape[1]):
        p=[i for i in range(r,len(A)) if A[i,c]]
        if not p: continue
        A[[r,p[0]]]=A[[p[0],r]]
        for i in range(len(A)):
            if i!=r and A[i,c]: A[i]^=A[r]
        r+=1
    return r
print('B: F2 label ranks',Counter(f2rank(lab[list(e)]) for e in mins))
# N_Q: for each Q of r0, roots r (r not in Q) with Q subset Off(r) and Off(r)\Q coverable by 2 flats with r covered
NQ=Counter(); inQ=0
for e in mins:
    Q=set(e); cnt=0
    for r2 in range(n):
        T2=offset(L[r2])
        if not all(T2[q] for q in Q): continue
        if r2 in Q: inQ+=1
        rest=T2.copy(); rest[list(Q)]=False
        # need two flats covering rest, r2 covered by them (r2 in rest if r2 not in Q)
        if r2 in Q: continue
        Tm=M[:,rest]; s=Tm.sum(1); need=rest.sum()
        k=np.nonzero(s>=need-s.max())[0]; Tk2=Tm[k]; s2=s[k]
        U=s2[:,None]+s2[None,:]-Tk2@Tk2.T
        if (U>=need).any(): cnt+=1
    NQ[cnt]+=1
print('B: N_Q over r0 Qs (roots outside Q having Q as exact cover-leftover):',NQ,' roots in Q with Q in Off:',inQ)
