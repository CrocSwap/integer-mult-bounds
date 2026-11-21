import sys,itertools;sys.path.insert(0,'.')
from rblaw import violations
from rb3 import CS6
from rb15 import *
F=frozenset
for perm in [(0, 2, 4, 1, 3, 5), (0, 3, 2, 5, 4, 1)]:
    R=[(F(perm[t] for t in M),[F(perm[t] for t in p) for p in P]) for M,P in CS6]
    print('perm',perm,'violations(full)',violations(6,R)[:4],flush=True)
    b,v=builds(6,R,nw=4,tr=10);print('  fixed walks','BUILDS' if b else 'stall %.2e'%v,flush=True)
    if not b:
        ok,info,S,z,Q=jbuild(6,R,starts=4);print('  joint','BUILDS' if ok else 'no',info,flush=True)
