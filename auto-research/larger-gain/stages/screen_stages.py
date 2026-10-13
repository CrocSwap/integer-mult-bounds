"""Nomination screen: PR564 local word at other odd stage counts.
Adapted from the retained PR501 follow-up by Rohan Arun with OpenAI Codex assistance.
This update was prepared with OpenAI Codex assistance, Apache-2.0.
Generalized idle windows follow the existing paired-chain pattern; no new physical
route, prefix, row, or Gaussian compiler admission is claimed.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import json,math,time,argparse,hashlib,os
import numpy as np
from scipy.optimize import milp,LinearConstraint,Bounds,brentq
from scipy.sparse import lil_matrix

ap=argparse.ArgumentParser();ap.add_argument('--extra-cold',type=int,default=0);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
O=a.out;O.mkdir(parents=True,exist_ok=False)
source=Path(os.environ.get('GAIN_PR564_SOURCE',Path(__file__).resolve().parents[3]/'research/complex-allcold'))/'data/PLAN.json'
D=json.loads(source.read_text());providers={}
for pid,desc in D['provider_registry'].items():
 local={int(r):n for r,n in desc['actual_paid_profile'].items()};wc=Counter(desc['widths'])
 for r,n in {1:a.extra_cold,2:2*a.extra_cold,3:-2*a.extra_cold}.items():local[r]+=n
 wc[9]-=a.extra_cold;wc[8]+=a.extra_cold;providers[pid]=(local,wc)
widths=[4,5,8,9];T=8;b=.0015956762845759986;ledger=[]
gaps={sum(r*n for r,n in H.items())-sum(r*n for r,n in wc.items())for H,wc in providers.values()};assert gaps=={1856}
(O/'SOURCE.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),extra_cold=a.extra_cold,scope='Updated bounded floating stage-count nomination with integer per-stage provider mixtures; requires new geometry, actual owner/spectator checks and exact invoice. Homogeneous-width auxiliary banks and at most8 roles per bin are searched. No global optimality claim.'),indent=2)+'\n')
for K in [4,3,2,5,6,7]:
 m=16*K+9;L=2*K+1;live0=2*K*112*T;wins=[]
 for p in range(1,K):wins.extend([(p,16*p,list(range(2*p))),(p,8,[2*p])]*2)
 for p in range(K-1):wins.extend([(p,16*(K-1-p),list(range(2*p+3,L)))]*2)
 win=dict(enumerate(wins));deficit=m*live0-(1856*T*L+sum(r for p,r,st in wins)*112*T)

 def pats(cap,k=0,pat=()):
  yield pat
  if len(pat)>=T:return
  for j in range(k,len(widths)):
   if widths[j]<=cap:yield from pats(cap-widths[j],j,pat+(widths[j],))
 vs=[('x',i,p) for i,(_,rank,st) in win.items() for p in pats(rank)]+[('y',i,(s,w)) for i,(_,rank,st) in win.items() for s in st for w in widths]+[('z',s,(w,q)) for s in range(L) for w in widths for q in range(1,min(T,(m-(9-w))//w)+1)]+[('p',s,pid)for s in range(L)for pid in providers]
 rows=[('copies',i) for i in win]+[('balance',i,w) for i in win for w in widths]+[('demand',s,w) for s in range(L) for w in widths]+[('provider',s)for s in range(L)];ri={r:j for j,r in enumerate(rows)};A=lil_matrix((len(rows),len(vs)),dtype=float)
 for j,(kind,i,arg) in enumerate(vs):
  if kind=='x':
   A[ri['copies',i],j]=1
   for w,n in Counter(arg).items():A[ri['balance',i,w],j]=n
  elif kind=='y':
   s,w=arg;A[ri['balance',i,w],j]=-1;A[ri['demand',s,w],j]=1
  elif kind=='z':w,q=arg;A[ri['demand',i,w],j]=q
  else:
   A[ri['provider',i],j]=1
   for w,n in providers[arg][1].items():A[ri['demand',i,w],j]=-n
 A=A.tocsr();rhs=np.array([112*T if row[0]=='copies' else T if row[0]=='provider' else 0 for row in rows])
 def pad(p):
  n=math.ceil(p/math.floor(.7*m));return [p//n+(i<p%n) for i in range(n)] if n else []
 def cost(r):return r*math.expm1(b*math.log(m/r))/b+32*m*m/1e16*m**b/b if r else 0
 c=np.array([sum(cost(r) for r in pad(win[i][1]-sum(arg))) if k=='x' else sum(cost(r) for r in pad(m-arg[0]*arg[1])) if k=='z' else sum(n*cost(r)for r,n in providers[arg][0].items())if k=='p' else 0 for k,i,arg in vs]);t=time.monotonic()
 res=milp(c,integrality=np.ones(len(vs)),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,rhs,rhs),options={'time_limit':20,'mip_rel_gap':1e-10});row=dict(pairs=K,m=m,stages=L,variables=len(vs),status=int(res.status),message=res.message,seconds=time.monotonic()-t,deficit=deficit)
 if res.x is not None:
  x=np.rint(res.x).astype(np.int64);assert np.array_equal(A@x,rhs);H=Counter();banks=0;mix=Counter()
  for val,(kind,i,arg) in zip(x,vs):
   if val and kind=='x':
    r=win[i][1]-sum(arg)
    for part in pad(r):H[part]+=int(val)
   if val and kind=='z':
    banks+=int(val)
    for r in pad(m-arg[0]*arg[1]):H[r]+=int(val)
   if val and kind=='p':
    H.update({r:int(val)*n for r,n in providers[arg][0].items()});mix[arg]+=int(val)
  live=live0+banks;assert m*live-sum(r*n for r,n in H.items())==deficit;assert m*m>2*max(H)**2
  root=brentq(lambda z:sum(n*(r/m)**(1-z) for r,n in H.items())/live+32*m*m*sum(H.values())/1e16*m**(z-1)/live-1,0,.01,xtol=1e-15)
  row.update(float_root=root,banks=banks,provider_counts=dict(mix),live=live,gap=float(res.mip_gap),profile=dict(sorted(H.items())),selection=[[k,i,list(a)if not isinstance(a,str)else a,int(v)] for (k,i,a),v in zip(vs,x) if v],windows=win)
 (O/f'K{K}.json').write_text(json.dumps(row,indent=2)+'\n');brief={k:v for k,v in row.items() if k not in ['profile','selection','windows']};ledger.append(brief);print(brief,flush=True)
(O/'COMPLETE.json').write_text(json.dumps(ledger,indent=2)+'\n')
