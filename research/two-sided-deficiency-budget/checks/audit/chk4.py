# (4,6) kill, own code, ALL 112 non-frame roots as r_1 (no orbit reduction), NO (5,2^5) cover filter.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('BX_DATA', os.path.join(HERE, '..', '..', 'data', 'data.json'))
WORK = os.environ.get('BX_WORK', '.')
import json, numpy as np, pickle
D=json.load(open(DATA))
LAB=[int(x) for x in D['LAB']]; L=np.rint(np.array(D['L'])*2).astype(int)
c=pickle.load(open(os.path.join(WORK,'c1.pkl'),'rb')); K2=c['K2']
def rk(mask):
    b=[]
    for t in range(112):
        if mask>>t&1:
            x=LAB[t]
            for y in b: x=min(x,x^y)
            if x: b.append(x)
    return len(b)
offm=lambda h: sum(1<<t for t in np.nonzero(L@np.array(h))[0].tolist())
roots=[h for h in c['roots'] if bin(offm(h)).count('1')==53]
OFF=[offm(h) for h in roots]; HV=np.array(roots,float)
assert len(roots)==112
worst=0; nX=0; nSm=0; hist={}
for i,T in enumerate(OFF):
    Xs=set(T&~u for u in K2 if bin(T&u).count('1')>=31)       # Sm must contain Off(r1)\U1
    for X in Xs:
        nX+=1; k=bin(X).count('1'); assert k in (21,22),k
        for Sm in ([X] if k==22 else [X]+[X|(1<<e) for e in range(112) if not X>>e&1]):
            nSm+=1
            comp=[j for j in range(112) if rk(OFF[j]&~Sm)<=7]
            r=np.linalg.matrix_rank(HV[comp]) if comp else 0
            hist[r]=hist.get(r,0)+1; worst=max(worst,r)
    print(i,len(Xs),worst,flush=True) if i%28==0 else None
print('#(r1,U1)',nX,'#Sm',nSm,'rank histogram of compatible roots',hist,'max',worst,'=> kill' if worst<4 else '=> NOT killed without cover filter')
