from qzdrive import *
import itertools, time
A=set(range(5))
masks=[A,A,{0,1,2},{0,1,2},{1,2},{1,2},{3,4},{3,4}]
pieces=[{0},{0},{1},{1},{1},{1},{2},{2},{2},{2},{3},{3},{4},{4}]
for order in [(0,1,2,3,4),(3,4,0,1,2),(1,2,0,3,4),(3,0,1,2,4),(0,3,1,4,2)]:
    pos={t:i+1 for i,t in enumerate(order)}
    place={i:pos[min(S)] for i,S in enumerate(pieces)}
    d=make_design(8,5,masks,pieces,order,place)
    t0=time.time(); ok,z,S,nr=try_design(d,tries=3)
    print(order,'chat %.3f'%chat(d),ok,'%.2e'%nr,'%.0fs'%(time.time()-t0),flush=True)
