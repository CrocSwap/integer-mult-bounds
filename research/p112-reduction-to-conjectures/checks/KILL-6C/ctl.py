# Controls on own E8 build (D8 + half-spin coordinates, x2 integral).
import itertools, numpy as np, random, sys
sys.path.insert(0,'.')
R=[]
for i,j in itertools.combinations(range(8),2):
    for s in (2,-2):
        for u in (2,-2):
            v=[0]*8; v[i]=s; v[j]=u; R.append(v)
for m in range(256):
    v=[1 if m>>k&1 else -1 for k in range(8)]
    if v.count(-1)%2==0: R.append(v)
R=np.array(R); L=np.array([r for r in R if tuple(r)>tuple(-r)]); assert len(L)==120
rk=lambda A: np.linalg.matrix_rank(np.array(A,float))
# (1) G2 by brute force: max lines in span of k roots, k=1,2,3
def inspan(B):
    B=np.array(B,float); r=rk(B); return int(sum(rk(np.vstack([B,l]))==r for l in L))
print('N1',max(inspan([L[i]]) for i in range(120)))
print('N2',max(inspan([L[i],L[j]]) for i,j in itertools.combinations(range(120),2)))
best=0
for i,j in itertools.combinations(range(120),2):
    B2=np.array([L[i],L[j]],float)
    for k in range(j+1,120):
        if rk(np.vstack([B2,L[k]]))==3:
            # count via projection: lines with rank 3 after adding
            pass
# exact N3 via Gram: lines in span(a,b,c) <=> rank stays 3; vectorized over all l
cnt3=0
for i,j,k in itertools.combinations(range(0,120),3):
    if (i*7+j*3+k)%9: continue   # 1/9 sample of triples (full: run with arg 'full')
    B=np.array([L[i],L[j],L[k]],float)
    if rk(B)<3: continue
    Q,_=np.linalg.qr(B.T); P=L-(L@Q)@Q.T; c=int((np.abs(P).sum(1)<1e-9).sum()); best=max(best,c)
print('N3 (sampled 1/9 of triples) max',best)
# (2) real configuration: phi = 12 roots spanning R^8; M_t = a minimum-size S with r_t in span(phi_S)
random.seed(1); idx=random.sample(range(120),12)
while rk(L[idx])<8: idx=random.sample(range(120),12)
Phi=L[idx].astype(float); M=[]
for t in range(120):
    for m in range(1,9):
        S=next((S for S in itertools.combinations(range(12),m) if rk(np.vstack([Phi[list(S)],L[t]]))==rk(Phi[list(S)])),None)
        if S: M.append(frozenset(S)); break
viol=0
for k in (1,2,3):
    for K in itertools.combinations(range(12),k):
        if sum(1 for S in M if S<=set(K))>{1:1,2:3,3:6}[k]: viol+=1
sizes=[sum(1 for S in M if j in S) for j in range(12)]; tot=sum(sizes)
print('real config: K-violations',viol,' sum|M_t|=',tot,' TC bound 237.33 holds:',tot>=237.34-0.01,' caps',sorted(sizes))
open('ctl_caps.txt','w').write(' '.join(map(str,sizes)))
