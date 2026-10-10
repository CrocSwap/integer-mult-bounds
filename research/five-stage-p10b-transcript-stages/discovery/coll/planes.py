"""Rank >= 2 entrance pool: exact pairwise intersections of first frames (dims 2..MAXD), nondegenerate, with member helpers. Usage: planes.py HELPERS.pkl OUT.pkl MAXD
Chafik Boukhalfa (chafreaky), Anthropic Claude assistance; Apache-2.0."""
import pickle,sys,collections,itertools,time
import numpy as np
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from linalg import nullspace,rref,integerize,det,gram
d=pickle.load(open(sys.argv[1],'rb'));ff=d['firstframe'];ft=d['ftab'];MAXD=int(sys.argv[3])
byframe=collections.defaultdict(list)
for s in d['helpers']:byframe[ff[s]].append(s)
F=[f for f in byframe if 2<=ft[f]['dim']<=MAXD];print('frames',len(F),flush=True)
B={f:np.array(ft[f]['B'],dtype=float) for f in F}
t0=time.time();cand={}
dims=np.array([ft[f]['dim'] for f in F])
for i,f in enumerate(F):
    for j in range(i+1,len(F)):
        g=F[j];k=dims[i]+dims[j]-np.linalg.matrix_rank(np.vstack([B[f],B[g]]))
        if k>=2:
            key=tuple(sorted((f,g)))
            A=[list(r) for r in ft[f]['A']]+[list(r) for r in ft[g]['A']]
            E=nullspace(A);R,_=rref(E);basis=[integerize(r) for r in R]
            kk=tuple(map(tuple,basis))
            if kk not in cand and det(gram(basis))!=0:cand[kk]=basis
print('candidate subspaces',len(cand),'time',time.time()-t0,flush=True)
allF=list(byframe);out={}
for kk,basis in cand.items():
    U=np.array(basis,dtype=np.int64).T;mem=[]
    for f in allF:
        if ft[f]['dim']<len(basis):continue
        A=np.array(ft[f]['A'],dtype=np.int64)
        if A.size==0 or not np.any(A@U):mem.extend(byframe[f])
    if len(mem)>1:out[kk]=(basis,mem)
print('subspaces with >=2 helpers',len(out),collections.Counter(len(b) for b,m in out.values()),flush=True)
pickle.dump(out,open(sys.argv[2],'wb'))
