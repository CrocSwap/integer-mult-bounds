"""RESCUEBUILD rb6: CP-SAT enumeration of k-stage designs (n=2k-2 roles) with chat(.99) > bar under PROVED mask-level laws:
 mains=2/stage; CROSS (all X,Y: #roles meeting both >= 2 min(runs)); PIECEFIX per X (|X|>=2); RESCUE (<=1 unrescued main stage/role);
 ADJ (linear-consecutive a,b: a role inside {a,b} needs a D>=3 role containing {a,b}); CELLRANK (new, RB.md): for disjoint cells X_i,
 |S| <= sum_i (|E(X_i)| - pi(X_i)), S = roles whose mask is a union of cells.  Options = (mask, labelled piece partition)."""
import sys,itertools,os
sys.path.insert(0,'.')
from rbcore import value
from decimal import Decimal as Dm
from ortools.sat.python import cp_model
def setparts(s):
    s=list(s)
    if not s: yield []; return
    a=s[0]
    for p in setparts(s[1:]):
        for i in range(len(p)): yield p[:i]+[p[i]|{a}]+p[i+1:]
        yield p+[frozenset({a})]
def options(k):
    out=[]
    for D in range(2,k+1):
        for M in itertools.combinations(range(k),D):
            M=frozenset(M)
            for P in setparts(M):
                if len(P)>int(os.environ.get('MAXP','99')):continue
                P=[frozenset(p) for p in P];sing=[p for p in P if len(p)==1];multi=[p for p in P if len(p)>1]
                for lab in itertools.product((0,1),repeat=len(sing)):   # 1 = main
                    mains=frozenset(next(iter(p)) for p,l in zip(sing,lab) if l)
                    idle=multi+[p for p,l in zip(sing,lab) if not l]
                    out.append((M,tuple(sorted(idle,key=sorted)),mains))
    return out
def runs(seq,lab):return sum(1 for i,x in enumerate(seq) if x==lab and (i==0 or seq[i-1]!=lab))
def cellfams(k):
    """all collections of >=1 disjoint nonempty cells, at least one cell of size >=2 (else trivial)"""
    st=list(range(k));fams=set()
    for lab in itertools.product(range(k+1),repeat=k):   # label 0 = unused, i = cell i
        cells={}
        for t,l in enumerate(lab):
            if l:cells.setdefault(l,set()).add(t)
        if not cells or max(len(c) for c in cells.values())<2:continue
        fams.add(frozenset(frozenset(c) for c in cells.values()))
    return list(fams)
