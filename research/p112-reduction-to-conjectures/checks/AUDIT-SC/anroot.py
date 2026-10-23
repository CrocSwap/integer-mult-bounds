# F3 facts (special 3-circuits) from left_root.txt, mapped to all 112 roots by G.
import numpy as np, pickle, itertools
from collections import Counter, defaultdict
import p112 as p
G=np.load('G.npy'); pos={g:i for i,g in enumerate(p.P)}; PL=p.PL
r0=p.P[0]; r0p=pos[r0]
L=[]
for line in open('left_root.txt'):
    if line.startswith('#'): print(line.strip()); continue
    lo,hi=line.split(); x=int(lo,16)|(int(hi,16)<<64); L.append(x)
L=sorted(set(L),key=lambda x:bin(x).count('1'))
# minimal
mins=[]
for x in L:
    if not any((m & ~x)==0 for m in mins): mins.append(x)
pcnt=lambda x:bin(x).count('1')
print('distinct leftovers',len(L),' minimal',len(mins),' size hist of minimal',sorted(Counter(map(pcnt,mins)).items()))
assert all(not (x>>r0p)&1 for x in mins)
def lines(x): return [i for i in range(112) if x>>i&1]
rank=lambda x:p.f2rank([PL[i] for i in lines(x)])
print('(a) min |L| =',min(map(pcnt,mins)))
m4=[x for x in mins if pcnt(x)==4]; print('(b) #4-leftovers per root',len(m4),' ranks',Counter(map(rank,m4)))
# coset reps g: g(r0)=r  (perm on global indices)
Pidx=np.array(p.P); inv={g:i for i,g in enumerate(p.P)}
rep={}
for g in G:
    r=int(g[r0])
    if r not in rep: rep[r]=g
    if len(rep)==112: break
def img(g,x):
    y=0
    for i in lines(x): y|=1<<inv[int(g[Pidx[i]])]
    return y
ALL=defaultdict(set)   # minimal leftover -> roots (P112 index)
for r,g in rep.items():
    for x in mins: ALL[img(g,x)].add(inv[r])
n_by=defaultdict(int)
for x,rs in ALL.items(): n_by[pcnt(x)]=max(n_by[pcnt(x)],len(rs))
print('max #roots per minimal leftover set, by size:',dict(sorted(n_by.items())))
# (c) 5-sets
served=defaultdict(set)
small=[(x,rs) for x,rs in ALL.items() if pcnt(x)<=5]
for x,rs in small:
    if pcnt(x)==5: served[x]|=rs
    else:
        for l in range(112):
            if not x>>l&1: served[x|1<<l]|=rs
best5=max(len({r for r in rs if not X>>r&1}) for X,rs in served.items())
print('(c) max #roots r not in X served by a 5-set X:',best5)
# (d) bound for 6-sets: 15*n4+6*n5+n6, and exact over X = union-based candidates? (bound)
print('(d) 6-set bound 15*n4+6*n5+n6 =',15*n_by[4]+6*n_by[5]+n_by[6])
# (e),(f): 4-flats. subspace canonical form: sorted tuple of its 16 elements
def span(vs):
    S={0}
    for v in vs:
        if v not in S: S|={s^v for s in S}
    return S
def flats4_containing(vs):
    S=span(vs); k=len(S).bit_length()-1
    res=[]
    if k>4: return res
    if k==4: return [frozenset(S)]
    # extend to all 4-dim subspaces containing S
    out=set()
    def ext(S):
        if len(S)==16: out.add(frozenset(S)); return
        for v in range(1,512):
            if v not in S: ext(S|{s^v for s in S})
    if k==3:
        for v in range(1,512):
            if v not in S: out.add(frozenset(S|{s^v for s in S}))
    else:
        ext(S)
    return list(out)
lam=lambda F: sum(1<<i for i in range(112) if PL[i] in F)
A=defaultdict(set); B=defaultdict(set)
for x,rs in ALL.items():
    ls=lines(x)
    if pcnt(x)>9: continue
    if rank(x)<=4:
        for F in flats4_containing([PL[i] for i in ls]): A[F]|=rs
    for l in ls:
        rest=[i for i in ls if i!=l]
        if p.f2rank([PL[i] for i in rest])<=4:
            for F in flats4_containing([PL[i] for i in rest]):
                if PL[l] not in F: B[(F,l)]|=rs
bestE=0
for F,rs in A.items():
    X=lam(F); bestE=max(bestE,len({r for r in rs if not X>>r&1}))
print('(e) max #roots outside X served, X = 4-flat set:',bestE, ' #4-flats serving some root:',len(A))
bestF=0
keys=set(B)|{(F,l) for F in A for l in range(112) if PL[l] not in F}
for F,l in keys:
    X=lam(F)|1<<l
    rs=A.get(F,set())|B.get((F,l),set())
    bestF=max(bestF,len({r for r in rs if not X>>r&1}))
print('(f) max #roots outside X served, X = 4-flat set + 1 line:',bestF)
pickle.dump({'ALLroot':dict(ALL)},open('rootleft.pkl','wb'))
