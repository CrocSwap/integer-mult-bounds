"""Discovery only: coordinated complete-call reassignment.

Prepared with OpenAI Codex assistance; Apache-2.0. See ../NOTICE.md.
SciPy/HiGHS nominates integer feasible maps; only the separate unchanged
physical verifier and rational engines may certify a kappa value. A timed-out
solve may supply a checked feasible incumbent; no optimality is claimed.
Run from the repository root. The frozen map, not a new search, is verified.
"""
import argparse, gzip, json, math, random, time
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy.optimize import linprog, milp, Bounds, LinearConstraint
from scipy.sparse import coo_matrix

ap=argparse.ArgumentParser();ap.add_argument('--passes',type=int,default=10);ap.add_argument('--seed',type=int,default=13);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--input',type=Path,default=Path('research/gauge44-slots/data'));ap.add_argument('--block',type=int,default=1);ap.add_argument('--limit',type=float,default=3);ap.add_argument('--target48',action='store_true');a=ap.parse_args()
p=a.input;plan=json.loads((p/'PLAN.json').read_text());roles=json.loads(gzip.decompress((p/'OWNERS.json.gz').read_bytes()))
rng=random.Random(a.seed);V=112;bins=[];eligible=defaultdict(list);lookup={}
for key,(cap,times) in plan['windows'].items():
 rep,ch=map(int,key.split(','))
 for port in range(V):
  fam=rep*896+(2*plan['pairs'][str(ch)]+plan['sides'][str(ch)])*V+port
  idx=len(bins);bins.append((rep,ch,port,cap,fam));lookup[rep,ch,port]=idx
  for t in times:eligible[t].append(idx)
for t,ids in eligible.items():assert len({bins[i][4] for i in ids})==len(ids)
bycall=defaultdict(list);assignment=[];used=np.zeros(len(bins),dtype=int)
for j,z in enumerate(roles):
 i=lookup[z['owner_replica'],z['child'],z['port']];assignment.append(i);used[i]+=z['width'];bycall[z['time']].append(j)
cap=np.array([b[3] for b in bins]);phi=np.array([r*math.expm1(.0016769*math.log(73/r))/.0016769 if r else 0 for r in range(49)])
def cost():return float(phi[cap-used].sum())
def save():
 offsets=Counter();out=[]
 for j,z in enumerate(roles):
  i=assignment[j];rep,ch,port,cp,fam=bins[i];new=z|dict(owner_replica=rep,child=ch,port=port,copy=rep*V+port,family=fam,offset=offsets[i]);offsets[i]+=z['width'];out.append(new)
 assert all(offsets[i]==used[i]<=cap[i] for i in range(len(bins)))
 a.out.mkdir(exist_ok=True,parents=True);(a.out/'OWNERS.json.gz').write_bytes(gzip.compress(json.dumps(out,sort_keys=True,separators=(',',':')).encode(),mtime=0))
 idle=Counter(int(x) for x in cap-used if x);H=Counter({int(r):n*72 for r,n in plan['provider_registry']['gauge44']['actual_paid_profile'].items()});H.update(idle)
 np=plan|dict(profile=dict(sorted(H.items())));(a.out/'PLAN.json').write_text(json.dumps(np,indent=2)+'\n');(a.out/'SEARCH.json').write_text(json.dumps(dict(seed=a.seed,cost=cost(),idle=dict(sorted(idle.items())),trace=trace),indent=2)+'\n')
