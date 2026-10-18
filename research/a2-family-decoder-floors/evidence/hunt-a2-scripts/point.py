# HUNT-A2: at a given rational parameter point, build the realisation, its catalogue, exact CP-SAT optimum over square
# decoders, an explicit completion, and the exact evaluation (P Q^T = M entrywise over Q; F2 ranks).
import sys, pickle, random, itertools, os
from ortools.sat.python import cp_model
from a2lib import *
name=sys.argv[1]; th=tuple(Fr(x) for x in sys.argv[2].split(',')); zX=tuple(Fr(x) for x in sys.argv[3].split(','))
A,B=build(th,zX)
# MOVE="i:c" : move triangle row u_i along the column direction e_i killing class {u_i} + O_{u_i} (free-term reduction, NOTES §2)
MOVE=os.environ.get('MOVE')
if MOVE:
    for mv in MOVE.split(';'):
        ii,cc=mv.split(':'); ii=int(ii); cc=Fr(cc); ui=X[ii]
        Kl=[ui]+[s_ for s_ in range(v) if Gm[ui][s_]==0]
        ns=nullspace([B[s_] for s_ in Kl],9); assert len(ns)==1, 'class not column-deficient'
        e=ns[0]; e=[x_/e[8] for x_ in e]
        A[ui]=[a_-cc*b_ for a_,b_ in zip(A[ui],e)]
        print('moved row',ui,'by',cc,'* e =',[str(x_) for x_ in e])
M=Mof(A,B)
if MOVE:
    viol=sum(1 for i in range(v) for j in range(v) if (Gm[i][j]==0 and i!=j and M[i][j]!=0) or (i==j and M[i][j]==0))
    print('extra zeros on non-orthogonal pairs:',sum(1 for i in range(v) for j in range(v) if i!=j and Gm[i][j]!=0 and M[i][j]==0))
else: viol=pattern_ok(M)
print('point',name,[str(x) for x in th],[str(x) for x in zX],'pattern violations',viol,'rank',rank(A,9),rank(B,9))
assert viol==0
out=catalogue(A,B)
def norm(x):
    i=next(k for k in range(9) if x[k]!=0); return tuple(a/x[i] for a in x)
rd=sorted(set(norm(x[1][0]) for x in out.values() if x[1])); cd=sorted(set(norm(x[2][0]) for x in out.values() if x[2]))
print('row classes',sum(1 for x in out.values() if x[1]),'dirs',len(rd),'col classes',sum(1 for x in out.values() if x[2]),'dirs',len(cd),
      'multi-dim',[(x[0],len(x[1]),len(x[2])) for x in out.values() if len(x[1])>1 or len(x[2])>1])
supp=lambda vecs,x:[u for u in range(v) if dot(vecs[u],x)!=0]
Rr=[supp(A,d) for d in rd]+[list(range(v))]; Ac=[supp(B,e) for e in cd]+[list(range(v))]
f=[[blk(Brows,a,b) for b in Ac] for a in Rr]
nr,nc=len(rd),len(cd); NT=9
def circuits(vecs):
    o=[]; n=len(vecs)
    for k in range(2,min(n,10)+1):
        for S in itertools.combinations(range(n),k):
            if any(set(C)<=set(S) for C in o): continue
            if rank([vecs[i] for i in S],9)<k: o.append(S)
    return o
cr=circuits(rd); cc=circuits(cd)
m=cp_model.CpModel()
x={(i,j):m.NewIntVar(0,NT if (i==nr and j==nc) else 1,'') for i in range(nr+1) for j in range(nc+1)}
m.Add(sum(x.values())==NT)
ur=[m.NewBoolVar('') for i in range(nr)]; uc=[m.NewBoolVar('') for j in range(nc)]
for i in range(nr): m.Add(sum(x[i,j] for j in range(nc+1))==ur[i])
for j in range(nc): m.Add(sum(x[i,j] for i in range(nr+1))==uc[j])
for i in range(nr):
    for j in range(nc):
        if dot(rd[i],cd[j])==0: m.Add(x[i,j]==0)
        else: m.Add(ur[i]+uc[j]-x[i,j]<=1)
for C in cr: m.Add(sum(ur[i] for i in C)<=len(C)-1)
for C in cc: m.Add(sum(uc[j] for j in C)<=len(C)-1)
m.Minimize(sum(f[i][j]*x[i,j] for i in range(nr+1) for j in range(nc+1)))
s=cp_model.CpSolver(); s.parameters.num_workers=1; s.parameters.max_time_in_seconds=900
POOL=int(os.environ.get('POOL','0'))
if POOL:
    m.ClearObjective(); m.Add(sum(f[i][j]*x[i,j] for i in range(nr+1) for j in range(nc+1))<=POOL)
    class CB(cp_model.CpSolverSolutionCallback):
        def __init__(s_): super().__init__(); s_.sols=[]
        def on_solution_callback(s_):
            s_.sols.append([(i,j) for (i,j),var in x.items() for _ in range(s_.Value(var))])
            if len(s_.sols)>=60: s_.StopSearch()
    cb=CB(); s.parameters.enumerate_all_solutions=True; s.Solve(m,cb); pool=cb.sols; print('pool',len(pool))
else:
    st=s.Solve(m); print('exact square optimum',s.StatusName(st),s.ObjectiveValue(),'bound',s.BestObjectiveBound())
    pool=[[(i,j) for (i,j),var in x.items() for _ in range(s.Value(var))]]
for pn,terms in enumerate(pool):
  name_=name if not POOL else f'{name}_{pn}'
  print('terms',terms,'pair costs',[f[i][j] for i,j in terms])
  rnd=random.Random(1)
  Tc=[t for t,(i,j) in enumerate(terms) if j<nc]
  for seed in range(3):
      xs=[]
      for t,(i,j) in enumerate(terms):
          cons=[cd[terms[s_][1]] for s_ in Tc if s_!=t]
          if i<nr: xv=list(rd[i])
          else:
              ns=nullspace(cons,9) if cons else [[Fr(int(a==b)) for a in range(9)] for b in range(9)]
              cf=[Fr(rnd.randint(-30,30)) for n in ns]; xv=[sum(c_*n[k] for c_,n in zip(cf,ns)) for k in range(9)]
          if j<nc: sc=dot(xv,cd[j]); xv=[a/sc for a in xv]
          xs.append(xv)
      r=evaluate(A,B,xs)
      if r:
          for t,(i,j) in enumerate(terms):
              if j<nc: print('  term',t,(i,j),'y prop cd?',norm(r[3][t])==cd[j])
      if r is None: print('singular completion'); continue
      print('completion',seed,'EXACT cost',r[0],r[1]); pickle.dump(dict(th=th,zX=zX,xs=xs,cost=r[0],costs=r[1]),open(f'dec_{name_}.pkl','wb')); break
