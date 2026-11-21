"""SA over tight B-linear decoders (rows Z16). cost = sum_z price(D_z,S_z)."""
from ncore import *
import pickle,random,sys,math
F=pickle.load(open('ztight_F.pkl','rb')); m=16
hint=[int(sum(int(H[t,i])<<i for i in range(9))) for t in range(n)]
# normals of S_z spans
Sz=[np.nonzero((C@(G@Z[k]))%4)[0] for k in range(m)]
def vec2int(v): return int(sum(int(v[i])<<i for i in range(len(v))))
def basis_add(B,x):
    for b in B:
        x=min(x,x^b)
    if x: B.append(x); return True
    return False
def inspan(B,x):
    for b in sorted(B,reverse=True):
        x=min(x,x^b)
    return x==0
def red(B):  # make proper xor basis (sorted reduce)
    out=[]
    for x in B: basis_add(out,x)
    return out
nrm=[]
for k in range(m):
    Kr=kernel((H[Sz[k]]@Beta)%2)  # u with beta(u,h_s)=0 on S: that's H_S^perp (beta)
    nrm.append([vec2int(r) for r in Kr])
def price_set(D,k):
    B=[]
    for t in D: basis_add(B,hint[t])
    d=len(B); # price = dim H_D - dim(H_D cap H_S^perp)
    # H_S^perp spanned by nrm[k]; compute dim of intersection = dim H_D + dim N - dim(H_D+N)
    B2=list(B)
    for x in nrm[k]: basis_add(B2,x)
    inter=d+len(nrm[k])-len(B2)
    return d-inter
# verify price formula vs Q-rank
rng=np.random.default_rng(1)
for _ in range(30):
    k=rng.integers(m); D=list(rng.choice(n,rng.integers(1,30),replace=False))
    assert price_set(D,k)==f2rank(Q[np.ix_(D,Sz[k])]),'price mismatch'
def run(seed,steps,T0,T1,init):
    random.seed(seed)
    Kt=list(init)
    D=[set(t for t in range(n) if Kt[t]>>k&1) for k in range(m)]
    pr=[price_set(D[k],k) for k in range(m)]; cur=sum(pr); best=cur; bestK=list(Kt)
    for it in range(steps):
        T=T0*(T1/T0)**(it/steps)
        t=random.randrange(n); new=random.choice(F[t]); old=Kt[t]
        if new==old: continue
        ch=old^new; delta=0; newp={}
        for k in range(m):
            if ch>>k&1:
                Dk=D[k]-{t} if old>>k&1 else D[k]|{t}
                p=price_set(Dk,k); newp[k]=p; delta+=p-pr[k]
        if delta<=0 or random.random()<math.exp(-delta/T):
            Kt[t]=new
            for k in newp:
                if old>>k&1: D[k].discard(t)
                else: D[k].add(t)
                pr[k]=newp[k]
            cur+=delta
            if cur<best: best=cur; bestK=list(Kt)
    return best,bestK
if __name__=='__main__':
    seed=int(sys.argv[1]); steps=int(sys.argv[2])
    random.seed(seed)
    init=[random.choice(F[t]) for t in range(n)]
    b,K=run(seed,steps,3.0,0.05,init)
    D=[[t for t in range(n) if K[t]>>k&1] for k in range(m)]
    print('seed',seed,'best',b,'prices',[price_set(D[k],k) for k in range(m)],flush=True)
    pickle.dump(K,open(f'zsa_best_{seed}.pkl','wb'))
