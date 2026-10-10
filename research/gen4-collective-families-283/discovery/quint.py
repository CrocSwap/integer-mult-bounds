"""Size-5 circuits: for each helper a (smallest member), N(a) = later helpers whose first frames meet a's (screened by inter.npy),
pair-hash 4-sum inside N(a) equal to h(a); exact evaluation via fameval."""
import pickle, json, random, collections, sys, time, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from fameval import Evaluator
d=pickle.load(open(sys.argv[1],'rb')); inter=np.load(sys.argv[2]); fids=pickle.load(open(sys.argv[2]+'.fids.pkl','rb')); OUT=sys.argv[3]
MAXN=int(sys.argv[4]) if len(sys.argv)>4 else 10**9
helpers=d['helpers']; resp=d['resp']; ff=d['firstframe']; v=d['v']
fpos={f:i for i,f in enumerate(fids)}
random.seed(1); key=[random.getrandbits(64) for _ in range(v)]
def h(R):
    x=0
    while R:
        b=R&-R; x^=key[b.bit_length()-1]; R^=b
    return x
hs=np.array([h(resp[s]) for s in helpers],dtype=np.uint64); hp=np.array([fpos[ff[s]] for s in helpers]); H=np.array(helpers)
nh=len(helpers); found=set(); t0=time.time(); degs=[]
for ia in range(nh):
    comp=np.nonzero(inter[hp[ia],hp[ia+1:]]>0)[0]+ia+1
    degs.append(len(comp))
    if len(comp)<4 or len(comp)>MAXN: continue
    iu=np.triu_indices(len(comp),1); pa=comp[iu[0]]; pb=comp[iu[1]]; P=hs[pa]^hs[pb]
    # 4-sum: pairs (x,y) with P[x]^P[y]==hs[ia]  <=> P[y]==P[x]^hs[ia]
    T=P^hs[ia]; order=np.argsort(P); Ps=P[order]
    pos=np.searchsorted(Ps,T); ok=pos<len(Ps); ok[ok]&=Ps[pos[ok]]==T[ok]
    for x in np.nonzero(ok)[0]:
        # all y with Ps==T[x]
        lo=pos[x]; hi=lo
        while hi<len(Ps) and Ps[hi]==T[x]: hi+=1
        for y in order[lo:hi]:
            m=(ia,pa[x],pb[x],pa[y],pb[y])
            if len(set(m))==5:
                hs5=tuple(sorted(H[list(m)]))
                assert resp[hs5[0]]^resp[hs5[1]]^resp[hs5[2]]^resp[hs5[3]]^resp[hs5[4]]==0
                found.add(hs5)
    if ia%2000==0: print(ia,len(found),time.time()-t0,flush=True)
print('size-5 circuits with pairwise-meeting frames', len(found), 'degree hist (pct)', np.percentile(degs,[50,90,99,100]), time.time()-t0, flush=True)
pickle.dump(sorted(found),open(OUT+'.circuits.pkl','wb'))
ev=Evaluator(d); fams=[]
for hs5 in sorted(found):
    f=ev.evaluate('quint',list(hs5))
    if f: fams.append(f)
print('quint families', len(fams), {str(k):c for k,c in ev.stats.items()})
shape=collections.Counter((tuple(sorted(f['dims'])),f['options'][0]['e'],round(f['options'][0]['gain'],2)) for f in fams)
for k,c in sorted(shape.items(), key=lambda x:x[0][2])[:30]: print('  ',k,c)
json.dump(dict(families=fams, stats={str(k):c for k,c in ev.stats.items()}), open(OUT,'w'))
