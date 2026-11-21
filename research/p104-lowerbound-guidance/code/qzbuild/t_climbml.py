import sys
from qzml import build_ml
from qzclimb2 import *
k=int(sys.argv[1])
d,C,taus=build_ml(k)
Vv,Ww,AB=build_ml.data
z0=np.concatenate([np.array([[float(x) for x in v] for v in Vv]).ravel(),np.array([[float(x) for x in w] for w in Ww]).ravel(),np.array([[float(a),float(b)] for a,b in AB]).ravel()])
# reconstruct pieces/place in make_design convention
pieces=[];place={};pos=0
for ev in d.events:
    if ev[0]=='H': pos+=1
    else: place[len(pieces)]=pos; pieces.append(frozenset(ev[1]))
order=tuple(h for h in d.hosts)
cur=climb2(d.n,k,[set(M) for M in d.masks],pieces,order,place,z0=z0,log=sys.stdout,tries=3)
