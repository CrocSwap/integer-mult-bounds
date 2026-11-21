from qzdrive import *
import time
A=set(range(4))
tests=[
 ('reset 2,2,6,6', [A,A,{2,3},{2,3},{2,3},{2,3}], [{2}]*4+[{3}]*4, (0,1,2,3)),
 ('chain 2,4,6,6', [A,A,{1,2,3},{1,2,3},{2,3},{2,3}], [{1}]*2+[{2}]*4+[{3}]*4, (0,1,2,3)),
]
for name,masks,pieces,order in tests:
    pos={t:i+1 for i,t in enumerate(order)}
    place={i:pos[min(S)] for i,S in enumerate(pieces)}
    d=make_design(6,4,masks,pieces,order,place)
    t0=time.time(); ok,z,S,nr=try_design(d,tries=6)
    print(name,'chat %.3f'%chat(d),ok,'%.2e'%nr,'%.0fs'%(time.time()-t0),flush=True)
    if ok: print('  ab',np.round(d.unpack(z)[2],3).tolist())
