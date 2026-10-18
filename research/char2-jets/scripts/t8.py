import sys, random, collections
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
import kit; kit.BIN=os.environ.get('TTD_BIN') or PKG+'/c/bin'
from kit import *; from cr2 import cfg_data, realise; from gr import gr; from gen import randcfg
seed=int(sys.argv[1]); N=int(sys.argv[2]); random.seed(seed)
stat=collections.Counter(); found=0
for it in range(N):
    v=random.randint(6,10); P,Q=randcfg(v, R=random.choice([1,1,2]))
    R_,A_,free=setup(P,Q)
    if len(free)>22 or len(free)<4: continue
    pi,sig=cfg_data(P,Q)
    best,ms=enum_raw(v,R_,A_,free,2)
    fullcr2 = isinstance(realise(pi,sig,set(free),k=1,limit=10**5),dict) or isinstance(realise(pi,sig,set(free),k=2,limit=10**5),dict)
    stat[('cfg', best-v, 'fullCR2' if fullcr2 else 'NONCR2')]+=1
    for c,g in ms:
        B=tomat(g,free,v); r=gr(B,pi,sig,trials=4)
        if r<v:
            stat['GR<v']+=1
            if found<5: print('GR<v', c, v, P, Q, g, flush=True); found+=1
        else: stat['GR=v']+=1
print(seed, sorted(stat.items(), key=str))
