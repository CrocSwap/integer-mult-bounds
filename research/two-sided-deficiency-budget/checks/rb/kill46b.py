# fast version of kill46: superset filter first (rank(Off(r')\X) <= 8), exact check only if the superset has rank >= 4.
import numpy as np, json, sys
from covm import *
reps=json.load(open('reps.json'))
roots=[i for i in range(len(H)) if len(off(H[i]))==53]
OFF={j:sum(1<<t for t in off(H[j])) for j in roots}
K7=K(7); mk=lambda s: sum(1<<t for t in s)
res=[]
for i in [r for r in reps if len(off(H[r]))==53]:
    T=off(H[i]); Tm=tomask(T); c=cnt(K7&Tm)
    Xs=set(toint(Tm&~u) for u in np.unique(K7[c>=31],axis=0))
    nsup=0; nexact=0; surv=0
    for X in Xs:
        sup=[j for j in roots if rank(OFF[j]&~X)<=8]
        if np.linalg.matrix_rank(np.array([H[j] for j in sup],float))<4: continue
        nsup+=1
        nX=bin(X).count('1')
        cands=[X] if nX==22 else [X]+[X|(1<<e) for e in range(112) if not X>>e&1]
        for Sm in cands:
            comp=[j for j in sup if rank(OFF[j]&~Sm)<=7]
            if len(comp)==0 or np.linalg.matrix_rank(np.array([H[j] for j in comp],float))<4: continue
            nexact+=1
            if Target([t for t in range(112) if Sm>>t&1]).covers([5,2,2,2,2,2]): surv+=1; print('SURVIVOR',i,bin(X).count('1'),[t for t in range(112) if Sm>>t&1],comp,flush=True)
    res.append((i,len(Xs),nsup,nexact,surv)); print('rep',i,'#X',len(Xs),'X passing superset',nsup,'Sm passing rank',nexact,'survivors',surv,flush=True)
