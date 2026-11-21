import itertools, numpy as np
R=[]
for i,j in itertools.combinations(range(8),2):
    for a in (2,-2):
        for b in (2,-2):
            v=[0]*8; v[i]=a; v[j]=b; R.append(tuple(v))
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: R.append(tuple(s))
L=[];seen=set()
for r in R:
    if tuple(-x for x in r) in seen: continue
    seen.add(r); L.append(r)
L=np.array(L)
def Q(P): return ((P@P.T)%8==0).astype(int)
def rk(M):
    M=M.copy()%2; r=0
    for c in range(M.shape[1]):
        p=[i for i in range(r,M.shape[0]) if M[i,c]]
        if not p: continue
        M[[r,p[0]]]=M[[p[0],r]]
        for i in range(M.shape[0]):
            if i!=r and M[i,c]: M[i]^=M[r]
        r+=1
    return r
HS=L[np.all(np.abs(L)==1,axis=1)]
a0=L[0]; E7=L[(L@a0)==0]; EA=np.vstack([E7,a0])
for nm,P in (('HS64',HS),('E7+A1',EA),('E7',E7),('P120',L)):
    q=Q(P); print(nm,len(P),'h=',rk(q),'zero rows',int((q.sum(1)==0).sum()),'diag all 1',bool(q.diagonal().all()),'symmetric',bool((q==q.T).all()),'distinct rows',len({tuple(r) for r in q}))
