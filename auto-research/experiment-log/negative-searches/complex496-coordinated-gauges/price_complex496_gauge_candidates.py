"""Whole-owner pooled pricing screen of changed gauge words; nomination, not admission."""
from pathlib import Path
from collections import Counter
from functools import lru_cache
from fractions import Fraction
import json,math,time,sys
import numpy as np
from scipy.optimize import milp,LinearConstraint,Bounds,brentq
from scipy.sparse import lil_matrix
R=Path(__file__).resolve().parent;D=json.load(open(R/'source496-review/provenance/POOLED-ALLOCATION.json'));SRC=R/'complex496-gauge-intersections';O=R/'complex496-gauge-pricing';O.mkdir(exist_ok=False)
win={int(i):(p,r,st) for i,(p,r,st) in D['windows'].items()};T=D['T'];m=D['ambient'];W=D['live'];ports=120;nstages=9;b=float(Fraction(json.load(open(R/'source496-review/EXPECTED.json'))['complex_lower']))
@lru_cache(None)
def model(widths):
 def pats(cap,k=0,pat=()):
  yield pat
  if len(pat)>=T:return
  for j in range(k,len(widths)):
   if widths[j]<=cap:yield from pats(cap-widths[j],j,pat+(widths[j],))
 vs=[('x',i,p) for i,(_,rank,st) in win.items() for p in pats(rank)]+[('y',i,(s,w)) for i,(_,rank,st) in win.items() for s in st for w in widths]
 rows=[('copies',i) for i in win]+[('balance',i,w) for i in win for w in widths]+[('demand',s,w) for s in range(nstages) for w in widths];ri={r:j for j,r in enumerate(rows)};A=lil_matrix((len(rows),len(vs)),dtype=float)
 for j,(k,i,arg) in enumerate(vs):
  if k=='x':
   A[ri['copies',i],j]=1
   for w,n in Counter(arg).items():A[ri['balance',i,w],j]=n
  else:
   s,w=arg;A[ri['balance',i,w],j]=-1;A[ri['demand',s,w],j]=1
 def cost(r):return r*math.expm1(b*math.log(m/r))/b+(32*m*m/1e16)*m**b/b if r else 0
 c=np.array([cost(win[i][1]-sum(arg)) if k=='x' else 0 for k,i,arg in vs]);return vs,rows,A.tocsr(),c
ledger=[]
for f in sorted(SRC.glob('*/RESULT.json')):
 d=json.load(open(f));wc={int(w):n for w,n in d['width_counts'].items()};vs,rows,A,c=model(tuple(sorted(wc)));rhs=np.array([ports*T if row[0]=='copies' else wc[row[2]]*T if row[0]=='demand' else 0 for row in rows]);t=time.monotonic();res=milp(c,integrality=np.ones(len(vs)),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,rhs,rhs),options={'time_limit':60,'mip_rel_gap':1e-10});row=dict(label=d['label'],status=int(res.status),message=res.message,seconds=time.monotonic()-t)
 if res.x is not None:
  x=np.rint(res.x).astype(np.int64);assert np.array_equal(A@x,rhs);H=Counter({int(r):n*T*nstages for r,n in d['profile'].items()})
  for val,(kind,i,arg) in zip(x,vs):
   r=win[i][1]-sum(arg) if kind=='x' else 0
   if val and r:H[r]+=int(val)
  deficit=m*W-sum(r*n for r,n in H.items());assert deficit==D['ambient']*D['live']-sum(int(r)*n for r,n in D['profile'].items()),deficit
  root=brentq(lambda z:sum(n*(r/m)**(1-z) for r,n in H.items())/W+32*m*m*sum(H.values())/1e16*m**(z-1)/W-1,0,.01,xtol=1e-15)
  row.update(float_root=root,profile=dict(sorted(H.items())),gap=float(res.mip_gap),better_than_parent_float=root>b+1e-15,selection=[[kind,i,list(arg),int(v)] for (kind,i,arg),v in zip(vs,x) if v])
 (O/(d['label']+'.json')).write_text(json.dumps(row,indent=2)+'\n');brief={k:v for k,v in row.items() if k not in ['selection','profile']};ledger.append(brief);print(brief,flush=True)
(O/'COMPLETE.json').write_text(json.dumps(ledger,indent=2)+'\n')
