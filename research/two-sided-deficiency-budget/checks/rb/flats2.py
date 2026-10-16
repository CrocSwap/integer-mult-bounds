# all parabolic subsystems (flats) of E8 of rank <=6 with >=18 lines: W(E8)-orbits of standard parabolics (subsets of simple roots).
# Output level-2 targets S = P112 \ flat with |S| <= 94, deduped, reps under the frame group (sym.py).
import numpy as np, itertools, json
from targ import L2, E8
R=E8; n=120
key={}
for i,r in enumerate(R): key[tuple(r)]=i; key[tuple(-r)]=i
v=np.array([1,2,3,5,8,13,21,34])*1.0+0.01*np.arange(8)
pos=[r if r@v>0 else -r for r in R]
simple=[i for i,r in enumerate(pos) if not any(key.get(tuple(r-p),-1)>=0 and (r-p)@v>0 and tuple(r-p) in key and any(np.array_equal(r-p,q) for q in pos) for p in pos if not np.array_equal(p,r))]
print('simple',len(simple))
S=[pos[i] for i in simple]
refl=[]
for a in S:
    refl.append([key[tuple(r-2*(r@a)//(a@a)*a)] for r in R])
def flat(idxs):
    M=np.array([R[i] for i in idxs],float); rk=np.linalg.matrix_rank(M)
    return frozenset(j for j in range(n) if np.linalg.matrix_rank(np.vstack([M,R[j]]))==rk)
std=set()
for k in range(1,7):
    for sub in itertools.combinations(range(8),k):
        f=flat([simple[i] for i in sub])
        if len(f)>=18: std.add(f)
print('standard types sizes',sorted(len(f) for f in std))
allf=set()
for f in std:
    if f in allf: continue
    st=[f]; allf.add(f)
    while st:
        x=st.pop()
        for p in refl:
            y=frozenset(p[j] for j in x)
            if y not in allf: allf.add(y); st.append(y)
print('flats',len(allf))
# P112 lines inside a flat: L2 rows are E8 roots
lid=[key[tuple(r)] for r in L2]
T=set()
for f in allf:
    s=frozenset(t for t in range(112) if lid[t] not in f)
    if len(s)<=94: T.add(s)
print('targets |S|<=94',len(T))
from sym import G, idx
PI=[[idx[tuple(M@r)] for r in L2] for M in G]
seen=set(); reps=[]
for s in T:
    if s in seen: continue
    reps.append(sorted(s)); st=[s]; seen.add(s)
    while st:
        x=st.pop()
        for pi in PI:
            y=frozenset(pi[t] for t in x)
            if y not in seen: seen.add(y); st.append(y)
from collections import Counter
print('reps',len(reps),sorted(Counter(len(r) for r in reps).items()))
json.dump(reps,open('lev2reps.json','w'))
