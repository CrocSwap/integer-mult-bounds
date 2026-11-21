"""MERGEROWS m6: P104 consistency: E8-56 half decoder (sign rows), NF classes and alpha+beta must stay <= 56 = C."""
import sys,numpy as np
from fractions import Fraction as Fr
from m5 import *
sys.path.insert(0,'../den4'); from qlib import CALL,Qof
O='code/orbitlp/'
W4=np.load(O+'e8W.npy')%4; V4=np.load(O+'e8V.npy')%4
sgn=lambda A: np.where(A==3,-1,A); Wi=sgn(W4); Vi=sgn(V4); Q=Qof(CALL[:104]); n=104
rows=[([Fr(int(Wi[t,k])) for t in range(n)],[Fr(int(Vi[t,k]),2) for t in range(n)]) for k in range(Wi.shape[1])]
bad=check_decoder(rows,Q); print('exact over Q? bad cells',bad)
pr=prices(rows,Q); print('rankQ',rk2(Q),'rows',len(rows),'prices',pr,'C',sum(pr))
print('classes',[len(c) for c in classes(rows,Q)])
g=gauge_max(rows,Q,300,0); print('S1 canon',g['canon'],'gmax',g['gmax'],g['gmax_sum'])
