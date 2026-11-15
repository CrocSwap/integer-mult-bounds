import sys,time
import numpy as np
from rs2 import *
from lay import build,B
def s(x): return {i for i,c in enumerate(x) if c=='1'}
LAY={'ilpmin':['1...','.1..','..1.','.11.','...1','1..1','1111','1111'],
 'srch':['1...','1...','.1..','..1.','111.','...1','...1','1..1','.1.1','..11','1111']}
if __name__=='__main__':
    name=sys.argv[1]; comm=int(sys.argv[2]); pos=int(sys.argv[3]); starts=int(sys.argv[4]); L=4
    ms=B(4,2) if name=='B' else [s(x) for x in LAY[name]]
    n=len(ms); Z=[[r for r,t in enumerate(ms) if k in t] for k in range(L)]; th=n+2-2*L
    o=[('S',Z[k]) for k in range(pos)]+[('T',)]*th+[('S',Z[k]) for k in range(pos,L)]
    m=Model(n,o,-0.5,()); m.comm=bool(comm); t0=time.time()
    h,b,z=run(m,starts,seed=5,nfev=1500)
    print('%s comm=%d pos=%d n=%d N=%d dim=%d solved %d/%d best %.1e (%.0fs)'%(name,comm,pos,n,m.N,m.dim,h,starts,b,time.time()-t0),flush=True)
    if h: np.save('sol_%s_%d_%d.npy'%(name,comm,pos),z)
