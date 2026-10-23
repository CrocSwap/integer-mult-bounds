"""Dylan Crow, with Anthropic Claude assistance; Apache-2.0. Compile v2: A-rules (built from sources) before the scatter, B-rules (helpers only) and deliveries after,
interleaved by frame dimension.  Low reads at the symbol's own frame along one nested chain per target."""
import e8lib as E, frames as Fm, price as P, compile as C
from collections import defaultdict, Counter
V=E.V
def needed_symbols(h):
    needed=set(); todo=[u for t in range(V) for u in h.need[t]]
    while todo:
        u=todo.pop()
        if u in needed: continue
        needed.add(u)
        if h.kids[u]: todo.extend(h.kids[u])
    return needed
PHASEMODE=['allA']
def phases(h,needed):
    ph={}
    def get(u):
        if u<V: return 'S'
        if u in ph: return ph[u]
        ks=[get(c) for c in h.kids[u]]
        if PHASEMODE[0]=='allA':
            ph[u]='A' if all(k in ('S','A') for k in ks) else 'B'
        else:
            ph[u]='A' if ('S' in ks and all(k in ('S','A') for k in ks)) else 'B'
        return ph[u]
    for u in needed:
        if u>=V: get(u)
    return ph
def choose_low(h, needed, ph, drop=frozenset(), mode='longest'):
    lowset=set()
    for t in range(V):
        it=sorted(h.need[t], key=lambda u:(h.dim[u],u)); best={}
        for j,u in enumerate(it):
            b=[u]
            for i in range(j):
                v=it[i]
                if h.dim[v]<h.dim[u] and Fm.inside(h.frame[v],h.frame[u]) and len(best[v])+1>len(b): b=best[v]+[u]
            best[u]=b
        ch=max(best.values(),key=len) if best else []
        for u in ch:
            if h.dim[u]<7 and (t,u) not in drop: lowset.add((t,u))
    return lowset
def compile2(h, lowset=None, drop=frozenset(), centres=None):
    needed=needed_symbols(h); ph=phases(h,needed)
    if lowset is None: lowset=choose_low(h,needed,ph,drop)
    # uses: (phaseorder, dim, kind, frame, who)   phaseorder 0=A 1=B ; kind 0 rule-child 1 delivery
    uses=defaultdict(list)
    for w in needed:
        if w<V: continue
        po=0 if ph[w]=='A' else 1
        for c in h.kids[w]: uses[c].append((po,h.dim[w],0,h.frame[w],w))
    for t in range(V):
        for u in h.need[t]:
            if (t,u) in lowset: uses[u].append((1,h.dim[u],1,h.frame[u],t))
            else: uses[u].append((1,7,1,Fm.HYP[t],t))
    chains={}; chain_of={}
    for u in needed:
        ev=sorted(uses[u],key=lambda e:(e[0],e[1],e[2],e[4]))
        cl=[]
        for e in ev:
            best=None
            for i,ch in enumerate(cl):
                last=ch[-1]
                if last[2]==1 and last[1]==7 and last[3]!=e[3]: continue
                if last[3]==e[3] or (last[1]<e[1] and Fm.inside(last[3],e[3])):
                    if best is None or cl[best][-1][1]<last[1]: best=i
            if best is None: cl.append([e]); best=len(cl)-1
            else: cl[best].append(e)
            chain_of[(u,e[2],e[4])]=best
        chains[u]=cl
    W=C.Word(); reg={}
    # sources: x takes a chain made only of A-uses (prefer the longest); others carriers
    for s in range(V):
        if s not in needed: continue
        cl=chains[s]; xi=None
        cand=[i for i,ch in enumerate(cl) if all(e[0]==0 for e in ch)]
        if cand: xi=max(cand,key=lambda i:len(cl[i]))
        car=[]
        for i in range(len(cl)):
            if i==xi: reg[(s,i)]=C.X(s)
            else: q=W.helper(); car.append(q); reg[(s,i)]=q
        if car: W.A.append((Fm.LINE[s],C.X(s),None,car))
    W.ncarrier=sum(1 for k,r in reg.items() if r>=2*V)
    inplace=[0]; ncopy=[0]
    def form(w,lst):
        F=h.frame[w]; info=[]
        for c in h.kids[w]:
            i=chain_of[(c,0,w)]; ch=chains[c][i]
            info.append((c,i,ch[-1][2]==0 and ch[-1][4]==w))
        host=None
        for c,i,end in info:
            if end and reg[(c,i)]>=2*V: host=(c,i); break
        if host:
            q=reg.pop(host); lst.append((F,q,[reg[(c,i)] for c,i,_ in info if (c,i)!=host],None)); inplace[0]+=1
        else:
            q=W.helper(); lst.append((F,q,[reg[(c,i)] for c,i,_ in info],None))
        reg[(w,0)]=q; n=len(chains[w])
        if n>1:
            qs=[W.helper() for _ in range(n-1)]; ncopy[0]+=n-1
            lst.append((F,q,None,qs))
            for i,qq in enumerate(qs): reg[(w,i+1)]=qq
    Arules=sorted((w for w in needed if w>=V and ph[w]=='A'),key=lambda w:(h.dim[w],w))
    for w in Arules: form(w,W.A)
    cent=centres or C.default_centres()
    for sup in cent:
        q=W.helper(); W.A.append((Fm.FULL,q,[C.X(s) for s in range(V) if sup>>s&1],None)); W.ret.append(q)
    # phase B events
    ev=[]
    for w in needed:
        if w>=V and ph[w]=='B': ev.append((h.dim[w],0,w))
    lowby=defaultdict(list)
    for (t,u) in lowset: lowby[u].append(t)
    for u in lowby: ev.append((h.dim[u],1,u))
    for t in range(V): ev.append((7,2,t))
    ev.sort()
    for d,k,a in ev:
        if k==0: form(a,W.B)
        elif k==1:
            u=a
            for t in sorted(lowby[u]):
                W.B.append((h.frame[u],C.Y(t),[reg[(u,chain_of[(u,1,t)])]],None))
        else:
            t=a; srcs=[reg[(u,chain_of[(u,1,t)])] for u in h.need[t] if (t,u) not in lowset]
            if srcs: W.B.append((Fm.HYP[t],C.Y(t),srcs,None))
    W.stats=dict(R=W.nh,carriers=W.ncarrier,Arules=len(Arules),Brules=sum(1 for w in needed if w>=V and ph[w]=='B'),
                 inplace=inplace[0],copies=ncopy[0],low=len(lowset),chains=sum(len(c) for c in chains.values()))
    return W
if __name__=='__main__':
    import pickle,sys
    from repair import Hier
    import __main__; __main__.Hier=Hier
    try:
        import ham1; __main__.SH=ham1.SH
    except Exception: pass
    h=pickle.load(open(sys.argv[1],'rb'))
    if len(sys.argv)>2: PHASEMODE[0]=sys.argv[2]
    W=compile2(h)
    print(W.stats)
    print('f2 check bad targets/x:',[len(z) for z in C.f2_check(W)])
    s,deficit,D,steps=C.evaluate(W)
    print('R',W.nh,'saving %.6e'%s,'deficit',deficit,'D %.0f'%D,sorted(steps.items()))
    import diag; diag.diag(W)
