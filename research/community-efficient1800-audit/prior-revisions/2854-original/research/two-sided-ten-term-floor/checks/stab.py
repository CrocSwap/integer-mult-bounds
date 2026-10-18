# permutation part of the frame stabiliser: perms pi of 8 coords s.t. {supp c_t} blocks map to blocks (sign patterns handled by sign flips)
import json, itertools, numpy as np
D=json.load(open('data.json')); FC=np.array(D['FC'],dtype=int); v=112
lines=set()
for t in range(v):
    r=tuple(FC[t]); r2=tuple(-x for x in r); lines.add(max(r,r2))
blocks=set(frozenset(np.nonzero(FC[t])[0]) for t in range(v)); print('blocks',len(blocks))
G=[]
for p in itertools.permutations(range(8)):
    if all(frozenset(p[i] for i in b) in blocks for b in blocks):
        # need sign vector s with signed perm preserving lines
        ok=False
        for s in itertools.product([1,-1],repeat=8):
            good=True
            for r in lines:
                w=[0]*8
                for i in range(8): w[p[i]]=s[i]*r[i]
                w=tuple(w); w2=tuple(-x for x in w)
                if max(w,w2) not in lines: good=False;break
            if good: ok=True;break
        if ok: G.append(p)
print('perm group order',len(G))
for k in range(5):
    orb=set()
    reps=[]
    for c in itertools.combinations(range(8),k):
        if frozenset(c) in orb: continue
        reps.append(c)
        for p in G: orb.add(frozenset(p[i] for i in c))
    print(k,'orbits',reps)
