"""Discovery: capacity-preserving cross-call whole-owner exchanges, followed by gap filling.
No scalar or theorem admission is claimed by this search.
"""
import json,gzip,collections,copy,random,time
from pathlib import Path
P=Path(__file__).resolve().parent;F=P.parent;B=F/'mixed47/candidate'
def rd(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
plan=rd(B/'PLAN.json');base=rd(B/'OWNERS.json.gz');meta=rd(B/'CONSTRUCTION.json');targets=meta['targets'];selected=set(meta['selected_times']);fields=('owner_replica','child','port','copy','family');windows=plan['windows'];parent=rd(F/'demotions1148-round43/baseline-replay/parent/t16/global8/base/split-centres/GLOBAL-TEMPLATE.json.gz');pairs={e['stage']:e['pair'] for e in parent['recipe'] if e['kind']=='local'};best=len(selected);results=[]
def bk(z):return (z['owner_replica'],z['child'],z['port'])
def bounds(k):return windows[f'{k[0]},{k[1]}']
for seed in range(8):
 start=time.monotonic();rng=random.Random(seed);roles=copy.deepcopy(base);used=collections.Counter();calls=collections.defaultdict(dict);families=collections.defaultdict(set)
 for z in roles:used[bk(z)]+=z['width'];calls[z['time']][z['helper']]=z;families[z['time']].add(z['family'])
 donor_pool=[z for z in roles if z['width']==4 and bounds(bk(z))[0]-used[bk(z)]==1];times=[t for t in calls if t not in selected];rng.shuffle(times);installed=set(selected);moves=[]
 for t in times:
  snapshots={};counts={};fam_snap={};trial=[];ok=True
  def save(z):
   snapshots.setdefault(id(z),(z,dict(z)));counts.setdefault(bk(z),used[bk(z)]);fam_snap.setdefault(z['time'],set(families[z['time']]))
  for h in targets:
   x=calls[t][h];assert x['width']==4;kx=bk(x)
   if bounds(kx)[0]-used[kx]!=1:
    choices=[]
    for y in donor_pool:
     ty=y['time'];ky=bk(y)
     if y['width']!=4 or ty==t or bounds(ky)[0]-used[ky]!=1:continue
     if t not in bounds(ky)[1] or ty not in bounds(kx)[1]:continue
     if y['family'] in families[t] or x['family'] in families[ty]:continue
     if y['family']//224==x['replica']*4+pairs[x['stage']] or x['family']//224==y['replica']*4+pairs[y['stage']]:continue
     choices.append(y)
    if not choices:ok=False;break
    y=rng.choice(choices);save(x);save(y);fx,fy=x['family'],y['family'];oldx={f:x[f] for f in fields};oldy={f:y[f] for f in fields};x.update(oldy);y.update(oldx);families[t].remove(fx);families[t].add(fy);families[y['time']].remove(fy);families[y['time']].add(fx);trial.append([t,h,y['time'],y['helper']])
   save(x);x['width']+=1;used[bk(x)]+=1
  if not ok:
   for z,old in snapshots.values():z.clear();z.update(old)
   for k,n in counts.items():used[k]=n
   for c,fs in fam_snap.items():families[c]=fs
  else:installed.add(t);moves.extend(trial)
 bins=collections.defaultdict(list)
 for z in roles:bins[bk(z)].append(z)
 for k,zs in bins.items():
  offset=0
  for z in sorted(zs,key=lambda z:(z['time'],z['helper'])):z['offset']=offset;offset+=z['width']
  assert offset<=bounds(k)[0]
 idle=collections.Counter()
 for key,(cap,ts) in windows.items():
  r,ch=map(int,key.split(','))
  for port in range(112):
   rem=cap-used[r,ch,port];assert rem>=0
   if rem:idle[rem]+=1
 profile=collections.Counter(idle)
 for t,cs in calls.items():
  pid='extra' if t in installed else 'gauge44';reg=plan['provider_registry'][pid];profile.update({int(k):v for k,v in reg['actual_paid_profile'].items()});assert len({z['family'] for z in cs.values()})==len(cs)
  for h,z in cs.items():assert z['time'] in bounds(bk(z))[1] and z['width']==reg['widths'][h]
 assert sum(r*n for r,n in profile.items())==plan['M']*plan['live']-plan['deficit']
 result=dict(seed=seed,extra_calls=len(installed),new_calls=len(installed)-len(selected),idle=dict(idle),profile=dict(profile),seconds=time.monotonic()-start,status='DISCOVERY_ONLY_PENDING_NATIVE_BOUND_STRICT_ADMISSION');results.append(result);print(result,flush=True);(P/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
 if len(installed)>best:
  best=len(installed);d=P/('best-'+str(seed));d.mkdir();(d/'OWNERS.json.gz').write_bytes(gzip.compress(json.dumps(roles,sort_keys=True,separators=(',',':')).encode(),mtime=0));(d/'DISPATCH.json').write_text(json.dumps([[s,r,'extra' if t in installed else 'gauge44'] for t,(s,r) in enumerate(plan['order'])]));(d/'PROFILE.json').write_text(json.dumps(dict(profile)));(d/'SEARCH.json').write_text(json.dumps(dict(result,selected_times=sorted(installed),moves=moves),indent=2));(P/'BEST.json').write_text(json.dumps(dict(result,directory=str(d)),indent=2))
(P/'FINISHED.json').write_text(json.dumps(dict(best_calls=best,trials=len(results))))
