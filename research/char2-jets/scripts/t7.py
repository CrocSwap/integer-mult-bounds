import sys, random, collections
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from cr2 import cfg_data; from gr import gr
random.seed(1)
for nm in ['tied_min.json','cex_min_1.json','gad.json','aff14.json','cex_joint_v7.json']:
    P,Q=load_cfg(nm); v=len(P); R,A,free=setup(P,Q); pi,sig=cfg_data(P,Q)
    c=collections.Counter()
    for dens in (0.1,0.3,0.6,1.0):
        for _ in range(100):
            g=sum(1<<i for i in range(len(free)) if random.random()<dens); B=tomat(g,free,v)
            c[(dens, gr(B,pi,sig)-v)]+=1
    print(nm, v, sorted(c.items()))
