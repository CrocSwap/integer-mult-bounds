"""NETC9 (own code): joint end-frame settlement graph of the native. For every native helper h that ends below V:
after h is pi-clean (tc), every op touching h with another HELPER p is an edge: supply p->h (h += c p) or sink h->p (p += c h).
Reports mutual-supply structure (SCCs, in/out degree, settle-frame multiplicities)."""
import sys, collections, pickle
W5='inputs/'
sys.path.insert(0, W5+'REBUILDKIT')
from fractions import Fraction as Q
from load import Word
w = Word(W5+'MAINFUSE/w7546.json.gz'); W=w.W; n=w.n; cls=w.cls; N=w.N; dim=w.dim
Hs=set(r for r in range(n) if cls[r]=='h'); top=max(dim)
V=[f for f in range(len(dim)) if dim[f]==top]
end={h:W['final'][h] for h in Hs}
low=sorted(h for h in Hs if dim[end[h]]<top)
print('helpers',len(Hs),'ending below top',len(low),'top dim',top,'#top frames',len(V))
T=set(low)
rows=[{r:Q(1)} if r<n else {} for r in range(N)]
def pic(R): return any(not(k<n and k in Hs) for k in R)
tc={h:-1 for h in low}; ev=collections.defaultdict(list)
for t,e in enumerate(W['program']):
    op=e[0]; r=e[1]
    if op=='MOVE': continue
    if op in('INIT','CLEAR'): rows[r]={}; continue
    if op=='SCALE':
        rows[r]={k:v*Q(e[2]) for k,v in rows[r].items()}; continue
    s=e[2]; q=Q(e[3]); R=rows[r]
    ev[t]=(r,s,q,e[4],pic(rows[s]))
    for k,v in list(rows[s].items()):
        nv=R.get(k,0)+q*v
        if nv: R[k]=nv
        else: R.pop(k,None)
    if r in T and pic(R): tc[r]=t
sup=collections.defaultdict(set); snk=collections.defaultdict(set); efr=collections.defaultdict(collections.Counter)
nops=collections.Counter()
for t,(r,s,q,fr,sd) in ev.items():
    if r in T and t>tc[r]:
        c='helper' if s in Hs else cls.get(s,'?')
        nops[('in',c,'T' if s in T else '-')]+=1
        if s in Hs: sup[r].add(s)
        efr[r][fr==end[r]]+=1
    if s in T and t>tc[s] and r!=s:
        c='helper' if r in Hs else cls.get(r,'?')
        nops[('out',c,'T' if r in T else '-')]+=1
        if r in Hs: snk[s].add(r)
print('post-clean ops:',sorted(nops.items(),key=lambda x:-x[1]))
# graph among low helpers: edge p->h if p supplies h's span
G=collections.defaultdict(set)
for h in low:
    for p in sup[h]|snk[h]:
        if p in T: G[h].add(p); G[p].add(h)
ud=sum(len(v) for v in G.values())//2
print('undirected T-T edges',ud,'T nodes with any T-neighbour',sum(1 for h in low if G[h]))
# components
seen=set(); comps=[]
for h in low:
    if h in seen or not G[h]: continue
    st=[h]; seen.add(h); c=[]
    while st:
        x=st.pop(); c.append(x)
        for y in G[x]:
            if y not in seen: seen.add(y); st.append(y)
    comps.append(c)
print('components (T-T)',sorted(map(len,comps),reverse=True)[:15],'singletons-with-no-T-edge',sum(1 for h in low if not G[h]))
print('suppliers per low helper (helper partners):',collections.Counter(min(len(sup[h]),9) for h in low))
print('suppliers NOT in T (supplier ends at top or is non-low):',sum(1 for h in low for p in sup[h] if p not in T),'of',sum(len(sup[h]) for h in low))
mut=sum(1 for h in low for p in sup[h] if p in T and h in sup[p])
print('mutual supply pairs (h<->p both supply):',mut//2)
print('end-dim histogram',collections.Counter(dim[end[h]] for h in low))
print('end frames distinct',len(set(end[h] for h in low)),'helpers per end frame',collections.Counter(collections.Counter(end[h] for h in low).values()))
pickle.dump(dict(low=low,tc=tc,sup={h:sorted(sup[h]) for h in low},snk={h:sorted(snk[h]) for h in low}),open('nat09.pkl','wb'))