def build(k,bar=Dm('128.891'),extra=None,cellrank=True,timelimit=600,maxsol=200000):
    n=2*k-2;O=options(k);m=cp_model.CpModel()
    val=[value(len(M),[len(p) for p in P]+[1]*len(mn)) for M,P,mn in O]
    c=[m.NewIntVar(0,n,'c%d'%i) for i in range(len(O))]
    m.Add(sum(c)==n)
    for t in range(k):m.Add(sum(c[i] for i,(M,P,mn) in enumerate(O) if t in mn)==2)
    SK=os.environ.get('SKIP','').split(',')
    if not cellrank:SK+=['local','pc2','more','pure']
    for lab in (itertools.product('XY.',repeat=k) if 'cross' not in SK else []):
        X={i for i in range(k) if lab[i]=='X'};Y={i for i in range(k) if lab[i]=='Y'}
        if not X or not Y:continue
        s=[x for x in lab if x!='.'];need=2*min(runs(s,'X'),runs(s,'Y'))
        if 'pc2' in SK: m.Add(sum(c[i] for i,(M,P,mn) in enumerate(O) if M&X and M&Y)>=need)
        else: m.Add(sum(c[i]*((1 if (M&X and M&Y) else 0)-sum(1 for p in P if p>=(X|Y))) for i,(M,P,mn) in enumerate(O))>=need)   # PIECE-CROSS-2 [P]
    for x in (range(2,k) if 'pfix' not in SK else []):
        for X in itertools.combinations(range(k),x):
            X=frozenset(X)
            m.Add(sum(c[i]*((not (M&X))+sum(1 for p in P if p>=X)) for i,(M,P,mn) in enumerate(O))<=n-2*x)
    used=[m.NewBoolVar('u%d'%i) for i in range(len(O))]
    for i in range(len(O)):m.Add(c[i]>=1).OnlyEnforceIf(used[i]);m.Add(c[i]==0).OnlyEnforceIf(used[i].Not())
    # RESCUE
    for i,(M,P,mn) in enumerate(O):
        if len(mn)<2 or 'rescue' in SK:continue
        bs=[]
        for t in mn:
            b=m.NewBoolVar('');bs.append(b)
            ex=sum(c[j] for j,(M2,P2,mn2) in enumerate(O) if any(t in p and p<=M for p in P2))
            m.Add(ex>=1).OnlyEnforceIf(b);m.Add(ex==0).OnlyEnforceIf(b.Not())
        m.Add(sum(bs)>=len(mn)-1).OnlyEnforceIf(used[i])
    # ADJ (linear consecutive)
    for a in (range(k-1) if 'adj' not in SK else []):
        ab=frozenset({a,a+1})
        inside=[i for i,(M,P,mn) in enumerate(O) if M<=ab]
        cover=[i for i,(M,P,mn) in enumerate(O) if M>=ab and len(M)>=3]
        z=m.NewBoolVar('')
        m.Add(sum(c[i] for i in inside)>=1).OnlyEnforceIf(z);m.Add(sum(c[i] for i in inside)==0).OnlyEnforceIf(z.Not())
        m.Add(sum(c[i] for i in cover)>=1).OnlyEnforceIf(z)
    if cellrank:
        for fam in cellfams(k):
            U=frozenset().union(*fam)
            S=[i for i,(M,P,mn) in enumerate(O) if M<=U and all((not (M&X)) or X<=M for X in fam)]
            rhs=[]
            for X in fam:
                for i,(M,P,mn) in enumerate(O):
                    co=(X<=M)-sum(1 for p in P if p>=X)
                    if co:rhs.append(co*c[i])
            m.Add(sum(c[i] for i in S)<=sum(rhs))
    if 'local' not in SK:
        # LOCAL-PIECEFIX [P, RB.md]: for X, T subset X^c: #{pieces q >= X : (U_{r in E(q)} M_r) - q subset T} + #{roles M_r subset T} <= max(0,2|T|-2)
        allS=[frozenset(x) for x in itertools.chain.from_iterable(itertools.combinations(range(k),j) for j in range(1,k+1))]
        pcount={Qs:sum(c[i]*sum(1 for p in P if p==Qs) for i,(M,P,mn) in enumerate(O)) for Qs in allS}
        g={}
        def G(Qs,T):
            if (Qs,T) not in g:
                bad=sum(c[i] for i,(M,P,mn) in enumerate(O) if M>=Qs and not M<=(Qs|T))
                gv=m.NewBoolVar('');m.Add(gv>=1-bad)
                z=m.NewIntVar(0,n,'');m.Add(z>=pcount[Qs]-n*(1-gv));g[(Qs,T)]=z
            return g[(Qs,T)]
        for X in allS:
            if len(X)==k:continue
            comp=[t for t in range(k) if t not in X]
            for j in range(0,len(comp)+1):
                for T in itertools.combinations(comp,j):
                    T=frozenset(T)
                    if 2*len(T)-2>=n:continue
                    lhs=[G(Qs,T) for Qs in allS if Qs>=X]+[c[i] for i,(M,P,mn) in enumerate(O) if T and M<=T]
                    m.Add(sum(lhs)<=max(0,2*len(T)-2))
    if 'more' not in SK:
        allS=[frozenset(x) for x in itertools.chain.from_iterable(itertools.combinations(range(k),j) for j in range(1,k+1))]
        pc={Qs:sum(c[i]*sum(1 for p in P if p==Qs) for i,(M,P,mn) in enumerate(O)) for Qs in allS}
        # e-row [P rank law, cwlp]: sum_r (#pieces incl. mains - 1) >= 2k-2
        m.Add(sum(c[i]*(len(P)+len(mn)-1) for i,(M,P,mn) in enumerate(O))>=2*k-2)
        # SPAN over every set partition (cells cover all stages): n <= sum_i min(2|X_i|, |R(X_i)| - pi(X_i))  [P]
        for part in setparts(range(k)):
            if len(part)==k:continue
            ys=[]
            for X in part:
                X=frozenset(X);y=m.NewIntVar(0,2*len(X),'');ys.append(y)
                m.Add(y<=sum(c[i] for i,(M,P,mn) in enumerate(O) if M&X)-sum(pc[Qs] for Qs in allS if Qs>=X))
            m.Add(sum(ys)>=n)
        # PC3 [P]: rank Ghat_XY <= |R(X,Y)| - #{pieces q >= X : every role containing q meets Y}  (and A-side with X<->Y)
        zz={}
        def Z(Qs,Y):
            if (Qs,Y) not in zz:
                bad=sum(c[i] for i,(M,P,mn) in enumerate(O) if M>=Qs and not (M&Y))
                g=m.NewBoolVar('');m.Add(g>=1-bad);z=m.NewIntVar(0,n,'');m.Add(z>=pc[Qs]-n*(1-g));zz[(Qs,Y)]=z
            return zz[(Qs,Y)]
        for lab in itertools.product('XY.',repeat=k):
            X=frozenset(i for i in range(k) if lab[i]=='X');Y=frozenset(i for i in range(k) if lab[i]=='Y')
            if not X or not Y:continue
            sq=[x for x in lab if x!='.'];need=2*min(runs(sq,'X'),runs(sq,'Y'))
            R=sum(c[i] for i,(M,P,mn) in enumerate(O) if M&X and M&Y)
            m.Add(R-sum(Z(Qs,Y) for Qs in allS if Qs>=X)>=need)
    if 'pure' not in SK:
        # PURE-CELL [P, RB.md]: if #roles with mask exactly X >= dbar := |E(X)|-pi(X), then V_E(X) is inside Z_X; so
        #   #{mask = X} + #{r containing X, |M_r - X| = 1} <= dbar  and  #{roles meeting but not containing X} >= 2
        for x in range(2,k):
            for X in itertools.combinations(range(k),x):
                X=frozenset(X)
                E=sum(c[i] for i,(M,P,mn) in enumerate(O) if M>=X)
                pi=sum(c[i]*sum(1 for p in P if p>=X) for i,(M,P,mn) in enumerate(O))
                pX=sum(c[i] for i,(M,P,mn) in enumerate(O) if M==X)
                s1=sum(c[i] for i,(M,P,mn) in enumerate(O) if M>=X and len(M-X)==1)
                out=sum(c[i] for i,(M,P,mn) in enumerate(O) if (M&X) and not M>=X)
                h=m.NewBoolVar('');m.Add(pX>=E-pi).OnlyEnforceIf(h);m.Add(pX<E-pi).OnlyEnforceIf(h.Not())
                m.Add(pX+s1<=E-pi).OnlyEnforceIf(h);m.Add(out>=2).OnlyEnforceIf(h)
                # SATURATED-CELL [P, RB.md]: under h, a piece q' meeting X, not inside X, has x_q', y_q' vanishing on E(X):
                #   needs >=2 roles containing q' but not X, or one such role o with |M_o - q'| >= 2
                for y in range(2,k):
                    for Qs in itertools.combinations(range(k),y):
                        Qs=frozenset(Qs)
                        if not (Qs&X) or Qs<=X:continue
                        pq=sum(c[i]*sum(1 for p in P if p==Qs) for i,(M,P,mn) in enumerate(O))
                        e=m.NewBoolVar('');m.Add(pq>=1).OnlyEnforceIf(e);m.Add(pq==0).OnlyEnforceIf(e.Not())
                        # enforce only when h and e
                        covs=[]
                        for t in range(k):
                            if t in Qs:continue
                            cv=m.NewBoolVar('');covs.append(cv)
                            m.Add(sum(c[i] for i,(M,P,mn) in enumerate(O) if M>=Qs and not M>=X and t in M)>=1).OnlyEnforceIf(cv)
                        m.Add(sum(covs)>=2).OnlyEnforceIf([h,e])   # v2: relays outside E(X) must reach >=2 stages outside q'
    if extra:extra(m,c,O)
    SC=10**6;need=int(bar*k/104*SC)
    m.Add(sum(c[i]*int(val[i]*SC) for i in range(len(O)))>need)
    return m,c,O,val
