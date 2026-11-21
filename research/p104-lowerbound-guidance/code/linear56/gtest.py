"""LINEAR56 gtest.py: test dim G_Omega >= dim Omega, G = span{ u_a * omega(.,p_a) : a in rows, omega in Omega }, u_a = B(q_a,.).
mode 'gen': random decompositions (any m); mode 'sub': 8 rows q-basis, p-basis, M invertible (not dual)."""
import sys, numpy as np, itertools
from lcore import *
from relax import poly_of_product
from quadtr import decomp
rng=np.random.default_rng(int(sys.argv[1])); mode=sys.argv[2]
PAIRS=list(itertools.combinations(range(8),2))
def omega_mat(v):
    W=np.zeros((8,8),np.int64)
    for x,(i,j) in zip(v,PAIRS): W[i,j]=W[j,i]=x
    return W
worst=99
for it in range(int(sys.argv[3])):
    if mode=='gen': rows=decomp(8+int(rng.integers(0,9)),rng)
    else:
        while True:
            Qm=rng.integers(0,2,(8,8)); Pm=rng.integers(0,2,(8,8))
            if f2rank(Qm)==8 and f2rank(Pm)==8 and f2rank((Qm.T@Bm@Pm)%2)==8: break
        rows=[(Qm[:,k],Pm[:,k]) for k in range(8)]
    d=int(rng.integers(1,28))
    # structured Omega sometimes: kernel-type
    Om=rng.integers(0,2,(d,28)); Om=rref(Om)[0].astype(np.int64); d=len(Om)
    gens=[]
    for q,p in rows:
        u=(Bm@q)%2
        for v in Om:
            l=(omega_mat(v)@p)%2   # linear form z -> omega(z,p)
            gens.append(poly_of_product(u,l))
    g=f2rank(np.array(gens)); worst=min(worst,g-d)
    if g<d: print('FAIL',mode,'d',d,'dimG',g,flush=True)
print(mode,'min (dimG - d) =',worst)
