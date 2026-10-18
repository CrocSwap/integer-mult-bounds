import json,gzip,sys
from pathlib import Path
from collections import Counter
base,word,out=map(Path,sys.argv[1:]);p=json.loads((base/'PLAN.json').read_text());rs=json.loads(gzip.decompress((base/'OWNERS.json.gz').read_bytes()));w=json.loads(gzip.decompress(word.read_bytes()));d=p['provider_registry']['gauge44'];widths=[len(w['helper_final'].get(str(224+h),list(range(9))))-len(w['start_extra'].get(str(224+h),[])) for h in range(480)];assert all(a>=b for a,b in zip(d['widths'],widths));d.update(widths=widths,actual_paid_profile=w['report']['local_profile']);used=Counter()
for r in rs:
 r['width']=widths[r['helper']];key=(r['owner_replica'],r['child'],r['port']);r['offset']=used[key];used[key]+=r['width']
H=Counter({int(r):72*c for r,c in w['report']['local_profile'].items()});idle=Counter()
for key,(cap,times) in p['windows'].items():
 rep,ch=map(int,key.split(','))
 for port in range(112):
  rem=cap-used[rep,ch,port];assert rem>=0
  if rem:idle[rem]+=1
H.update(idle);p['profile']={str(r):c for r,c in sorted(H.items())};assert sum(r*c for r,c in H.items())==520704
out.mkdir(exist_ok=False);(out/'PLAN.json').write_text(json.dumps(p,indent=2)+'\n');(out/'OWNERS.json.gz').write_bytes(gzip.compress(json.dumps(rs,sort_keys=True,separators=(',',':')).encode(),mtime=0));print('idle',dict(idle))
