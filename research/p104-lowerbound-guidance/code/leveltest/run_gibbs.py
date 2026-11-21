import numpy as np,sys,collections
from lt import *
seed=int(sys.argv[1]); steps=int(sys.argv[2]); mode=sys.argv[3]; extra=int(sys.argv[4]); every=int(sys.argv[5])
rng=np.random.default_rng(seed); NB='../'
n=104
def f2solve(A,c):
    A=A%2; c=c%2; r,m=A.shape; M=np.concatenate([A,c[:,None]],1).astype(np.int64); piv=[]; row=0
    for col in range(m):
        p=next((i for i in range(row,r) if M[i,col]),None)
        if p is None: continue
        M[[row,p]]=M[[p,row]]
        for i in range(r):
            if i!=row and M[i,col]: M[i]^=M[row]
        piv.append(col); row+=1
    if M[row:,m].any(): return None
    free=[j for j in range(m) if j not in piv]; x=np.zeros(m,np.int64)
    x[free]=rng.integers(0,2,len(free))
    for i,col in enumerate(piv): x[col]=(M[i,m]+M[i,free]@x[free])%2
    return x
def kernel_f2(A):
    A=A%2; r,m=A.shape; M=A.copy().astype(np.int64); piv=[]; row=0
    for col in range(m):
        p=next((i for i in range(row,r) if M[i,col]),None)
        if p is None: continue
        M[[row,p]]=M[[p,row]]
        for i in range(r):
            if i!=row and M[i,col]: M[i]^=M[row]
        piv.append(col); row+=1
    free=[j for j in range(m) if j not in piv]; out=[]
    for f in free:
        x=np.zeros(m,np.int64); x[f]=1
        for i,col in enumerate(piv): x[col]=M[i,f]
        out.append(x)
    return out
def resample(W,V,t,side):
    if side=='V': V,W=W,V
    P=np.nonzero(Q104[t])[0]; A=V[P]%4; c=np.array([2 if p==t else 0 for p in P])
    K=kernel_f2(A); w0=np.zeros(A.shape[1],np.int64)
    for kv in K:
        if rng.random()<0.5: w0=(w0+kv)%2
    w1=f2solve(A,((c-A@w0)%4)//2)
    if w1 is not None: W=W.copy(); W[t]=(w0+2*w1)%4
    if side=='V': W,V=V,W
    return W,V
def check(W,V): return not ((((W@V.T)-2*np.eye(n,dtype=np.int64))%4)*Q104).any()
if mode=='e8':
    W=np.load(NB+'orbitlp/e8W.npy')%4; V=np.load(NB+'orbitlp/e8V.npy')%4
    W=np.concatenate([W,np.zeros((n,extra),np.int64)],1); V=np.concatenate([V,np.zeros((n,extra),np.int64)],1)
else:
    from run_all_inv import inv4
    W0=C104%4; V0=(C104@Gb)%4; m=extra
    while True:
        Xm=rng.integers(0,4,(8,m)); Pi=inv4(Xm[:,:8])
        if Pi is not None: break
    Ym=np.zeros((8,m),dtype=np.int64); Ym[:,:8]=Pi.T; W=(W0@Xm)%4; V=(V0@Ym)%4
best=None; rows=[]
for s in range(steps+1):
    if s%every==0:
        assert check(W,V)
        r=evaluate(Q104,W,V,rng,nrand=3)
        for o in ('fwd','mir'):
            x=r[o]; rows.append((s,o,x['D'],x['S'],x['f2']))
            assert x['S']<=x['D']
            if x['S']<56: print('S<56 !!',s,o,x,flush=True); np.save('cexS_W_%s%d_%d.npy'%(mode,seed,s),W); np.save('cexS_V_%s%d_%d.npy'%(mode,seed,s),V)
        print(mode,seed,s,'fwd D/S/f2',r['fwd']['D'],r['fwd']['S'],r['fwd']['f2'],'mir',r['mir']['D'],r['mir']['S'],r['mir']['f2'],flush=True)
    t=int(rng.integers(n)); W,V=resample(W,V,t,'W' if rng.random()<0.5 else 'V')
print('SUMMARY',mode,seed,'minS',min(r[3] for r in rows),'min f2',min(r[4] for r in rows),'minD',min(r[2] for r in rows),'maxD',max(r[2] for r in rows))
