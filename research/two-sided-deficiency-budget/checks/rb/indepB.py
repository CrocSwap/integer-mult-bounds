import os
# Implementation B for (I1) caps at w=7 and for kill46: functional pairs enumerated directly, F2 rank by numpy elimination.
import numpy as np, json, itertools
D=json.load(open(os.environ.get('BX_DATA','../data/data.json'))); LAB=D['LAB']
L2=np.rint(np.array(D['L'])*2).astype(int); E8=np.rint(np.array(D['E8'])*2).astype(int)
bits=np.array([[(x>>b)&1 for b in range(9)] for x in LAB],dtype=np.uint8)
def f2rank(rows):
    M=bits[list(rows)].copy(); r=0
    for c in range(9):
        p=[i for i in range(r,len(M)) if M[i,c]]
        if not p: continue
        M[[r,p[0]]]=M[[p[0],r]]
        for i in range(len(M)):
            if i!=r and M[i,c]: M[i]^=M[r]
        r+=1
    return r
Off=lambda h: [t for t in range(112) if L2[t]@h!=0]
phis=np.array([[(p>>b)&1 for b in range(9)] for p in range(512)],dtype=np.uint8)
Z=(bits@phis.T)%2==0   # Z[t,phi]
kern=[]
for a in range(1,512):
    for b in range(a+1,512):
        if (a^b)>b: kern.append(Z[:,a]&Z[:,b])   # each 2-dim functional space once: {a,b,a^b}, a<b<a^b
kern=np.array(kern); print('codim-2 spaces',len(kern))
rootsP=[r for r in E8 if sum(1 for t in range(112) if L2[t]@r!=0)==53]
for h,name in [(E8[0],'?'),]: pass
caps={}
for r in E8:
    T=Off(r); caps.setdefault(len(T),set()).add(int(kern[:,T].sum(1).max()))
print('cap7 by |Off(root)|',caps,flush=True)
# kill46 independent: every P112 root as r1 (no symmetry used)
surv=0; tot=0
R1=[r for r in rootsP if (abs(r)==2).sum()==2][:1]+[r for r in rootsP if (abs(r)==1).all()][:1]
print('r1 reps',R1,flush=True)
for r1 in R1:
    T=np.array(Off(r1)); cnts=kern[:,T].sum(1)
    for idx in np.nonzero(cnts>=31)[0]:
        X=set(T[~kern[idx,T]].tolist()); tot+=1
        cands=[X] if len(X)==22 else [X]+[X|{e} for e in range(112) if e not in X]
        for Sm in cands:
            comp=[r for r in rootsP if f2rank([t for t in Off(r) if t not in Sm])<=7]
            if np.linalg.matrix_rank(np.array(comp,float))>=4: surv+=1
print('(r1,U1) pairs',tot,'Sm with >=4 independent compatible roots',surv)
