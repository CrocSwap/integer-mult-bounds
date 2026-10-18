"""Large-call-block nomination via knapsack column generation and integer patterns.
Baseline columns guarantee a literal feasible point. All final integer equations and
owner assignments are checked; separate unchanged physical admission is mandatory.
"""
import argparse,gzip,json,math,random,time
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from scipy.optimize import linprog,milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--passes',type=int,default=12);ap.add_argument('--block',type=int,default=12);ap.add_argument('--seed',type=int,default=263);ap.add_argument('--limit',type=float,default=5);ap.add_argument('--rounds',type=int,default=30);a=ap.parse_args();rng=random.Random(a.seed);plan=json.loads((a.input/'PLAN.json').read_text());roles=json.loads(gzip.decompress((a.input/'OWNERS.json.gz').read_bytes()));N=len(plan['order']);bins=[];eligible=defaultdict(set);lookup={}
for key,(cap,times) in plan['windows'].items():
 rep,ch=map(int,key.split(','))
 for port in range(112):
  fam=rep*896+(2*plan['pairs'][str(ch)]+plan['sides'][str(ch)])*112+port;i=len(bins);bins.append((rep,ch,port,cap,fam));lookup[rep,ch,port]=i
  for t in times:eligible[t].add(i)
bycall=defaultdict(list);assignment=[];used=np.zeros(len(bins),dtype=int)
for j,z in enumerate(roles):
 i=lookup[z['owner_replica'],z['child'],z['port']];assignment.append(i);used[i]+=z['width'];bycall[z['time']].append(j)
cap=np.array([z[3] for z in bins]);phi=np.array([r*math.expm1(.0016775*math.log(73/r))/.0016775 if r else 0 for r in range(49)])
def cost():return float(phi[cap-used].sum())
trace=[]
def save():
 offsets=Counter();out=[]
 for j,z in enumerate(roles):
  i=assignment[j];rep,ch,port,cp,fam=bins[i];out.append(z|dict(owner_replica=rep,child=ch,port=port,copy=rep*112+port,family=fam,offset=offsets[i]));offsets[i]+=z['width']
 assert all(offsets[i]==used[i]<=cap[i] for i in range(len(bins)))
 a.out.mkdir(exist_ok=True,parents=True);(a.out/'OWNERS.json.gz').write_bytes(gzip.compress(json.dumps(out,sort_keys=True,separators=(',',':')).encode(),mtime=0));idle=Counter(int(x) for x in cap-used if x);H=Counter({int(r):n*N for r,n in plan['provider_registry']['gauge44']['actual_paid_profile'].items()});H.update(idle);(a.out/'PLAN.json').write_text(json.dumps(plan|dict(profile={str(r):n for r,n in sorted(H.items())}),indent=2)+'\n');(a.out/'SEARCH.json').write_text(json.dumps(dict(seed=a.seed,cost=cost(),idle=dict(sorted(idle.items())),trace=trace),indent=2)+'\n')
