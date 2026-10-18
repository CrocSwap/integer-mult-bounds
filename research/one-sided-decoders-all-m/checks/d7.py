# D7-type hyperplanes (normal = norm-4 E8 vector): P112 Off sizes; pair-coverable by two 7-flats?
from base import *
import itertools
E8r=[np.array([float(c) for c in r]) for r in E8L]
allr=E8r+[-r for r in E8r]
n4=set()
for a,b in itertools.combinations(range(len(allr)),2):
    s=allr[a]+allr[b]
    if abs(s@s-4)<1e-9:
        k=tuple(np.round(s*2).astype(int)); 
        if tuple(-x for x in k) not in n4: n4.add(k)
print('norm-4 directions',len(n4))
Lnp=np.array([[float(c) for c in r] for r in L])
sizes=[]
for k in n4:
    h=np.array(k)/2.0
    off=int(sum(abs(Lnp@h)>1e-9)); sizes.append(off)
from collections import Counter
print('P112 |Off(h)| for norm-4 h:',Counter(sizes))
par=lambda x: bin(x).count('1')&1
mask={z:sum(1<<t for t in range(v) if not par(z&LAB[t])) for z in range(1,512)}
pc=lambda m: bin(m).count('1')
F7=set()
for a in range(1,512):
    for b in range(a+1,512):
        m=mask[a]&mask[b]
        if pc(m)>=34: F7.add(m)
F7=list(F7); print('7-flats >=34 lines',len(F7))
bad=0
for k in n4:
    h=np.array(k)/2.0
    T=sum(1<<t for t in range(v) if abs(Lnp[t]@h)>1e-9)
    if pc(T)!=70: continue
    P=[m&T for m in F7 if pc(m&T)>=34]
    if any((T&~x&~y)==0 for x,y in itertools.combinations(P,2)): bad+=1
print('70-line Off sets pair-coverable:',bad)
