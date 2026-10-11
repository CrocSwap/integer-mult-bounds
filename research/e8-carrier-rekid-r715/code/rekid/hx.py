"""Target-level plan search with F2 cancellation moves. plans[t] = list of specs; spec = ordered list of atom ids (symbols or sources);
need[t] = {sym(spec)} with parity dedup; XOR content must equal HYP[t]."""
import os,sys,json,ast,random,time,pickle
from collections import Counter
os.environ['E8COORD']='ham'
import ham2x as H2, c2x as C2, compile as C, frames as Fm, e8lib as E, ham1
V=120
def load(pfile='params-r740.json'):
    Pd={ast.literal_eval(k):v for k,v in json.load(open(pfile))}
    H2.P.clear(); H2.P.update(Pd)
    h=H2.build(0,True)
    atoms={t:dict(a) for t,a in H2.ATOMS.items()}
    return h,atoms
def default_plans(atoms):
    plans={}
    for t,A in atoms.items():
        sp=[[A['D']],[A['p5']],[A['p6'],A['a'],A['b']]]
        fo=A['fo']
        if fo==0: sp+=[[A['q1'],A['q2'],A['d']],[A['r1'],A['r2']]]
        elif fo==1: sp+=[[A['q1'],A['q2']],[A['r1'],A['r2'],A['d']]]
        else: sp+=[[A['q1'],A['q2']],[A['r1'],A['r2']],[A['d']]]
        plans[t]=sp
    return plans
def need_of(h,spec_list):
    cnt=Counter()
    for sp in spec_list:
        if sp: cnt[h.sym(list(sp))]+=1
    return set(u for u,c in cnt.items() if c%2==1)
def check_target(h,t):
    x=0
    for u in h.need[t]: x^=h.content[u]
    return x==Fm.HYP[t]
def R_of(h):
    W=C2.compile2(h)
    return W.nh,W
class Search:
    def __init__(self,h,atoms,plans,seed,cancel=True,pool_mode='all'):
        self.h=h; self.atoms=atoms; self.plans=plans; self.rng=random.Random(seed); self.cancel=cancel
        self.targets=sorted(plans)
        self.pool={}
        N0=len(h.content)
        for t in self.targets:
            pl=[u for u in range(V,N0) if Fm.inside(h.frame[u],Fm.HYP[t])]
            src=[s for s in range(V) if Fm.HYP[t]>>s&1]
            self.pool[t]=(pl,src)
        for t in self.targets:
            h.need[t]=need_of(h,plans[t]); assert check_target(h,t),t
        self.R,_=R_of(h)
    def propose(self,t):
        rng=self.rng; sp=[list(s) for s in self.plans[t]]
        r=rng.random()
        pl,src=self.pool[t]
        allatoms=[x for s in sp for x in s]
        if r<0.55:
            # toggle atom into two specs (i,j); j may be new
            if self.cancel and rng.random()<0.5:
                x=rng.choice(pl) if rng.random()<0.8 else rng.choice(src)
            else:
                x=rng.choice(allatoms)
            i=rng.randrange(len(sp)); 
            j=rng.randrange(len(sp)+1)
            if j==i: return None
            if j==len(sp): sp.append([])
            for k in (i,j):
                if x in sp[k]: sp[k].remove(x)
                else: sp[k].insert(rng.randrange(len(sp[k])+1),x)
        elif r<0.7:
            if len(sp)<2: return None
            i,j=rng.sample(range(len(sp)),2)
            m=sp[i]+sp[j]; c=Counter(m)
            m=[x for x in dict.fromkeys(m) if c[x]%2==1]
            sp=[s for k,s in enumerate(sp) if k not in (i,j)]+[m]
        elif r<0.85:
            i=rng.randrange(len(sp))
            if len(sp[i])<2: return None
            k=rng.randrange(1,len(sp[i])); a,b=sp[i][:k],sp[i][k:]
            sp[i]=a; sp.append(b)
        else:
            i=rng.randrange(len(sp))
            if len(sp[i])<2: return None
            a,b=rng.sample(range(len(sp[i])),2); sp[i][a],sp[i][b]=sp[i][b],sp[i][a]
        sp=[s for s in sp if s]
        return sp
    def step(self,temp=0.0):
        t=self.rng.choice(self.targets)
        new=self.propose(t)
        if new is None: return False
        old_plan=self.plans[t]; old_need=self.h.need[t]
        try:
            nn=need_of(self.h,new)
        except Exception as e:
            return False
        self.h.need[t]=nn
        x=0
        for u in nn: x^=self.h.content[u]
        if x!=Fm.HYP[t]:
            self.h.need[t]=old_need; return False
        R,_=R_of(self.h)
        if R<=self.R or (temp>0 and self.rng.random()<temp**(R-self.R)):
            self.R=R; self.plans[t]=new; return True
        self.h.need[t]=old_need; return False
if __name__=='__main__':
    seed=int(sys.argv[1]); iters=int(sys.argv[2]); mode=sys.argv[3]; out=sys.argv[4]
    pfile=sys.argv[5] if len(sys.argv)>5 else 'params-r740.json'
    h,atoms=load(pfile); plans=default_plans(atoms)
    S=Search(h,atoms,plans,seed,cancel=(mode=='cancel'))
    print('start R',S.R,flush=True)
    t0=time.time(); best=S.R; acc=0
    for it in range(iters):
        ok=S.step(temp=0.0 if mode!='anneal' else 0.02)
        acc+=ok
        if S.R<best:
            best=S.R; pickle.dump(S.plans,open(out,'wb')); pickle.dump(S.h,open(out+'.h','wb')); print(it,'R',best,'acc',acc,'%.0fs'%(time.time()-t0),flush=True)
        if it%5000==0: print('it',it,'R',S.R,'acc',acc,'%.0fs'%(time.time()-t0),flush=True)
    pickle.dump(S.plans,open(out+'.final','wb')); print('final',S.R,best)
