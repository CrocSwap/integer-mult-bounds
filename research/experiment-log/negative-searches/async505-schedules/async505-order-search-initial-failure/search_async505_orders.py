"""Bounded asynchronous order search preserving each replica's controller.
LP/MILP outputs are allocation nominations pending explicit owner realization.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
from fractions import Fraction
import json,gzip,math,random,secrets,time
import numpy as np
from scipy.optimize import linprog,milp,LinearConstraint,Bounds,brentq
from scipy.sparse import lil_matrix
R=Path(__file__).resolve().parent;O=R/'async505-order-search';O.mkdir(exist_ok=False);seed=secrets.randbits(64);rng=random.Random(seed)
D=json.load(open(R/'source505-review/inputs/ASYNC-3.json'));parent=json.load(gzip.open(R/'stage4-local-verification/baseline/split-centres/GLOBAL-TEMPLATE.json.gz'));checks=json.load(open(R/'stage4-local-verification/baseline/split-centres/LOCAL-CHECKS.json'));wc={int(w):v for w,v in D['baseline_widths'].items()};widths=sorted(wc);m=D['M'];nrep=D['T'];nstages=D['L'];ports=120;b=float(Fraction(json.load(open(R/'async505-retimed-candidate/audit/EXACT-ASSEMBLY.json'))['complex_lower']));rank={z['child']:z['rank']for z in parent['idle_children']};pair={z['stage']:z['pair']for z in parent['recipe']if z['kind']=='local'};blocks={};st=None
for e in parent['execution_schedule']:
 if e['kind']in('bank_padding_cover_sweep','translate_every_live_family'):continue
 if e['kind']=='local_cover_sweep':st=e['stage'];blocks[st]=[]
 blocks[st].append(e)
@lru_cache(None)
def pats(cap,limit,start=0):
 out=[()]
 if limit:
  for j in range(start,len(widths)):
   w=widths[j]
   if w<=cap:out.extend((w,)+p for p in pats(cap-w,limit-1,j))
 return out
cost=lambda r:r*math.expm1(b*math.log(m/r))/b+32*m*m/1e16*m**b/b if r else 0
localH=Counter()
for c in parent['calls']:localH.update({int(k):v for k,v in checks[c['orientation']]['paid_profile'].items()})
localcost=sum(n*cost(r)for r,n in localH.items());baseH=json.load(open(R/'async505-retimed-candidate/hosted/HOSTED.json'))['global_profile'];basecost=sum(n*cost(int(r))for r,n in baseH.items())
def windows(order):
 schedule=[(r,e)for s,r in order for e in blocks[s]];last={};bounds={};calls={}
 for pos,(r,e)in enumerate(schedule):
  if e['kind']=='local_cover_sweep':last[r,pair[e['stage']]]=pos;calls[e['stage'],r]=pos
  elif e['kind']=='bridge':last[r,e['src']]=last[r,e['dst']]=pos
  elif e['kind']=='idle_cover_sweep':
   for i in e['child_indices']:
    if i in rank:bounds[r,i]=(last.get((r,e['pair']),-1),pos)
 return {k:(rank[k[1]],[t for t,c in enumerate(order)if lo<calls[c]<hi])for k,(lo,hi)in bounds.items()}
def model(win):
 vs=[('x',i,p)for i,(r,ts)in win.items()for p in pats(r,len(ts))]+[('y',i,(t,w))for i,(r,ts)in win.items()for t in ts for w in widths]
 rows=[('copies',i)for i in win]+[('balance',i,w)for i in win for w in widths]+[('demand',t,w)for t in range(nrep*nstages)for w in widths]+[('distinct',i,t)for i,(r,ts)in win.items()for t in ts];ri={r:j for j,r in enumerate(rows)};A=lil_matrix((len(rows),len(vs)),dtype=float)
 for j,(kind,i,a)in enumerate(vs):
  if kind=='x':
   A[ri['copies',i],j]=1
   for w,n in Counter(a).items():A[ri['balance',i,w],j]=n
  else:
   t,w=a;A[ri['balance',i,w],j]=-1;A[ri['demand',t,w],j]=1;A[ri['distinct',i,t],j]=1
 A=A.tocsr();neq=next(j for j,r in enumerate(rows)if r[0]=='distinct');rhs=np.array([ports if r[0]in('copies','distinct')else wc[r[2]]if r[0]=='demand'else 0 for r in rows]);c=np.array([cost(win[i][0]-sum(a))if k=='x'else 0 for k,i,a in vs]);return vs,A,rhs,neq,c
reference=[tuple(x)for x in D['order']];assert {f'{r},{i}':[v[0],v[1]]for (r,i),v in windows(reference).items()}==D['windows']
candidates=[dict(label='reference',order=reference)]
# Vary replica offsets nonuniformly and per-stage pacing; preserve strict local order.
for j in range(48):
 span=rng.uniform(1.5,7.5);delays=sorted([0.0]+[rng.uniform(0,span)for _ in range(nrep-1)])
 times={}
 for r in range(nrep):
  now=delays[r]
  for s in range(nstages):
   if s:now+=rng.uniform(.75,1.25)if j%2 else 1.0
   times[s,r]=now
 order=sorted(times,key=lambda k:(times[k],k));candidates.append(dict(label=f'random-{j}',span=span,delays=delays,jitter=bool(j%2),order=order))
ledger=[];seen=set()
for case in candidates:
 order=case['order'];sig=tuple(order)
 if sig in seen:continue
 seen.add(sig);win=windows(order);vs,A,rhs,neq,c=model(win);start=time.monotonic();q=linprog(c,A_eq=A[:neq],b_eq=rhs[:neq],A_ub=A[neq:],b_ub=rhs[neq:],bounds=(0,None),method='highs');row=dict(**case,status=q.status,message=q.message,seconds=time.monotonic()-start)
 if q.success:row.update(objective=float(q.fun)+localcost,gain=basecost-float(q.fun)-localcost)
 ledger.append(row);(O/'LP-LEDGER.json').write_text(json.dumps(dict(seed=seed,baseline_cost=basecost,rows=ledger),indent=2)+'\n');print('LP',case['label'],q.status,row.get('gain'),flush=True)
for row in sorted([x for x in ledger if x.get('gain',0)>1e-6 and x['label']!='reference'],key=lambda x:-x['gain'])[:4]:
 order=[tuple(x)for x in row['order']];win=windows(order);vs,A,rhs,neq,c=model(win);lo=rhs.astype(float);lo[neq:]=-np.inf;start=time.monotonic();q=milp(c,integrality=np.ones(len(vs)),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,lo,rhs),options={'time_limit':60,'mip_rel_gap':1e-9});out=dict(label=row['label'],order=order,windows={f'{r},{i}':v for (r,i),v in win.items()},status=int(q.status),message=q.message,seconds=time.monotonic()-start)
 if q.x is not None:
  x=np.rint(q.x).astype(np.int64);assert np.array_equal((A@x)[:neq],rhs[:neq])and np.all((A@x)[neq:]<=rhs[neq:]);H=localH.copy()
  for val,(k,i,a)in zip(x,vs):
   r=win[i][0]-sum(a)if k=='x'else 0
   if val and r:H[r]+=int(val)
  assert m*D['live']-sum(r*n for r,n in H.items())==D['deficit'];root=brentq(lambda z:sum(n*(r/m)**(1-z)for r,n in H.items())/D['live']+32*m*m*sum(H.values())/1e16*m**(z-1)/D['live']-1,0,.01,xtol=1e-15)
  out.update(objective=float(c@x)+localcost,gain=basecost-float(c@x)-localcost,gap=float(q.mip_gap),profile=dict(sorted(H.items())),float_root=root,selection=[[k,list(i),list(a),int(v)]for (k,i,a),v in zip(vs,x)if v])
 (O/(row['label']+'-MILP.json')).write_text(json.dumps(out,indent=2)+'\n');print('MILP',{k:v for k,v in out.items()if k not in ['order','windows','selection','profile']},flush=True)
(O/'COMPLETE.json').write_text(json.dumps(dict(seed=seed,cases=len(ledger),scope='Floating allocation search only. Literal owner matching, physical audit and exact arithmetic are not implied.'),indent=2)+'\n')
