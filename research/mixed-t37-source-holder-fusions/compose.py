import json,gzip,copy,os,sys,importlib.util,hashlib
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent;F=P.parent;ROOT=F/'joint1148-round45/source';os.environ['K8_BASE_WORD']=str(P/'source/FULL-WORD.json.gz');sys.path.insert(0,str(ROOT/'research/k8-eight-ends/discovery'));import screen_end_groups as S
w=copy.deepcopy(S.w);extra=json.loads(gzip.decompress((F/'mixed47/word-619-627-651.json.gz').read_bytes()));old=json.loads(gzip.decompress((ROOT/'research/k8-joint-entrances/FULL-WORD.json.gz').read_bytes()));changed=[h for h in extra['start_extra'] if extra['start_extra'][h]!=old['start_extra'][h]]
for h in changed:assert w['start_extra'][h]==old['start_extra'][h];w['start_extra'][h]=extra['start_extra'][h]
w=S.optimize(w);(P/'mixed-fusion-word.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));base=S.w['report']['local_profile'];ext=w['report']['local_profile'];print('BASE',base,'EXTRA',ext,flush=True)
plan=json.loads((F/'cross48/candidate/PLAN.json').read_text());profile=Counter({int(k):v for k,v in json.loads((F/'cross48/candidate/CONSTRUCTION.json').read_text())['idle'].items()})
for c in plan['provider_calls']:profile.update({int(k):v for k,v in (ext if c['provider']=='extra' else base).items()})
assert S.promo.widths(w)==Counter({int(k):v for k,v in extra['report']['width_inventory'].items()});assert sum(k*v for k,v in profile.items())==plan['M']*plan['live']-plan['deficit'];(P/'PROFILE.json').write_text(json.dumps(dict(profile),indent=2));(P/'COMPOSITION.json').write_text(json.dumps(dict(changed_helpers=changed,base_profile=base,extra_profile=ext,provider_counts=dict(Counter(c['provider'] for c in plan['provider_calls'])),status='DISCOVERY_ONLY'),indent=2));print('PROFILE',dict(profile),flush=True)
