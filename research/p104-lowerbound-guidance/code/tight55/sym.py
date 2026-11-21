import sys; sys.path.insert(0,'../nonlin'); sys.path.insert(0,'../linear56')
import os; os.chdir('../nonlin')
from ncore import *
import pickle, itertools
CL=pickle.load(open('zclauses.pkl','rb'))
Zbm=Zb%2; Cbm=Cb%2
zi={tuple(v):i for i,v in enumerate(Zbm.tolist())}; assert len(zi)==16
ci={tuple(v):i for i,v in enumerate(Cbm.tolist())}; assert len(ci)==104
# B graph on Z16
Bz=(Zbm@Bm@Zbm.T)%2
# basis of F2^8 from Z16
basis=[];
for i in range(16):
    if f2rank(np.array([Zbm[j] for j in basis]+[Zbm[i]]))>len(basis): basis.append(i)
assert len(basis)==8
Mb=np.array([Zbm[i] for i in basis])
# express all of F2^8 coefficient: solve g via images: g(Mb row i)=img_i ; g = Mb^-1 * Img (row vec convention x->x@g)
from lcore import solve2
def inv2(M):
    R,_=rref(np.concatenate([M,np.eye(8,dtype=np.int64)],1)); return R[:,8:].astype(np.int64)
Mi=inv2(Mb)
# enumerate permutations of Z16 preserving Bz via backtracking
perms=[]
def bt(p):
    k=len(p)
    if k==16: perms.append(tuple(p)); return
    for c in range(16):
        if c in p: continue
        if all(Bz[k,j]==Bz[c,p[j]] for j in range(k)): bt(p+[c])
bt([])
print('graph autos of B on Z16:',len(perms))
good=[]
for p in perms:
    Img=np.array([Zbm[p[i]] for i in basis])
    g=(Mi@Img)%2   # x -> x@g
    if not (((Zbm@g)%2)==Zbm[list(p)]).all(): continue
    if not ((g@Bm@g.T)%2==Bm).all(): continue
    # preserves P104 set?
    im=(Cbm@g)%2
    if not all(tuple(v) in ci for v in im.tolist()): continue
    pp=[ci[tuple(v)] for v in im.tolist()]
    # check clause invariance: port t -> pp[t], row z -> p[z]
    ok=True
    for t in range(n):
        s1=set(sum(1<<p[z] for z in range(16) if r>>z&1) for r in CL[t])
        if s1!=set(CL[pp[t]]): ok=False;break
    good.append((p,ok))
print('lin autos preserving P104:',len(good),'clause-invariant:',sum(o for _,o in good))
pickle.dump([p for p,o in good if o],open('../tight55/perms.pkl','wb'))
