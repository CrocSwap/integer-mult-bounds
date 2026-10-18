"""Discovery: common-window pattern MILP plus exact bipartite edge colouring.
No search result is an admission witness. Frozen owners must pass the physical checker.
"""
import argparse,gzip,json,math,random,time
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix,csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--passes',type=int,default=100);ap.add_argument('--seed',type=int,default=251);ap.add_argument('--limit',type=float,default=1);a=ap.parse_args();rng=random.Random(a.seed);plan=json.loads((a.input/'PLAN.json').read_text());roles=json.loads(gzip.decompress((a.input/'OWNERS.json.gz').read_bytes()));N=len(plan['order']);bins=[];eligible=defaultdict(set);lookup={};V=112
for key,(cap,times) in plan['windows'].items():
 rep,ch=map(int,key.split(','))
 for port in range(V):
  fam=rep*896+(2*plan['pairs'][str(ch)]+plan['sides'][str(ch)])*V+port;idx=len(bins);bins.append((rep,ch,port,cap,fam));lookup[rep,ch,port]=idx
  for t in times:eligible[t].add(idx)
bycall=defaultdict(list);assignment=[];used=np.zeros(len(bins),dtype=int)
for j,z in enumerate(roles):
 i=lookup[z['owner_replica'],z['child'],z['port']];assignment.append(i);used[i]+=z['width'];bycall[z['time']].append(j)
cap=np.array([b[3] for b in bins]);phi=np.array([r*math.expm1(.0016775*math.log(73/r))/.0016775 if r else 0 for r in range(49)])
def cost():return float(phi[cap-used].sum())
trace=[]
def save():
 offsets=Counter();out=[]
 for j,z in enumerate(roles):
  i=assignment[j];rep,ch,port,cp,fam=bins[i];out.append(z|dict(owner_replica=rep,child=ch,port=port,copy=rep*V+port,family=fam,offset=offsets[i]));offsets[i]+=z['width']
 assert all(offsets[i]==used[i]<=cap[i] for i in range(len(bins)))
 a.out.mkdir(exist_ok=True,parents=True);(a.out/'OWNERS.json.gz').write_bytes(gzip.compress(json.dumps(out,sort_keys=True,separators=(',',':')).encode(),mtime=0));idle=Counter(int(x) for x in cap-used if x);H=Counter({int(r):n*N for r,n in plan['provider_registry']['gauge44']['actual_paid_profile'].items()});H.update(idle);(a.out/'PLAN.json').write_text(json.dumps(plan|dict(profile={str(r):c for r,c in sorted(H.items())}),indent=2)+'\n');(a.out/'SEARCH.json').write_text(json.dumps(dict(seed=a.seed,cost=cost(),idle=dict(sorted(idle.items())),trace=trace),indent=2)+'\n')

def colour(pattern_bins,width_demand,ts):
 """Each width has B*demand edges. Split into demand degree-B vertices,
 regularize the bipartite multigraph, then peel B perfect matchings."""
 B=len(ts);left=[];slots=defaultdict(list);real_bins=[]
 for idx,pat in pattern_bins:
  right=len(real_bins);real_bins.append(idx)
  for w,num in pat.items():slots[w].extend([right]*num)
 adj=[];label=[]
 for w,n in sorted(width_demand.items()):
  assert len(slots[w])==B*n;rng.shuffle(slots[w])
  for j in range(n):adj.append(Counter(slots[w][j*B:(j+1)*B]));label.append(w)
 left_count=len(adj);size=max(left_count,len(real_bins));adj.extend(Counter() for _ in range(size-left_count));right_degs=Counter()
 for row in adj:right_degs.update(row)
 deficits=[[i,B-right_degs[i]] for i in range(size) if right_degs[i]<B];k=0
 for i in range(size):
  rem=B-sum(adj[i].values())
  while rem:
   j,avail=deficits[k];take=min(rem,avail);adj[i][j]+=take;rem-=take;deficits[k][1]-=take
   if deficits[k][1]==0:k+=1
 assert all(sum(row.values())==B for row in adj)
 mapping={};order=list(ts);rng.shuffle(order)
 for t in order:
  rr=[];cc=[]
  for i,row in enumerate(adj):
   for j,n in row.items():
    if n:rr.append(i);cc.append(j)
  A=coo_matrix((np.ones(len(rr),dtype=int),(rr,cc)),shape=(size,size)).tocsr();matching=maximum_bipartite_matching(A,perm_type='column');assert np.all(matching>=0) and len(set(matching))==size
  helpers=defaultdict(list)
  for j in bycall[t]:
   if roles[j]['width'] in width_demand:helpers[roles[j]['width']].append(j)
  for i,j in enumerate(matching):
   assert adj[i][int(j)]>0;adj[i][int(j)]-=1
   if i<left_count:
    assert j<len(real_bins);mapping[helpers[label[i]].pop()]=real_bins[int(j)]
  assert not any(helpers.values())
 return mapping
