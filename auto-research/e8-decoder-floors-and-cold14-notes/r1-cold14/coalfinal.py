import sys,json,gzip,copy,time
from collections import Counter
GK='/Users/joelpulikkan/imb-src/pr568/research/complex-multicold/vendor/pr558/vendor/pr552/complex-local/static44/gk'
sys.path.insert(0,GK)
import gk_word as G,gk_common as C
G.V=C.V=112;G.DATA=C.DATA=7168
V={int(k):v for k,v in json.load(open('V.json')).items()}
w=json.loads(gzip.open(sys.argv[1]).read())
regs=lambda e:[e[1]]+([e[2]] if e[0]=='add' else [])
base=G.profile(w);val=lambda p:sum(V[r]*c for r,c in p.items())
P=w['ports']
def finalframe(r):
    if r<112 or r>=224: return G.FULL
    return G.perp(P[r-112])
seq=[('A',i,e) for i,e in enumerate(w['A'])]+[('B',i,e) for i,e in enumerate(w['B'])]
lastk={}
for k,(part,i,e) in enumerate(seq):
    for r in regs(e): lastk[r]=k
found=[]
for k,(part,i,e) in enumerate(seq):
    rs=regs(e)
    if not any(lastk[r]==k for r in rs): continue
    F=G.basis(e[-1]);fin=[finalframe(r) for r in rs if lastk[r]==k]
    Fp=G.basis(list(F)+list(min(fin,key=len)))
    if Fp==F: continue
    old=w[part][i];w[part][i]=old[:-1]+[list(Fp)]
    try:
        p=G.profile(w);d=val(p)-val(base)
        found.append((round(d,3),part,i,old,len(Fp),{r:p[r]-base[r] for r in set(p)|set(base) if p[r]!=base[r]}))
    except AssertionError as ex: found.append(('ERR',part,i,old,str(ex)[:80]))
    w[part][i]=old
print(len(found))
c=Counter((x[0] if x[0]=='ERR' else 'ok') for x in found);print(c)
for f in found[:30]:print(f)
