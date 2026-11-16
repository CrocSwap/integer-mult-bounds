import sys,os,time
sys.path.insert(0,'../SC-B2'); os.chdir('../SC-B2')
from cov4 import *
gens=load_gens('grp.out'); print(len(gens))
P=frozenset(parabolic((0,1,2,3,4,5))); T=[t for t in range(n) if t not in P]; print(len(T))
for comp in ([6,6,5,5,5,4],[6,6,5,5,5,5],[6,6,5,5,5,4,1]):
    t=time.time(); r=cover_set4(T,comp,gens,verbose=True,tmo=900); print(comp,r,round(time.time()-t,1),flush=True)
