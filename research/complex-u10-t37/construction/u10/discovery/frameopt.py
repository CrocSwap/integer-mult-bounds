# Exact per-component frame optimiser (chain contract only; cones checked by audit_local afterwards).
import sys,itertools,collections
sys.path.insert(0,'/tmp/don')
from mover import basis,regs,FULLF
def span(B):
    s=1  # bit0 = zero vector
    for y in B:
        t=s; x=0
        # s |= s shifted by xor y : do explicitly
        nv=0
        bits=s
        while bits:
            lb=bits&-bits; i=lb.bit_length()-1; nv|=1<<(i^y); bits^=lb
        s|=nv
    return s
SPC={}
def mem(F):
    F=tuple(F); r=SPC.get(F)
    if r is None: r=span(F); SPC[F]=r
    return r
def subspaces(dimk):
    # all subspaces of F2^k as basis tuples of coordinate vectors (ints < 2^k)
    out=set()
    vecs=range(1,1<<dimk)
    out.add(())
    frontier={()}
    while frontier:
        nf=set()
        for S in frontier:
            ms=span(S)
            for x in vecs:
                if not ms>>x&1:
                    T=basis(list(S)+[x])
                    if T not in out: out.add(T); nf.add(T)
        frontier=nf
    return list(out)
SUBS={k:subspaces(k) for k in range(0,5)}
def between(L,U):
    L=basis(L);U=basis(U)
    if len(L)==len(U): return [L]
    mL=mem(L); comp=[]
    cur=list(L)
    for x in U:
        if not span(basis(cur))>>x&1: comp.append(x); cur.append(x)
    k=len(comp)
    if k>4: return None
    res=[]
    for W in SUBS[k]:
        vs=[]
        for c in W:
            v=0
            for i in range(k):
                if c>>i&1: v^=comp[i]
            vs.append(v)
        res.append(basis(list(L)+vs))
    return res
