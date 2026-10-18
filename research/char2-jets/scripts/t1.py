import sys, time
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from satlib import enumerate_B
from cr2 import *
P,Q = load_cfg('tied_min.json'); R,A,free = setup(P,Q); pi,sig = cfg_data(P,Q)
print('free', len(free))
for k in (1,2,3,4):
    t=time.time(); r = realise(pi,sig,set(free),k=k); print('full pattern GF(2^%d):'%k, 'REAL' if isinstance(r,dict) else r, round(time.time()-t,1))
opt = enumerate_B(P,Q,(4,4,4)); print(len(opt))
res={}
for ent in opt:
    r = None
    for k in (1,2,3):
        r = realise(pi,sig,set(ent),k=k)
        if isinstance(r,dict): break
    res.setdefault((len(ent), 'REAL k=%d'%k if isinstance(r,dict) else str(r)),0)
    res[(len(ent), 'REAL k=%d'%k if isinstance(r,dict) else str(r))]+=1
print(res)
