import argparse,collections,copy,gzip,hashlib,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--base-word',type=Path,required=True);ap.add_argument('--word',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(exist_ok=False)
def rd(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def write(n,d):
 raw=json.dumps(d,sort_keys=True,separators=(',',':')).encode();(a.out/n).write_bytes(gzip.compress(raw,mtime=0) if n.endswith('.gz') else raw+b'\n')
plan=rd(a.base/'PLAN.json');roles=rd(a.base/'OWNERS.json.gz');base=rd(a.base_word);word=rd(a.word);v=len(plan['provider_registry']['gauge44']['ports']);targets=sorted(int(h)-2*v for h in word['start_extra'] if word['start_extra'][h]!=base['start_extra'][h]);assert targets
assert all(len(base['start_extra'][str(h+2*v)])-len(word['start_extra'][str(h+2*v)])==1 for h in targets)
bk=lambda z:(z['owner_replica'],z['child'],z['port']);used=collections.Counter();calls=collections.defaultdict(dict)
for z in roles:used[bk(z)]+=z['width'];calls[z['time']][z['helper']]=z
fields=('owner_replica','child','port','copy','family');selected=[];exchanges=[]
for t,call in sorted(calls.items()):
 gaps={h for h,z in call.items() if z['width']==call[targets[0]]['width'] and plan['windows'][f"{z['owner_replica']},{z['child']}"][0]-used[bk(z)]==1}
 if len(gaps)<len(targets):continue
 assert all(call[h]['width']==4 for h in targets)
 donors=iter(sorted(gaps-set(targets)))
 for h in targets:
  if h not in gaps:
   donor=next(donors);x,y=call[h],call[donor];oldx={f:x[f] for f in fields};oldy={f:y[f] for f in fields};x.update(oldy);y.update(oldx);exchanges.append([t,h,donor])
 for h in targets:call[h]['width']+=1;used[bk(call[h])]+=1
 selected.append(t)
bins=collections.defaultdict(list)
for z in roles:bins[bk(z)].append(z)
for key,zs in bins.items():
 offset=0
 for z in sorted(zs,key=lambda z:(z['time'],z['helper'])):z['offset']=offset;offset+=z['width']
 assert offset<=plan['windows'][f'{key[0]},{key[1]}'][0]
idle=collections.Counter()
for key,(cap,ts) in plan['windows'].items():
 r,ch=map(int,key.split(','))
 for p in range(v):
  rem=cap-used[r,ch,p];assert rem>=0
  if rem:idle[rem]+=1
profile=collections.Counter(idle)
for t,(s,r) in enumerate(plan['order']):
 local=word if t in selected else base;profile.update({int(k):n for k,n in local['report']['local_profile'].items()});call=calls[t]
 assert len(call)==len(plan['provider_registry']['gauge44']['widths']);assert len({z['family'] for z in call.values()})==len(call)
 for h,z in call.items():
  cap,ts=plan['windows'][f"{z['owner_replica']},{z['child']}"];assert t in ts;assert [z['stage'],z['replica']]==[s,r];assert z['width']==plan['provider_registry']['gauge44']['widths'][h]+int(t in selected and h in targets)
assert sum(r*n for r,n in profile.items())==plan['M']*plan['live']-plan['deficit']
write('OWNERS.json.gz',roles);write('PROFILE.json',dict(profile));write('DISPATCH.json',[[s,r,'extra' if t in selected else 'gauge44'] for t,(s,r) in enumerate(plan['order'])]);write('CONSTRUCTION.json',dict(selected_times=selected,extra_calls=len(selected),targets=targets,exchanges=exchanges,idle=dict(idle),profile=dict(profile),status='LITERAL_MAP_AND_PROFILE_RECOUNT_ONLY_PENDING_NATIVE_AND_GLOBAL_ADMISSION'))
print('calls',len(selected),'targets',targets,'idle',dict(idle),'profile',dict(profile),flush=True)
