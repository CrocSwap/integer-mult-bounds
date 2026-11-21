import sys; sys.path.insert(0,'../nonlin'); sys.path.insert(0,'../linear56')
from ncore import *
import pickle
perms=pickle.load(open('../tight55/perms.pkl','rb'))
vec=lambda v: int(sum(int(v[i])<<i for i in range(len(v))))
basis=[]
for i in range(16):
    if f2rank(np.array([Zb[j] for j in basis]+[Zb[i]]))>len(basis): basis.append(i)
Mb=np.array([Zb[i] for i in basis])
R,_=rref(np.concatenate([Mb,np.eye(8,dtype=np.int64)],1)); Mi=R[:,8:].astype(np.int64)
assert ((Mi@Mb)%2==np.eye(8)).all()
cbs=set(vec(Cb[t]) for t in range(n)); zbs=set(vec(Zb[k]) for k in range(16))
allx=np.array([[ (x>>i)&1 for i in range(8)] for x in range(256)])
out=[]
for p in perms:
    g=(Mi@np.array([Zb[p[i]] for i in basis]))%2
    im=[vec(r) for r in (allx@g)%2]
    assert sorted(im)==list(range(256))
    assert set(im[x] for x in cbs)==cbs and set(im[x] for x in zbs)==zbs
    assert all(im[vec(Zb[k])]==vec(Zb[p[k]]) for k in range(16))
    out.append({x:im[x] for x in range(1,256)})
pickle.dump(out,open('f2perms.pkl','wb')); print('perms',len(out),'all preserve ports+Z16')
