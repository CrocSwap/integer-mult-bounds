import sys, time, os, subprocess
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
import kit
kit.BIN = os.environ.get('TTD_BIN') or PKG+'/c/bin'
from kit import *
from cr2 import *
def cr2(pi,sig,ent):
    for k in (1,2,3):
        r = realise(pi,sig,set(ent),k=k,limit=2*10**5)
        if isinstance(r,dict): return k
    return 0 if r is None else -1
names = sys.argv[1:]
for nm in names:
    P,Q = load_cfg(nm); v=len(P)
    best, ms, R, A, free = enum(P,Q,1)
    pi,sig = cfg_data(P,Q)
    out={}
    for c,g in ms:
        ent=[free[i] for i in range(len(free)) if g>>i&1]
        key=(c, cr2(pi,sig,ent)); out[key]=out.get(key,0)+1
    print(nm, 'v',v,'f',len(free),'best',best, {k:out[k] for k in sorted(out)})