initial=cost();print('initial',initial,flush=True)
for iteration in range(a.passes):
 begin=time.monotonic();B=a.block;ws=[4,5,7,8,9];occupants=defaultdict(list)
 for j,i in enumerate(assignment):occupants[i].append(roles[j]['time'])
 if iteration%3==0:
  t=rng.randrange(N-B+1);ts=list(range(t,t+B))
 else:
  choices=[i for i in occupants if cap[i]==48 and 0<cap[i]-used[i]<48] or [i for i in occupants if cap[i]==48];target=rng.choice(choices);chosen=set(occupants[target]);others=[t for t in range(N) if t not in chosen];rng.shuffle(others);ts=sorted(chosen|set(others[:max(0,B-len(chosen))]));B=len(ts)
 js=[j for t in ts for j in bycall[t]];oldcost=cost();old={j:assignment[j] for j in js}
 for j in js:used[assignment[j]]-=roles[j]['width']
 groups=defaultdict(list);mask_by_bin=defaultdict(int)
 for k,t in enumerate(ts):
  for i in eligible[t]:mask_by_bin[i]|=1<<k
 for i,mask in mask_by_bin.items():
  v=int(cap[i]-used[i]);groups[v,mask].append(i)
 keys=sorted(groups);gidx={key:g for g,key in enumerate(keys)};bin_group={i:g for g,key in enumerate(keys) for i in groups[key]};dem=Counter((ts.index(roles[j]['time']),roles[j]['width']) for j in js);rhs=np.array([len(groups[key]) for key in keys]+[dem[k,w] for k in range(B) for w in ws]);patterns=[];costs=[];known=set()
 def add(g,pat):
  p=tuple(pat)
  if (g,p) in known:return
  v,mask=keys[g];assert sum(p)<=v and all(not w or mask>>k&1 for k,w in enumerate(p));known.add((g,p));patterns.append((g,p));costs.append(phi[v-sum(p)]-phi[v])
 baseline=defaultdict(lambda:[0]*B)
 for j,i in old.items():
  k=ts.index(roles[j]['time']);assert baseline[i][k]==0;baseline[i][k]=roles[j]['width']
 for g,key in enumerate(keys):
  add(g,[0]*B)
  for i in groups[key]:
   if i in baseline:add(g,baseline[i])
 def matrix():
  rr=[];cc=[];vals=[]
  for col,(g,p) in enumerate(patterns):
   rr.append(g);cc.append(col);vals.append(1)
   for k,w in enumerate(p):
    if w:rr.append(len(keys)+k*len(ws)+ws.index(w));cc.append(col);vals.append(1)
  return coo_matrix((vals,(rr,cc)),shape=(len(rhs),len(patterns))).tocsc()
 lp=None;pricing=[]
 for rnd in range(a.rounds):
  A=matrix();lp=linprog(np.array(costs),A_eq=A,b_eq=rhs,bounds=(0,None),method='highs');assert lp.success,lp.message;dual=lp.eqlin.marginals;before=len(patterns);best_rc=0
  beta=dual[len(keys):].reshape(B,len(ws))
  for g,(v,mask) in enumerate(keys):
   dp=np.full(v+1,-np.inf);dp[0]=0;parents=[]
   for k in range(B):
    new=dp.copy();pick=np.zeros(v+1,dtype=int)
    if mask>>k&1:
     for wi,w in enumerate(ws):
      if w>v:continue
      cand=dp[:-w]+beta[k,wi];where=np.flatnonzero(cand>new[w:]+1e-10)+w;new[where]=cand[where-w];pick[where]=w
    dp=new;parents.append(pick)
   reduced=phi[v-np.arange(v+1)]-phi[v]-dp-dual[g]
   for fill in np.argsort(reduced)[:2]:
    rc=float(reduced[fill]);best_rc=min(best_rc,rc)
    if rc>=-1e-7:continue
    rem=int(fill);pat=[0]*B
    for k in range(B-1,-1,-1):pat[k]=int(parents[k][rem]);rem-=pat[k]
    assert rem==0;add(g,pat)
  pricing.append(dict(round=rnd,columns=len(patterns),added=len(patterns)-before,min_reduced_cost=best_rc,lp_gain=oldcost-float(phi[cap-used].sum()+lp.fun)))
  if rnd%10==0:print('pricing',iteration,pricing[-1],flush=True)
  if len(patterns)==before:break
 A=matrix();sol=milp(np.array(costs),integrality=np.ones(len(patterns)),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,rhs,rhs),options=dict(time_limit=a.limit,mip_rel_gap=0));accept=False
 if sol.x is not None:
  xx=np.rint(sol.x).astype(int)
  if max(abs(xx-sol.x))<1e-5 and np.array_equal(A@xx,rhs) and float(phi[cap-used].sum()+np.dot(costs,xx))<oldcost-1e-6:
   helpers=defaultdict(list)
   for j in js:helpers[ts.index(roles[j]['time']),roles[j]['width']].append(j)
   for (g,pat),count in zip(patterns,xx):
    for _ in range(count):
     i=groups[keys[g]].pop()
     for k,w in enumerate(pat):
      if w:j=helpers[k,w].pop();assignment[j]=i;used[i]+=w
   assert not any(helpers.values()) and np.all(used<=cap) and cost()<oldcost-1e-6;accept=True
 if not accept:
  for j,i in old.items():assignment[j]=i;used[i]+=roles[j]['width']
 r=dict(iteration=iteration,calls=ts,cost=cost(),gain=oldcost-cost(),accepted=accept,solver_status=int(sol.status),groups=len(keys),columns=len(patterns),pricing=pricing,seconds=time.monotonic()-begin);trace.append(r);save();print({k:v for k,v in r.items() if k!='pricing'},flush=True)
save();print('gain',initial-cost(),flush=True)
