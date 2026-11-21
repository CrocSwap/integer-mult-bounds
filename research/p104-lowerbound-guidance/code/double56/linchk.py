import sys,json,numpy as np; sys.path.insert(0,'../orbitlp')
from geo import Q, D56
from rho import *
from lin import inv4
E=json.load(open(D56+'e8base.json')); R=np.array(E['C'])[:104]; Gb=np.array(E['Gb'])
W=np.load('../orbitlp/e8W.npy')%4; V=np.load('../orbitlp/e8V.npy')%4
# solve R X = W mod 4: R has unit-ish rows; find 8 rows of R invertible mod 4
import itertools
for rows in itertools.combinations(range(104),8):
    Ri=inv4(R[list(rows)])
    if Ri is not None: break
X=(Ri@W[list(rows)])%4; Y=(Ri@V[list(rows)])%4
print('W linear?',((R@X-W)%4==0).all(),'V linear?',((R@Y-V)%4==0).all())
print('X Y^T',((X@Y.T)%4).tolist()); print('Gb mod4',(Gb%4).tolist())
np.save('e8X.npy',X); np.save('e8Y.npy',Y)
