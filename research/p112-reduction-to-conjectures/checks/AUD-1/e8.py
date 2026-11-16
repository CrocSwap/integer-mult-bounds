# AUD-1 own E8 build (independent of lib.py/gen.py): even coords, Bourbaki simple roots
import itertools, numpy as np
from fractions import Fraction as Fr
R=[]
for i,j in itertools.combinations(range(8),2):
    for si in (1,-1):
        for sj in (1,-1):
            v=[0]*8; v[i]=2*si; v[j]=2*sj; R.append(tuple(v))   # doubled coords
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: R.append(tuple(s))
assert len(R)==240
lines=sorted({max(r,tuple(-x for x in r)) for r in R}, reverse=True)
assert len(lines)==120
S=np.array([[1,-1,-1,-1,-1,-1,-1,1],[2,2,0,0,0,0,0,0],[-2,2,0,0,0,0,0,0],[0,-2,2,0,0,0,0,0],
            [0,0,-2,2,0,0,0,0],[0,0,0,-2,2,0,0,0],[0,0,0,0,-2,2,0,0],[0,0,0,0,0,-2,2,0]])  # doubled
L=np.array(lines)
C=np.rint(np.linalg.solve(S.T.astype(float),L.T.astype(float))).astype(int).T  # coeffs in simple roots
assert (C@S==L).all()
lab=[int(sum(((c%2)<<k) for k,c in enumerate(row)))|(1<<8) for row in C]
assert len(set(lab))==120
ip=lambda a,b: int(np.dot(a,b))   # doubled coords -> 4*true ip
orth=[[ip(L[a],L[b])==0 for b in range(120)] for a in range(120)]
def off(h): return [t for t in range(120) if abs(np.dot(L[t],h))>1e-9]
def mask(ts): 
    m=0
    for t in ts: m|=1<<t
    return m
def refl_perm(r):
    r=np.array(r); out=[]
    for t in range(120):
        v=L[t]-2*np.dot(L[t],r)//np.dot(r,r)*r
        v=tuple(v); v=max(v,tuple(-x for x in v)); out.append(lines.index(v))
    return out
def frames():
    F=[]
    def rec(cur,cand):
        if len(cur)==8: F.append(tuple(cur)); return
        for k,c in enumerate(cand):
            rec(cur+[c],[d for d in cand[k+1:] if orth[c][d]])
    rec([],list(range(120))); return F
def orbits(objs,perms):
    idx={o:i for i,o in enumerate(objs)}; seen=[-1]*len(objs); reps=[]
    for i,o in enumerate(objs):
        if seen[i]>=0: continue
        reps.append(i); seen[i]=i; st=[o]
        while st:
            x=st.pop()
            for p in perms:
                y=tuple(sorted(p[t] for t in x)); j=idx[y]
                if seen[j]<0: seen[j]=i; st.append(y)
    return reps,[seen.count(r) for r in reps]
def flats7():
    ms=set()
    for f in range(1,512):
        for g in range(f+1,512):
            m=0
            for t in range(120):
                if bin(lab[t]&f).count('1')%2==0 and bin(lab[t]&g).count('1')%2==0: m|=1<<t
            ms.add(m)
    return sorted(ms)