initial=cost();print('initial',initial,flush=True)
for iteration in range(a.passes):
 B=rng.choice([6,8,10,12,16,20]);B=min(B,N);start=rng.randrange(N-B+1);ts=list(range(start,start+B));ws=rng.choice([[9],[7,9],[4,8,9],[4,5,7,8,9],[8,9]])
 js=[j for t in ts for j in bycall[t] if roles[j]['width'] in ws];dem=Counter(roles[j]['width'] for j in bycall[ts[0]] if roles[j]['width'] in ws);assert all(Counter(roles[j]['width'] for j in bycall[t] if roles[j]['width'] in ws)==dem for t in ts)
 oldcost=cost();old={j:assignment[j] for j in js}
 for j in js:used[assignment[j]]-=roles[j]['width']
 common=set.intersection(*(eligible[t] for t in ts));fixed={assignment[j] for t in ts for j in bycall[t] if roles[j]['width'] not in ws};common-=fixed;groups=defaultdict(list)
 for i in common:
  rem=int(cap[i]-used[i])
  if rem>=min(ws):groups[rem].append(i)
 vals=sorted(groups);patterns=[];c=[];rr=[];cc=[];aa=[];ws=sorted(dem)
 def enum(rem,k=0,pat=(),left=B):
  if k==len(ws):yield pat,rem;return
  for n in range(min(left,rem//ws[k])+1):yield from enum(rem-n*ws[k],k+1,pat+(n,),left-n)
 for g,v in enumerate(vals):
  for pat,rem in enum(v):
   col=len(patterns);patterns.append((v,pat));c.append(phi[rem]-phi[v]);rr.append(g);cc.append(col);aa.append(1)
   for k,n in enumerate(pat):
    if n:rr.append(len(vals)+k);cc.append(col);aa.append(n)
 accept=False;status=-1
 if patterns:
  A=coo_matrix((aa,(rr,cc)),shape=(len(vals)+len(ws),len(patterns))).tocsc();rhs=np.array([len(groups[v]) for v in vals]+[B*dem[w] for w in ws]);res=milp(np.array(c),integrality=np.ones(len(patterns)),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,rhs,rhs),options=dict(time_limit=a.limit,mip_rel_gap=0));status=int(res.status)
  if res.x is not None:
   xx=np.rint(res.x).astype(int)
   if max(abs(xx-res.x))<1e-5 and np.array_equal(A@xx,rhs) and float(phi[cap-used].sum()+np.dot(c,xx))<oldcost-1e-6:
    selection=[]
    for (v,pat),count in zip(patterns,xx):
     for _ in range(count):
      i=groups[v].pop()
      if any(pat):selection.append((i,{w:n for w,n in zip(ws,pat) if n}))
    mapping=colour(selection,dem,ts);assert set(mapping)==set(js)
    for j,i in mapping.items():assignment[j]=i;used[i]+=roles[j]['width']
    assert cost()<oldcost-1e-6 and np.all(used<=cap);accept=True
 if not accept:
  for j,i in old.items():assignment[j]=i;used[i]+=roles[j]['width']
 r=dict(iteration=iteration,calls=ts,widths=ws,common_bins=len(common),solver_status=status,accepted=accept,gain=oldcost-cost(),cost=cost());trace.append(r)
 if accept or iteration%20==0:print(r,flush=True);save()
save();print('gain',initial-cost(),flush=True)