class Col(cp_model.CpSolverSolutionCallback):
    def __init__(s_,c,maxsol):super().__init__();s_.c=c;s_.sols=[];s_.maxsol=maxsol
    def on_solution_callback(s_):
        s_.sols.append(tuple(s_.Value(v) for v in s_.c))
        if len(s_.sols)>=s_.maxsol:s_.StopSearch()
def canon(k,des):
    """des: tuple of (M,P,mn) -> canonical form under dihedral group on positions"""
    best=None
    for r in range(k):
        for f in (1,-1):
            mp=lambda t:(f*t+r)%k
            img=tuple(sorted((tuple(sorted(map(mp,M))),tuple(sorted(tuple(sorted(map(mp,p))) for p in P)),tuple(sorted(map(mp,mn)))) for M,P,mn in des))
            if best is None or img<best:best=img
    return best
if __name__=='__main__':
    k=int(sys.argv[1]);cr=os.environ.get('CR','1')=='1'
    m,c,O,val=build(k,cellrank=cr)
    sv=cp_model.CpSolver();sv.parameters.num_workers=1;sv.parameters.enumerate_all_solutions=True;sv.parameters.max_time_in_seconds=float(os.environ.get('TL','900'))
    cb=Col(c,200000);st=sv.Solve(m,cb)
    print('k',k,'cellrank',cr,'status',sv.StatusName(st),'raw sols',len(cb.sols),'options',len(O),flush=True)
    seen={}
    for s in cb.sols:
        des=tuple(O[i] for i,x in enumerate(s) for _ in range(x))
        v=sum(val[i]*x for i,x in enumerate(s))*104/k
        seen.setdefault(canon(k,des),float(v))
    print('canonical designs',len(seen))
    import pickle;pickle.dump(seen,open('rb6_k%d_cr%d.pkl'%(k,cr),'wb'))
    for d,v in sorted(seen.items(),key=lambda x:-x[1])[:10]:print(round(v,3),d)
