import numpy as np, random
from ds_lib import *
L=e8_lines(); HS=halfspin(L); EA=e7a1(L); E7=EA[:-1]
for nm,P in (('P120',L),('halfspin',HS),('E7+A1',EA),('E7',E7)):
    print(nm,len(P),'h=',hrank(P))
# tau-triviality test: random even pairs (u,v): Q[u,v] all row/col sums even; tau = sum/2 mod 2
def tau_search(P,trials=20000,seed=1):
    Q=Qmat(P).astype(np.int64); n=len(P); rng=np.random.default_rng(seed); bad=0; ex=None; good=0
    for t in range(trials):
        u=rng.random(n)<rng.uniform(0.1,0.9)
        # find v: alternate: v must satisfy Q[u,:]v=0 mod2 and v subset of Z(u)={y:(Q^T u)_y even}
        Z=((Q[u].sum(0))%2==0)
        idx=np.nonzero(Z)[0]
        if len(idx)==0: continue
        A=(Q[np.ix_(u,idx)]%2).astype(np.uint8)
        # random kernel vector of A over F2
        M=A.copy(); r=0; piv=[]
        rows,cols=M.shape
        for c in range(cols):
            p=next((i for i in range(r,rows) if M[i,c]),None)
            if p is None: continue
            M[[r,p]]=M[[p,r]]
            for i in np.nonzero(M[:,c])[0]:
                if i!=r: M[i]^=M[r]
            piv.append(c); r+=1
        free=[c for c in range(cols) if c not in piv]
        if not free: continue
        x=np.zeros(cols,dtype=np.uint8)
        for c in free: x[c]=rng.integers(2)
        for i,c in enumerate(piv): x[c]=(M[i,free].astype(int)@x[free].astype(int))%2
        v=np.zeros(n,bool); v[idx[x==1]]=True
        if v.sum()==0: continue
        S=Q[np.ix_(u,v)]
        assert (S.sum(0)%2==0).all() and (S.sum(1)%2==0).all()
        good+=1
        if S.sum()%4==2:
            bad+=1
            if ex is None or (u.sum()+v.sum())<ex[0]: ex=(u.sum()+v.sum(),np.nonzero(u)[0].tolist(),np.nonzero(v)[0].tolist())
    return good,bad,ex
for nm,P in (('halfspin',HS),('E7+A1',EA),('E7',E7)):
    g,b,ex=tau_search(P)
    print(nm,'even pairs tested',g,'tau=1 defects',b,'smallest ex',ex if ex is None else (ex[0],ex[1][:12],ex[2][:12]))
