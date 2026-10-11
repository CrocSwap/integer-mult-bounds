"""like hx.py but objective = nine-stage saving estimate of the REUSED word (eumemic's search objective), i.e. what the pipeline really keeps."""
import os,sys,pickle,time,random
from collections import Counter
os.environ['E8COORD']='ham'
sys.path.insert(0,'../reg/code/reuse')
import hx, fullword, reuse as RU
from hx import Fm
def local_hist(w):
    fd=[Fm.closure(sum(1<<s for s in f))[1] if f else 0 for f in w['frames']]
    cur=list(w['start']); H=Counter()
    def climb(r,f):
        if cur[r]!=f: H[fd[f]-fd[cur[r]]]+=1; cur[r]=f
    for ph in ('D','A'):
        for f,d,s in w[ph]:
            for x in [d]+s: climb(x,f)
    for q in w['ret']: H[fd[cur[q]]]+=1
    for ph in ('B','C'):
        for f,d,s in w[ph]:
            for x in [d]+s: climb(x,f)
    for r in range(len(cur)): climb(r,w['final'][r])
    return H
def nine(w):
    v,R=w['v'],w['R']; m,W=64,64*v+9*R
    prof=Counter({r:72*n for r,n in local_hist(w).items()})
    for r,n in ((7,48*v),(14,32*v),(28,32*v),(42,32*v)): prof[r]+=n
    lo,hi=0.0,0.05
    for _ in range(100):
        s=(lo+hi)/2
        if sum(n*(r/m)**(1-s) for r,n in prof.items())<W: lo=s
        else: hi=s
    return lo
def score(h):
    W=hx.C2.compile2(h)
    w,_=RU.reuse(fullword.build(W))
    return nine(w),w['R'],W.nh
class S2(hx.Search):
    def __init__(self,*a,**k):
        super().__init__(*a,**k)
        self.s9,self.Rr,self.Rraw=score(self.h)
    def step(self,temp=0.0):
        t=self.rng.choice(self.targets)
        new=self.propose(t)
        if new is None: return False
        old_need=self.h.need[t]
        try: nn=hx.need_of(self.h,new)
        except Exception: return False
        self.h.need[t]=nn
        x=0
        for u in nn: x^=self.h.content[u]
        if x!=Fm.HYP[t]: self.h.need[t]=old_need; return False
        try: s9,Rr,Rraw=score(self.h)
        except (AssertionError,KeyError,IndexError): self.h.need[t]=old_need; return False
        if s9>=self.s9-1e-12:
            self.s9,self.Rr,self.Rraw=s9,Rr,Rraw; self.plans[t]=new; return True
        self.h.need[t]=old_need; return False
if __name__=='__main__':
    seed=int(sys.argv[1]); iters=int(sys.argv[2]); mode=sys.argv[3]; out=sys.argv[4]
    h,atoms=hx.load(); plans=hx.default_plans(atoms)
    S=S2(h,atoms,plans,seed,cancel=(mode=='cancel'))
    print('start s9 %.6e Rreused %d Rraw %d'%(S.s9,S.Rr,S.Rraw),flush=True)
    t0=time.time(); best=S.s9; acc=0
    for it in range(iters):
        acc+=S.step()
        if S.s9>best+1e-12:
            best=S.s9; pickle.dump(S.plans,open(out,'wb')); pickle.dump(S.h,open(out+'.h','wb'))
            print(it,'s9 %.6e Rreused %d Rraw %d acc %d %.0fs'%(S.s9,S.Rr,S.Rraw,acc,time.time()-t0),flush=True)
        if it%1000==0: print('it',it,'s9 %.6e R %d acc %d %.0fs'%(S.s9,S.Rr,acc,time.time()-t0),flush=True)
    pickle.dump(S.h,open(out+'.final.h','wb')); print('final %.6e %d'%(S.s9,S.Rr))
