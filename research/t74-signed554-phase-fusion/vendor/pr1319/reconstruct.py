"""Double the pinned owner witness; seek one extra provider using exact augmenting paths.
No window, bin, or one-owner-per-call constraint is relaxed.
The scalar words are unchanged. Full parent/compiler/global admission is separate.
"""
import argparse,collections,copy,gzip,importlib.util,json,time
from pathlib import Path
assert __debug__, 'Assertions are required'
F=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();P=args.out.resolve();P.mkdir(parents=True,exist_ok=False)
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def dump(p,x):
 b=json.dumps(x,sort_keys=True,separators=(',',':')).encode();p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
plan=read(F/'inputs/PLAN.json');old=read(F/'inputs/OWNERS.json.gz');parent=read(F/'inputs/GLOBAL-TEMPLATE.json.gz');T=plan['T'];order=[[s,r+T*g] for s,r in plan['order'] for g in range(2)];dispatch={(s,r+T*g):pid for s,r,pid in read(F/'inputs/DISPATCH.json') for g in range(2)}
source=F/'vendor/build_parent.py';sp=importlib.util.spec_from_file_location('windows',source);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);windows,schedule=mod.actual_windows(parent,order)
roles=[]
for z in old:
 for group in range(2):
  r=dict(z);r.update(replica=z['replica']+T*group,owner_replica=z['owner_replica']+T*group,time=2*z['time']+group,copy=z['copy']+112*T*group,family=z['family']+896*T*group);roles.append(r)
bins=collections.defaultdict(list);fixed=collections.defaultdict(set)
for z in roles:
 k=z['owner_replica'],z['child'],z['port'];bins[k].append(z)
 if z['width'] not in (4,5):fixed[z['time']].add(z['family'])
holes=[]
for k,rr in bins.items():
 cap=windows[f'{k[0]},{k[1]}'][0]
 if cap-sum(r['width'] for r in rr)==1:
  assert sorted(r['width'] for r in rr)==[4,9,9,9];holes.append(k)
assert len(holes)==4,holes
slots={w:{} for w in (4,5)};family={}
for k,rr in bins.items():
 family[k]=rr[0]['family']
 for w in (4,5):
  ts={r['time'] for r in rr if r['width']==w}
  if ts:slots[w][k]=ts
# Only the four single-width-4 holes switch bin type.
initial={w:{k:set(ts) for k,ts in d.items()} for w,d in slots.items()};lost=[]
for k in holes:assert len(slots[4][k])==1;lost.extend(slots[4].pop(k));slots[5][k]=set()
caps={w:{k:(1 if k in holes else len(ts)) for k,ts in d.items()} for w,d in slots.items()};adj={w:collections.defaultdict(list) for w in (4,5)}
for w,d in slots.items():
 for k in d:
  for t in windows[f'{k[0]},{k[1]}'][1]:
   if family[k] not in fixed[t]:adj[w][t].append(k)
print('PREPARED',len(roles),'holes',holes,'lost_calls',lost,'edges',{w:sum(map(len,a.values())) for w,a in adj.items()},flush=True)
def augment(assign,w,start,donor=None):
 """Find a whole-bin alternating path; donor is the call whose demand may drop."""
 queue=collections.deque([start]);prev={start:None};seenbins=set();end=None
 while queue and end is None:
  t=queue.popleft()
  for k in adj[w][t]:
   if k in seenbins or t in assign[k]:continue
   seenbins.add(k)
   if (donor is None and len(assign[k])<caps[w][k]) or (donor is not None and donor in assign[k]):end=(t,k);break
   for t2 in sorted(assign[k]):
    if t2 not in prev:prev[t2]=(t,k);queue.append(t2)
 if end is None:return False
 t,k=end
 if donor is not None:assign[k].remove(donor)
 assign[k].add(t)
 while prev[t] is not None:
  before,k=prev[t];assign[k].remove(t);assign[k].add(before);t=before
 return True
candidates=[t for t,sr in enumerate(order) if dispatch[tuple(sr)]=='gauge44'];found=None;attempts=[]
for target in candidates:
 assign={w:{k:set(ts) for k,ts in d.items()} for w,d in slots.items()};remaining=4;ok=True
 for t in lost:
  if t==target:remaining-=1;continue
  if not augment(assign[4],4,t,donor=target):ok=False;break
  remaining-=1
 if ok:
  assert remaining==0
  for _ in range(4):
   if not augment(assign[5],5,target):ok=False;break
 attempts.append(dict(time=target,call=order[target],success=ok))
 if ok:found=target;print('FOUND',target,order[target],flush=True);break
 if len(attempts)%20==0:print('TRIED',len(attempts),flush=True)
if found is None:dump(P/'RESULT.json',dict(status='NO_SINGLE_UPGRADE_WITH_FIXED_OTHER_WIDTHS',attempts=attempts));raise SystemExit(0)
dispatch[tuple(order[found])]='extra';registry=plan['provider_registry'];pool=collections.defaultdict(list)
for t,sr in enumerate(order):
 for h,w in enumerate(registry[dispatch[tuple(sr)]]['widths']):pool[t,w].append(h)
new=[]
for k,rr in bins.items():
 items=[(r['time'],r['width']) for r in rr if r['width'] not in (4,5)]
 for w in (4,5):items += [(t,w) for t in assign[w].get(k,set())]
 offset=0
 for t,w in sorted(items):
  assert pool[t,w],(t,w);helper=pool[t,w].pop();stage,replica=order[t]
  new.append(dict(stage=stage,replica=replica,time=t,helper=helper,width=w,owner_replica=k[0],child=k[1],port=k[2],offset=offset,copy=112*k[0]+k[2],family=family[k]));offset+=w
 assert offset<=windows[f'{k[0]},{k[1]}'][0]
assert not any(pool.values()) and len(new)==len(roles)
used=collections.defaultdict(set);occupied=collections.Counter()
for r in new:
 assert r['time'] in windows[f"{r['owner_replica']},{r['child']}"][1]
 assert r['family'] not in used[r['time']];used[r['time']].add(r['family']);occupied[r['owner_replica'],r['child'],r['port']]+=r['width']
idle=collections.Counter()
for key,(cap,times) in windows.items():
 r,ch=map(int,key.split(','))
 for port in range(112):
  rem=cap-occupied[r,ch,port];assert rem>=0
  if rem:idle[rem]+=1
assert idle=={48:22748},idle
H=collections.Counter(idle)
for sr in order:
 for r,n in registry[dispatch[tuple(sr)]]['actual_paid_profile'].items():H[int(r)]+=n
assert sum(r*n for r,n in H.items())==2*sum(int(r)*n for r,n in plan['profile'].items())
new.sort(key=lambda r:(r['time'],r['helper']));dump(P/'OWNERS.json.gz',new);dump(P/'ORDER.json',order);dump(P/'DISPATCH.json',[[s,r,dispatch[s,r]] for s,r in order]);dump(P/'PROFILE.json',dict(sorted(H.items())));dump(P/'RESULT.json',dict(status='PASS_EXACT_SINGLE_UPGRADE_T74_OWNER_SCREEN',target_time=found,target_call=order[found],roles=len(new),dispatch=dict(collections.Counter(dispatch.values())),idle=dict(idle),attempts=attempts,scope='Literal strict windows, bin capacities, per-call helper widths and distinct physical families checked. Local programs reused unchanged. Full T74 parent binding, finite invoice and global admission not yet run.'));print('PASS_OWNER_SCREEN',dict(idle),dict(H),flush=True)