def optimise(w,b=0.001665,m=73,verbose=False,maxcomp=200000):
    f=lambda r:r*((m/r)**b-1) if r>0 else 0.0
    v=112;R=w['report']['R'];n=2*v+R
    full=basis(FULLF)
    end=[full]*v+[basis([x for x in range(1,512) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*R
    for q,U in w['helper_final'].items(): end[int(q)]=basis(U)
    start=[(p,) for p in w['ports']]+[()]*(v+R)
    for q,U in w['start_extra'].items(): start[int(q)]=basis(U)
    nodes=[]  # dict(fixed:F or None, regs, ref)
    seqs=[[] for _ in range(n)]
    def add(regsl,fixed,ref):
        k=len(nodes); nodes.append(dict(regs=regsl,fixed=fixed,ref=ref))
        for r in regsl: seqs[r].append(k)
        return k
    for r in range(n): add([r],start[r],None)
    for i,e in enumerate(w['A']): add(regs(e),None,('A',i))
    lev={int(t):basis(U) for t,U in w.get('target_levels',{}).items()}
    for q,U in zip(w['centers'],w['center_frames']): add([q],basis(U),None)
    for t in range(v): add([v+t],lev.get(t,()),None)
    for i,e in enumerate(w['B']): add(regs(e),None,('B',i))
    for j,(i,U) in enumerate(w['early_cleanup']): add(regs(w['cleanup'][i]),None,('T',j))
    for r in range(n): add([r],end[r],None)
    prv=collections.defaultdict(dict); nxt=collections.defaultdict(dict)
    for r in range(n):
        s=seqs[r]
        for a,c in zip(s,s[1:]): nxt[a][r]=c; prv[c][r]=a
    N=len(nodes); L=[None]*N; U=[None]*N
    order=list(range(N))  # creation order is a topological order
    for k in order:
        z=nodes[k]
        J=basis([x for r in z['regs'] if r in prv[k] for x in L[prv[k][r]]])
        if z['fixed'] is not None:
            if (mem(J)&~mem(z['fixed'])): return None,'fixed lower violation %s'%k
            L[k]=z['fixed']
        else: L[k]=J
    for k in reversed(order):
        z=nodes[k]
        if z['fixed'] is not None: U[k]=z['fixed']; continue
        M=None
        for r in z['regs']:
            c=nxt[k][r]; mm=mem(U[c])
            M=mm if M is None else M&mm
        vecs=[x for x in range(1,512) if M>>x&1]
        U[k]=basis(vecs)
        if mem(L[k])&~mem(U[k]): return None,'interval empty %s'%(z['ref'],)
    choice={}
    free=[k for k in range(N) if nodes[k]['fixed'] is None and len(L[k])!=len(U[k])]
    F=[L[k] if nodes[k]['fixed'] is None else nodes[k]['fixed'] for k in range(N)]
    # components among free nodes connected by register adjacency
    fs=set(free); par={k:k for k in free}
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for k in free:
        for r,c in nxt[k].items():
            if c in fs: par[find(k)]=find(c)
    comps=collections.defaultdict(list)
    for k in free: comps[find(k)].append(k)
    stats=collections.Counter()
    orig={}
    for k,z in enumerate(nodes):
        if z['ref'] is None: continue
        s,i=z['ref']
        o=w['A'][i][-1] if s=='A' else (w['B'][i][-1] if s=='B' else w['early_cleanup'][i][1])
        orig[k]=basis(o)
    OPT={}
    for k in free:
        o=between(L[k],U[k])
        if o is None: return None,'big interval'
        OPT[k]=o
        ok=orig.get(k)
        if ok is not None and not (mem(L[k])&~mem(ok)) and not (mem(ok)&~mem(U[k])): F[k]=ok
    def feasible_all():
        for k in free:
            for r,p in prv[k].items():
                if mem(F[p])&~mem(F[k]): return False
            for r,q in nxt[k].items():
                if mem(F[k])&~mem(F[q]): return False
        return True
    # repair infeasibility greedily: lower to L where violations
    for it in range(50):
        bad=False
        for k in free:
            for r,p in prv[k].items():
                if mem(F[p])&~mem(F[k]): F[k]=basis(list(F[k])+list(F[p])); bad=True
        for k in free:
            for r,q in nxt[k].items():
                if mem(F[k])&~mem(F[q]): bad=True
        if not bad: break
    if not feasible_all():
        for k in free: F[k]=L[k]
    def local(k,Fk):
        c=0.0
        for r,p in prv[k].items():
            if mem(F[p])&~mem(Fk): return None
            c+=f(len(Fk)-len(F[p]))
        for r,q in nxt[k].items():
            if mem(Fk)&~mem(F[q]): return None
            c+=f(len(F[q])-len(Fk))
        return c
    for sweep in range(30):
        improved=0
        for k in free:
            cur=local(k,F[k]); best=(cur,F[k])
            for Fk in OPT[k]:
                c=local(k,Fk)
                if c is not None and c<best[0]-1e-15: best=(c,Fk)
            if best[1]!=F[k]: F[k]=best[1]; improved+=1
        # pair moves along register adjacency
        for k in free:
            for r,q in list(nxt[k].items()):
                if q not in fs: continue
                old=(F[k],F[q]); c0=local(k,F[k])+local(q,F[q])-f(len(F[q])-len(F[k]))
                bestp=(c0,old)
                for a in OPT[k]:
                    F[k]=a
                    for bq in OPT[q]:
                        if mem(a)&~mem(bq): continue
                        F[q]=bq
                        ca=local(k,a); cb=local(q,bq)
                        if ca is None or cb is None: continue
                        c=ca+cb-f(len(bq)-len(a))
                        if c<bestp[0]-1e-15: bestp=(c,(a,bq))
                F[k],F[q]=bestp[1]
                if bestp[1]!=old: improved+=1
        if not improved: break
    stats=collections.Counter(len(v) for v in comps.values())
    for k,z in enumerate(nodes):
        if z['ref'] is None: continue
        s,i=z['ref']
        if s=='A': w['A'][i][-1]=list(F[k])
        elif s=='B': w['B'][i][-1]=list(F[k])
        else: w['early_cleanup'][i][1]=list(F[k])
    return w,dict(free=len(free),comps=dict(stats))
