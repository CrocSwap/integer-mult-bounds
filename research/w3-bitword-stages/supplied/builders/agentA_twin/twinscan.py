# Generalized twin scan: sigma0 helper h whose only forward consumer is k (single ADD k+=h), k gives nothing before it.
# Candidate pivot entrance E = f_h ∩ f_k (first frames). Estimate gains.
import sys, json, collections, pickle, math
import numpy as np
from fractions import Fraction
sys.path.insert(0,'/home/claude/work/eval')
from cost import load_snapshot
IN=sys.argv[1]
s,fr,dim,rec=load_snapshot(IN)
v=s['v']; n=s['n']; ZERO=s['ZERO']; FULL=s['FULL']; FR=fr['frames']
init={r:s['initial'][str(r)] for r in range(n)}
g=lambda r: r*math.log(120/r) if r>0 else 0
moves=collections.defaultdict(list)
for k in np.nonzero(rec[:,0]==0)[0]: moves[int(rec[k,1])].append(int(k))
adds_dst=collections.defaultdict(list); adds_src=collections.defaultdict(list)
for k in np.nonzero(rec[:,0]==1)[0]:
    f=int(rec[k,4])
    if 0<dim[f]<24:
        adds_dst[int(rec[k,1])].append(int(k)); adds_src[int(rec[k,2])].append(int(k))
def first(r):
    m=moves[r]
    return int(rec[m[0],3]) if m else None
# intersection dimension of two frames via ranks (float is fine for dims; exactness for chosen E later)
Bc={}
def Bm(f):
    if f not in Bc: Bc[f]=np.array(FR[str(f)]['B'],dtype=float)
    return Bc[f]
def idim(f1,f2):
    a=Bm(f1); b=Bm(f2)
    return a.shape[0]+b.shape[0]-np.linalg.matrix_rank(np.vstack([a,b]))
cands=[]; tot=0.0; hist=collections.Counter()
for h in range(2*v,n):
    if init[h]!=ZERO or not moves[h]: continue
    cons=adds_src[h]
    if len(cons)!=1: continue
    k=cons[0]; c=int(rec[k,1])
    if c<2*v or c>=n or init[c]!=ZERO or not moves[c]: continue
    if any(kk<k for kk in adds_src[c]): continue
    fh=first(h); fc=first(c)
    if fh is None or fc is None or dim[fh]==0 or dim[fc]==0: continue
    # h must be at fh when... ensure h's first event is after its first move (it is) ; c's first event after its first move
    e=idim(fh,fc)
    if e<=0: continue
    best=0; be=0
    for ee in range(1,e+1):
        if ee>=dim[fh]: break   # pivot must still move up (or could equal)
        gain=(g(dim[fh])-g(dim[fh]-ee))-(g(ee)+g(dim[fc]-ee)-g(dim[fc]) if dim[fc]>ee else g(ee)-g(dim[fc]))
        if gain>best: best=gain; be=ee
    if best>0:
        cands.append((h,c,int(k),fh,fc,be,best)); tot+=best; hist[(dim[fh],dim[fc],be)]+=1
print('candidates',len(cands),'potential gain %.0f'%tot)
for kk,cnt in hist.most_common(15): print(kk,cnt)
pickle.dump(cands,open('twincands.pkl','wb'))
