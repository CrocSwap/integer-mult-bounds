import sys,json,gzip,copy,time
from collections import Counter
GK='/Users/joelpulikkan/imb-src/pr568/research/complex-multicold/vendor/pr558/vendor/pr552/complex-local/static44/gk'
sys.path.insert(0,GK)
import gk_word as G,gk_common as C
G.V=C.V=112;G.DATA=C.DATA=7168
V={int(k):v for k,v in json.load(open('V.json')).items()}
w=json.loads(gzip.open(sys.argv[1]).read())
regs=lambda e:[e[1]]+([e[2]] if e[0]=='add' else [])
base=G.profile(w)
val=lambda p:sum(V[r]*c for r,c in p.items())
print('base',dict(base),val(base))
# next frame per register occurrence
occ={}
seq=[('A',i,e) for i,e in enumerate(w['A'])]+[('B',i,e) for i,e in enumerate(w['B'])]
nxt={}
last={}
for k in range(len(seq)-1,-1,-1):
    part,i,e=seq[k]
    for r in regs(e):
        nxt[(k,r)]=last.get(r)
        last[r]=k
found=[]
t0=time.time()
for k,(part,i,e) in enumerate(seq):
    F=G.basis(e[-1])
    cands=set()
    nf=[]
    for r in regs(e):
        j=nxt[(k,r)]
        if j is not None: nf.append(G.basis(seq[j][2][-1]))
        else: nf.append(G.FULL if (r<112 or r>=224) else G.perp(w['ports'][r-112]))
    for f in nf: cands.add(G.basis(list(F)+list(f)))
    if len(nf)==2: cands.add(G.basis(list(F)+list(nf[0])+list(nf[1])))
    cands.discard(F)
    for Fp in cands:
        z=copy.deepcopy(w[part][i]);old=w[part][i];w[part][i]=z;z[-1]=list(Fp)
        try:
            p=G.profile(w);d=val(p)-val(base)
            if d>1e-9: found.append((d,part,i,old,list(Fp),{r:p[r]-base[r] for r in set(p)|set(base) if p[r]!=base[r]}))
        except AssertionError: pass
        w[part][i]=old
print('scan s',time.time()-t0,'found',len(found))
for f in sorted(found,reverse=True)[:40]: print(f)
json.dump(found,open('coal-found-final.json','w'))
