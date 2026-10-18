# Audit: verify that the signed-permutation frame stabiliser preserves the full L3 structure (O_z family, compat, frame classes),
# so the AGL(3,2) orbit reduction of I^c is legitimate. Run from cards/LOWD.
import json, itertools, pickle, numpy as np
D=json.load(open('data.json')); FC=[tuple(int(x) for x in r) for r in D['FC']]; LAB=D['LAB']; v=112
par=lambda x: bin(x).count('1')&1
O={z:frozenset(t for t in range(v) if par(z&LAB[t])) for z in range(1,512)}
Oinv={}
for z,s in O.items(): Oinv.setdefault(s,[]).append(z)
assert all(len(l)==1 for l in Oinv.values()), 'O_z not injective'
compat,null=pickle.load(open('null.pkl','rb'))
lineidx={}
for t,r in enumerate(FC): lineidx[r]=t; lineidx[tuple(-x for x in r)]=t
blocks=set(frozenset(i for i in range(8) if FC[t][i]) for t in range(v))
G=[]
for p in itertools.permutations(range(8)):
    if not all(frozenset(p[i] for i in b) in blocks for b in blocks): continue
    for s in itertools.product([1,-1],repeat=8):
        pi=[]
        for r in FC:
            w=[0]*8
            for i in range(8): w[p[i]]=s[i]*r[i]
            w=tuple(w)
            if w not in lineidx: break
            pi.append(lineidx[w])
        else:
            G.append((p,pi)); break
print('group order',len(G))
bad=0
for p,pi in G:
    zmap={}
    for z in range(1,512):
        img=frozenset(pi[t] for t in O[z])
        if img not in Oinv: bad+=1; break
        zmap[z]=Oinv[img][0]
    else:
        for i in range(8):
            if set(zmap[z] for z in compat[i])!=set(compat[p[i]]): bad+=1; break
print('elements failing O-family/compat invariance:',bad)
reps=set()
for c in itertools.combinations(range(8),3):
    reps.add(min(tuple(sorted(p[i] for i in c)) for p,_ in G))
print('orbits on 3-sets:',reps)
