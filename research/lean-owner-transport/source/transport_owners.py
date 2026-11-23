"""Transport PR523 slots to PR522 widths, retaining whole-family ownership.
Discovery only; run the independent physical verifier on the result.
"""
from pathlib import Path
from collections import defaultdict,Counter
import json,gzip,hashlib,sys
SOURCE,LOCAL,OUT=map(Path,sys.argv[1:4]);OUT.mkdir(exist_ok=False)
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
plan=read(SOURCE/'inputs/ASYNC112-PLAN.json');roles=read(SOURCE/'inputs/OWNERS112.json.gz');can=read(LOCAL/'CANONICAL-WORD.json.gz');v=can['v'];widths=[can['h']-len(can['frames'][f])for f in can['start'][2*v:]];oldwidths=plan['baseline_widths'];assert all(a<=b for a,b in zip(sorted(widths),sorted(oldwidths)))
bycall=defaultdict(list);groups=defaultdict(list)
for z in roles:bycall[z['time']].append(z);groups[z['owner_replica'],z['child'],z['port']].append(z)
left={g:plan['windows'][f'{g[0]},{g[1]}'][0]-sum(z['width']for z in zs)for g,zs in groups.items()}
for t,zs in sorted(bycall.items()):
 avail=list(zs)
 for h in sorted(range(len(widths)),key=lambda h:(-widths[h],h)):
  w=widths[h];possible=[z for z in avail if z['width']>=w];assert possible
  def key(z):
   g=z['owner_replica'],z['child'],z['port'];return(z['width']-w,left[g]if z['width']==w else-left[g],z['family'])
  z=min(possible,key=key);avail.remove(z);g=z['owner_replica'],z['child'],z['port'];left[g]+=z['width']-w;z['helper']=h;z['width']=w
 assert not avail and len({z['family']for z in zs})==len(widths)
for g,zs in groups.items():
 off=0
 for z in sorted(zs,key=lambda z:z['offset']):z['offset']=off;off+=z['width']
 assert off<=plan['windows'][f'{g[0]},{g[1]}'][0]
H=Counter({int(r):len(plan['order'])*n for r,n in can['local_profile'].items()})
for k,(rank,window)in plan['windows'].items():
 rep,child=map(int,k.split(','))
 for port in range(v):
  remainder=rank-sum(z['width']for z in groups.get((rep,child,port),[]))
  if remainder:H[remainder]+=1
plan.update(baseline_widths=widths,profile=dict(sorted(H.items())),status='NEW_LITERAL_WIDTH_DOMINANCE_TRANSPORT_PENDING_GLOBAL_AUDIT')
(OUT/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');raw=json.dumps(sorted(roles,key=lambda z:(z['time'],z['helper'])),sort_keys=True,separators=(',',':')).encode();(OUT/'OWNERS.json.gz').write_bytes(gzip.compress(raw,mtime=0));print('NOMINATED',len(roles),dict(sorted(H.items())))
