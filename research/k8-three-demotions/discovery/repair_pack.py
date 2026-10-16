"""Repair a changed width inventory by complete-call transportation."""
import json,gzip,math,random
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
P=Path(__file__).resolve().parent;ROOT=P.parents[2];PRE=ROOT/'research/k8-eight-ends-t16'
rd=lambda f:json.loads(gzip.decompress(f.read_bytes()) if f.suffix=='.gz' else f.read_bytes())
plan=rd(PRE/'PLAN.json.gz');roles=rd(PRE/'OWNERS.json.gz');w=rd(P.parent/'FULL-WORD.json.gz');widths=[len(w['helper_final'].get(str(h),[0]*9))-len(w['start_extra'].get(str(h),[])) for h in range(224,704)]
bins=[];lookup={};eligible=defaultdict(list)
for key,(cap,times) in plan['windows'].items():
 rep,ch=map(int,key.split(','))
 for port in range(112):
  fam=rep*896+(2*plan['pairs'][str(ch)]+plan['sides'][str(ch)])*112+port;i=len(bins);bins.append((rep,ch,port,cap,fam));lookup[rep,ch,port]=i
  for t in times:eligible[t].append(i)
bycall=defaultdict(list);assignment=[];used=np.zeros(len(bins),dtype=int)
for j,z in enumerate(roles):
 i=lookup[z['owner_replica'],z['child'],z['port']];assignment.append(i);bycall[z['time']].append(j)
 if z['width']==widths[z['helper']]:used[i]+=z['width']
 else:assignment[-1]=-1
 z['width']=widths[z['helper']]
cap=np.array([b[3] for b in bins]);phi=np.array([r*math.expm1(.001678*math.log(73/r))/.001678 if r else 0 for r in range(49)])
for t,js in bycall.items():
 for j in js:
  if assignment[j]>=0:used[assignment[j]]-=roles[j]['width']
 dem=Counter(roles[j]['width'] for j in js);groups=defaultdict(list)
 for i in eligible[t]:
  if cap[i]-used[i]>=min(dem):groups[int(cap[i]-used[i])].append(i)
 ws=sorted(dem);vs=sorted(groups);edges=[(w,v) for w in ws for v in vs if w<=v];rr=[];cc=[];dd=[]
 for k,(ww,v) in enumerate(edges):rr.extend([ws.index(ww),len(ws)+vs.index(v)]);cc.extend([k,k]);dd.extend([1,1])
 A=coo_matrix((dd,(rr,cc)),shape=(len(ws)+len(vs),len(edges))).tocsr();c=np.array([phi[v-ww]-phi[v] for ww,v in edges]);b=np.array([dem[ww] for ww in ws]+[len(groups[v]) for v in vs]);res=linprog(c,A_eq=A[:len(ws)],b_eq=b[:len(ws)],A_ub=A[len(ws):],b_ub=b[len(ws):],bounds=(0,None),method='highs');assert res.success,(t,res.message);xx=np.rint(res.x).astype(int);assert np.max(abs(xx-res.x))<1e-5 and np.array_equal(A[:len(ws)]@xx,b[:len(ws)]) and np.all(A[len(ws):]@xx<=b[len(ws):])
 helpers=defaultdict(list)
 for j in js:helpers[roles[j]['width']].append(j)
 for (ww,v),n in zip(edges,xx):
  for _ in range(n):i=groups[v].pop();j=helpers[ww].pop();assignment[j]=i;used[i]+=ww
assert all(i>=0 for i in assignment) and np.all(used<=cap)
offset=Counter();out=[]
for j,z in enumerate(roles):
 i=assignment[j];rep,ch,port,cp,fam=bins[i];out.append(z|dict(owner_replica=rep,child=ch,port=port,copy=rep*112+port,family=fam,offset=offset[i]));offset[i]+=z['width']
idle=Counter(int(x) for x in cap-used if x);H=Counter({int(r):144*n for r,n in w['report']['local_profile'].items()});H.update(idle);plan['profile']={str(r):n for r,n in sorted(H.items())};plan['provider_registry']['gauge44']['widths']=widths;plan['provider_registry']['gauge44']['actual_paid_profile']=w['report']['local_profile']
for c in plan['per_call_widths']:c['widths']=widths
outdir=P/'repair3';outdir.mkdir(exist_ok=True);(outdir/'OWNERS.json.gz').write_bytes(gzip.compress(json.dumps(out,sort_keys=True,separators=(',',':')).encode(),mtime=0));(outdir/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('PASS_REPAIR',dict(sorted(idle.items())))
