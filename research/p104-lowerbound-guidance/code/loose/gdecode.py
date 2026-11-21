"""decode a kissat model of f2gen.py; recompute every slot's U, ports, price, generic f, mod-2 decodability (independent of CNF)."""
import sys; sys.path.insert(0,'../nonlin'); sys.path.insert(0,'../linear56')
from ncore import *
import pickle
mp=pickle.load(open(sys.argv[1]+'.map','rb')); J=mp['J']
val=set()
for line in open(sys.argv[2]):
    if line.startswith('v'):
        for x in line.split()[1:]:
            x=int(x)
            if x>0: val.add(x)
vec=lambda v: int(sum(int(v[i])<<i for i in range(len(v))))
cb=[vec(Cb[t]) for t in range(n)]; zb=[vec(Zb[k]) for k in range(16)]
allv=np.array(list(itertools.product([0,1],repeat=9)))
gens={t:[] for t in range(n)}; tot=0; rows=[]
for s in [('z',k) for k in range(16)]+[('g',j) for j in range(J)]:
    Fm=[[1 if mp['f'][s,i,c] in val else 0 for c in range(9)] for i in range(9) if mp['used'][s,i] in val]
    inU=~(((allv@np.array(Fm).T)%2).any(1)) if Fm else np.ones(512,bool)
    Ul=set(map(tuple,allv[inU].tolist()))
    P=[t for t in range(n) if tuple(H[t].tolist()) in Ul]
    if not P: continue
    if s[0]=='z': g=zb[s[1]]
    else: g=sum(1<<i for i in range(8) if mp['F'][s[1],i] in val)
    d=span_dim([H[t] for t in P])
    disc= s[0]=='z' and span_dim([H[t] for t in P]+[np.array([1]+[(g>>i)&1 for i in range(8)])])==d
    p=d-int(disc); tot+=p; rows.append((s,g,p,len(P)))
    for t in P: gens[t].append(g)
ex=[t for t in range(n) if mp['ex'][t] in val]
def inspan(gs,x):
    Bs=[]
    for g in gs:
        for b in Bs: g=min(g,g^b)
        if g: Bs.append(g)
    for b in sorted(Bs,reverse=True): x=min(x,x^b)
    return x==0
ok=all(inspan(gens[t],cb[t]) or t in ex for t in range(n))
for r in rows: print(r)
print('row cost',tot,'exempt',len(ex),'TOTAL',tot+len(ex),'mod-2 decodable',ok)
