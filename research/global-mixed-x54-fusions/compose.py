import os,sys,json,gzip,copy
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent;F=P.parent;ROOT=F/'joint1148-round45/source';os.environ['K8_BASE_WORD']=str(F/'x54fusion50/gauge44-word.json.gz');sys.path.insert(0,str(ROOT/'research/k8-eight-ends/discovery'));import screen_end_groups as S
rd=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes());base=copy.deepcopy(S.w);old=rd(P/'source/data/FOUR-WORD.json.gz');w=copy.deepcopy(base);w['start_extra']=copy.deepcopy(old['start_extra']);w=S.optimize(w);assert w['helper_final']==base['helper_final']==old['helper_final'];plan=rd(P/'source/data/PLAN.json.gz');words={'demote3':base,'demote4':w};profiles={k:x['report']['local_profile'] for k,x in words.items()}
for k,x in words.items():
 ws=[len(x['helper_final'].get(str(h),list(range(9))))-len(x['start_extra'].get(str(h),[])) for h in range(224,704)];assert ws==plan['provider_registry'][k]['widths'],k
roles=rd(P/'source/data/OWNERS.json.gz');dispatch={(c['stage'],c['replica']):c['provider'] for c in plan['provider_calls']};used=Counter();seen=set()
for z in roles:
 c=(z['stage'],z['replica']);assert plan['order'][z['time']]==list(c);assert z['width']==plan['provider_registry'][dispatch[c]]['widths'][z['helper']];k=z['owner_replica'],z['child'],z['port'];cap,ts=plan['windows'][f'{k[0]},{k[1]}'];assert z['time'] in ts and (z['time'],z['family']) not in seen;seen.add((z['time'],z['family']));used[k]+=z['width'];assert used[k]<=cap
idle=Counter()
for key,(cap,ts) in plan['windows'].items():
 r,ch=map(int,key.split(','))
 for port in range(112):
  rem=cap-used[r,ch,port]
  if rem:idle[rem]+=1
profile=Counter(idle)
for k in dispatch.values():profile.update({int(r):n for r,n in profiles[k].items()})
assert sum(r*n for r,n in profile.items())==plan['M']*plan['live']-plan['deficit'];(P/'extra-word.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));(P/'PROFILE.json').write_text(json.dumps(dict(profile),indent=2));(P/'COMPOSITION.json').write_text(json.dumps(dict(status='NOMINATION_ONLY_PENDING_NATIVE_AND_STRICT_ADMISSION',profile=dict(profile),idle=dict(idle),provider_profiles=profiles,provider_counts=dict(Counter(dispatch.values()))),indent=2));print(profiles,dict(idle),dict(profile),flush=True)
