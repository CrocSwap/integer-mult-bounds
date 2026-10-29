# D(w-multiset): which parabolic subsets J (rank<=7) of E8 simple roots have Phi\Phi_J coverable by flats of dims w
import sys,os,itertools,json,time
sys.path.insert(0,'../SC-B2'); os.chdir('../SC-B2')
from cov3 import *
ws=sorted(map(int,sys.argv[1].split(',')),reverse=True); out=sys.argv[2]
cap=sum(g[w] for w in ws)
f=open(out,'a')
seen={}
for r in range(7,-1,-1):
    for J in itertools.combinations(range(8),r):
        P_=frozenset(parabolic(J)); T=[t for t in range(n) if t not in P_]
        if len(T)>cap: continue
        key=frozenset(P_)
        t0=time.time(); res=cover_set3(T,ws)
        f.write(json.dumps(dict(w=ws,J=list(J),psi=len(P_),res=res,t=round(time.time()-t0,1)))+"\n"); f.flush()
