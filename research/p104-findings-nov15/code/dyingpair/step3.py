"""DYINGPAIR step 3 [N rs2]: L=6 nl=4. 'B' = nested control; 'dp' = pair entering stage 0 dying after 1; 'ds' = single. single thread."""
import os; os.environ['OMP_NUM_THREADS']='1'; os.environ['OPENBLAS_NUM_THREADS']='1'; os.environ['VECLIB_MAXIMUM_THREADS']='1'
import sys, time; sys.path.insert(0,'.')
import numpy as np
from rs2 import Model, run
from lay import build, B
name=sys.argv[1]; starts=int(sys.argv[2]); seed=int(sys.argv[3]) if len(sys.argv)>3 else 7; L=6; nl=4
ms=[set(m) for m in B(L,nl)]
if name in ('dp','ds','dpx','dsx'):
    c=2 if name.startswith('dp') else 1
    for _ in range(c): ms.remove(set(range(0,nl))); ms.append({0,1})
    if name.endswith('x'): ms.append({1})
n,o,th=build(ms,L,nl); m=Model(n,o,-0.5,())
print(name,'Z',[sum(1 for s in ms if k in s) for k in range(L)],'n',n,'thin',th,'dim',m.dim,flush=True)
for i in range(starts):
    t0=time.time(); h,b,z=run(m,1,seed=seed*1000+i,nfev=1500)
    print('start %d solved %d best %.1e (%.0fs)'%(i,h,b,time.time()-t0),flush=True)
    if h: np.save('sol_%s_%d.npy'%(name,i),z)
