"""Joint integer pattern and call flow; nominations still require physical admission."""
from pathlib import Path
from collections import Counter,defaultdict
import json,time,sys
import numpy as np
from scipy.optimize import milp,linprog,Bounds,LinearConstraint,brentq
from scipy.sparse import lil_matrix
R=Path(__file__).resolve().parent
# Reuse only model definitions, never execute the old aggregate search.
source=(R/'price_partial_coordinated.py').read_text()
namespace={'__file__':str(R/'price_partial_coordinated.py')}
source=source[:source.index('reference=[tuple(x)')]
source=source.replace("O=R/'partial-coordinated-pricing';O.mkdir(exist_ok=False)","O=R/'partial-coordinated-restricted';O.mkdir(exist_ok=False)")
exec(compile(source,'price_partial_coordinated-definitions','exec'),namespace)
D=namespace['D'];O=namespace['O'];win=namespace['windows']([tuple(x)for x in D['order']]);pats=namespace['pats'];cost=namespace['cost'];wc=namespace['wc'];localH=namespace['localH'];localcost=namespace['localcost'];basecost=namespace['basecost'];m=namespace['m']
nom=json.loads((R/'partial-coordinated-pricing/reference-MILP.json').read_text())
menu=defaultdict(set)
for kind,i,p,count in nom['selection']:
 if kind=='x':menu[win[tuple(i)][0]].add(tuple(p))
for cap in menu:
 menu[cap].add(())
 for w in wc:menu[cap].add((w,)*(cap//w))
patterns=[(i,p)for i,(cap,ts)in win.items()for p in pats(cap,len(ts))if p in menu[cap]]
vs=[('x',j,None,None)for j in range(len(patterns))]+[('z',j,t,w)for j,(i,p)in enumerate(patterns)for t in win[i][1]for w in set(p)]
rows=[('copies',i)for i in win]+[('slots',j,w)for j,(i,p)in enumerate(patterns)for w in set(p)]+[('demand',t,w)for t in range(len(D['order']))for w in wc]+[('distinct',j,t)for j,(i,p)in enumerate(patterns)if p for t in win[i][1]]
ri={k:j for j,k in enumerate(rows)};A=lil_matrix((len(rows),len(vs)),dtype=float)
for k,(typ,j,t,w)in enumerate(vs):
 i,p=patterns[j]
 if typ=='x':
  A[ri['copies',i],k]=1
  for width,n in Counter(p).items():A[ri['slots',j,width],k]=-n
  if p:
   for call in win[i][1]:A[ri['distinct',j,call],k]=-1
 else:A[ri['slots',j,w],k]=1;A[ri['demand',t,w],k]=1;A[ri['distinct',j,t],k]=1
A=A.tocsr();rhs=np.array([120 if r[0]=='copies'else wc[r[2]]if r[0]=='demand'else 0 for r in rows]);neq=next(j for j,r in enumerate(rows)if r[0]=='distinct');lo=rhs.astype(float);lo[neq:]=-np.inf
c=np.array([cost(win[patterns[j][0]][0]-sum(patterns[j][1]))if typ=='x'else 0 for typ,j,t,w in vs]);print('MODEL',len(vs),len(rows),flush=True)
q=linprog(c,A_eq=A[:neq],b_eq=rhs[:neq],A_ub=A[neq:],b_ub=rhs[neq:],bounds=(0,None),method='highs');print('LP',q.status,'gain',basecost-localcost-q.fun if q.success else None,flush=True)
(O/'LP.json').write_text(json.dumps(dict(status=int(q.status),message=q.message,gain=basecost-localcost-q.fun if q.success else None,variables=len(vs),rows=len(rows)),indent=2)+'\n')
start=time.monotonic();q=milp(c,integrality=np.ones(len(vs)),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,lo,rhs),options={'time_limit':60,'mip_rel_gap':1e-9})
out=dict(label='joint-pattern-call-flow',order=D['order'],windows=D['windows'],status=int(q.status),message=q.message,seconds=time.monotonic()-start)
if q.x is not None:
 x=np.rint(q.x).astype(np.int64);assert np.array_equal((A@x)[:neq],rhs[:neq])and np.all((A@x)[neq:]<=rhs[neq:]);H=localH.copy();sel=[];y=defaultdict(int)
 for val,(typ,j,t,w)in zip(x,vs):
  if not val:continue
  i,p=patterns[j]
  if typ=='x':
   sel.append(['x',list(i),list(p),int(val)]);left=win[i][0]-sum(p)
   if left:H[left]+=int(val)
  else:y[i,t,w]+=int(val)
 sel.extend(['y',list(i),[t,w],v]for (i,t,w),v in y.items())
 assert m*D['live']-sum(r*n for r,n in H.items())==D['deficit']
 root=brentq(lambda z:sum(n*(r/m)**(1-z)for r,n in H.items())/D['live']+32*m*m*sum(H.values())/1e16*m**(z-1)/D['live']-1,0,.01,xtol=1e-15)
 out.update(objective=float(c@x)+localcost,gain=basecost-localcost-float(c@x),gap=float(q.mip_gap),profile=dict(sorted(H.items())),float_root=root,selection=sel)
(O/'NOMINATION.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items()if k not in ['order','windows','selection','profile']},flush=True)
