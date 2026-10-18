"""Partial leaver cells: for a key (p,eps) with leaver operands in two request blocks, replace the face events,
the three face copies, the target reads (incl. own rows) and the M formation by a helper-free circuit.
Exact: symbolic replay over atoms; frames: full-word replay."""
import pickle,json,sys,itertools as it
from collections import Counter,defaultdict
from fractions import Fraction as Q
sys.path.insert(0,sys.path[0])
from rawframes import basis,inside,hyper,FULL
from copyelim import replay,rows_of,fee
v=120
def load(cen,proto):
    d=pickle.load(open(cen,'rb'));P=json.load(open(proto))['binary_ports']
    return d,P,[list(e) for e in d['A']+d['B']],240+d['NH']
def key_parts(d,W,key):
    face={c:f for (c,pp,ee),f in d['face'].items() if (pp,ee)==key}
    req=d['requests']
    lv=[c for c in sorted(face) if (c,)+key in req];m=[c for c in sorted(face) if (c,)+key not in req]
    assert len(lv)==2 and len(m)==1
    c3=m[0];z=face[c3]['t']
    atoms=[];targets=[]
    for c in lv:atoms+= [face[c]['s'],face[c]['t']];targets+=[t for t,_ in req[(c,)+key]]
    atoms.append(z)
    pk={k[3]:val[0] for k,val in d['packets'].items() if (k[1],k[2])==key}
    copies=[r for (k,val) in d['packets'].items() if (k[1],k[2])==key for r in [val[0]] if r>=2*v and r not in atoms]
    Mreg=d['Ms'][(c3,)+key][0]
    return dict(lv=lv,c3=c3,atoms=atoms,targets=targets,copies=copies,M=Mreg,face=face)
def first_write_after(W,r,k0):
    return next((k for k in range(k0+1,len(W)) if W[k][1]==r),None)
def segment(d,W,K):
    """events to delete: face events in lv blocks, copy events, target reads of atoms/copies (own rows incl.), M event."""
    A=set(K['atoms']);C=set(K['copies']);T=set(v+t for t in K['targets'])
    dele=[]
    for k,e in enumerate(W):
        if e[0]!='add':continue
        t,s=e[1],e[2]
        if t in C and s in A:dele.append(k)                       # copy
        elif t in T and (s in A or s in C):dele.append(k)          # target reads (own rows, faces, copies)
        elif t in A and s in A and t!=K['atoms'][4] :dele.append(k)   # face events in leaver blocks, M event
        elif t==K['M'] and t in C and s in C:dele.append(k)            # M formed inside a copy (4567 class)
    return dele
def symbolic(W,K,dele,nreg):
    """values of atoms at the first deleted event; contributions to targets; M value; check deleted set is closed."""
    k0=dele[0]
    # atom registers must not be written between k0 and their last deleted use, except by deleted events
    sym={}
    for i,r in enumerate(K['atoms']):sym[r]={i:Q(1)}
    for r in K['copies']:sym[r]={}
    for t in K['targets']:sym[v+t]={}
    for k in dele:
        e=W[k];t,s,q=e[1],e[2],Q(e[3],e[4])
        for j,x in sym.get(s,{}).items():
            sym[t][j]=sym[t].get(j,Q(0))+q*x
            if not sym[t][j]:del sym[t][j]
    # writes to atoms by non-deleted events between k0 and their last deleted use?
    last=max(dele);bad=[]
    for k in range(k0,last+1):
        if k in set(dele):continue
        e=W[k]
        if e[1] in K['atoms'] or (e[1] in K['copies'] and e[1]!=K['M']) or (e[1]==K['M'] and k>max(dele)) or (v+0<=e[1]<2*v and e[1]-v in K['targets'] and e[0]=='add' and e[2] in sym):bad.append(k)
        if e[0]=='add' and (e[2] in K['copies']) and e[2]!=K['M']:bad.append(('copyread',k))
    return sym,bad
def frames_at(W,P,nreg,k0):
    cur=[(p,) for p in P]+[()]*(nreg-len(P))
    for e in W[:k0]:
        regs=(e[1],e[2]) if e[0]=='add' else (e[1],)
        G=basis(list(e[-1])+[x for r in regs for x in cur[r]])
        for r in regs:cur[r]=G
    return cur
