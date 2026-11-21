"""rb23: CEGAR sup for larger k with a LIGHT CP-SAT model (mains, PC3 on stage pairs, PIECEFIX, RESCUE, e-row) over options with
<= MAXP blocks; every argmax is checked with the FULL direct law set (rblaw.violations) + STAR-ZERO and cut if killed.
Result = sup over the MAXP-restricted design space under all laws (a LOWER bound on the unrestricted mask-level sup).
usage: MAXP=3 rb23.py k maxiter"""
import sys,os,time,itertools;sys.path.insert(0,'.')
from rb6 import options,canon,runs
from rbcore import value
from rblaw import violations,star_zero
from rb10 import roles_of
from decimal import Decimal as Dm
from ortools.sat.python import cp_model
k=int(sys.argv[1]);mi=int(sys.argv[2]);n=2*k-2
O=options(k);val=[value(len(M),[len(p) for p in P]+[1]*len(mn)) for M,P,mn in O]
m=cp_model.CpModel();c=[m.NewIntVar(0,n,'') for _ in O];m.Add(sum(c)==n)
for t in range(k):m.Add(sum(c[i] for i,(M,P,mn) in enumerate(O) if t in mn)==2)
for s,t in itertools.combinations(range(k),2):
    m.Add(sum(c[i]*((1 if (s in M and t in M) else 0)-sum(1 for p in P if s in p and t in p)) for i,(M,P,mn) in enumerate(O))>=2)
for x in range(2,k):
    for X in itertools.combinations(range(k),x):
        X=frozenset(X);m.Add(sum(c[i]*((not (M&X))+sum(1 for p in P if p>=X)) for i,(M,P,mn) in enumerate(O))<=n-2*x)
m.Add(sum(c[i]*(len(P)+len(mn)-1) for i,(M,P,mn) in enumerate(O))>=2*k-2)
used=[m.NewBoolVar('') for _ in O]
for i in range(len(O)):m.Add(c[i]>=1).OnlyEnforceIf(used[i]);m.Add(c[i]==0).OnlyEnforceIf(used[i].Not())
for i,(M,P,mn) in enumerate(O):
    if len(mn)<2:continue
    bs=[]
    for t in mn:
        b=m.NewBoolVar('');bs.append(b)
        m.Add(sum(c[j] for j,(M2,P2,mn2) in enumerate(O) if any(t in p and p<=M for p in P2))>=1).OnlyEnforceIf(b)
    m.Add(sum(bs)>=len(mn)-1).OnlyEnforceIf(used[i])
SC=10**6;m.Maximize(sum(c[i]*int(val[i]*SC) for i in range(len(O))))
def forbid(des):
    for r in range(k):
        for f in (1,-1):
            mp=lambda t:(f*t+r)%k;img={}
            for M,P,mn in des:
                o=(frozenset(map(mp,M)),tuple(sorted((frozenset(map(mp,p)) for p in P),key=sorted)),frozenset(map(mp,mn)))
                j=O.index(o);img[j]=img.get(j,0)+1
            ds=[]
            for j,cnt in img.items():
                d=m.NewBoolVar('');m.Add(c[j]==cnt).OnlyEnforceIf(d);m.Add(c[j]!=cnt).OnlyEnforceIf(d.Not());ds.append(d)
            m.Add(sum(ds)<=len(ds)-1)
t0=time.time()
for it in range(mi):
    sv=cp_model.CpSolver();sv.parameters.num_workers=1;sv.parameters.max_time_in_seconds=1200
    st=sv.Solve(m)
    if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):print('it',it,sv.StatusName(st));break
    v=[sv.Value(x) for x in c];des=tuple(O[i] for i,x in enumerate(v) for _ in range(x))
    val_=float(sum(val[i]*x for i,x in enumerate(v))*104/k);R=roles_of(canon(k,des))
    vi=violations(k,R);kz=star_zero(k,R) if not vi else []
    print('it',it,sv.StatusName(st),'val %.3f'%val_,'killed:'+str(vi[0][0] if vi else kz[0][0]) if (vi or kz) else 'SURVIVES','t=%.0f'%(time.time()-t0),
          canon(k,des) if not (vi or kz) else '',flush=True)
    if not (vi or kz):break
    forbid(des)
