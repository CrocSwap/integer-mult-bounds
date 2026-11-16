# Orbits of the 448 dense 7-flats (36 lines) under the frame stabiliser (signed permutations of F0 coords preserving the line set).
import itertools, pickle
from lib import *
par=lambda x: bin(x).count('1')&1
res=set()
for a in range(1,512):
    for b in range(a+1,512):
        if (a^b)<b: continue
        Yl=frozenset(t for t in range(n) if not par(a&LAB[t]) and not par(b&LAB[t]))
        if len(Yl)>=36: res.add(Yl)
res=sorted(res,key=lambda s:sorted(s))
key={}
for t in range(n):
    key[tuple(C[t])]=t; key[tuple(-x for x in C[t])]=t
sup=set(frozenset(supp8(t)) for t in range(n))
gens=[]
for pm in itertools.permutations(range(8)):
    if all(frozenset(pm[i] for i in s) in sup for s in sup):
        gens.append(pm)
print('support-preserving perms',len(gens))
def act(pm,sg,t):
    v=[0]*8
    for i in range(8): v[pm[i]]=sg[i]*C[t][i]
    return key.get(tuple(v))
G=[]
for pm in gens[:60]+[tuple(range(8))]:
    for i in range(9):
        sg=[1]*8
        if i<8: sg[i]=-1
        img=[act(pm,sg,t) for t in range(n)]
        if None not in img: G.append(img)
print('generators',len(G))
idx={Y:i for i,Y in enumerate(res)}
orb=[-1]*len(res); reps=[]
for i,Y in enumerate(res):
    if orb[i]>=0: continue
    reps.append(i); stack=[Y]; orb[i]=len(reps)-1
    while stack:
        Z=stack.pop()
        for g in G:
            W2=frozenset(g[t] for t in Z); j=idx[W2]
            if orb[j]<0: orb[j]=len(reps)-1; stack.append(W2)
from collections import Counter
print('orbits',len(reps),'sizes',Counter(orb),'reps',reps)
pickle.dump(reps,open('orbits7.pkl','wb'))
