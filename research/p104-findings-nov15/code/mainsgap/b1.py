# B1: per-main exact best chain holding every partner's chart SET fixed (time relaxed).
import sys, pickle, math, itertools; sys.path.insert(0,'../../PRICEKIT'); import pricekit as pk
from collections import Counter, defaultdict
d=pickle.load(open('data.pkl','rb')); cls,stays,contacts,dim,frames=d['cls'],d['stays'],d['contacts'],d['dim'],d['frames']
def span(b):
    s={0}
    for v in b: s|={x^v for x in s}
    return frozenset(s)
sp=[span(b) for b in frames]
g=lambda r: r*math.log(r) if r>1 else 0.0
def val(ch): return sum(g(dim[b]-dim[a]) for a,b in zip(ch,ch[1:]))
res={}
for m in sorted(cls):
    st=stays[m]; path=[s[0] for s in st]; S,F=path[0],path[-1]
    inI=lambda G: sp[S]<=sp[G]<=sp[F]
    need=[]
    for p in set(p for _,p,_,_ in contacts.get(m,[])):
        Hp=set(s[0] for s in stays[p] if s[0] is not None and inI(s[0]))
        assert Hp, (m,p)
        if S in Hp or F in Hp: continue
        need.append(frozenset(Hp))
    need=list(set(need))
    cand=sorted(set().union(*need) if need else set(), key=lambda G: dim[G])
    best=[None,-1]
    # DFS over chains in candidate poset (strictly increasing subspaces), prune by upper bound
    def ub(last, remaining):  # best possible: one hop from last to F
        return g(dim[F]-dim[last])
    def dfs(chain, uncovered, acc):
        last=chain[-1]
        if not uncovered:
            v=acc+g(dim[F]-dim[last])
            if v>best[1]+1e-12: best[0]=chain+[F]; best[1]=v
            return
        if acc+ub(last,uncovered)<=best[1]+1e-12: return
        # must cover the uncovered set containing the lowest-dim forced... branch on a set: pick uncovered set with fewest options above last
        for G in cand:
            if not (sp[last]<sp[G]): continue
            rest=[U for U in uncovered if G not in U]
            if any(not any(sp[G]<sp[H] for H in U) for U in rest): continue
            dfs(chain+[G], rest, acc+g(dim[G]-dim[last]))
    dfs([S], need, 0.0)
    res[m]=dict(cls=cls[m], actual=val(path), bound=best[1], chain=best[0], path=path, nneed=len(need))
pickle.dump(res,open('b1.pkl','wb'))
agg=defaultdict(lambda:[0,0,0,0,0])
for m,r in res.items():
    a=agg[r['cls']]; a[0]+=1; a[1]+=r['actual']; a[2]+=r['bound']; a[3]+=g(8); a[4]+=(r['bound']>r['actual']+1e-9)
    if r["bound"]<r["actual"]-1e-9: print("VIOL",m,r["cls"],r["actual"],r["bound"],r["path"],r["chain"],[dim[x] for x in r["path"]])
for k,a in sorted(agg.items()): print(k,'n',a[0],'actual %.1f B1 %.1f ideal %.1f  improvable mains %d'%tuple(a[1:]))
