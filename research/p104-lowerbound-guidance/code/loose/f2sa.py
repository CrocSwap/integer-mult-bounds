"""F2-REL: rows f in F2^8\\0 with port sets D_f; port t needs cbar_t in span{f : t in D_f}.
price_f = rank{h_t : t in D_f} (f not in Zbar16), = dim(span h_D + h_z) - 1 (f = zbar). SA over per-port recipes."""
import sys,random,math,pickle
sys.path.insert(0,'.')
from lcore2 import *
cb=[int(sum(int(Cb[t,i])<<i for i in range(8))) for t in range(n)]
zb=[int(sum(int(Zb[k,i])<<i for i in range(8))) for k in range(16)]
hz={zb[k]:int(sum(int(v)<<i for i,v in enumerate([1]+list(Zb[k])))) for k in range(16)}
def ins(B,x):
    for b in B: x=min(x,x^b)
    if x: B.append(x); return True
    return False
def rk(xs):
    B=[]
    for x in xs: ins(B,x)
    return len(B)
def price_f(f,D):
    if not D: return 0
    if f in hz: return rk([hint[t] for t in D]+[hz[f]])-1
    return rk([hint[t] for t in D])
def indep(fs):
    return rk(fs)==len(fs)
def run(seed,steps,T0,T1,init=None,disc=True):
    rnd=random.Random(seed)
    rec=init if init else [[cb[t]] for t in range(n)]
    D={}
    for t in range(n):
        for f in rec[t]: D.setdefault(f,set()).add(t)
    pr={f:price_f(f,D[f]) for f in D}; cur=sum(pr.values()); best=cur; bestrec=[list(r) for r in rec]
    for it in range(steps):
        T=T0*(T1/T0)**(it/steps)
        t=rnd.randrange(n)
        s=rnd.choice([1,2,2,3,3,3,4,4,5])
        act=[f for f in D if D[f]]
        fs=[]
        for _ in range(s-1):
            fs.append(rnd.choice(act) if act and rnd.random()<0.9 else rnd.randrange(1,256))
        last=cb[t]
        for f in fs: last^=f
        if last==0: continue
        fs.append(last)
        if not indep(fs): continue
        old=rec[t]; new=fs
        if set(old)==set(new): continue
        ch=set(old)^set(new); delta=0; newp={}
        for f in ch:
            Df=set(D.get(f,set()))
            if f in old: Df.discard(t)
            else: Df.add(t)
            p=price_f(f,Df); newp[f]=(p,Df); delta+=p-pr.get(f,0)
        if delta<=0 or rnd.random()<math.exp(-delta/T):
            rec[t]=new
            for f,(p,Df) in newp.items(): D[f]=Df; pr[f]=p
            cur+=delta
            if cur<best: best=cur; bestrec=[list(r) for r in rec]
    return best,bestrec
if __name__=='__main__':
    seed=int(sys.argv[1]); steps=int(sys.argv[2])
    b,rec=run(seed,steps,float(sys.argv[3]) if len(sys.argv)>3 else 2.0,0.05)
    # recompute exactly
    D={}
    for t in range(n):
        assert rk(rec[t])==len(rec[t]); x=0
        for f in rec[t]: x^=f
        assert x==cb[t]
        for f in rec[t]: D.setdefault(f,set()).add(t)
    tot=sum(price_f(f,D[f]) for f in D)
    print('seed',seed,'best',b,'recheck',tot,'rows',sorted((price_f(f,D[f]),len(D[f]),f in hz) for f in D if D[f])[::-1][:20],flush=True)
    pickle.dump(rec,open(f'f2sa_{seed}.pkl','wb'))
