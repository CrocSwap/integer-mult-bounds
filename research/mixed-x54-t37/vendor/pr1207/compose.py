import json,gzip,os,sys,importlib.util,copy
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent;F=P.parent;ROOT=F/'joint1148-round45/source';os.environ['K8_BASE_WORD']=str(F/'fusion49/source/FULL-WORD.json.gz');sys.path.insert(0,str(ROOT/'research/k8-eight-ends/discovery'));import screen_end_groups as S
spec=importlib.util.spec_from_file_location('tri',P/'source/build_tri.py');tri=importlib.util.module_from_spec(spec);spec.loader.exec_module(tri);rc=json.loads((P/'MAPPED-RECIPE.json').read_text());profiles={};results=[]
for key,word in [('gauge44',F/'fusion49/source/FULL-WORD.json.gz'),('extra',F/'fusion49/mixed-fusion-word.json.gz')]:
 old=json.loads(gzip.decompress(word.read_bytes()));w=tri.apply(old,rc);w=S.optimize(w);assert S.promo.widths(w)==S.promo.widths(old)
 for k in ['start_extra','helper_final','centers','center_frames','ports']:assert w[k]==old[k],k
 profiles[key]=w['report']['local_profile'];delta={r:w['report']['local_profile'].get(r,0)-old['report']['local_profile'].get(r,0) for r in set(w['report']['local_profile'])|set(old['report']['local_profile'])};results.append(dict(provider=key,profile=profiles[key],delta=delta));(P/(key+'-word.json.gz')).write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));print(results[-1],flush=True)
plan=json.loads((F/'fusion49/candidate/PLAN.json').read_text());profile=Counter({int(k):v for k,v in json.loads((F/'fusion49/candidate/CONSTRUCTION.json').read_text())['idle'].items()})
for c in plan['provider_calls']:profile.update({int(k):v for k,v in profiles[c['provider']].items()})
assert sum(k*v for k,v in profile.items())==plan['M']*plan['live']-plan['deficit'];(P/'PROFILE.json').write_text(json.dumps(dict(profile),indent=2));(P/'COMPOSITION.json').write_text(json.dumps(dict(providers=results,profile=dict(profile),status='DISCOVERY_ONLY'),indent=2));print('PROFILE',dict(profile),flush=True)
