"""DOUBLE56 clique_chk.py: (1) tau-triviality of J_n, I_n exhaustively for small n (every even 0/1 submatrix has sum = 0 mod 4);
(2) random mod-4 decoders on J_8 (random rows + completion): rho_A+rho_B >= 8 and x^T X y = 0 on the Rado spaces X x Y."""
import sys,numpy as np,itertools
from rho import *
from sa import complete
def tau_trivial(Q):
    n=Q.shape[0]; bad=0
    for u in range(1,1<<n):
        U=[i for i in range(n) if u>>i&1]
        for v in range(1,1<<n):
            Vv=[i for i in range(n) if v>>i&1]
            M=Q[np.ix_(U,Vv)]
            if (M.sum(1)%2).any() or (M.sum(0)%2).any(): continue
            if M.sum()%4: bad+=1
    return bad
star=np.array([[1,0,0,1],[0,1,0,1],[0,0,1,1],[1,1,1,1]])
print('tau-defects: J5',tau_trivial(np.ones((5,5),int)),'I5',tau_trivial(np.eye(5,dtype=int)),'J3+J2',tau_trivial(np.block([[np.ones((3,3),int),np.zeros((3,2),int)],[np.zeros((2,3),int),np.ones((2,2),int)]])),'star(h=3)',tau_trivial(star))
rng=np.random.default_rng(5); Q=np.ones((8,8),np.int64); mn=99
for trial in range(300):
    m=int(rng.integers(1,10)); Ws=rng.integers(0,4,(8,m)); Vs=rng.integers(0,4,(8,m))
    # bias: sparse
    Ws*= (rng.random((8,m))<0.6); Vs*=(rng.random((8,m))<0.6)
    W,V=complete(Ws,Vs,Q)
    s=trank(spaces_B(W,V,Q),8,2)+trank(spaces_A(W,V,Q),8,2); mn=min(mn,s)
    assert s>=8,(s,W,V)
print('J8 random decoders: min rho sum',mn,'(theorem: >= 8)')
