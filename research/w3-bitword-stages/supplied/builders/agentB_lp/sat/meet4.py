# SAT search for all-but-one designs in the abstract contamination model, with optional
# sigma>0 fresh registers (dirty start at a nonzero frame; dirt must cancel in outputs).
import sys, itertools, math, time, argparse, json
from pysat.formula import IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
g=lambda r: r*math.log(120/r) if r>0 else 0.0
ap=argparse.ArgumentParser()
ap.add_argument('--n',type=int,default=10)
ap.add_argument('--nf',type=int,default=10)
ap.add_argument('--T',type=int,default=5)
ap.add_argument('--maxlev',type=int,default=9)
ap.add_argument('--sym',type=str,default='')
ap.add_argument('--sigF',type=int,default=1)       # allow sigma>0 fresh registers
ap.add_argument('--totalcap',type=float,default=0)
ap.add_argument('--forcesig',type=str,default='')
ap.add_argument('--forcerole',type=str,default='')   # e.g. RO: all R are outputs (F partners)
ap.add_argument('--reps',type=str,default='0,5,10,15')
ap.add_argument('--solver',type=str,default='cadical195')
ap.add_argument('--out',type=str,default='')
a=ap.parse_args()
n=a.n; NF=a.nf; T=a.T; N=n+NF; NB=n+NF   # content bits: blocks + dirt of each fresh reg
pool=IDPool(); H=[]
V=lambda *x: pool.id(x)
regs=list(range(N)); isR=lambda r: r<n
TRUE=V('TRUE'); H.append([TRUE])
def card_eq(lits,k): H.extend(CardEnc.equals(lits=lits,bound=k,vpool=pool,encoding=EncType.seqcounter).clauses)
def card_le(lits,k): H.extend(CardEnc.atmost(lits=lits,bound=k,vpool=pool,encoding=EncType.seqcounter).clauses)
for r in regs:
    H.append([V('O',r),V('M',r)]); H.append([-V('O',r),-V('M',r)])
    card_eq([V('tgt',r,z) for z in range(n)],1)
for z in range(n):
    for role in ('O','M'):
        aux=[]
        for r in regs:
            q=V('rt',role,r,z); aux.append(q)
            H.extend([[-q,V(role,r)],[-q,V('tgt',r,z)],[q,-V(role,r),-V('tgt',r,z)]])
        card_eq(aux,1)
def meet(r,s,t): return V('meet',min(r,s),max(r,s),t)
# sigma flags
for r in regs:
    if isR(r) or not a.sigF: H.append([-V('sig',r)])
# forced roles
if a.forcerole=='RO':
    for r in regs: H.append([V('O',r)] if isR(r) else [V('M',r)])
elif a.forcerole=='RM':
    for r in regs: H.append([V('M',r)] if isR(r) else [V('O',r)])
# forced sigma
for r in regs:
    if not isR(r) and a.forcesig:
        if a.forcesig=='all': H.append([V('sig',r)])
        elif a.forcesig in ('O','M'): H.append([-V(a.forcesig,r),V('sig',r)])
        elif a.forcesig=='half' and r<n+5: H.append([V('sig',r)])
# initial state
for r in regs:
    for x in range(n):
        if isR(r):
            H.append([V('K',r,0,x)] if x==r else [-V('K',r,0,x)])
        else:
            H.append([V('sig',r),-V('K',r,0,x)])     # not sig -> K0 empty
    if not isR(r):
        H.append([-V('sig',r)]+[V('K',r,0,x) for x in range(n)])   # sig -> K0 nonempty
    for x in range(NB):
        if isR(r): H.append([V('C',r,0,x)] if x==r else [-V('C',r,0,x)])
        else:
            if x==n+(r-n): H.extend([[-V('C',r,0,x),V('sig',r)],[V('C',r,0,x),-V('sig',r)]])
            else: H.append([-V('C',r,0,x)])
