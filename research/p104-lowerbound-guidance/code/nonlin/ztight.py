"""Tight B-linear class: rows y_z = G z, z in Z16 (any tight B-linear decoder merges to this, <=16 rows).
Per port: minimal feasible supports K subset Z16. Then local search on sum_z price(D_z,S_z)."""
from blin import *
import pickle,sys
Zm=Z  # 16x8 integer roots
zb=Zb
m=16
allK=np.arange(1<<m)
# span sets
vecint=lambda v: int(sum(int(v[i])<<i for i in range(8)))
zint=[vecint(zb[k]) for k in range(m)]
span=np.zeros((1<<m,256),bool); span[0,0]=True
for K in range(1,1<<m):
    k=(K&-K).bit_length()-1; P=K&~(1<<k)
    s=span[P]; idx=np.nonzero(s)[0]
    span[K]=s; span[K,idx^zint[k]]=True
# all w-bar in F2^16 with sum wbar z = c_t (mod 2): wbar = w0 + kernel
Wb=np.array(list(itertools.product([0,1],repeat=m)),np.int64)
img=(Wb@Zm)            # integer sums
imgb=img%2
imgi=np.array([vecint(r) for r in imgb])
supp=(Wb*(1<<np.arange(m))).sum(1)
F={}
for t in range(n):
    sel=np.nonzero(imgi==vecint(Cb[t]))[0]
    feas=np.zeros(1<<m,bool)
    for i in sel:
        Ev=((img[i]-C[t])//2)%2; E=vecint(Ev)
        sw=supp[i]
        feas|= ((allK&sw)==sw) & span[:,E]
    Ks=np.nonzero(feas)[0]
    Ks=sorted(Ks,key=lambda x:bin(x).count('1'))
    mins=[]
    for K in Ks:
        if not any((a&K)==a for a in mins): mins.append(int(K))
    F[t]=mins
pickle.dump(F,open('ztight_F.pkl','wb'))
print('min support sizes per port:',sorted(set(min(bin(k).count('1') for k in F[t]) for t in range(n))))
print('#minimal supports per port: min/max',min(len(F[t]) for t in F),max(len(F[t]) for t in F))
