import sys,json,gzip,copy,time
from multiprocessing import Pool
GK='/Users/joelpulikkan/imb-src/pr568/research/complex-multicold/vendor/pr558/vendor/pr552/complex-local/static44/gk'
sys.path.insert(0,GK)
import gk_word as G,gk_common as C
G.V=C.V=112;G.DATA=C.DATA=7168
V={int(k):v for k,v in json.load(open('V.json')).items()}
w0=json.loads(gzip.open(sys.argv[1]).read())
W=int(sys.argv[2])
def regs(e):return(e[1],e[2])if e[0]=='add'else(e[1],)
def commute(x,y):
    if x[0]=='add'and y[0]=='add':return x[1]!=y[2]and y[1]!=x[2]
    return not set(regs(x))&set(regs(y))
val=lambda p:sum(V[r]*c for r,c in p.items())
base=G.profile(w0);bv=val(base)
def nextframe(L,j,r):
    for k in range(j+1,len(L)):
        if r in regs(L[k]):return G.basis(L[k][-1])
    return None
def work(args):
    part,k=args
    w=copy.deepcopy(w0);L=w[part];out=[]
    for d in list(range(1,W+1))+[-x for x in range(1,W+1)]:
        j=k+d
        if not 0<=j<len(L):continue
        passed=range(k+1,j+1) if j>k else range(j,k)
        if not all(commute(L[k],L[q]) for q in passed):continue
        z=copy.deepcopy(w);Z=z[part];Z.insert(j,Z.pop(k))
        e=Z[j];F=G.basis(e[-1]);nf=[f for f in (nextframe(Z,j,r) for r in regs(e)) if f]
        cands={G.basis(list(F)+list(f)) for f in nf}
        if len(nf)==2:cands.add(G.basis(list(F)+list(nf[0])+list(nf[1])))
        cands.discard(F)
        for Fp in cands:
            old=Z[j];Z[j]=old[:-1]+[list(Fp)]
            try:
                p=G.profile(z);dv=val(p)-bv
                if dv>1e-9:out.append((dv,part,k,j,old,list(Fp),{r:p[r]-base[r] for r in set(p)|set(base) if p[r]!=base[r]}))
            except AssertionError:pass
            Z[j]=old
    return out
if __name__=='__main__':
    tasks=[(p,k) for p in ('A','B') for k in range(len(w0[p]))]
    t=time.time()
    with Pool(9) as pool:res=pool.map(work,tasks,chunksize=50)
    found=[x for r in res for x in r]
    print('scan',time.time()-t,'found',len(found))
    for f in sorted(found,reverse=True)[:40]:print(f)
    json.dump(found,open('movecoal-'+sys.argv[3]+'.json','w'))
