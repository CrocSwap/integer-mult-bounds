# End-to-end check of Lemma CR2: build realisation, check supports, incidences, diagonal; then for random admissible B
# compute N = sum_j D(p~_j) B D(q~_j) over GF(2^k) and check it is diagonal with nonzero diagonal.
import sys, random
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from cr2 import *
for nm,k in [('cex_min_1.json',2),('cex_joint_v7.json',1),('gad.json',1),('aff14.json',1)]:
    P,Q=load_cfg(nm); v=len(P); R,A,free=setup(P,Q); pi,sig=cfg_data(P,Q)
    r=realise(pi,sig,set(free),k=k); F=GF(k)
    Pt=[r[('p',t)] for t in range(v)]; Qt=[r[('l',s)] for s in range(v)]
    assert all(all(Pt[t][j]==0 for j in range(3) if j not in pi[t]) for t in range(v))
    assert all(all(Qt[t][j]==0 for j in range(3) if j not in sig[t]) for t in range(v))
    for trial in range(200):
        g=random.getrandbits(len(free)); B=tomat(g,free,v)
        N=[[0]*v for _ in range(v)]
        for j in range(3):
            for t in range(v):
                for s in range(v):
                    if B[t][s]: N[t][s]^=F.mul[F.mul[Pt[t][j]][Qt[s][j]]][1]
        assert all((N[t][s]==0)==(t!=s) for t in range(v) for s in range(v)), (nm,trial)
        assert sum(blockranks(B,R,A))>=v
    print(nm,'OK: N diagonal nonzero for 200 random B; cost>=v on each')
