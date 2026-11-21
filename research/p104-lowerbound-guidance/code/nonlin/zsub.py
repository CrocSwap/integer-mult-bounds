"""SA over row subspaces U_z (tight B-linear class, rows Z16). Port t may use row z iff h_t in U_z.
objective = sum_z price(P cap U_z, S_z) + lam * #ports with no feasible support inside allowed rows."""
from ncore import *
import random,math,sys,functools
FE=np.load('zfeas.npy'); m=16
hint=np.array([int(sum(int(H[t,i])<<i for i in range(9))) for t in range(n)])
Sz=[np.nonzero((C@(G@Z[k]))%4)[0] for k in range(m)]
par=np.array([[bin(a&b).count('1')&1 for b in range(512)] for a in range(512)],np.uint8) # dot
def ports_in(funcs):
    ok=np.ones(n,bool)
    for f in funcs: ok&= par[f][hint]==0
    return np.nonzero(ok)[0]
@functools.lru_cache(maxsize=None)
def pr(k,ports):
    D=list(ports)
    if not D: return 0
    return f2rank(Q[np.ix_(D,Sz[k])])
def evaluate(U,lam):
    allowed=np.zeros(n,np.int64); c=0
    for k in range(m):
        P=ports_in(U[k]); c+=pr(k,tuple(P)); allowed[P]|=(1<<k)
    bad=int((~FE[np.arange(n),allowed]).sum())
    return c+lam*bad,c,bad
def run(seed,steps,lam=4.0,T0=4.0,T1=0.1,init=None):
    random.seed(seed)
    U=init if init else [[random.randrange(1,512) for _ in range(random.randrange(0,3))] for k in range(m)]
    cur,c,b=evaluate(U,lam); best=(1e9,None)
    for it in range(steps):
        T=T0*(T1/T0)**(it/steps)
        k=random.randrange(m); V=list(U[k]); r=random.random()
        if r<0.4 and len(V)<9: V.append(random.randrange(1,512))
        elif r<0.7 and V: V.pop(random.randrange(len(V)))
        elif V: V[random.randrange(len(V))]=random.randrange(1,512)
        else: V=[random.randrange(1,512)]
        U2=list(U); U2[k]=V
        new,c2,b2=evaluate(U2,lam)
        if new<=cur or random.random()<math.exp(-(new-cur)/T):
            U,cur,c,b=U2,new,c2,b2
            if b==0 and c<best[0]: best=(c,[list(x) for x in U])
    return best
if __name__=='__main__':
    seed=int(sys.argv[1]); steps=int(sys.argv[2])
    b=run(seed,steps)
    print('seed',seed,'best feasible cost',b[0],flush=True)
    if b[1]:
        import pickle; pickle.dump(b[1],open(f'zsub_{seed}.pkl','wb'))
        print([pr(k,tuple(ports_in(b[1][k]))) for k in range(m)])
