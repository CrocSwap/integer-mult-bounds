import json
from qzdrive import *
np.set_printoptions(precision=3, suppress=True, linewidth=150)
sp=json.load(open('spec_k4s1.json'))
d=make_design(sp['n'],sp['k'],sp['masks'],[frozenset(p) for p in sp['pieces']],tuple(sp['order']),{int(a):b for a,b in sp['place'].items()})
ok,z,S,nr=try_design(d,tries=12,seed=1); print(ok,nr)
V,W,Vm,Wm,Tw,P,ab=d.frames(z)
for e,(Sx,h) in enumerate(d.inc):
    print(e,sorted(Sx),'host' if h is not None else 'idle','v',V[e],'w',W[e])
for t,X in enumerate(Tw): print('V of host',t,'stage',d.hosts[t]); print(X-np.eye(6))
