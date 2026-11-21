# NETDOUBLE samem2 (own code): skewed SAME-M transforms of E8-56: W=W0 U, V=V0 U^{-T} (U unit mod 4, m=8, or padded m>8 forms).
# Tracks min rho_B and min rho_A separately (SAME-M DOUBLE56 needs min rho_B + min rho_A >= 56 over a same-M family).
import sys, random, numpy as np
sys.path.insert(0,'../orbitlp')
from samem import rhos, cost, inv4, W0, V0, M0
rng=np.random.default_rng(int(sys.argv[1])); random.seed(int(sys.argv[1]))
best={'B':(99,None),'A':(99,None)}
for tr in range(int(sys.argv[2])):
    kind=tr%3
    if kind==0:   # U = I + 2E
        U=(np.eye(8,dtype=int)+2*rng.integers(0,2,(8,8)))%4
    elif kind==1: # unipotent lower triangular, random entries
        U=np.tril(rng.integers(0,4,(8,8)),-1)+np.eye(8,dtype=int)
        U=U[rng.permutation(8)][:,rng.permutation(8)]
    else:
        while True:
            U=rng.integers(0,4,(8,8))
            if inv4(U) is not None: break
    Ui=inv4(U); W=(W0@U)%4; V=(V0@Ui.T)%4
    assert ((W@V.T)%4==M0).all()
    rB,rA=rhos(W,V); c=cost(W,V)
    if rB<best['B'][0]: best['B']=(rB,rA,c,kind)
    if rA<best['A'][0]: best['A']=(rA,rB,c,kind)
    print(tr,kind,'C',c,'rhoB',rB,'rhoA',rA,flush=True)
print('min rhoB',best['B'],'min rhoA',best['A'],'sum of mins',best['B'][0]+best['A'][0])
