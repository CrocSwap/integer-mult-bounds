# STRAYS-MASK §3: which intersections O_z ∩ O_z' (z, z' label classes of dense B, z = z' allowed) are NOT certified spanning
# in every rank-8 realisation by Lemma 1.1 (IDEAL3; valid for any line set X, not only classes).
import sys, pickle, time
from cert2 import *
unit=sys.argv[1]
F0, F1 = load_frames()
if unit=='P112': L=[E8[i] for i in range(120) if i not in set(F0)]
else: L=[E8[i] for i in range(120) if i not in set(F0)|set(F1)]
v,G,frames,nbar=setup(L,8)
basis=colspace_vectors(B0rows(L),v); h=len(basis)
cls={}
for co in range(1,1<<h):
    w=0
    for i in range(h):
        if co>>i&1: w^=basis[i]
    cls[co]=w
def cert(X): return min(bin(s).count('1') for s in propagate(X,frames,nbar,v))==0
t0=time.time(); unc=[]
keys=sorted(cls)
for a in keys:
    for b in keys:
        if b<a: continue
        X=cls[a]&cls[b]
        if not cert(X): unc.append((a,b))
print(unit,"h",h,"frames",len(frames),"classes",len(cls),"uncertified pairs (z<=z')",len(unc),"diag",sum(1 for a,b in unc if a==b),"time",round(time.time()-t0),flush=True)
pickle.dump({'h':h,'basis':basis,'cls':cls,'unc':unc},open(f'pairs_{unit}.pkl','wb'))
