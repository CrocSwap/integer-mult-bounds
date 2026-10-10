# SAT search for all-but-one designs (abstract contamination model), with symmetry breaking,
# stop limits (distinct |K| levels per register) and exact cost evaluation of the found design.
import sys, itertools, math, time, argparse, json
from pysat.formula import IDPool, CNF
from pysat.card import CardEnc, EncType, ITotalizer
from pysat.solvers import Solver
g=lambda r: r*math.log(120/r) if r>0 else 0.0
ap=argparse.ArgumentParser()
ap.add_argument('--n',type=int,default=10)
ap.add_argument('--nf',type=int,default=10)
ap.add_argument('--T',type=int,default=5)
ap.add_argument('--ni',type=int,default=0)
ap.add_argument('--maxlev',type=int,default=9)      # max distinct levels (stops) per register (excluding R start level)
ap.add_argument('--forbid',type=str,default='')     # comma list of forbidden |K| levels for stops
ap.add_argument('--costcap',type=float,default=0)   # if >0: per-register cap on path cost (approx via forbidden level pairs)
ap.add_argument('--solver',type=str,default='cadical195')
ap.add_argument('--out',type=str,default='')
ap.add_argument('--timeout',type=int,default=0)
ap.add_argument('--sym',type=str,default='')
ap.add_argument('--cap',type=float,default=0)
ap.add_argument('--totalcap',type=float,default=0)
ap.add_argument('--reps',type=str,default='0,5,10,15')
ap.add_argument('--capR',type=float,default=0)
ap.add_argument('--capF',type=float,default=0)
ap.add_argument('--copyround',type=int,default=0)
a=ap.parse_args()
n=a.n; NF=a.nf; T=a.T; N=n+NF
pool=IDPool(); H=[]
V=lambda *x: pool.id(x)
regs=list(range(N)); isR=lambda r: r<n
def card_eq(lits,k): H.extend(CardEnc.equals(lits=lits,bound=k,vpool=pool,encoding=EncType.seqcounter).clauses)
def card_le(lits,k): H.extend(CardEnc.atmost(lits=lits,bound=k,vpool=pool,encoding=EncType.seqcounter).clauses)
for r in regs:
    H.append([V('O',r),V('M',r),V('I',r)])
    for x,y in itertools.combinations(['O','M','I'],2): H.append([-V(x,r),-V(y,r)])
    card_eq([V('tgt',r,z) for z in range(n)],1)
for z in range(n):
    for role in ('O','M'):
        aux=[]
        for r in regs:
            q=V('rt',role,r,z); aux.append(q)
            H.extend([[-q,V(role,r)],[-q,V('tgt',r,z)],[q,-V(role,r),-V('tgt',r,z)]])
        card_eq(aux,1)
card_le([V('I',r) for r in regs],a.ni)
# slot index for symmetry breaking among fresh registers: slot = 2*z + (role M)
for r in range(n,N):
    for s in range(2*n):
        z,ro=divmod(s,2)
        V('slot',r,s)
    for s in range(2*n):
        z,ro=divmod(s,2)
        sl=V('slot',r,s)
        H.extend([[-sl,V('tgt',r,z)],[-sl,V('M' if ro else 'O',r)],[sl,-V('tgt',r,z),-V('M' if ro else 'O',r)]])
for r in (range(n,N-1) if not a.sym else []):
    # slot(r) < slot(r+1): forbid slot(r)=s and slot(r+1)=s' with s'<=s (only when neither is internal)
    for s in range(2*n):
        for s2 in range(0,s+1):
            H.append([-V('slot',r,s),-V('slot',r+1,s2)])
def meet(r,s,t): return V('meet',min(r,s),max(r,s),t)
for r in regs:
    for x in range(n):
        val = isR(r) and x==r
        H.append([V('K',r,0,x)] if val else [-V('K',r,0,x)])
        H.append([V('C',r,0,x)] if val else [-V('C',r,0,x)])
