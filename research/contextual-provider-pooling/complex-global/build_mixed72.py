"""Select each complete provider from actual rank16 slot availability; compact literal owner intervals."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,gzip,hashlib,json
ap=argparse.ArgumentParser();ap.add_argument('--owners',type=Path,required=True);ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--providers',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists();a.out.mkdir(parents=True)
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
z=read(a.plan);roles=read(a.owners);locations=read(a.providers);records={}
for pid,name in locations.items():
 d=Path(name);cw=read(d/'CANONICAL-WORD.json.gz');checks=read(d/'LOCAL-CHECKS.json');assert(cw['v'],cw['R'],cw['h'])==(112,504,9)
 H={int(r):n for r,n in checks['forward']['paid_profile'].items()};assert H=={int(r):n for r,n in checks['backward']['paid_profile'].items()}
 records[pid]={'widths':[9-len(cw['frames'][f])for f in cw['start'][224:]],'profile':H}
assert set(records)=={'n0','n2','n6','n8'}
c=Counter()
for q in roles:
 if q['width']==4 and z['windows'][f"{q['owner_replica']},{q['child']}"][0]==16:c[q['time']]+=1
selector={f'{s},{rep}':'n'+str(c[t])for t,(s,rep)in enumerate(z['order'])};assert Counter(selector.values())=={'n8':55,'n0':15,'n6':1,'n2':1}
bins=defaultdict(list)
for q in roles:
 pid=selector[f"{q['stage']},{q['replica']}"];w=records[pid]['widths'][q['helper']]
 assert w==q['width']or(q['width']==4 and w==5)
 q['width']=w;bins[q['owner_replica'],q['child'],q['port']].append(q)
for k,rs in bins.items():
 off=0
 for q in sorted(rs,key=lambda q:q['offset']):q['offset']=off;off+=q['width']
 assert off<=z['windows'][f'{k[0]},{k[1]}'][0]
h=Counter()
for pid in selector.values():h.update(records[pid]['profile'])
for key,(rank,times)in z['windows'].items():
 rep,ch=map(int,key.split(','))
 for port in range(112):
  left=rank-sum(q['width']for q in bins[rep,ch,port]);assert left>=0
  if left:h[left]+=1
assert 73*7168-sum(r*n for r,n in h.items())==2560
z.update(status='SOURCE_BOUND_MIXED_PROVIDER_LITERAL_PLAN',mode='selected promotion only in rank16 owner slots',provider_for_call=selector,profile=dict(sorted(h.items())),local_profiles={k:v['profile']for k,v in records.items()})
for key in ['patterns','stage_assignments','numeric_saving','solver_status','gap','local_profile','numeric_saving_scope']:z.pop(key,None)
raw=json.dumps(roles,sort_keys=True,separators=(',',':')).encode();(a.out/'OWNERS.json.gz').write_bytes(gzip.compress(raw,mtime=0));(a.out/'PLAN.json').write_text(json.dumps(z,indent=2)+'\n',encoding='utf8',newline='\n')
r={'status':'PASS_LITERAL_PROVIDER_SELECTION_AND_OFFSET_COMPACTION','provider_counts':dict(Counter(selector.values())),'profile':dict(sorted(h.items())),'source_owners_sha256':hashlib.sha256(a.owners.read_bytes()).hexdigest(),'source_plan_lf_sha256':hashlib.sha256(a.plan.read_bytes().replace(b'\r\n',b'\n')).hexdigest(),'owner_content_sha256':hashlib.sha256(raw).hexdigest(),'scope':'Provider widths/profile read from actual canonical/local receipts. Independent chronology, source lift, charts and invoice follow.'};(a.out/'MIXED-CONSTRUCTION.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(r,indent=2))
