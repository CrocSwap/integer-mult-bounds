import sys,os,time,json
import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,'..','g777'))
from cov2 import *
import cov as C
P=frozenset(C.parabolic((0,1,2,3,4,5))); T=[t for t in range(C.n) if t not in P]; print(len(T),flush=True)
for comp in sys.argv[1:]:
    ws=sorted(map(int,comp.split(',')),reverse=True); t=time.time()
    r=cover_set(T,ws); print(ws,r,round(time.time()-t,1),flush=True)
