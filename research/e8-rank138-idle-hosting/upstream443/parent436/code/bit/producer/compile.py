"""Dylan Crow, with Anthropic Claude assistance; Apache-2.0. Compile a Re-Pair hierarchy into an explicit bit word (frames = root masks) and price it.
Registers: x 0..119, y 120..239, helpers 240.. .  Gate: (phase, frame, dst, [srcs])  dst += sum(srcs) over F2."""
import e8lib as E, frames as Fm, price as P
from collections import defaultdict, Counter
V=E.V
class Word:
    def __init__(self):
        self.nh=0; self.A=[]; self.B=[]; self.ret=[]
    def helper(self):
        r=2*V+self.nh; self.nh+=1; return r
def X(s): return s
def Y(t): return V+t
def compile_h(h, low=True, drop=frozenset(), centres=None):
    need=h.need
    needed=set(); todo=[u for t in range(V) for u in need[t]]
    while todo:
        u=todo.pop()
        if u in needed: continue
        needed.add(u)
        if h.kids[u]: todo.extend(h.kids[u])
    rules=sorted((u for u in needed if h.kids[u]), key=lambda u:(h.dim[u],u))
    # low reads: longest nested chain of needed symbols per target
    lowset=set()
    if low:
        for t in range(V):
            it=sorted(need[t], key=lambda u:(h.dim[u],u)); best={}
            for j,u in enumerate(it):
                b=[u]
                for i in range(j):
                    v=it[i]
                    if (h.dim[v]<h.dim[u] and Fm.inside(h.frame[v],h.frame[u])) and len(best[v])+1>len(b): b=best[v]+[u]
                best[u]=b
            ch=max(best.values(),key=len) if best else []
            for u in ch:
                if h.dim[u]<7 and (t,u) not in drop: lowset.add((t,u))
    uses=defaultdict(list)
    for w in rules:
        for c in h.kids[w]: uses[c].append((0,h.dim[w],h.frame[w],w))
    for t in range(V):
        for u in need[t]:
            if (t,u) in lowset: uses[u].append((1,h.dim[u],h.frame[u],t))
            else: uses[u].append((1,7,Fm.HYP[t],t))
    chains={}; chain_of={}
    for u in needed:
        ev=sorted(uses[u]); cl=[]
        for e in ev:
            best=None
            for i,ch in enumerate(cl):
                last=ch[-1]
                if last[0]==1 and last[1]==7 and last[2]!=e[2]: continue
                if last[2]==e[2] or (last[1]<e[1] and Fm.inside(last[2],e[2])):
                    if best is None or cl[best][-1][1]<last[1]: best=i
            if best is None: cl.append([e]); best=len(cl)-1
            else: cl[best].append(e)
            chain_of[(u,e[0],e[3])]=best
        chains[u]=cl
    W=Word(); reg={}
    # phase A: sources
    for s in range(V):
        if s not in needed: continue
        cl=chains[s]
        xi=None
        for i,ch in enumerate(cl):
            if all(e[0]==0 for e in ch): xi=i; break
        car=[]
        for i,ch in enumerate(cl):
            if i==xi: reg[(s,i)]=X(s)
            else:
                q=W.helper(); car.append(q); reg[(s,i)]=q
        if car: W.A.append((Fm.LINE[s],X(s),None,car))   # fan-out copy: each carrier += x_s at line
    inplace=0
    for w in rules:
        F=h.frame[w]; ks=h.kids[w]
        info=[]
        for c in ks:
            i=chain_of[(c,0,w)]; ch=chains[c][i]
            info.append((c,i,ch[-1][0]==0 and ch[-1][3]==w))
        host=None
        for c,i,end in info:
            if end and reg[(c,i)]>=2*V: host=(c,i); break
        if host:
            q=reg.pop(host); srcs=[reg[(c,i)] for c,i,_ in info if (c,i)!=host]
            W.A.append((F,q,srcs,None)); inplace+=1
        else:
            q=W.helper(); W.A.append((F,q,[reg[(c,i)] for c,i,_ in info],None))
        reg[(w,0)]=q
        n=len(chains[w])
        if n>1:
            qs=[W.helper() for _ in range(n-1)]
            W.A.append((F,q,None,qs))
            for i,qq in enumerate(qs): reg[(w,i+1)]=qq
    # totals
    cent=centres or default_centres()
    for sup in cent:
        q=W.helper(); W.A.append((Fm.FULL,q,[X(s) for s in range(V) if sup>>s&1],None)); W.ret.append(q)
    # phase B: deliveries sorted by frame dim
    ev=[]
    for t in range(V):
        hyp=[]
        for u in need[t]:
            r=reg[(u,chain_of[(u,1,t)])]
            if (t,u) in lowset: ev.append((h.dim[u],h.frame[u],Y(t),[r]))
            else: hyp.append(r)
        if hyp: ev.append((7,Fm.HYP[t],Y(t),hyp))
    ev.sort(key=lambda e:(e[0],e[2]))
    for d,F,yt,srcs in ev: W.B.append((F,yt,srcs,None))
    W.stats=dict(R=W.nh,rules=len(rules),inplace=inplace,low=len(lowset),chains=sum(len(c) for c in chains.values()))
    return W