for t in range(1,T+1):
    for a_,b_,c_ in itertools.combinations(regs,3):
        ab,ac,bc=meet(a_,b_,t),meet(a_,c_,t),meet(b_,c_,t)
        H.extend([[-ab,-bc,ac],[-ab,-ac,bc],[-ac,-bc,ab]])
    for r in regs:
        for x in range(n):
            k_new=V('K',r,t,x); k_old=V('K',r,t-1,x)
            terms=[k_old]
            for s in regs:
                if s==r: continue
                q=V('Ka',r,s,t,x)
                H.extend([[-q,meet(r,s,t)],[-q,V('K',s,t-1,x)],[q,-meet(r,s,t),-V('K',s,t-1,x)]])
                terms.append(q)
            H.append([-k_new]+terms)
            for tm in terms: H.append([k_new,-tm])
        for z in range(n):
            H.append([V('I',r),-V('tgt',r,z),-V('K',r,t,z)])
        for s in regs:
            if s==r: continue
            H.append([-V('give',r,s,t),meet(r,s,t)])
        gl=[V('give',r,s,t) for s in regs if s!=r]
        recv=V('recv',r,t)
        H.append([-recv]+gl)
        for l in gl: H.append([recv,-l])
    for r in regs:
        for s in regs:
            if s!=r: H.append([-V('give',r,s,t),-V('recv',s,t)])
    for r in regs:
        for x in range(n):
            prev=V('C',r,t-1,x)
            for s in regs:
                if s==r: continue
                q=V('Ca',r,s,t,x)
                H.extend([[-q,V('give',r,s,t)],[-q,V('C',s,t-1,x)],[q,-V('give',r,s,t),-V('C',s,t-1,x)]])
                nx=V('Cx',r,s,t,x)
                H.extend([[-nx,prev,q],[-nx,-prev,-q],[nx,-prev,q],[nx,prev,-q]])
                prev=nx
            cur=V('C',r,t,x)
            H.extend([[-cur,prev],[cur,-prev]])
            H.append([-cur,V('K',r,t,x)])
for z in range(n):
    for r in regs:
        for s in regs:
            if r==s: continue
            pr=[-V('rt','O',r,z),-V('rt','M',s,z)]
            for x in range(n):
                if x!=z: H.extend([pr+[V('C',r,T,x),V('C',s,T,x)],pr+[-V('C',r,T,x),-V('C',s,T,x)]])
                else: H.extend([pr+[V('C',r,T,x),-V('C',s,T,x)],pr+[-V('C',r,T,x),V('C',s,T,x)]])
# levels: lv[r][t][k] = |K[r][t]| >= k  (k=1..n) via totalizer
LV={}
TRUE=V('TRUE'); H.append([TRUE])
for r in regs:
    for t in range(1,T+1):
        xs=[V('K',r,t,x) for x in range(n)]
        prev=[TRUE]+[-TRUE]*n    # at least j of first 0 inputs
        for i,xi in enumerate(xs,1):
            cur=[TRUE]
            for j in range(1,n+1):
                c=V('cnt',r,t,i,j)
                a1=prev[j]; a2=prev[j-1]
                # c <-> a1 or (xi and a2)
                H.append([-c,a1,xi]); H.append([-c,a1,a2])
                H.append([c,-a1]); H.append([c,-xi,-a2])
                cur.append(c)
            prev=cur
        LV[(r,t)]=prev[1:]   # LV[k-1] <-> sum>=k (exact)
# visited level indicators: vis[r][k] = exists t: |K|==k
forb=set(int(x) for x in a.forbid.split(',') if x)
for r in regs:
    vlits=[]
    for k in range(1,n+1):
        vk=V('vis',r,k); vlits.append(vk)
        eqs=[]
        for t in range(1,T+1):
            rhs=LV[(r,t)]
            e=V('eq',r,t,k)
            ge=rhs[k-1]; gt=rhs[k] if k<n else None
            cl=[[-e,ge]]+([[-e,-gt]] if gt else [])+[[e,-ge]+([gt] if gt else [])]
            H.extend(cl); eqs.append(e)
        H.append([-vk]+eqs)
        for e in eqs: H.append([vk,-e])
        if k in forb: H.append([-vk])
    # stop count: distinct levels visited, excluding level 1 for R (start)
    cnt=[V('vis',r,k) for k in range(1,n+1) if not (isR(r) and k==1)]
    card_le(cnt,a.maxlev)
    capr = (a.capR if isR(r) else a.capF) or a.cap
    if capr>0:
        levs=list(range(1,n))
        for mask in range(1<<len(levs)):
            Vs=[levs[i] for i in range(len(levs)) if mask>>i&1]
            if isR(r) and 1 in Vs: continue   # level 1 for R is the start; handled as same pattern without it
            dims=[3] if isR(r) else [0]
            for k in Vs:
                d=2*k+1
                if d>dims[-1]: dims.append(d)
            for role in ('O','M'):
                tail=[21,22,24] if role=='O' else [21,24]
                dd=dims+[x for x in tail if x>dims[-1]]
                c=sum(g(dd[i]-dd[i-1]) for i in range(1,len(dd)))
                if c>capr:
                    cl=[-V(role,r)]
                    for k in range(1,n+1):
                        if isR(r) and k==1: continue
                        cl.append(-V('vis',r,k) if k in Vs else V('vis',r,k))
                    H.append(cl)
