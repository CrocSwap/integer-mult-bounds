import time
from qzfast import *
d=Design(4,3,[{0,1},{0,1},{0,1,2},{0,1,2}],[('H',2),('H',0),('I',{0}),('I',{0}),('H',1),('I',{1}),('I',{1})],'C1')
print('chat',chat(d),'HP',HP(3))
S=Sys(d)
for sd in range(5):
    t0=time.time(); z=np.random.default_rng(sd).normal(size=d.nv)
    z,nr=lm(S,z,it=400)
    V,W,ab=d.unpack(z); print(sd,'%.2e'%nr,'ab',np.round(ab,3).tolist(),'%.1fs'%(time.time()-t0),flush=True)