_DC=None
def default_centres():
    """T0 = all lines; T_i = {S : B(a_i,S)=1} for a basis a_i of E8/2E8 given by 8 lines spanning it mod 2."""
    global _DC
    if _DC: return _DC
    # pick 8 lines whose images are independent mod 2 : use B-matrix rank
    B=[[E.G[a][b]&1 for b in range(V)] for a in range(V)]
    rows=[]; basis=[]; piv={}
    for a in range(V):
        m=sum(B[a][b]<<b for b in range(V)); m0=m
        while m:
            p=m.bit_length()-1
            if p in piv: m^=piv[p]
            else: piv[p]=m; basis.append(a); break
        if len(basis)==8: break
    _DC=[(1<<V)-1]+[sum(B[a][b]<<b for b in range(V)) for a in basis]
    return _DC
def decoder(cent):
    """for each target t, the set of centres it reads so that sum = 1 + B(t,.) (as masks); verify."""
    import itertools
    full=(1<<V)-1
    B=[sum((E.G[a][b]&1)<<b for b in range(V)) for a in range(V)]
    reads=[]
    for t in range(V):
        want=full^B[t]
        found=None
        for k in range(len(cent)+1):
            for C in itertools.combinations(range(len(cent)),k):
                m=0
                for c in C: m^=cent[c]
                if m==want: found=C; break
            if found is not None: break
        assert found is not None
        reads.append(found)
    return reads
def chains_of_word(W, cent_reads=None):
    """legality replay: returns per-register list of frame dims, asserts nesting and common frame."""
    nreg=2*V+W.nh
    cur=[Fm.LINE[s] for s in range(V)]+[0]*V+[0]*W.nh
    dims=[[1] for _ in range(V)]+[[0] for _ in range(V+W.nh)]
    def climb(r,F):
        if cur[r]==F: return
        assert Fm.inside(cur[r],F) and cur[r]!=F, ('not nested',r)
        cur[r]=F; dims[r].append(Fm.dim(F))
    for ph in ('A','B'):
        if ph=='B':
            for q in W.ret: assert cur[q]==Fm.FULL
            assert all(cur[Y(t)]==0 for t in range(V))
        for F,dst,srcs,outs in getattr(W,ph):
            regs=[dst]+(srcs or [])+(outs or [])
            assert len(set(regs))==len(regs)
            for r in regs: climb(r,F)
    for s in range(V): climb(X(s),Fm.FULL)
    for t in range(V): climb(Y(t),Fm.HYP[t])
    for q in range(2*V,nreg): climb(q,Fm.FULL)
    return dims
def f2_check(W, need_low=None):
    """forward F2 replay on source columns only (no dirt): y_t must end with exactly x_t (after centre reads)."""
    val=[1<<s for s in range(V)]+[0]*V+[0]*W.nh
    for F,dst,srcs,outs in W.A:
        if srcs is not None:
            for s in srcs: val[dst]^=val[s]
        if outs is not None:
            for o in outs: val[o]^=val[dst]
    cent=[val[q] for q in W.ret]
    reads=decoder(cent)
    for t in range(V):
        for c in reads[t]: val[Y(t)]^=cent[c]
    for F,dst,srcs,outs in W.B:
        if srcs is not None:
            for s in srcs: val[dst]^=val[s]
        if outs is not None:
            for o in outs: val[o]^=val[dst]
    bad=[t for t in range(V) if val[Y(t)]!=1<<t]
    xbad=[s for s in range(V) if val[s]!=1<<s]
    return bad,xbad
def evaluate(W):
    dims=chains_of_word(W)
    steps=Counter()
    for d in dims:
        for a,b in zip(d,d[1:]): steps[b-a]+=1
    s,deficit,D=P.price(steps,W.nh)
    return s,deficit,D,steps
if __name__=='__main__':
    import pickle,sys
    from repair import Hier
    import __main__; __main__.Hier=Hier
    h=pickle.load(open(sys.argv[1],'rb'))
    W=compile_h(h)
    print(W.stats)
    print('f2 check bad targets/x:',[len(z) for z in f2_check(W)])
    s,deficit,D,steps=evaluate(W)
    print('R',W.nh,'saving %.6e'%s,'deficit',deficit,'D %.0f'%D,sorted(steps.items()))
