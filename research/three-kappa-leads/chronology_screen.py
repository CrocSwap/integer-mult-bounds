"""Exploratory floating LP column generation; exact certificate remains separate."""
import os,sys,json,importlib.util,math,time
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
ROOT=Path(__file__).resolve().parents[2]
os.environ['OWNER_SOURCE_REPO']=str(ROOT)
from dependency import source
P=source()/'owners'
s=importlib.util.spec_from_file_location('source_context',P/'source_context.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
c=v.common.context();d=json.loads((P/'CANDIDATE.json').read_text());W=v.W;INV=v.INV
k=0.0017300475520933442

def patterns(cap,dual):
 # Dynamic program over occupied integer mass; values are exploratory floats.
 dp=[None]*(cap+1);dp[0]=(0.,(0,)*6)
 for used in range(cap+1):
  if dp[used] is None:continue
  val,q=dp[used]
  for i,w in enumerate(W):
   if used+w<=cap and (dp[used+w] is None or val+dual[i]>dp[used+w][0]):
    nq=list(q);nq[i]+=1;dp[used+w]=(val+dual[i],tuple(nq))
 return min(((((cap-u)**(1-k) if cap>u else 0)-z[0]),z[1]) for u,z in enumerate(dp) if z is not None)

def solve(order,label):
 win=c.owner.windows(c.template,order,45)
 G=[[*key,n] for key,n in sorted(Counter((cap,lo,hi) for cap,lo,hi in win.values()).items())]
 for g in G:g[3]*=112
 # Seed every group with all predecessor pattern types of its capacity.
 bycap={cap:set() for cap,lo,hi,n in G}
 for gi,q,n in d['x']:bycap[d['groups'][gi][0]].add(tuple(q))
 for cap in bycap:
  bycap[cap].add((0,)*6)
  for i,w in enumerate(W):bycap[cap].add(tuple(cap//w if j==i else 0 for j in range(6)))
 pools=[set(bycap[g[0]]) for g in G]
 flows=[(gi,t,i) for gi,(cap,lo,hi,n) in enumerate(G) for t in range(lo+1,hi+1) for i,w in enumerate(W) if w<=cap]
 gt=sorted({(gi,t) for gi,t,i in flows});gtidx={key:i for i,key in enumerate(gt)}
 ne=len(G)*7+405*6
 b=np.zeros(ne)
 for gi,g in enumerate(G):b[gi*7]=g[3]
 for t in range(405):
  for i,w in enumerate(W):b[len(G)*7+t*6+i]=INV[w]
 for it in range(40):
  rr=[];cc=[];vv=[];ur=[];uc=[];uv=[];cost=[];xs=[]
  for gi,g in enumerate(G):
   for q in sorted(pools[gi]):
    j=len(cost);xs.append((gi,q));left=g[0]-sum(w*n for w,n in zip(W,q));cost.append(left**(1-k) if left else 0)
    rr.append(gi*7);cc.append(j);vv.append(1)
    for i,n in enumerate(q):
     if n:rr.append(gi*7+1+i);cc.append(j);vv.append(n)
  nx=len(cost)
  for gi,t,i in flows:
   j=len(cost);cost.append(0)
   rr.extend([gi*7+1+i,len(G)*7+t*6+i]);cc.extend([j,j]);vv.extend([-1,1]);ur.append(gtidx[gi,t]);uc.append(j);uv.append(1)
  A=coo_matrix((vv,(rr,cc)),shape=(ne,len(cost))).tocsr();U=coo_matrix((uv,(ur,uc)),shape=(len(gt),len(cost))).tocsr()
  res=linprog(cost,A_ub=U,b_ub=[G[gi][3] for gi,t in gt],A_eq=A,b_eq=b,bounds=(0,None),method='highs')
  if not res.success:raise RuntimeError(res.message)
  added=0;worst=0
  for gi,(cap,lo,hi,n) in enumerate(G):
   value,q=patterns(cap,res.eqlin.marginals[gi*7+1:gi*7+7]);reduced=value-res.eqlin.marginals[gi*7];worst=min(worst,reduced)
   if reduced < -1e-7 and q not in pools[gi]:pools[gi].add(q);added+=1
  local=sum(n*405*r**(1-k) for r,n in v.LOCAL.items());den=896*45*73**(1-k)
  print(label,it,'vars',len(cost),'obj',res.fun,'moment',(local+res.fun)/den,'added',added,'reduced',worst,flush=True)
  if not added or it == 0:
   result={'label':label,'status':'FLOAT_LP_EXPLORATORY_ONLY','order':order,'groups':G,'moment_at_comparator':(local+res.fun)/den,'idle_objective':res.fun,'worst_reduced_cost':worst,'x':[[gi,list(q),float(a)] for (gi,q),a in zip(xs,res.x[:nx]) if a>1e-7],'z':[[gi,t,W[i],float(a)] for (gi,t,i),a in zip(flows,res.x[nx:]) if a>1e-7]}
   Path('/tmp/three-kappa-'+label+'.json').write_text(json.dumps(result));return result
 raise RuntimeError('column generation round cap')
order=d['order'];swap=order[:];swap[332],swap[333]=swap[333],swap[332]
for label,clock in [('join-swap',swap)]:solve(clock,label)
