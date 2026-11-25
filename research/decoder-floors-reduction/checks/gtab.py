# g(w) = max #P112 lines whose labels lie in a w-dim subspace of F2^9 (w = 9 - codim), codim 1..5 via functionals.
import json, numpy as np, itertools
D=json.load(open('data.json')); LAB=D['LAB']; v=len(LAB)
par=lambda x: bin(x).count('1')&1
Z=np.array([[1-par(phi&LAB[t]) for t in range(v)] for phi in range(512)],dtype=bool)  # Z[phi,t]: phi(u_t)=0
def pack(b): 
    x=0
    for i,bb in enumerate(b):
        if bb: x|=1<<i
    return x
M=[pack(Z[p]) for p in range(512)]
pc=lambda x: bin(x).count('1')
# codim c subspace = common kernel of a c-dim space of functionals; enumerate by greedy span closure up to c=4 using row-reduced reps
best={}
best[1]=max(pc(M[p]) for p in range(1,512))
b2=0
for a in range(1,512):
    for b in range(a+1,512):
        b2=max(b2,pc(M[a]&M[b]))
best[2]=b2
# codim 3/4: restrict to functional triples where pair count is large enough to matter (prune)
pairs=[(a,b,M[a]&M[b]) for a in range(1,512) for b in range(a+1,512)]
b3=0; cand=[]
for a,b,m in pairs:
    if pc(m)<=b3: continue
    for c in range(b+1,512):
        if c==a^b: continue
        x=m&M[c]; n=pc(x)
        if n>b3: b3=n
best[3]=b3
print({9-c:best[c] for c in best})