if a.sym:
    if a.sym=='z5': bp=lambda X: (X%5+1)%5+5*(X//5)
    elif a.sym=='z10': bp=lambda X: (X+1)%10
    elif a.sym=='z2': bp=lambda X: (X+5)%10
    rp=lambda r: bp(r) if r<n else n+bp(r-n)
    for r in regs:
        for z in range(n): H.extend([[-V('tgt',r,z),V('tgt',rp(r),bp(z))],[V('tgt',r,z),-V('tgt',rp(r),bp(z))]])
        for ro in 'OMI': H.extend([[-V(ro,r),V(ro,rp(r))],[V(ro,r),-V(ro,rp(r))]])
        for t in range(1,T+1):
            for x in range(n):
                for nm_ in ('K','C'):
                    H.extend([[-V(nm_,r,t,x),V(nm_,rp(r),t,bp(x))],[V(nm_,r,t,x),-V(nm_,rp(r),t,bp(x))]])
            for s_ in regs:
                if s_==r: continue
                H.extend([[-V('give',r,s_,t),V('give',rp(r),rp(s_),t)],[V('give',r,s_,t),-V('give',rp(r),rp(s_),t)]])
                if r<s_:
                    m1=meet(r,s_,t); m2=meet(rp(r),rp(s_),t)
                    H.extend([[-m1,m2],[m1,-m2]])
if a.copyround:
    for r in range(n,N):
        H.extend(CardEnc.atmost(lits=[meet(r,x,1) for x in range(n)],bound=1,vpool=pool,encoding=EncType.seqcounter).clauses)
        for s_ in range(n,N):
            if s_>r: H.append([-meet(r,s_,1)])
    for x,y in itertools.combinations(range(n),2): H.append([-meet(x,y,1)])
if a.totalcap>0:
    reps=[int(x) for x in a.reps.split(',')]
    allu=[]
    for r in reps:
        U=[V('u',r,j) for j in range(1,121)]
        for j in range(1,120): H.append([-U[j],U[j-1]])
        allu+=U
        levs=list(range(1,n))
        for mask in range(1<<len(levs)):
            Vs=[levs[i] for i in range(len(levs)) if mask>>i&1]
            if isR(r) and 1 in Vs: continue
            dims=[3] if isR(r) else [0]
            for k in Vs:
                d=2*k+1
                if d>dims[-1]: dims.append(d)
            for role in ('O','M'):
                tail=[21,22,24] if role=='O' else [21,24]
                dd=dims+[x for x in tail if x>dims[-1]]
                c=sum(g(dd[i]-dd[i-1]) for i in range(1,len(dd)))
                ci=int(math.ceil(c-1e-9))
                cl=[-V(role,r)]
                for k in range(1,n+1):
                    if isR(r) and k==1: continue
                    cl.append(-V('vis',r,k) if k in Vs else V('vis',r,k))
                H.append(cl+[V('u',r,min(ci,120))])
    B=int(math.floor(a.totalcap))
    H.extend(CardEnc.atmost(lits=allu,bound=B,vpool=pool,encoding=EncType.totalizer).clauses)
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
        role=[x for x in 'OMI' if val(x,r)][0]
        z=[z for z in range(n) if val('tgt',r,z)][0]
        levels=sorted(set(k for k in (sum(1 for x in range(n) if val('K',r,t,x)) for t in range(1,T+1)) if k>0))
        dims=[0] if not isR(r) else [3]
        for k in levels:
            d=2*k+1
            if d>dims[-1]: dims.append(d)
        tail=[21,22,24] if role=='O' else ([21,24] if role=='M' else [24])
        for d in tail:
            if d>dims[-1]: dims.append(d)
        cost=sum(g(dims[i]-dims[i-1]) for i in range(1,len(dims)))
        cost_post = cost
        total+=cost
        hist=[]
        for t in range(0,T+1):
            K=''.join('%d'%x for x in range(n) if val('K',r,t,x))
            C=''.join('%d'%x for x in range(n) if val('C',r,t,x))
            met=[s for s in regs if s!=r and t>0 and val('meet',min(r,s),max(r,s),t)]
            gv=[s for s in regs if s!=r and t>0 and val('give',r,s,t)]
            hist.append((t,K,C,met,gv))
        design.append(dict(r=r,R=isR(r),role=role,tgt=z,dims=dims,cost=cost,hist=hist))
        print('reg %2d %s %s tgt %d dims %s cost %.1f'%(r,'R' if isR(r) else 'F',role,z,dims,cost))
        for h in hist[1:]: print('      t%d K=%s C=%s meet=%s recv_from=%s'%h)
    print('TOTAL COST %.1f'%total)
    if a.out: json.dump(design,open(a.out,'w'))
