# B3: per-main exact best chain when the main must perform the SAME ADD multiset (exact arithmetic):
#  - every other register's timed path and events are fixed;
#  - each main contact may slide only inside its partner-side commutation window, and must happen at a chart
#    where the partner sits during that window;
#  - main-side order: recv-blocks / give-blocks / SCALE barriers keep their order (chart index along the chain is
#    nondecreasing in block index).  Time beyond that is relaxed (so B3 >= any exact single-main reroute).
import sys, pickle, math, bisect; sys.path.insert(0,'../../PRICEKIT'); import pricekit as pk
from collections import defaultdict
d=pickle.load(open('data.pkl','rb')); cls,stays,dim,frames=d['cls'],d['stays'],d['dim'],d['frames']
W=pk.load('../../ATTACK/STACK7616/best7616.json.gz'); prog=W['program']; TT=len(prog)
def span(b):
    s={0}
    for v in b: s|={x^v for x in s}
    return frozenset(s)
sp=[span(b) for b in frames]
g=lambda r: r*math.log(r) if r>1 else 0.0
def val(ch): return sum(g(dim[b]-dim[a]) for a,b in zip(ch,ch[1:]))
read=defaultdict(list); write=defaultdict(list); mev=defaultdict(list)
for t,e in enumerate(prog):
    op=e[0]
    if op in('ADD','COPY'): write[e[1]].append(t); read[e[2]].append(t)
    elif op=='SCALE': write[e[1]].append(t); read[e[1]].append(t)
    elif op in('INIT','CLEAR'): write[e[1]].append(t); read[e[1]].append(t)
def window(t, lst):
    i=bisect.bisect_left(lst,t); lo=lst[i-1] if i>0 else -1
    j=bisect.bisect_right(lst,t); hi=lst[j] if j<len(lst) else TT
    return lo,hi
def build(m):
    st=stays[m]; path=[s[0] for s in st]; S,F=path[0],path[-1]
    ev=[]
    for t,e in enumerate(prog):
        if e[0] in('ADD','COPY') and (e[1]==m) != (e[2]==m):
            if e[1]==m: ev.append((t,'recv',e[2]))
            else: ev.append((t,'give',e[1]))
        elif e[0]=='SCALE' and e[1]==m: ev.append((t,'scale',None))
    blocks=[]; kind=None
    for t,k,p in ev:
        if k=='scale': blocks.append([]); kind='scale'; continue
        if k!=kind: blocks.append([]); kind=k
        # partner-side window: give -> p modified by us, non-commuting = p READ (incl. scale/init/clear); recv -> p WRITTEN
        # (exclude this very event from the lists)
        lst=[x for x in (read[p] if k=='give' else write[p]) if x!=t]
        lo,hi=window(t,lst)
        H=frozenset(G for G,s,e in stays[p] if G is not None and s<hi and e>lo and sp[S]<=sp[G]<=sp[F])
        assert any(G==e2 for G in H for e2 in [prog[t][4]]), (m,t)
        blocks[-1].append(H)
    blocks=[sorted(set(b),key=len) for b in blocks if b]
    return S,F,path,blocks
nodes=[0]
def solve(m):
    S,F,path,blocks=build(m)
    allH=set().union(*[set().union(*b) for b in blocks]) if blocks else set()
    cand=sorted([G for G in allH if G not in (S,F)], key=lambda G: dim[G])
    best=[None,-1.0]; memo={}
    def advance(G, j, rem):
        # greedily assign at chart G: rem = remaining contacts (frozenset of H) of block j
        while True:
            rem=frozenset(H for H in rem if G not in H)
            if rem: return j, rem
            j+=1
            if j>=len(blocks): return j, frozenset()
            rem=frozenset(blocks[j])
    def feasible_rest(G, j, rem):
        # every remaining contact must have a chart strictly above G (necessary)
        for H in rem:
            if not any(sp[G]<sp[X] for X in H): return False
        for b in blocks[j+1:]:
            for H in b:
                if not any(sp[G]<sp[X] for X in H): return False
        return True
    def dfs(chain, j, rem, acc):
        nodes[0]+=1; last=chain[-1]
        if acc+g(dim[F]-dim[last])<=best[1]+1e-12: return
        key=(last,j,rem)
        if memo.get(key,-1e18)>=acc-1e-12: return
        memo[key]=acc
        # finish at F?
        j2,rem2=advance(F,j,rem)
        if j2>=len(blocks):
            v=acc+g(dim[F]-dim[last])
            if v>best[1]+1e-12: best[0]=chain+[F]; best[1]=v
        for G in cand:
            if not sp[last]<sp[G]: continue
            j2,rem2=advance(G,j,rem)
            if j2==j and rem2==rem: continue   # useless stop (pure loss by superadditivity)
            if j2<len(blocks) and not feasible_rest(G,j2,rem2): continue
            dfs(chain+[G], j2, rem2, acc+g(dim[G]-dim[last]))
    j0,r0=advance(S,0,frozenset(blocks[0]) if blocks else frozenset())
    if j0>=len(blocks): best=[[S,F],g(dim[F]-dim[S])]
    else: dfs([S],j0,r0,0.0)
    return best,path,len(blocks)
if __name__=='__main__':
    res={}
    for m in sorted(cls):
        best,path,nb=solve(m)
        res[m]=dict(cls=cls[m],actual=val(path),bound=best[1],chain=best[0],path=path,nblocks=nb)
        if best[1]<val(path)-1e-9: print('VIOL',m,cls[m],val(path),best,path,[dim[x] for x in path])
    pickle.dump(res,open('b3.pkl','wb'))
    agg=defaultdict(lambda:[0,0,0,0,0])
    for m,r in res.items():
        a=agg[r['cls']]; a[0]+=1; a[1]+=r['actual']; a[2]+=r['bound']; a[3]+=g(8); a[4]+=(r['bound']>r['actual']+1e-9)
    for k,a in sorted(agg.items()): print(k,'n',a[0],'actual %.1f B3 %.1f ideal %.1f  improvable mains %d'%tuple(a[1:]))
    print('nodes',nodes[0])
