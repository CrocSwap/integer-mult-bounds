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
sk_all=None
G=(L@L.T)!=0   # non-orthogonal
ri=0; T=(L@L[ri])!=0; idxT=np.nonzero(T)[0]; jr=list(idxT).index(ri)
Tm=M[:,T]; s=Tm.sum(1); keep=np.nonzero(s>=T.sum()-13-s.max())[0]; Tk=Tm[keep]; sk=s[keep]
lefts=set()
for c0 in range(0,len(Tk),1500):
    blk=Tk[c0:c0+1500]; U=sk[c0:c0+1500,None]+sk[None,:]-blk@Tk.T
    cov=(blk[:,jr][:,None]+Tk[:,jr][None,:])>0
    ii,jj=np.nonzero((U>=T.sum()-13)&cov)
    for a,b in zip(ii,jj): lefts.add(tuple(idxT[(blk[a]|Tk[b])==0]))
mins=[e for e in lefts if not any(set(f)<set(e) for f in lefts)]
from collections import Counter
print('B2: r0 minimal leftovers <=13:',Counter(len(e) for e in mins),flush=True)
worst=0
for e in mins:
    if len(e)!=12: continue
    base=np.zeros(n,bool); base[list(e)]=True
    for l in [None]+[t for t in range(n) if not base[t]]:
        E=base.copy()
        if l is not None: E[l]=True
        cnt=G[:,E].sum(1)     # |Off(r) n E| (G[r,r] true: r in E excluded below)
        sup=((cnt>=8)&~E).sum()
        worst=max(worst,sup)
print('B2: max #roots outside E with |Off(r) n E|>=8, E = M (+1 line):',worst,' need <=22')
