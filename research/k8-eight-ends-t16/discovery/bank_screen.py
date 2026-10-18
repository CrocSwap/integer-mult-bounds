"""Relaxed stage-private homogeneous banks; no physical feasibility claim."""
import json,gzip,math
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.optimize import linprog,brentq
P=Path(__file__).resolve().parent;ROOT=P.parents[2];p=json.loads(gzip.decompress((ROOT/'research/k8-eight-ends/PLAN.json.gz').read_bytes()));desc=p['provider_registry']['gauge44'];H0={int(r):n for r,n in desc['actual_paid_profile'].items()};inv=Counter(desc['widths']);ws=sorted(inv);results=[]
for K in range(2,7):
 L=2*K+1;m=16*K+9;V=224*K;caps={8:224*(K-1),**{16*p:448 for p in range(1,K)}};limit=int(m/math.sqrt(2));columns=[];rs=[];banks=[]
 def split(r):
  if not r:return []
  n=math.ceil(r/limit);return [r//n+(i<r%n) for i in range(n)]
 def enum(cap,idx=0,vec=()):
  if idx==len(ws):yield vec,cap;return
  for n in range(cap//ws[idx]+1):yield from enum(cap-n*ws[idx],idx+1,vec+(n,))
 for j,cap in enumerate(caps):
  for vec,rem in enum(cap):columns.append([int(i==j) for i in range(len(caps))]+list(vec));rs.append(split(rem));banks.append(0)
 # This screen follows the inherited homogeneous per-stage banks and at most eight replicas.
 for j,w in enumerate(ws):
  for q in range(1,min(8,(m-(9-w))//w)+1):
   columns.append([0]*len(caps)+[q if i==j else 0 for i in range(len(ws))]);rs.append(split(m-q*w));banks.append(1)
 A=np.array(columns).T;rhs=np.array(list(caps.values())+[L*inv[w] for w in ws]);b=.0016763;cost=lambda r:r*math.expm1(b*math.log(m/r))/b;c=np.array([sum(cost(r) for r in rr) for rr in rs]);sol=linprog(c,A_eq=A,b_eq=rhs,bounds=(0,None),method='highs');assert sol.success
 H=Counter({r:L*n for r,n in H0.items()});count=0
 for x,rr,bank in zip(sol.x,rs,banks):
  if x<1e-9:continue
  for r in rr:H[r]+=x
  count+=x*bank
 root=brentq(lambda z:sum(n*(r/m)**(1-z) for r,n in H.items())/(V+count)-1,0,.01,xtol=1e-15);result=dict(pairs=K,stages=L,m=m,bank_count_relaxed=count,complex_relaxed=root,kappa_relaxed=root/(1+root),profile=dict(sorted(H.items())),status='FLOATING_RELAXATION_NOT_A_SUPPLIER');results.append(result);print({k:v for k,v in result.items() if k!='profile'},flush=True)
(P/'BANK-STAGES.json').write_text(json.dumps(results,indent=2)+'\n')
