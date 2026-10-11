"""plan SA (all 120 targets, frame targets biased) from a snapshot; objective s9 of reused word."""
import os,sys,pickle,time,random
os.environ['E8COORD']='ham'
import hx, hx2, ham1, ham2x
from hx import Fm
seed=int(sys.argv[1]); iters=int(sys.argv[2]); snap=sys.argv[3]; out=sys.argv[4]; pfr=float(sys.argv[5]) if len(sys.argv)>5 else 0.6
h0,atoms=hx.load(); plans=hx.default_plans(atoms)
for t,sp in ham2x.FSPEC.items(): plans[t]=[list(s) for s in sp]
h=pickle.load(open(snap,'rb'))
class S3(hx2.S2):
    def step(self,temp=0.0):
        fr=[t for t in self.targets if t in ham2x.FSPEC]
        if self.rng.random()<pfr: t=self.rng.choice(fr)
        else: t=self.rng.choice(self.targets)
        new=self.propose(t)
        if new is None: return False
        old_need=self.h.need[t]
        try: nn=hx.need_of(self.h,new)
        except Exception: return False
        self.h.need[t]=nn
        x=0
        for u in nn: x^=self.h.content[u]
        if x!=Fm.HYP[t]: self.h.need[t]=old_need; return False
        try: s9,Rr,Rraw=hx2.score(self.h)
        except (AssertionError,KeyError,IndexError): self.h.need[t]=old_need; return False
        if s9>=self.s9-1e-12:
            self.s9,self.Rr,self.Rraw=s9,Rr,Rraw; self.plans[t]=new; return True
        self.h.need[t]=old_need; return False
S=S3(h,atoms,plans,seed,cancel=True)
print('start s9 %.6e Rreused %d Rraw %d'%(S.s9,S.Rr,S.Rraw),flush=True)
t0=time.time(); best=S.s9; acc=0
for it in range(iters):
    acc+=S.step()
    if S.s9>best+1e-12:
        best=S.s9; pickle.dump(S.h,open(out,'wb'))
        print(it,'s9 %.6e Rreused %d Rraw %d acc %d %.0fs'%(S.s9,S.Rr,S.Rraw,acc,time.time()-t0),flush=True)
    if it%2000==0: print('it',it,'s9 %.6e R %d acc %d %.0fs'%(S.s9,S.Rr,acc,time.time()-t0),flush=True)
print('final %.6e %d'%(S.s9,S.Rr))
