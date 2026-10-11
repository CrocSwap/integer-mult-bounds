"""Candidate collective-kernel families on gen4: twin pairs (any e), size-3 and size-4 F2 circuits of helper responses
with a common nondegenerate entrance inside all members' first frames and a common per-family cut."""
import pickle, json, math, random, itertools, collections, sys, time, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from linalg import *
d = pickle.load(open(sys.argv[1],'rb')); OUT=sys.argv[2]
helpers=d['helpers']; resp=d['resp']; lastread=d['lastread']; touch=d['touch']; ff=d['firstframe']; ftab=d['ftab']; v=d['v']
phi=lambda r: 0.0 if r<=0 else r*math.log(100/r)
random.seed(1); key=[random.getrandbits(64) for _ in range(v)]
def h(R):
    x=0
    while R:
        b=R&-R; x^=key[b.bit_length()-1]; R^=b
    return x
classes={}
for s in helpers: classes.setdefault(resp[s],[]).append(s)
R=list(classes); m=len(R); H=np.array([h(r) for r in R],dtype=np.uint64); hidx={int(x):i for i,x in enumerate(H)}
assert len(hidx)==m
t0=time.time()
Hs=np.sort(H)
tri=set()
for a in range(m):
    X=H[a]^H[a+1:]
    for j in np.nonzero(np.isin(X,Hs))[0]:
        b=a+1+int(j); c=hidx[int(X[j])]
        if c>b: assert R[a]^R[b]==R[c]; tri.add((a,b,c))
print('triangles (class level)', len(tri), time.time()-t0, flush=True)
iu=np.triu_indices(m,1); P=H[iu[0]]^H[iu[1]]; order=np.argsort(P,kind='stable'); Ps=P[order]
quad=set(); i=0
while i<len(Ps):
    j=i
    while j+1<len(Ps) and Ps[j+1]==Ps[i]: j+=1
    if j>i:
        prs=[(int(iu[0][order[k]]),int(iu[1][order[k]])) for k in range(i,j+1)]
        for (a,b),(c,e) in itertools.combinations(prs,2):
            q=tuple(sorted((a,b,c,e))); assert len(set(q))==4
            assert R[a]^R[b]^R[c]^R[e]==0; quad.add(q)
    i=j+1
print('quadruples (class level)', len(quad), time.time()-t0, flush=True)
del P,order,Ps
twins=[tuple(sorted(ss)) for ss in classes.values() if len(ss)>1]
# expand to helper tuples
def expand(cls_tuple):
    for combo in itertools.product(*(classes[R[c]] for c in cls_tuple)): yield tuple(sorted(combo))
cands=[]
for t in twins:
    for pr in itertools.combinations(t,2): cands.append(('pair',pr))
for t in tri:
    for hs in expand(t): cands.append(('tri',hs))
for q in quad:
    for hs in expand(q): cands.append(('quad',hs))
print('helper-level candidates', collections.Counter(k for k,_ in cands), flush=True)
from fameval import Evaluator
ev=Evaluator(d); fams=[]
for kind,hs in cands:
    f=ev.evaluate(kind,list(hs))
    if f: fams.append(f)
stats=ev.stats
print('families', len(fams), time.time()-t0)
for k,c in sorted(stats.items(), key=lambda x:str(x)): print('  ',k,c)
shape=collections.Counter((f['kind'],tuple(sorted(f['dims'])),f['options'][0]['e'],round(f['options'][0]['gain'],2)) for f in fams)
print('top shapes by best gain:'); 
for k,c in sorted(shape.items(), key=lambda x:x[0][3])[:40]: print('  ',k,c)
json.dump(dict(families=fams, stats={str(k):c for k,c in stats.items()}), open(OUT,'w'))
