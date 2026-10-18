# OS-CHARGE base: P112 lines, F0 coords, labels (1, r mod 2), root code.
import sys
from oscommon import *
import numpy as np, itertools
D=load('P112'); L=D['L']; v=D['v']; F0=D['F0']
E8L=E8
def f2rank(vs):
    return len(span_basis(list(vs)))
# F2 basis of E8/2E8 via 8 roots with nondegenerate Gram mod 2
def pick_basis():
    import random
    rng=random.Random(0)
    while True:
        bs=rng.sample(E8L,8)
        G=np.array([[float(dot(a,b)) for b in bs] for a in bs])
        if abs(abs(np.linalg.det(G))-1)<1e-6: return bs
BAS=pick_basis()
def xbar(r): return sum((int(dot(r,b))&1)<<j for j,b in enumerate(BAS))
def mylab(r): return 1|(xbar(r)<<1)   # bit0 = affine coordinate
LAB=[mylab(r) for r in L]
Z=[mylab(f) for f in F0]           # z_i = (1, f_i bar) = kappa_i
FC=np.array([[int(dot(r,f)) for f in F0] for r in L])  # F0 coords (<r,f_i>), entries 0,+-1
