import sys,numpy as np; sys.path.insert(0,'../orbitlp')
from geo import Q
from rho import *
W=np.load('../orbitlp/e8W.npy'); V=np.load('../orbitlp/e8V.npy')
print('decoder',check_decoder(W,V,Q),'C',cost(W,V,Q))
rb,ra,RB,RA=rhos(W,V,Q)
print('rhoB',rb,'rhoA',ra,'dims R_t',sorted(set(len(x) for x in RB)),'R_s',sorted(set(len(x) for x in RA)))
print('rado B',rado_ub(RB,104)[0],'rado A',rado_ub(RA,104)[0])
