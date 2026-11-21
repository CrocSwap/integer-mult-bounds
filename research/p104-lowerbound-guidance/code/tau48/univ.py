"""TAU48 univ.py: universal tau-form of Q on C^perp x C^perp (C = label code = colspace Q mod 2): T(x,y) = x^T Q y / 2 mod 2."""
import numpy as np
from gibbs import *
from canon import basis, R, perp
C1=basis(R[1]); P=perp(C1)
S=P@Q@P.T; assert not (S%2).any()
T=(S//2)%2; print('dim Cperp',len(P),'rank universal tau-form',rk(T), 'symmetric', ((T-T.T)%2==0).all(), 'diag', T.diagonal().sum())
