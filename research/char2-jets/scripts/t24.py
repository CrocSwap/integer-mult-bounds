# configurations with a directed cycle of wild incidences: is the full pattern CR2 (order 0, any base)?
import sys, random, collections
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from cr2 import realise, cfg_data; from gen import randcfg
random.seed(4); st=collections.Counter()
def wildcyc(P,Q):
    v=len(P); adj={t:[s for s in range(v) if s!=t and all(P[t][j] and Q[s][j] for j in range(3)) and sum(P[t][j]*Q[s][j] for j in range(3))==0] for t in range(v)}
    col={}
    def dfs(u):
        col[u]=1
        for w in adj[u]:
            if col.get(w)==1 or (w not in col and dfs(w)): return True
        col[u]=2; return False
    return any(t not in col and dfs(t) for t in range(v))
n=0
while n<300:
    v=random.randint(6,12); P,Q=randcfg(v,R=random.choice([1,2,3]),pfix=0.0)
    if not wildcyc(P,Q): continue
    n+=1; R_,A_,free=setup(P,Q); pi,sig=cfg_data(P,Q); k=0
    for kk in (1,2,3):
        r=realise(pi,sig,set(free),k=kk,limit=2*10**5)
        if isinstance(r,dict): k=kk; break
        if r=='timeout': k=-1; break
    st[k]+=1
print('wild-cycle configs: CR2 field GF(2^k) ->', dict(st))
