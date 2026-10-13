"""Mix legal local profiles across complete invocations; allocation relaxation only.
A gain would require explicit assignment satisfying the chosen per-invocation word,
not merely aggregate width conservation or unconstrained edge coloring.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import json,math,time
import numpy as np
from scipy.optimize import milp,linprog,LinearConstraint,Bounds,brentq
from scipy.sparse import lil_matrix
R=Path(__file__).resolve().parent;O=R/'complex501-heterogeneous-words';O.mkdir(exist_ok=False);D=json.load(open(R/'source496-review/provenance/POOLED-ALLOCATION.json'));T=D['T'];m=D['ambient'];live0=D['live'];L=9;b=float(Fraction(json.load(open(R/'source501-delta-review/EXPECTED.json'))['complex_lower']));win={int(i):(p,r,st) for i,(p,r,st) in D['windows'].items()};candidates=[];seen=set()
for src in ['complex501-selective-gauges','complex501-kernel-gauge-trades']:
 for f in sorted((R/src).glob('*/RESULT.json')):
  d=json.load(open(f));H={int(r):n for r,n in d['profile'].items()};wc={int(w):n for w,n in d['width_counts'].items()};sig=json.dumps([H,wc],sort_keys=True)
  if sig in seen:continue
  seen.add(sig);assert sum(wc.values())==560;candidates.append(dict(source=str(f.relative_to(R)),label=d['label'],profile=H,widths=wc))
widths=sorted({w for c in candidates for w in c['widths']})
def pats(cap,k=0,pat=()):
 yield pat
 if len(pat)>=T:return
 for j in range(k,len(widths)):
  if widths[j]<=cap:yield from pats(cap-widths[j],j,pat+(widths[j],))
def pad(p):
 n=math.ceil(p/51);return [p//n+(i<p%n) for i in range(n)] if n else []
def cost(r):return r*math.expm1(b*math.log(m/r))/b+32*m*m/1e16*m**b/b if r else 0
vs=[('x',i,p) for i,(_,rank,st) in win.items() for p in pats(rank)]+[('y',i,(s,w)) for i,(_,rank,st) in win.items() for s in st for w in widths]+[('z',s,(w,q)) for s in range(L) for w in widths for q in range(1,min(T,m//w)+1)]+[('word',s,j) for s in range(L) for j in range(len(candidates))]
rows=[('copies',i) for i in win]+[('balance',i,w) for i in win for w in widths]+[('demand',s,w) for s in range(L) for w in widths]+[('calls',s) for s in range(L)];ri={r:j for j,r in enumerate(rows)};A=lil_matrix((len(rows),len(vs)),dtype=float)
for j,(k,i,arg) in enumerate(vs):
 if k=='x':
  A[ri['copies',i],j]=1
  for w,n in Counter(arg).items():A[ri['balance',i,w],j]=n
 elif k=='y':
  s,w=arg;A[ri['balance',i,w],j]=-1;A[ri['demand',s,w],j]=1
 elif k=='z':w,q=arg;A[ri['demand',i,w],j]=q
 else:
  A[ri['calls',i],j]=1
  for w,n in candidates[arg]['widths'].items():A[ri['demand',i,w],j]=-n
A=A.tocsr();rhs=np.array([120*T if row[0]=='copies' else T if row[0]=='calls' else 0 for row in rows]);c=np.array([cost(win[i][1]-sum(a)) if k=='x' else sum(cost(r) for r in pad(m-a[0]*a[1])) if k=='z' else sum(n*cost(r) for r,n in candidates[a]['profile'].items()) if k=='word' else 0 for k,i,a in vs]);base=json.load(open(R/'leader-pr502-evidence/EXPECTED.json'));H0={int(r):n for r,n in base['global_profile'].items()};basecost=sum(n*cost(r) for r,n in H0.items());t=time.monotonic();res=linprog(c,A_eq=A,b_eq=rhs,bounds=(0,None),method='highs');assert res.success
info=dict(status='FLOAT_LP_RELAXATION_ONLY',candidates=len(candidates),widths=widths,variables=len(vs),rows=len(rows),baseline_cost=basecost,objective=float(res.fun),cost_gain=basecost-float(res.fun),seconds=time.monotonic()-t,scope='Relaxed heterogeneous word assignment. Aggregate feasible widths do not certify physical invocation ownership.')
(O/'CANDIDATES.json').write_text(json.dumps(candidates,indent=2)+'\n');(O/'LP.json').write_text(json.dumps(info,indent=2)+'\n');print(info,flush=True)
if res.fun<basecost-1e-6:
 t=time.monotonic();res=milp(c,integrality=np.ones(len(vs)),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,rhs,rhs),options={'time_limit':90,'mip_rel_gap':1e-9});row=dict(status=int(res.status),message=res.message,seconds=time.monotonic()-t)
 if res.x is not None:
  x=np.rint(res.x).astype(np.int64);assert np.array_equal(A@x,rhs);H=Counter();banks=0;choices=[]
  for v,(k,i,a) in zip(x,vs):
   if not v:continue
   if k=='x':
    r=win[i][1]-sum(a)
    if r:H[r]+=int(v)
   elif k=='z':
    banks+=int(v)
    for r in pad(m-a[0]*a[1]):H[r]+=int(v)
   elif k=='word':
    for r,n in candidates[a]['profile'].items():H[r]+=int(v)*n
    choices.append(dict(stage=i,candidate=a,label=candidates[a]['label'],count=int(v)))
  live=live0+banks;assert m*live-sum(r*n for r,n in H.items())==2496
  root=brentq(lambda z:sum(n*(r/m)**(1-z) for r,n in H.items())/live+32*m*m*sum(H.values())/1e16*m**(z-1)/live-1,0,.01,xtol=1e-15)
  row.update(objective=float(c@x),cost_gain=basecost-float(c@x),gap=float(res.mip_gap),banks=banks,profile=dict(sorted(H.items())),float_root=root,words=choices,selection=[[k,i,list(a) if isinstance(a,tuple) else a,int(v)] for (k,i,a),v in zip(vs,x) if v])
 (O/'MILP.json').write_text(json.dumps(row,indent=2)+'\n');print({k:v for k,v in row.items() if k not in ['words','selection','profile']},flush=True)
