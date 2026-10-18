# tied_min sub-configurations: full-pattern CR2 status; for non-CR2 ones with f<=28, is some minimiser CR2?
import sys, itertools, collections
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
import kit; kit.BIN=os.environ.get('TTD_BIN') or PKG+'/c/bin'
from kit import *; from cr2 import *
P0,Q0 = load_cfg('tied_min.json'); v0=len(P0)
def iscr2(pi,sig,E,ks=(1,2,3)):
    for k in ks:
        r = realise(pi,sig,set(E),k=k,limit=2*10**5)
        if isinstance(r,dict): return k
    return 0
stat=collections.Counter(); minimal=[]; nonlist=[]
noncr2=set()
for m in range(1,v0+1):
  for S in itertools.combinations(range(v0),m):
    if any(set(T)<=set(S) for T in minimal): 
        noncr2.add(S); stat[(m,'non(sup)')]+=1; continue
    P=[P0[i] for i in S]; Q=[Q0[i] for i in S]; R,A,free=setup(P,Q); pi,sig=cfg_data(P,Q)
    k=iscr2(pi,sig,free)
    if k: stat[(m,'cr2')]+=1
    else:
        stat[(m,'non')]+=1; minimal.append(S); noncr2.add(S)
print(sorted(stat.items()))
print('minimal non-CR2 subsets:', minimal)
import json; json.dump(sorted(noncr2), open('tm_noncr2.json','w'))