for t in range(1,T+1):
    for a_,b_,c_ in itertools.combinations(regs,3):
        ab,ac,bc=meet(a_,b_,t),meet(a_,c_,t),meet(b_,c_,t)
        H.extend([[-ab,-bc,ac],[-ab,-ac,bc],[-ac,-bc,ab]])
    for r in regs:
        for x in range(n):
            k_new=V('K',r,t,x); k_old=V('K',r,t-1,x); terms=[k_old]
            for s in regs:
                if s==r: continue
                q=V('Ka',r,s,t,x)
                H.extend([[-q,meet(r,s,t)],[-q,V('K',s,t-1,x)],[q,-meet(r,s,t),-V('K',s,t-1,x)]])
                terms.append(q)
            H.append([-k_new]+terms)
            for tm in terms: H.append([k_new,-tm])
        for s in regs:
            if s==r: continue
            H.append([-V('give',r,s,t),meet(r,s,t)])
        gl=[V('give',r,s,t) for s in regs if s!=r]
        rc=V('recv',r,t); H.append([-rc]+gl)
        for l in gl: H.append([rc,-l])
    for r in regs:
        for s in regs:
            if s!=r: H.append([-V('give',r,s,t),-V('recv',s,t)])
    for r in regs:
        for x in range(NB):
            prev=V('C',r,t-1,x)
            for s in regs:
                if s==r: continue
                q=V('Ca',r,s,t,x)
                H.extend([[-q,V('give',r,s,t)],[-q,V('C',s,t-1,x)],[q,-V('give',r,s,t),-V('C',s,t-1,x)]])
                nx=V('Cx',r,s,t,x)
                H.extend([[-nx,prev,q],[-nx,-prev,-q],[nx,-prev,q],[nx,prev,-q]]); prev=nx
            cur=V('C',r,t,x); H.extend([[-cur,prev],[cur,-prev]])
            if x<n: H.append([-cur,V('K',r,t,x)])
# targets never contaminated (all t incl 0)
for r in regs:
    for t in range(0,T+1):
        for z in range(n): H.append([-V('tgt',r,z),-V('K',r,t,z)])
# final merge
for z in range(n):
    for r in regs:
        for s in regs:
            if r==s: continue
            pr=[-V('rt','O',r,z),-V('rt','M',s,z)]
            for x in range(NB):
                want=(x<n and x!=z)
                if want: H.extend([pr+[V('C',r,T,x),V('C',s,T,x)],pr+[-V('C',r,T,x),-V('C',s,T,x)]])
                else: H.extend([pr+[V('C',r,T,x),-V('C',s,T,x)],pr+[-V('C',r,T,x),V('C',s,T,x)]])
# exact level counters for t=0..T
LV={}
for r in regs:
    for t in range(0,T+1):
        xs=[V('K',r,t,x) for x in range(n)]
        prev=[TRUE]+[-TRUE]*n
        for i,xi in enumerate(xs,1):
            cur=[TRUE]
            for j in range(1,n+1):
                c=V('cnt',r,t,i,j); a1=prev[j]; a2=prev[j-1]
                H.extend([[-c,a1,xi],[-c,a1,a2],[c,-a1],[c,-xi,-a2]]); cur.append(c)
            prev=cur
        LV[(r,t)]=prev[1:]
# visited levels: vis[r][k] (any t in 0..T with |K|==k, k>=1). start level for R is 1; for sig F it's |K0|.
for r in regs:
    for k in range(1,n+1):
        vk=V('vis',r,k); eqs=[]
        for t in range(0,T+1):
            rhs=LV[(r,t)]; e=V('eq',r,t,k)
            ge=rhs[k-1]; gt=rhs[k] if k<n else None
            H.extend([[-e,ge]]+([[-e,-gt]] if gt else [])+[[e,-ge]+([gt] if gt else [])]); eqs.append(e)
        H.append([-vk]+eqs)
        for e in eqs: H.append([vk,-e])
    if not isR(r):
        # st[k]: start level = |K0| == k (only meaningful if sig)
        for k in range(1,n+1):
            st=V('st',r,k); rhs=LV[(r,0)]
            ge=rhs[k-1]; gt=rhs[k] if k<n else None
            H.extend([[-st,ge]]+([[-st,-gt]] if gt else [])+[[st,-ge]+([gt] if gt else [])])
    cnt=[V('vis',r,k) for k in range(1,n+1) if not (isR(r) and k==1)]
    if a.maxlev<9: card_le(cnt,a.maxlev+ (0 if isR(r) else 1)) if False else None
def pattern_cost(isr,sigf,Vs,role):
    if isr: dims=[3]; levs=[k for k in Vs if k>1]
    elif sigf: dims=[2*min(Vs)+1]; levs=[k for k in Vs if k>min(Vs)]
    else: dims=[0]; levs=list(Vs)
    for k in sorted(levs):
        d=2*k+1
        if d>dims[-1]: dims.append(d)
    tail=[21,22,24] if role=='O' else [21,24]
    dd=dims+[x for x in tail if x>dims[-1]]
    return sum(g(dd[i]-dd[i-1]) for i in range(1,len(dd)))
if a.maxlev<9:
    for r in regs:
        # number of stops beyond the start
        cnt=[V('vis',r,k) for k in range(1,n+1)]
        if isR(r): card_le([V('vis',r,k) for k in range(2,n+1)],a.maxlev)
        else:
            # stops = vis count (non-sig) or vis count - 1 (sig): enforce vis count <= maxlev + sig
            ex=V('extra',r); H.extend([[-ex,V('sig',r)],[ex,-V('sig',r)]])
            card_le(cnt+[-ex],a.maxlev+1)
