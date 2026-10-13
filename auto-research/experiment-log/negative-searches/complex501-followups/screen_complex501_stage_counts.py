"""Nomination screen: PR501 local word at other odd stage counts.
Generalized idle windows follow the existing paired-chain pattern; no new physical
route, prefix, row, or Gaussian compiler admission is claimed.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import json,math,time
import numpy as np
from scipy.optimize import milp,LinearConstraint,Bounds,brentq
from scipy.sparse import lil_matrix
R=Path(__file__).resolve().parent;O=R/'complex501-stage-counts';O.mkdir(exist_ok=False)
D=json.load(open(R/'source496-review/provenance/POOLED-ALLOCATION.json'));local={int(r):n for r,n in json.load(open(R/'source501-delta-review/provenance/RETIME-FROZEN.json'))['local_profile'].items()};wc=Counter(D['widths']);widths=sorted(wc);T=D['T'];b=float(Fraction(json.load(open(R/'source501-delta-review/EXPECTED.json'))['complex_lower']));ledger=[]
for K in [4,3,5,2,6,7]:
 m=16*K+9;L=2*K+1;live0=2*K*120*T;wins=[]
 for p in range(1,K):wins.extend([(p,16*p,list(range(2*p))),(p,8,[2*p])]*2)
 for p in range(K-1):wins.extend([(p,16*(K-1-p),list(range(2*p+3,L)))]*2)
 win=dict(enumerate(wins));deficit=m*live0-(sum(r*n for r,n in local.items())*T*L+sum(r for p,r,st in wins)*120*T-sum(D['widths'])*T*L)
 if K==4:assert sorted(wins)==sorted((p,r,st) for p,r,st in D['windows'].values())
 def pats(cap,k=0,pat=()):
  yield pat
  if len(pat)>=T:return
  for j in range(k,len(widths)):
   if widths[j]<=cap:yield from pats(cap-widths[j],j,pat+(widths[j],))
 vs=[('x',i,p) for i,(_,rank,st) in win.items() for p in pats(rank)]+[('y',i,(s,w)) for i,(_,rank,st) in win.items() for s in st for w in widths]+[('z',s,(w,q)) for s in range(L) for w in widths for q in range(1,min(T,m//w)+1)]
 rows=[('copies',i) for i in win]+[('balance',i,w) for i in win for w in widths]+[('demand',s,w) for s in range(L) for w in widths];ri={r:j for j,r in enumerate(rows)};A=lil_matrix((len(rows),len(vs)),dtype=float)
 for j,(kind,i,arg) in enumerate(vs):
  if kind=='x':
   A[ri['copies',i],j]=1
   for w,n in Counter(arg).items():A[ri['balance',i,w],j]=n
  elif kind=='y':
   s,w=arg;A[ri['balance',i,w],j]=-1;A[ri['demand',s,w],j]=1
  else:w,q=arg;A[ri['demand',i,w],j]=q
 A=A.tocsr();rhs=np.array([120*T if row[0]=='copies' else wc[row[2]]*T if row[0]=='demand' else 0 for row in rows])
 def pad(p):
  n=math.ceil(p/math.floor(.7*m));return [p//n+(i<p%n) for i in range(n)] if n else []
 def cost(r):return r*math.expm1(b*math.log(m/r))/b+32*m*m/1e16*m**b/b if r else 0
 c=np.array([cost(win[i][1]-sum(arg)) if k=='x' else sum(cost(r) for r in pad(m-arg[0]*arg[1])) if k=='z' else 0 for k,i,arg in vs]);t=time.monotonic()
 res=milp(c,integrality=np.ones(len(vs)),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,rhs,rhs),options={'time_limit':60,'mip_rel_gap':1e-10});row=dict(pairs=K,m=m,stages=L,variables=len(vs),status=int(res.status),message=res.message,seconds=time.monotonic()-t,deficit=deficit)
 if res.x is not None:
  x=np.rint(res.x).astype(np.int64);assert np.array_equal(A@x,rhs);H=Counter({r:n*T*L for r,n in local.items()});banks=0
  for val,(kind,i,arg) in zip(x,vs):
   if val and kind=='x':
    r=win[i][1]-sum(arg)
    if r:H[r]+=int(val)
   if val and kind=='z':
    banks+=int(val)
    for r in pad(m-arg[0]*arg[1]):H[r]+=int(val)
  live=live0+banks;assert m*live-sum(r*n for r,n in H.items())==deficit
  root=brentq(lambda z:sum(n*(r/m)**(1-z) for r,n in H.items())/live+32*m*m*sum(H.values())/1e16*m**(z-1)/live-1,0,.01,xtol=1e-15)
  row.update(float_root=root,banks=banks,live=live,gap=float(res.mip_gap),profile=dict(sorted(H.items())),selection=[[k,i,list(a),int(v)] for (k,i,a),v in zip(vs,x) if v],windows=win)
 (O/f'K{K}.json').write_text(json.dumps(row,indent=2)+'\n');brief={k:v for k,v in row.items() if k not in ['profile','selection','windows']};ledger.append(brief);print(brief,flush=True)
(O/'COMPLETE.json').write_text(json.dumps(ledger,indent=2)+'\n')
