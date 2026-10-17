# AUDIT-IQ: transport r0's minimal leftovers (<=13: Q 8-sets, M 12-sets) to all roots via W; count; served roots for E=M(+l).
import numpy as np, itertools, pickle
from collections import defaultdict
import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'a2_g777.py')).read().split('# all 7-dim subspaces')[0])   # E8 build only
lab,T0,mins=pickle.load(open('a2_left.pkl','rb'))
pc=lambda x: x.bit_count()
idx={tuple(int(x) for x in L[t]):t for t in range(n)}
def perm_of(r):  # reflection in line r (doubled coords): v -> v - (v.r)/4 * r
    out=[]
    for t in range(n):
        v=L[t]-((L[t]@L[r])//4)*L[r]; out.append(idx[canon([int(x) for x in v])])
    return out
P=[perm_of(r) for r in range(n)]
def act(p,m): return sum(1<<p[t] for t in range(n) if m>>t&1)
# BFS: word mapping line 0 -> every line
to={0:list(range(n))}; fr=[0]
while fr:
    nf=[]
    for a in fr:
        for r in range(n):
            b=P[r][a]
            if b not in to: to[b]=[P[r][x] for x in to[a]]; nf.append(b)
    fr=nf
assert len(to)==n
small=[m for m in mins if pc(m)<=13]
print('r0 minimal leftovers <=13 by size',{k:sum(1 for m in small if pc(m)==k) for k in (8,12)})
serve=defaultdict(set)
for r,p in to.items():
    assert p[0]==r
    for m in small: serve[act(p,m)].add(r)
Q=[s for s in serve if pc(s)==8]; M=[s for s in serve if pc(s)==12]
print('distinct Q',len(Q),'roots per Q',set(len(serve[s]) for s in Q),'distinct M',len(M),'roots per M',sorted(set(len(serve[s]) for s in M)))
print('any root inside its own leftover',any(s>>r&1 for s in serve for r in serve[s]))
# Stab(r0)-orbits on r0's M-sets (reflections in lines perp to line 0)
M0=[m for m in small if pc(m)==12]; pos={m:i for i,m in enumerate(M0)}; par=list(range(len(M0)))
def f(x):
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
for r in range(n):
    if G[0][r]!=0: continue
    for i,m in enumerate(M0):
        a,b=f(i),f(pos[act(P[r],m)])
        if a!=b: par[a]=b
reps=sorted({f(i) for i in range(len(M0))}); print('Stab(r0) orbits on r0 M-sets',len(reps))
allsets=list(serve.items()); best=0
for ri in reps:
    m=M0[ri]; cand=[(s,rs) for s,rs in allsets if pc(s&~m)<=1]
    for l in [None]+[t for t in range(n) if not m>>t&1]:
        E=m|(0 if l is None else 1<<l)
        sv=set().union(*[rs for s,rs in cand if s&~E==0]) if cand else set()
        sv={r for r in sv if not E>>r&1}; best=max(best,len(sv))
print('max served roots outside E over E=M or M+{l}:',best)
