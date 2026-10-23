# AUDIT-BX independent checks (own code; only data.json shared)
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('BX_DATA', os.path.join(HERE, '..', '..', 'data', 'data.json'))
WORK = os.environ.get('BX_WORK', '.')
import json, numpy as np, itertools, sys
D=json.load(open(DATA))
LAB=[int(x) for x in D['LAB']]; L=np.rint(np.array(D['L'])*2).astype(int); E=np.rint(np.array(D['E8'])*2).astype(int)
n=len(L)
def canon(v):
    v=np.array(v); i=np.nonzero(v)[0][0]; return tuple(v if v[i]>0 else -v)
Lset=set(canon(x) for x in L); Eset=set(canon(x) for x in E)
frame=[np.array(x) for x in Eset-Lset]
print('P112 lines',len(Lset),'E8 lines',len(Eset),'frame lines',len(frame), 'P112 subset E8',Lset<=Eset)
# --- labels: first-coordinate property, distinctness
print('labels distinct',len(set(LAB))==n, 'common bit set', [b for b in range(9) if all(l>>b&1 for l in LAB)])
# --- d_1 over roots and norm-4 vectors (all 240 roots, all norm-4 = sums of orthogonal roots)
R=np.vstack([E,-E])
offsz=lambda h: int(np.count_nonzero(L@h))
roots=[canon(r) for r in E]
n4=set()
for i in range(240):
    for j in range(240):
        if R[i]@R[j]==0: n4.add(canon(R[i]+R[j]))
print('norm4 lines',len(n4), 'norms', set(int(np.array(v)@np.array(v)) for v in n4))
from collections import Counter
print('root Off sizes',Counter(offsz(np.array(h)) for h in roots))
print('norm4 Off sizes',Counter(offsz(np.array(h)) for h in n4))
# --- every E6 (= roots orthogonal to an A2) contains >=2 frame lines -> d_2
A2=set()
for i in range(240):
    for j in range(240):
        if R[i]@R[j]==-4: A2.add(frozenset([canon(R[i]),canon(R[j]),canon(R[i]+R[j])]))
print('#A2',len(A2))
cnts=Counter(); szs=Counter()
for a in A2:
    a=[np.array(x) for x in a]
    e6=[r for r in roots if all(np.array(r)@x==0 for x in a)]
    assert len(e6)==36
    nf=sum(1 for r in e6 if canon(r) not in Lset); cnts[nf]+=1
print('frame lines per E6',sorted(cnts.items()),'=> max P112 lines in an E6 =',36-min(cnts))
# max P112 lines in any rank-6 space: rank-6 parabolics with >=35 E8 lines are only E6; D6 has 30.
# --- y: label rank helper
def rk(idx):
    b=[]
    for t in idx:
        x=LAB[t]
        for y in b: x=min(x,x^y)
        if x: b.append(x)
    return len(b)
# --- own kernel masks for codim 1,2 (brute force over functionals / pairs)
Zm=[sum(1<<t for t in range(n) if bin(phi&LAB[t]).count('1')%2==0) for phi in range(512)]
K1=[Zm[p] for p in range(1,512)]
K2=set()
for p in range(1,512):
    for q in range(p+1,512):
        K2.add(frozenset([p,q,p^q]))
K2=[Zm[min(s)]&Zm[max(s)] for s in K2]
print('#codim1',len(K1),'#codim2',len(K2),'(gauss 511, 43435)')
print('global g(8),g(7)',max(bin(m).count('1') for m in K1),max(bin(m).count('1') for m in K2))
offm=lambda h: sum(1<<t for t in np.nonzero(L@np.array(h))[0].tolist())
tab=Counter()
for h in roots+sorted(n4):
    T=offm(h); s=bin(T).count('1')
    tab[(s,max(bin(T&m).count('1') for m in K1),max(bin(T&m).count('1') for m in K2))]+=1
print('per-target (|Off|, cap8, cap7):',sorted(tab.items()))
import pickle; pickle.dump(dict(roots=roots,n4=sorted(n4),K2=K2,frame=[tuple(f) for f in frame]),open(os.path.join(WORK,'c1.pkl'),'wb'))
