# joint check for the last (4,6) survivor: four weight-7 lows, Sm = union of the six small lows (<=22 lines, (5,2^5)-coverable)
import numpy as np, json
from covm import *
from targ import L2
reps=json.load(open('reps.json'))
roots=[i for i in range(len(H)) if len(off(H[i]))==53]
K7=K(7); 
def mk(s): return sum(1<<t for t in s)
found=0; stats=[]
for i in [r for r in reps if len(off(H[r]))==53]:
    T=off(H[i]); Tm=tomask(T); c=cnt(K7&Tm)
    Us=np.unique(K7[c>=31],axis=0)
    Xs=set(toint(tomask(T)&~u) for u in Us)
    for X in Xs:
        nX=bin(X).count('1'); assert nX in (21,22)
        cands=[X] if nX==22 else [X]+[X|(1<<e) for e in range(112) if not X>>e&1]
        for Sm in cands:
            if not Target([t for t in range(112) if Sm>>t&1]).covers([5,2,2,2,2,2]): continue
            comp=[j for j in roots if rank(mk(off(H[j]))&~Sm)<=7]
            V=np.array([H[j] for j in comp],float)
            rk=np.linalg.matrix_rank(V) if len(comp) else 0
            stats.append((nX,bin(Sm).count('1'),len(comp),rk))
            if rk>=4: found+=1
print('root reps',[len(off(H[r])) for r in reps if len(off(H[r]))==53],'Sm candidates passing (5,2^5):',len(stats),'max rank of compatible roots',max([s[3] for s in stats],default=None),'survivors',found)
print(sorted(set(stats))[:20])
