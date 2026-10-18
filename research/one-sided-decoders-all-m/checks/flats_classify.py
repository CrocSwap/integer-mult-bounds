# Flats of the E8 root system of rank <= 7 with many lines (standard-parabolic enumeration) and the frame-line count of the E6 flats.
# Classical input (Bourbaki, Lie V s3: Phi cap V is W-conjugate to a standard parabolic subsystem Phi_J): CONDITIONAL [verify].
import itertools, numpy as np
from base import *                      # E8L (120 lines, exact Fractions), F0 (the frame), dot
S2=[(1,-1,-1,-1,-1,-1,-1,1),(2,2,0,0,0,0,0,0),(-2,2,0,0,0,0,0,0),(0,-2,2,0,0,0,0,0),(0,0,-2,2,0,0,0,0),(0,0,0,-2,2,0,0,0),(0,0,0,0,-2,2,0,0),(0,0,0,0,0,-2,2,0)]
A=np.array(S2,float).T/2.0              # columns = Bourbaki simple roots of E8 (norm 2)
R=[]                                    # 240 roots in doubled coordinates
for i,j in itertools.combinations(range(8),2):
    for si in (2,-2):
        for sj in (2,-2):
            v=[0]*8; v[i]=si; v[j]=sj; R.append(v)
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: R.append(list(s))
R=np.array(R,float)/2.0
assert len(R)==240 and np.allclose((R*R).sum(1),2)
coef=np.rint(np.linalg.solve(A,R.T).T).astype(int)       # simple-root coordinates (all roots integral, same sign)
assert np.allclose(coef@A.T,R)
G=np.rint(A.T@A).astype(int)                              # Cartan matrix of the chosen simple system
assert all(G[i,i]==2 for i in range(8)) and sorted(set(G[np.triu_indices(8,1)]))==[-1,0]
def lines_J(J): return sum(1 for c in coef if all(c[i]==0 for i in range(8) if i not in J))//2
res={}
for k in range(1,8):
    for J in itertools.combinations(range(8),k): res[J]=lines_J(J)
for k in range(1,8):
    print('rank',k,'max lines in a standard parabolic of rank',k,':',max(res[J] for J in res if len(J)==k))
Nu=[max(res[J] for J in res if len(J)==k) for k in range(1,8)]
assert Nu==[1,3,6,12,20,36,63], Nu
big=sorted([(n,len(J)) for J,n in res.items() if n>=36])
from collections import Counter
print('standard parabolics of rank <= 7 with >= 36 lines: (lines, rank) ->',Counter(big))
assert set(Counter(big))=={(63,7),(42,7),(37,7),(36,6)} and Counter(big)[(63,7)]==1
print('=> types E7 (63 lines), D7 (42), E6+A1 (37), E6 (36); no other flat of rank <= 7 has >= 36 lines')
# E6 flats = orthogonal complements of A2 flats: frame lines inside each
L8=[np.array([float(c) for c in r]) for r in E8L]; Fz=[np.array([float(c) for c in f]) for f in F0]
a2=set()
for a in range(120):
    for b in range(120):
        if abs(abs(L8[a]@L8[b])-1)<1e-9:
            a2.add(frozenset(t for t in range(120) if abs(L8[t]@L8[a])<1e-9 and abs(L8[t]@L8[b])<1e-9))
nfr=Counter(sum(1 for f in Fz if any(np.allclose(f,L8[t]) or np.allclose(f,-L8[t]) for t in S)) for S in a2)
print('E6 flats (lines orthogonal to an A2):',len(a2),'sizes',Counter(len(S) for S in a2),'frame lines inside:',dict(nfr))
assert len(a2)==1120 and set(len(S) for S in a2)=={36} and min(nfr)>=2
print('flats_classify OK')
