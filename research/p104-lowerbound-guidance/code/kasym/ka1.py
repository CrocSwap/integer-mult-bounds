"""KASYM ka1: dump optimal duals of cc1 LP (base+RC+RC2) by row family. usage: ka1.py k.."""
import os,sys,time
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
sys.path.insert(0,'code/callercut')
import cc1,cc2,numpy as np
for k in [int(a) for a in sys.argv[1:]]:
    t0=time.time();L=cc1.LP(k,list(range(3,k+1)));sup=cc2.solve_store(L);w,wx,we,y,wm=L.du
    print('k',k,'prim c^ %.4f'%(104*L.prim/k),'time %.0fs'%(time.time()-t0),'y %.5f wm %.5f'%(y,wm))
    names=['sep','e','ones']+['wit%d'%l for l in L.ells]+['coord%d'%th for th in range(2,k+1)]+['shal']+['pfix%d'%x for x in range(1,k)]+['%s%d'%(kd,a) for kd,a,b in L.rowsE]
    du=list(w)+list(wx)+list(we)
    for nm,v in zip(names,du):
        if abs(v)>1e-9:print('  %-8s %.6g'%(nm,v))
    print('  support',sup,flush=True)
