"""SLACK t1 [N rs3]: L=4, left arm stages 0,1,2 (centre 2), right arm stage 3.  Lone role e on [0,1] (dies before the centre).
Rows: ctl = nested B(3+1); e = + lone role; eL01 = + 1 line over [0,1] on Z0 cap Z1 (incl e: cap |S|-4 = 1, allowed);
TEST r01 = + 1 line over [0,1] supported on Z_0 \\ e (needs rank(Y0,Y1|Z0\\e) <= 3 AND X-side);  TEST r02 = 1 line over [0,2] on Z_0\\e."""
import os; os.environ['OMP_NUM_THREADS']='1'; os.environ['OPENBLAS_NUM_THREADS']='1'; os.environ['VECLIB_MAXIMUM_THREADS']='1'
import sys, time; sys.path.insert(0,'.')
import numpy as np
from rs3 import Model, run
L=4; nl=int(os.environ.get("NL","3"))
def masks(e=True):
    ms=[set(range(L))]*2 + [set(range(k,nl)) for k in range(nl) for _ in range(2)] + [set(range(nl,k+1)) for k in range(L-1,nl-1,-1) for _ in range(2)]
    if e: ms=ms+[{0,1}]
    return ms
def build(ms):
    n=len(ms); Z=[[r for r,s in enumerate(ms) if k in s] for k in range(L)]; th=n+2-2*L
    return n,[('S',Z[k]) for k in range(nl)]+[('T',)]*th+[('S',Z[k]) for k in range(nl,L)],Z
row=sys.argv[1]; starts=int(sys.argv[2]); nfev=int(sys.argv[3]) if len(sys.argv)>3 else 1500
ms=masks(row!='ctl'); n,o,Z=build(ms); e=n-1
B0=[r for r in Z[0] if r!=e]
lines={'ctl':(),'e':(),'eL01':(((0,1),1,None),),'r01':(((0,1),1,B0),),'r02':(((0,1,2),1,B0),),'r12':(((1,2),1,None),),'r01x':(((0,1),2,B0),)}[row]
m=Model(n,o,-0.5,lines)
print(row,'n',n,'Z',[len(z) for z in Z],'dim',m.dim,flush=True)
t0=time.time(); hits=0
for i in range(starts):
    h,b,z=run(m,1,seed=1000+i,nfev=nfev); hits+=h
    print('  start %d solved %d best %.1e (%.0fs)'%(i,h,b,time.time()-t0),flush=True)
    if h: np.save('sol_%s_%d.npy'%(row,i),z)
print(row,'solved',hits,'/',starts)
