"""decode a kissat model of f2rel.py; recompute U_f, prices (dim U - [f in Z16, (1,f) in U]) and mod-2 decodability independently."""
import sys; sys.path.insert(0,'../nonlin'); sys.path.insert(0,'../linear56')
from ncore import *
import pickle
mp=pickle.load(open(sys.argv[1]+'.map','rb'))
val=set()
for line in open(sys.argv[2]):
    if line.startswith('v'):
        for x in line.split()[1:]:
            x=int(x)
            if x>0: val.add(x)
vec=lambda v: int(sum(int(v[i])<<i for i in range(len(v))))
cb=[vec(Cb[t]) for t in range(n)]; zs=set(vec(Zb[k]) for k in range(16))
allv=np.array(list(itertools.product([0,1],repeat=9)))
tot=0; rows={}; F={t:[] for t in range(n)}
for g in range(1,256):
    Fm=[[1 if mp['f'][g,i,c] in val else 0 for c in range(9)] for i in range(9) if mp['used'][g,i] in val]
    inU=~(((allv@np.array(Fm).T)%2).any(1)) if Fm else np.ones(512,bool)
    U=allv[inU]; Ul=set(map(tuple,U.tolist()))
    P=[t for t in range(n) if tuple(H[t].tolist()) in Ul]
    if not P: continue
    d=span_dim([H[t] for t in P]); nvec=tuple([1]+[(g>>i)&1 for i in range(8)])
    disc= g in zs and span_dim([H[t] for t in P]+[np.array(nvec)])==d
    p=d-int(disc); tot+=p; rows[g]=(p,len(P),g in zs)
    for t in P: F[t].append(g)
ex=[t for t in range(n) if mp['ex'][t] in val]
def inspan(gs,x):
    B=[]
    for g in gs:
        for b in B: g=min(g,g^b)
        if g: B.append(g)
    for b in sorted(B,reverse=True): x=min(x,x^b)
    return x==0
ok=all(inspan(F[t],cb[t]) or t in ex for t in range(n))
print('rows (price,|D|,tight):',sorted(rows.values(),reverse=True))
print('row cost',tot,'exempt',len(ex),'TOTAL',tot+len(ex),'all ports mod-2 decodable',ok)