def search(K,sym,cur0,P,maxdepth=18,maxstates=3_000_000,Mreg=None):
    atoms=K['atoms'];na=len(atoms)
    Ys=[v+t for t in K['targets']]
    goal={y:frozenset(sym[y]) for y in Ys}
    coefY={y:set(sym[y].values()) for y in Ys}
    Mgoal=frozenset(sym[K['M']]);Mreg=K['M'] if Mreg is None else Mreg
    regs=atoms+Ys;idx={r:i for i,r in enumerate(regs)}
    hy={y:hyper(P[y-v]) for y in Ys}
    S0=tuple(frozenset([i]) for i in range(na))+tuple(frozenset() for _ in Ys)
    F0=tuple(cur0[r] for r in regs)
    from collections import deque
    start=(S0,F0);seen={start:None};q=deque([(start,0)]);sol=[]
    while q:
        (S,F),dep=q.popleft()
        if all(S[idx[y]]==goal[y] for y in Ys) and S[idx[Mreg]]==Mgoal:
            sol.append((S,F));
            if len(sol)>=200:break
            continue
        if dep>=maxdepth or len(seen)>maxstates:continue
        for ti,t in enumerate(regs):
            for si,s in enumerate(regs[:na]):
                if ti==si:continue
                a,b=S[ti],S[si]
                if not b or a&b:continue
                if t in Ys:
                    if not (b<=goal[t]-a):continue
                    G=basis(list(F[ti])+list(F[si]))
                    if not inside(G,hy[t]):continue
                else:
                    G=basis(list(F[ti])+list(F[si]))
                NS=list(S);NS[ti]=a|b;NF=list(F);NF[ti]=G;NF[si]=G
                st=(tuple(NS),tuple(NF))
                if st in seen:continue
                seen[st]=((S,F),(t,s))
                q.append((st,dep+1))
    def path(st):
        out=[]
        while seen[st] is not None:
            prev,g=seen[st];out.append(g);st=prev
        return out[::-1]
    return [path(s) for s in sol],len(seen)
def taint_of(F,Ys,P):
    m=0
    for i,y in enumerate(Ys):
        if not inside(F,hyper(P[y-v])):m|=1<<i
    return m
def tsearch(K,sym,cur0,P,maxdepth=20,maxsol=5000,Mhosts=None,yy=True,extra=0):
    """BFS in the exact taint model. Returns all solutions of length <= minimal+extra."""
    atoms=K['atoms'];na=len(atoms);Ys=[v+t for t in K['targets']];ny=len(Ys)
    regs=atoms+Ys;nr=len(regs)
    full=lambda s:frozenset(s)
    goal=[None]*na+[frozenset(sym[y]) for y in Ys]
    Mgoal=frozenset(sym[K['M']])
    Mhosts=[atoms.index(K['M'])] if Mhosts is None else Mhosts
    S0=tuple(frozenset([i]) for i in range(na))+tuple(frozenset() for _ in Ys)
    T0=tuple(taint_of(cur0[r],Ys,P) for r in regs)
    assert all(T0[na+i]==0 for i in range(ny)),T0
    forb=[0]*na+[1<<i for i in range(ny)]
    from collections import deque
    start=(S0,T0);dist={start:0};par=defaultdict(list);q=deque([start]);best=None;goals=[]
    while q:
        st=q.popleft();dep=dist[st]
        if best is not None and dep>best+extra:break
        S,T=st
        if all(S[na+i]==goal[na+i] for i in range(ny)) and any(S[h]==Mgoal for h in Mhosts):
            if best is None:best=dep
            goals.append(st);continue
        if dep>=maxdepth:continue
        for ti in range(nr):
            for si in range(nr):
                if ti==si:continue
                a,b=S[ti],S[si]
                if not b or a&b:continue
                isy_t=ti>=na;isy_s=si>=na
                if isy_s and not (isy_t and yy):continue
                if isy_t and not (b<=goal[ti]-a):continue
                J=T[ti]|T[si]
                if J&(forb[ti]|forb[si]):continue
                NS=list(S);NS[ti]=a|b;NT=list(T);NT[ti]=J;NT[si]=J
                ns=(tuple(NS),tuple(NT))
                if ns not in dist:
                    dist[ns]=dep+1;q.append(ns)
                if dist[ns]==dep+1:par[ns].append((st,(regs[ti],regs[si])))
    return best,goals,par,dist,len(dist)
