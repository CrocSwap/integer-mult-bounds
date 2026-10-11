import math, collections
from linalg import *
phi=lambda r: 0.0 if r<=0 else r*math.log(100/r)
class Evaluator:
    def __init__(self,d):
        self.d=d; self.icache={}; self.stats=collections.Counter()
    def evaluate(self,kind,hs):
        d=self.d; ff=d['firstframe']; ftab=d['ftab']; lastread=d['lastread']; touch=d['touch']; stats=self.stats
        cut=max(lastread[s] for s in hs); first=min(touch[s] for s in hs)
        if cut>=first: stats[(kind,'no common cut')]+=1; return None
        fr=tuple(sorted(set(ff[s] for s in hs)))
        if fr not in self.icache:
            E=intersect([ftab[f]['B'] for f in fr],[ftab[f]['A'] for f in fr])
            self.icache[fr]=(E, nondeg_subspaces(E) if E else {})
        E,subs=self.icache[fr]
        if not E: stats[(kind,'zero intersection')]+=1; return None
        if not subs: stats[(kind,'no nondegenerate subspace')]+=1; return None
        dims={s:ftab[ff[s]]['dim'] for s in hs}
        options=[]
        for e,basis in subs.items():
            assert rank(basis)==e and contains(E,basis), 'entrance basis outside the exact intersection'
            for f in fr: assert all(sum(a*b for a,b in zip(arow,brow))==0 for arow in ftab[f]['A'] for brow in basis), 'entrance outside a first frame'
            best=None
            for p in hs:
                g=phi(dims[p]-e)-phi(dims[p])+sum(phi(e)+phi(dims[q]-e)-phi(dims[q]) for q in hs if q!=p)
                if best is None or g<best[0]: best=(g,p)
            options.append(dict(e=e,pivot=best[1],gain=best[0],basis=basis,gram_det=det(gram(basis))))
        options.sort(key=lambda o:o['gain'])
        stats[(kind,'ok',len(E),max(subs))]+=1
        return dict(kind=kind,members=list(hs),cut=cut,first_touch=first,dims=[dims[s] for s in hs],dim_intersection=len(E),E=E,options=options)