trace=[];initial=cost();print('initial',initial,Counter(cap-used),flush=True)
if a.block>1:
 import itertools
 for it in range(a.passes):
  # Nearby calls share narrow windows; random distant calls provide escape paths.
  t=rng.randrange(72);ts=sorted({t,*rng.sample([k for k in range(72) if k!=t],a.block-1)})
  if it%2:ts=sorted(rng.sample(list(range(max(0,t-6),min(72,t+7))),a.block))
  if a.target48:
   occupants=defaultdict(list)
   for j,i in enumerate(assignment):
    if cap[i]==48:occupants[i].append(roles[j]['time'])
   target=rng.choice([x for x in occupants.values() if len(x)==a.block]);ts=sorted(target);assert len(set(ts))==len(ts)
  ws=[4,8,9] if a.target48 else [4,5,7,8,9]
  oldcost=cost();js=[j for t in ts for j in bycall[t] if roles[j]['width'] in ws];oldassign={j:assignment[j] for j in js}
  for j in js:used[assignment[j]]-=roles[j]['width']
  es=[set(eligible[t])-{assignment[j] for j in bycall[t] if roles[j]['width'] not in ws} for t in ts]
  allids=set().union(*es);groups=defaultdict(list)
  for i in allids:
   v=int(cap[i]-used[i]);mask=sum(1<<k for k in range(len(ts)) if i in es[k]);groups[v,mask].append(i)
  keys=sorted(groups);dem=Counter((ts.index(roles[j]['time']),roles[j]['width']) for j in js)
  rows=[];cols=[];vals=[];patterns=[];costs=[]
  for g,(v,mask) in enumerate(keys):
   opts=[([0]+ws if mask>>k&1 else [0]) for k in range(len(ts))]
   for pat in itertools.product(*opts):
    if sum(pat)>v:continue
    col=len(patterns);patterns.append((g,pat));costs.append(phi[v-sum(pat)]-phi[v]);rows.append(g);cols.append(col);vals.append(1)
    for k,w in enumerate(pat):
     if w:rows.append(len(keys)+k*len(ws)+ws.index(w));cols.append(col);vals.append(1)
  A=coo_matrix((vals,(rows,cols)),shape=(len(keys)+len(ws)*len(ts),len(patterns))).tocsc();b=np.array([len(groups[k]) for k in keys]+[dem[k,w] for k in range(len(ts)) for w in ws])
  res=milp(np.array(costs),integrality=np.ones(len(patterns)),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,b,b),options=dict(time_limit=a.limit,mip_rel_gap=0))
  accept=False
  if res.x is not None:
   xx=np.rint(res.x).astype(int)
   if np.max(abs(xx-res.x))<1e-5 and np.array_equal(A@xx,b):
    after=float(phi[cap-used].sum()+np.dot(costs,xx))
    if after<oldcost-1e-6:
     helpers=defaultdict(list)
     for j in js:helpers[ts.index(roles[j]['time']),roles[j]['width']].append(j)
     for (g,pat),n in zip(patterns,xx):
      for _ in range(n):
       i=groups[keys[g]].pop()
       for k,w in enumerate(pat):
        if w:j=helpers[k,w].pop();assignment[j]=i;used[i]+=w
     assert not any(helpers.values());assert cost()<oldcost-1e-6;accept=True
  if not accept:
   for j in js:assignment[j]=oldassign[j];used[assignment[j]]+=roles[j]['width']
  trace.append(dict(iteration=it,calls=ts,cost=cost(),gain=oldcost-cost(),solver_status=int(res.status),accepted=accept))
  if accept or it%20==0:save();print(trace[-1],flush=True)
 save();print('gain',initial-cost(),flush=True);raise SystemExit
for it in range(a.passes):
 order=list(range(72));rng.shuffle(order);changed=0
 for t in order:
  js=bycall[t];ids=eligible[t];oldcost=cost();dem=Counter(roles[j]['width'] for j in js)
  for j in js:used[assignment[j]]-=roles[j]['width']
  avail=cap[ids]-used[ids];groups=defaultdict(list)
  for i,v in zip(ids,avail):
   if v>=min(dem):groups[int(v)].append(i)
  ws=sorted(dem);vs=sorted(groups);edges=[(w,v) for w in ws for v in vs if w<=v];rr=[];cc=[];dd=[]
  for k,(w,v) in enumerate(edges):rr.extend([ws.index(w),len(ws)+vs.index(v)]);cc.extend([k,k]);dd.extend([1,1])
  A=coo_matrix((dd,(rr,cc)),shape=(len(ws)+len(vs),len(edges))).tocsr();c=np.array([phi[v-w]-phi[v] for w,v in edges])
  b=np.array([dem[w] for w in ws]+[len(groups[v]) for v in vs]);res=linprog(c,A_eq=A[:len(ws)],b_eq=b[:len(ws)],A_ub=A[len(ws):],b_ub=b[len(ws):],bounds=(0,None),method='highs')
  assert res.success;xx=np.rint(res.x).astype(int);assert np.max(abs(xx-res.x))<1e-5;assert np.array_equal(A[:len(ws)]@xx,b[:len(ws)]);assert np.all(A[len(ws):]@xx<=b[len(ws):])
  helpers=defaultdict(list)
  for j in js:helpers[roles[j]['width']].append(j)
  for g in groups.values():rng.shuffle(g)
  for (w,v),n in zip(edges,xx):
   for _ in range(n):
    i=groups[v].pop();j=helpers[w].pop();assignment[j]=i;used[i]+=w
  newcost=cost();assert newcost<=oldcost+1e-6
  if oldcost-newcost>1e-6:changed+=1
 trace.append(dict(pass_number=it,cost=cost(),changed=changed));save();print(trace[-1],flush=True)
 if changed==0 and it>=2:break
print('gain',initial-cost(),flush=True)
