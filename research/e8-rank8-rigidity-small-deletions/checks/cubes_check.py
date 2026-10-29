# W(E6) = Stab of ordered pair (0,2) acting on 118 lines (W6.pkl from grp.py). Checks that data/cubes4.txt (GAP orbit reps of
# 4-subsets, 1-based) are pairwise inequivalent AND their number equals the Burnside orbit count => complete set of orbit reps.
import pickle,sys
import numpy as np
from math import comb
W=pickle.load(open('W6.pkl','rb')); A=np.array([list(p) for p in W],dtype=np.int64); print('group order',len(A))
pts=[x for x in range(120) if x not in(0,2)]
assert len(pts)==118
tot=0
for p in A:
    seen=[0]*120; cyc={}
    for x in pts:
        if seen[x]: continue
        n=0;y=x
        while not seen[y]: seen[y]=1;y=p[y];n+=1
        cyc[n]=cyc.get(n,0)+1
    c1,c2,c3,c4=[cyc.get(k,0) for k in(1,2,3,4)]
    tot+=comb(c1,4)+comb(c1,2)*c2+comb(c2,2)+c1*c3+c4
assert tot%len(A)==0; nb=tot//len(A); print('Burnside orbits of 4-subsets',nb)
reps=[tuple(int(x) for x in l.split()) for l in open(sys.argv[1]) if l.strip()]
keys=set()
for r in reps:
    im=np.sort(A[:,list(r)],axis=1); k=(im[:,0]*120**3+im[:,1]*120**2+im[:,2]*120+im[:,3]).min(); keys.add(int(k))
print('reps',len(reps),'distinct orbits',len(keys))
assert len(reps)==len(keys)==nb and all(0 not in r and 2 not in r for r in reps)
print('PASS cubes4.txt is a complete set of W(E6)-orbit reps of 4-subsets (%d)'%nb)