def paths(goal,par,limit=2000):
    out=[]
    def rec(st,acc):
        if len(out)>=limit:return
        if not par.get(st):out.append(acc[::-1]);return
        for prev,g in par[st]:rec(prev,acc+[g])
    rec(goal,[]);return out
YYLOG=[]
def coeffs(K,sym):
    """rank-one factorisation C[y][j]=r_y*c_j over atoms; M = mu * c."""
    Ys=[v+t for t in K['targets']];na=len(K['atoms'])
    c=[None]*na
    # pick c from first target that has each atom
    y0=Ys[0];r={y0:Q(1)}
    for j,x in sym[y0].items():c[j]=x
    changed=True
    while changed:
        changed=False
        for y in Ys:
            if y not in r:
                j=next((j for j in sym[y] if c[j] is not None),None)
                if j is not None:r[y]=sym[y][j]/c[j];changed=True
            if y in r:
                for j,x in sym[y].items():
                    if c[j] is None:c[j]=x/r[y];changed=True
    for y in Ys:
        for j,x in sym[y].items():assert x==r[y]*c[j],('not rank one',y,j)
    Mv=sym[K['M']];j0=next(iter(Mv));mu=Mv[j0]/c[j0]
    assert all(Mv[j]==mu*c[j] for j in Mv),'M not proportional'
    return r,c,mu
def build(W,K,sym,dele,sol,host,newh=(),halpha=None):
    """sol: list of (treg,sreg) register ids. returns new W."""
    atoms=K['atoms'];Ys=[v+t for t in K['targets']]
    r,c,mu=coeffs(K,sym)
    # atom register value = alpha_reg * sum_{j in set} c_j x_j ; initially alpha = 1/c_own
    alpha={a:1/c[i] for i,a in enumerate(atoms)}
    for h in newh:alpha[h]=None
    if halpha:alpha.update(halpha)
    gates=[]
    for t,s in sol:
        if t in Ys and s in Ys:q=r[t]/r[s];YYLOG.append((t,s,str(q)))
        elif t in Ys:q=r[t]/alpha[s]
        else:
            if alpha[t] is None:alpha[t]=alpha[s]
            q=alpha[t]/alpha[s]
        gates.append(['add',t,s,q.numerator,q.denominator,[]])
    # host ends with alpha_host*sum c_j x_j ; M register must hold mu*sum c_j x_j
    fix=mu/alpha[host]
    if fix!=1:gates.append(['scale',host,fix.numerator,fix.denominator,[]])
    last=dele[-1];M=K['M']
    ownregs={v+t:K['own'][t] for t in K['targets']} if 'own' in K else {}
    isown=lambda e:e[0]=='add' and e[1] in ownregs and e[2]==ownregs[e[1]]
    import os as _os
    if ownregs and _os.environ.get('PCELL_MOVEOWN'):
        k0=next(k for k in dele if not isown(W[k]))
    elif ownregs:
        dele=[k for k in dele if not isown(W[k])]
        gates=[g for g in gates if not isown(g)]
        k0=dele[0]
    else:k0=dele[0]
    ds=set(dele)
    NW=[]
    for k,e in enumerate(W):
        if k==k0:NW.extend(gates)
        if k in ds:continue
        if k>k0 and host!=M:
            e=list(e)
            if e[1]==M:e[1]=host
            if e[0]=='add' and e[2]==M:e[2]=host
        NW.append(e)
    return NW
def check(W,NW,K,host,n,P,H0):
    R0=rows_of(W,n);R=rows_of(NW,n);n0=len(R0)
    M=K['M'];bad=[]
    R0=R0+[{}]*(len(R)-len(R0))
    for x in range(len(R)):
        if x in K['atoms'] or x in K['copies'] or x>=n0:continue
        if R[x]!=R0[x]:bad.append(x)
    if R[host]!=R0[M]:bad.append(('host',host))
    H,fb=replay(NW,P,n)
    dH=Counter(H);dH.subtract(H0);dH={a:b for a,b in dH.items() if b}
    return bad,fb,dH
