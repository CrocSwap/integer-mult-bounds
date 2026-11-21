from qzdrive import *
import time
A=set(range(4))
masks,pieces,order=[A,A,{1,2,3},{1,2,3},{2,3},{2,3}], [{1}]*2+[{2}]*4+[{3}]*4, (0,1,2,3)
pos={t:i+1 for i,t in enumerate(order)}
place={i:pos[min(S)] for i,S in enumerate(pieces)}
d=make_design(6,4,masks,pieces,order,place)
for sd in range(1,4):
    t0=time.time(); ok,z,S,nr=try_design(d,tries=8,seed=sd)
    print('chain k4 seed',sd,ok,'%.2e'%nr,'%.0fs'%(time.time()-t0),flush=True)
    if ok: break
