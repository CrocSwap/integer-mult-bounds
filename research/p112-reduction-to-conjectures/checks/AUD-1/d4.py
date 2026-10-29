import sys,itertools,numpy as np; sys.path.insert(0,'.')
from e8 import lines
D=[np.array(l) for l in lines if all(x==0 for x in l[4:])]; print('D4 lines',len(D))
rk=lambda vs: np.linalg.matrix_rank(np.array(vs,float))
H=set()
for a,b,c in itertools.combinations(range(12),3):
    if rk([D[a],D[b],D[c]])==3:
        s=frozenset(t for t in range(12) if rk([D[a],D[b],D[c],D[t]])==3)
        if len(s)==6: H.add(s)
H=list(H); print('6-root hyperplanes',len(H), 'max lines in any hyperplane', max(len(frozenset(t for t in range(12) if rk([D[a],D[b],D[c],D[t]])==3)) for a,b,c in itertools.combinations(range(12),3) if rk([D[a],D[b],D[c]])==3))
from collections import Counter
inter=Counter(len(H[i]&H[j]) for i,j in itertools.combinations(range(len(H)),2)); print('pair intersections (#lines:count)',dict(inter))
# max clique: hyperplanes pairwise meeting in >=3 root lines (A2)
adj=lambda i,j: len(H[i]&H[j])>=3
best=0
for k in range(1,7):
    if any(all(adj(i,j) for i,j in itertools.combinations(c,2)) for c in itertools.combinations(range(len(H)),k)): best=k
print('max clique pairwise >=3 common roots',best)
# also: are there 5 distinct hyperplanes and 10 distinct roots r_ab with r_ab in H_k for all k not in ab (direct search)
cnt=0
for c in itertools.combinations(range(len(H)),5):
    pass