if a.totalcap>0:
    reps=[int(x) for x in a.reps.split(',')]
    allu=[]
    for r in reps:
        U=[V('u',r,j) for j in range(1,121)]
        for j in range(1,120): H.append([-U[j],U[j-1]])
        allu+=U
        for mask in range(1,1<<9):
            Vs=[k+1 for k in range(9) if mask>>k&1]
            if isR(r) and 1 not in Vs: continue
            for sigf in ([False] if isR(r) else [False,True]):
                for role in ('O','M'):
                    c=pattern_cost(isR(r),sigf,Vs,role)
                    ci=min(120,int(math.ceil(c-1e-9)))
                    cl=[-V(role,r)]
                    for k in range(1,10): cl.append(-V('vis',r,k) if k in Vs else V('vis',r,k))
                    if not isR(r): cl.append(-V('sig',r) if sigf else V('sig',r))
                    if sigf:
                        # start level must be min(Vs)
                        cl.append(-V('st',r,min(Vs)))
                    H.append(cl+[V('u',r,ci)])
    B=int(math.floor(a.totalcap))
    H.extend(CardEnc.atmost(lits=allu,bound=B,vpool=pool,encoding=EncType.totalizer).clauses)
if a.sym:
    if a.sym=='z5': bp=lambda X: (X%5+1)%5+5*(X//5)
    elif a.sym=='z10': bp=lambda X: (X+1)%10
    rp=lambda r: bp(r) if r<n else n+bp(r-n)
    cbp=lambda x: bp(x) if x<n else n+bp(x-n)
    for r in regs:
        for z in range(n): H.extend([[-V('tgt',r,z),V('tgt',rp(r),bp(z))],[V('tgt',r,z),-V('tgt',rp(r),bp(z))]])
        for ro in ('O','M','sig'): H.extend([[-V(ro,r),V(ro,rp(r))],[V(ro,r),-V(ro,rp(r))]])
        for t in range(0,T+1):
            for x in range(n): H.extend([[-V('K',r,t,x),V('K',rp(r),t,bp(x))],[V('K',r,t,x),-V('K',rp(r),t,bp(x))]])
            for x in range(NB): H.extend([[-V('C',r,t,x),V('C',rp(r),t,cbp(x))],[V('C',r,t,x),-V('C',rp(r),t,cbp(x))]])
        for t in range(1,T+1):
            for s_ in regs:
                if s_==r: continue
                H.extend([[-V('give',r,s_,t),V('give',rp(r),rp(s_),t)],[V('give',r,s_,t),-V('give',rp(r),rp(s_),t)]])
                if r<s_:
                    m1=meet(r,s_,t); m2=meet(rp(r),rp(s_),t); H.extend([[-m1,m2],[m1,-m2]])
print('vars',pool.top,'clauses',len(H),file=sys.stderr,flush=True)
t0=time.time()
S=Solver(name=a.solver,bootstrap_with=H)
ok=S.solve()
print('SAT' if ok else 'UNSAT','time %.1f'%(time.time()-t0),flush=True)
if ok:
    Mset=set(l for l in S.get_model() if l>0)
    val=lambda *x: pool.id(x) in Mset
    total=0; design=[]
    for r in regs:
        role='O' if val('O',r) else 'M'
        z=[z for z in range(n) if val('tgt',r,z)][0]
        sig=val('sig',r)
        Ks=[frozenset(x for x in range(n) if val('K',r,t,x)) for t in range(T+1)]
        Vs=sorted(set(len(K) for K in (Ks if (sig or isR(r)) else Ks[1:]) if len(K)>0))
        c=pattern_cost(isR(r),sig,Vs,role); total+=c
        hist=[]
        for t in range(0,T+1):
            K=''.join('%d'%x for x in range(n) if val('K',r,t,x))
            C=''.join(('%d'%x if x<n else 'd%d'%(x-n)) for x in range(NB) if val('C',r,t,x))
            met=[s for s in regs if s!=r and t>0 and val('meet',min(r,s),max(r,s),t)]
            gv=[s for s in regs if s!=r and t>0 and val('give',r,s,t)]
            hist.append((t,K,C,met,gv))
        design.append(dict(r=r,R=isR(r),role=role,tgt=z,sig=sig,cost=c,hist=hist))
        print('reg %2d %s%s %s tgt %d levels %s cost %.1f'%(r,'R' if isR(r) else 'F','(sig)' if sig else '',role,z,Vs,c))
        for h in hist: print('      t%d K=%s C=%s meet=%s recv_from=%s'%h)
    print('TOTAL COST %.1f'%total)
    if a.out: json.dump(design,open(a.out,'w'))
