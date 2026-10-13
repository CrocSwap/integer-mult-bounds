"""Async whole-owner allocation relaxation with explicit per-call word choices.
Aggregate nominations need a subsequent literal owner matching and physical audit.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import json,math,time
import numpy as np
from scipy.optimize import linprog,milp,LinearConstraint,Bounds,brentq
from scipy.sparse import lil_matrix
R=Path(__file__).resolve().parent;O=R/'async505-order24-word-mix';O.mkdir(exist_ok=False)
D=json.load(open(R/'async505-order24-realized/PLAN.json'));cs=json.load(open(R/'complex501-heterogeneous-words/CANDIDATES.json'));win={tuple(map(int,k.split(','))):(r,ts)for k,(r,ts)in D['windows'].items()};m=D['M'];b=float(Fraction(json.load(open(R/'async505-order24-realized/audit/EXACT-ASSEMBLY.json'))['complex_lower']));widths=sorted({int(w)for z in cs for w in z['widths']});ports=120
@lru_cache(None)
def pats(cap,limit,start=0):
 out=[()]
 if limit:
  for j in range(start,len(widths)):
   w=widths[j]
   if w<=cap:out.extend((w,)+p for p in pats(cap-w,limit-1,j))
 return out
cost=lambda r:r*math.expm1(b*math.log(m/r))/b+32*m*m/1e16*m**b/b if r else 0
vs=[('x',i,p)for i,(rank,ts)in win.items()for p in pats(rank,len(ts))]+[('y',i,(t,w))for i,(rank,ts)in win.items()for t in ts for w in widths]+[('word',t,j)for t in range(len(D['order']))for j in range(len(cs))]
rows=[('copies',i)for i in win]+[('balance',i,w)for i in win for w in widths]+[('demand',t,w)for t in range(len(D['order']))for w in widths]+[('calls',t)for t in range(len(D['order']))]+[('distinct',i,t)for i,(rank,ts)in win.items()for t in ts];ri={r:j for j,r in enumerate(rows)};A=lil_matrix((len(rows),len(vs)),dtype=float)
for j,(kind,i,a)in enumerate(vs):
 if kind=='x':
  A[ri['copies',i],j]=1
  for w,n in Counter(a).items():A[ri['balance',i,w],j]=n
 elif kind=='y':
  t,w=a;A[ri['balance',i,w],j]=-1;A[ri['demand',t,w],j]=1;A[ri['distinct',i,t],j]=1
 else:
  A[ri['calls',i],j]=1
  for w,n in cs[a]['widths'].items():A[ri['demand',i,int(w)],j]=-n
A=A.tocsr();rhs=np.array([ports if row[0]in('copies','distinct')else 1 if row[0]=='calls'else 0 for row in rows]);neq=next(j for j,row in enumerate(rows)if row[0]=='distinct');lower=rhs.astype(float);lower[neq:]=-np.inf
c=np.array([cost(win[i][0]-sum(a))if k=='x'else sum(n*cost(int(r))for r,n in cs[a]['profile'].items())if k=='word'else 0 for k,i,a in vs]);H0=json.load(open(R/'async505-order24-realized/hosted/HOSTED.json'))['global_profile'];basecost=sum(n*cost(int(r))for r,n in H0.items())
print('MODEL',len(vs),len(rows),'baseline',basecost,flush=True)
for mode in ['baseline','heterogeneous']:
 hi=np.full(len(vs),np.inf)
 for j,(k,i,a)in enumerate(vs):
  if k=='word':hi[j]=0 if mode=='baseline'and a else 1
 t=time.monotonic();lp=linprog(c,A_eq=A[:neq],b_eq=rhs[:neq],A_ub=A[neq:],b_ub=rhs[neq:],bounds=list(zip(np.zeros(len(vs)),hi)),method='highs');assert lp.success,lp.message
 info=dict(mode=mode,status='FLOAT_LP_RELAXATION',variables=len(vs),rows=len(rows),objective=float(lp.fun),baseline_cost=basecost,gain=basecost-float(lp.fun),seconds=time.monotonic()-t)
 (O/(mode+'-LP.json')).write_text(json.dumps(info,indent=2)+'\n');print('LP',info,flush=True)
 if info['gain']<1e-7:continue
 t=time.monotonic();res=milp(c,integrality=np.ones(len(vs)),bounds=Bounds(0,hi),constraints=LinearConstraint(A,lower,rhs),options={'time_limit':90,'mip_rel_gap':1e-9});row=dict(mode=mode,status=int(res.status),message=res.message,seconds=time.monotonic()-t)
 if res.x is not None:
  x=np.rint(res.x).astype(np.int64);assert np.array_equal((A@x)[:neq],rhs[:neq])and np.all((A@x)[neq:]<=rhs[neq:]);H=Counter();choices=[]
  for v,(k,i,a)in zip(x,vs):
   if not v:continue
   if k=='x':
    r=win[i][0]-sum(a)
    if r:H[r]+=int(v)
   elif k=='word':
    for r,n in cs[a]['profile'].items():H[int(r)]+=int(v)*n
    choices.append(dict(call=i,stage=D['order'][i][0],replica=D['order'][i][1],candidate=a,label=cs[a]['label'],count=int(v)))
  assert m*D['live']-sum(r*n for r,n in H.items())==D['deficit']
  root=brentq(lambda z:sum(n*(r/m)**(1-z)for r,n in H.items())/D['live']+32*m*m*sum(H.values())/1e16*m**(z-1)/D['live']-1,0,.01,xtol=1e-15)
  row.update(objective=float(c@x),gain=basecost-float(c@x),gap=float(res.mip_gap),profile=dict(sorted(H.items())),float_root=root,words=choices,selection=[[k,list(i)if isinstance(i,tuple)else i,list(a)if isinstance(a,tuple)else a,int(v)]for (k,i,a),v in zip(vs,x)if v])
 (O/(mode+'-MILP.json')).write_text(json.dumps(row,indent=2)+'\n');print('MILP',{k:v for k,v in row.items()if k not in ['words','selection','profile']},flush=True)
