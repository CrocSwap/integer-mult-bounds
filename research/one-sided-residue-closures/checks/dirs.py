# AUDIT-SC: complete list of P112 Off-masks with |Off| <= 89 (non-E8 directions), own derivation:
#  rank-7 perp: h primitive E8 vector of norm = det(E8 cap V) <= det Q(Psi) <= 12 (types table) -> enumerate norm <= 16;
#  rank-6 perp: V^perp is a root-spanned plane (Hermite, det <= 4) -> generic h in that plane;  rank <= 5: <= 20 lines -> |Off| >= 92.
import numpy as np, itertools, pickle
import p112 as p
LA=p.LA  # doubled coords
P=np.array(p.P)
vecs=[]
rng=np.arange(-3,4)
# integer vectors (true coords), doubled
g=np.array(np.meshgrid(*[rng]*8,indexing='ij')).reshape(8,-1).T
g=g[(g.sum(1)%2==0)&((g**2).sum(1)<=16)&((g**2).sum(1)>0)]
vecs.append(2*g)
h=np.array([-5,-3,-1,1,3,5])
g2=np.array(np.meshgrid(*[h]*8,indexing='ij')).reshape(8,-1).T   # doubled half-integers
g2=g2[((g2.sum(1)//2)%2==0)&((g2**2).sum(1)<=64)]
vecs.append(g2)
V=np.concatenate(vecs); print('E8 vectors norm<=16:',len(V))
# primitive: not 2*E8 vector etc. -> just dedupe directions by canonical primitive form via gcd of doubled coords handled by mask dedupe
D=(V@LA.T)   # 4*<v,l>
perp=(D==0)
rk={}
masks={}
def rank_lines(ix):
    if len(ix)==0: return 0
    return np.linalg.matrix_rank(LA[ix].astype(float))
cnt7=0
for k in range(len(V)):
    Z=np.nonzero(perp[k])[0]
    if len(Z)<23: continue
    r=rank_lines(Z)
    if r!=7: continue
    off=tuple(sorted(set(P.tolist())-set(Z.tolist())))
    isroot=(V[k]@V[k]==8)
    masks.setdefault(off,set()).add(('r7','root' if isroot else 'non', int(V[k]@V[k])//4))
# rank-6 families: planes spanned by two roots
for a,b in itertools.combinations(range(120),2):
    A=LA[[a,b]]
    Z=np.nonzero(((LA@A.T)==0).all(1))[0]
    if len(Z)<23: continue
    if rank_lines(Z)!=6: continue
    off=tuple(sorted(set(P.tolist())-set(Z.tolist())))
    masks.setdefault(off,set()).add(('r6fam',))
out={}
for off,tags in masks.items():
    if len(off)<=89: out[off]=tags
roots=[o for o,t in out.items() if any(x[0]=='r7' and x[1]=='root' for x in t)]
non=[o for o,t in out.items() if not any(x[0]=='r7' and x[1]=='root' for x in t)]
from collections import Counter
print('masks |Off|<=89: total',len(out),' E8-root masks',len(roots),' non-E8',len(non))
print('size hist non-E8',sorted(Counter(len(o) for o in non).items()))
print('fam masks', sum(1 for o in non if any(x[0]=='r6fam' for x in out[o])), 'sizes',sorted(Counter(len(o) for o in non if any(x[0]=='r6fam' for x in out[o])).items()))
pickle.dump({'non':non,'rootmasks':roots,'tags':out},open('dirs.pkl','wb'))
