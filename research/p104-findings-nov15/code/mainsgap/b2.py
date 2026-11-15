# B2: per-main exact best chain holding every partner's TIMED chart path fixed; main's own times free.
# One contact per partner required (relaxation of the word's full contact list and of all data dependencies).
import sys, pickle, math; sys.path.insert(0,'../../PRICEKIT')
from collections import defaultdict
d=pickle.load(open('data.pkl','rb')); cls,stays,contacts,dim,frames=d['cls'],d['stays'],d['contacts'],d['dim'],d['frames']
def span(b):
    s={0}
    for v in b: s|={x^v for x in s}
    return frozenset(s)
sp=[span(b) for b in frames]
g=lambda r: r*math.log(r) if r>1 else 0.0
def val(ch): return sum(g(dim[b]-dim[a]) for a,b in zip(ch,ch[1:]))
res={}; nodes=[0]
def solve(m, path_given=None):
    st=stays[m]; path=[s[0] for s in st]; S,F=path[0],path[-1]
    P={}
    for p in set(p for _,p,_,_ in contacts.get(m,[])):
        P[p]=[(G,s,e) for G,s,e in stays[p] if G is not None and sp[S]<=sp[G]<=sp[F]]
    plist=list(P)
    cand=sorted(set(G for p in plist for G,_,_ in P[p] if G not in (S,F)), key=lambda G: dim[G])
    best=[None,-1.0]
    memo={}
    def dfs(chain, a, unc, acc):
        # at chart last, arrived at time a; unc = partners not yet served
        nodes[0]+=1
        last=chain[-1]
        if acc+g(dim[F]-dim[last])<=best[1]+1e-12: return
        key=(last,a,unc)
        if memo.get(key,-1e18)>=acc-1e-12: return
        memo[key]=acc
        here=[s for p in unc for (G,s,e) in P[p] if G==last and e>a and s>=a] 
        deps=sorted(set([a]+here))   # leave just after time d (d=a means immediately)
        for dep in deps:
            served=frozenset(p for p in unc if any(G==last and e>a and s<=dep and (s<dep or s==a or dep>a or s<a) for G,s,e in P[p]))
            # precise: overlap of (a, dep+eps) with (s,e): s<dep+eps and e>a  <=> s<=dep and e>a
            served=frozenset(p for p in unc if any(G==last and s<=dep and e>a for G,s,e in P[p]))
            rest=unc-served
            # try finishing: jump to F at time dep
            if all(any(G==F and e>dep for G,s,e in P[p]) for p in rest):
                v=acc+g(dim[F]-dim[last])
                if v>best[1]+1e-12: best[0]=chain+[F]; best[1]=v
            # feasibility of rest via later stops
            for G in cand:
                if not (sp[last]<sp[G]): continue
                if not any(H==G and e>dep for p in rest for H,s,e in P[p]): continue
                if any(not any((sp[G]<=sp[H]) and e>dep for H,s,e in P[p]) for p in rest): continue
                dfs(chain+[G], dep, rest, acc+g(dim[G]-dim[last]))
    dfs([S], -1, frozenset(plist), 0.0)
    return best, path
if __name__=='__main__':
    for m in sorted(cls):
        best,path=solve(m)
        res[m]=dict(cls=cls[m], actual=val(path), bound=best[1], chain=best[0], path=path)
        if best[1]<val(path)-1e-9: print('VIOL',m,cls[m],val(path),best,path)
    pickle.dump(res,open('b2.pkl','wb'))
    agg=defaultdict(lambda:[0,0,0,0,0])
    for m,r in res.items():
        a=agg[r['cls']]; a[0]+=1; a[1]+=r['actual']; a[2]+=r['bound']; a[3]+=g(8); a[4]+=(r['bound']>r['actual']+1e-9)
    for k,a in sorted(agg.items()): print(k,'n',a[0],'actual %.1f B2 %.1f ideal %.1f  improvable mains %d'%tuple(a[1:]))
    print('nodes',nodes[0])
