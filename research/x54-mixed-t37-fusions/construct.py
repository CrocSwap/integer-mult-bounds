"""Rebuild literal cross-call exchanges from the nominated journal; no solver required."""
import argparse,collections,gzip,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--search',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(exist_ok=False)
def rd(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def wr(n,d):
 raw=json.dumps(d,sort_keys=True,separators=(',',':')).encode();(a.out/n).write_bytes(gzip.compress(raw,mtime=0) if n.endswith('.gz') else raw+b'\n')
plan=rd(a.base/'PLAN.json');roles=rd(a.base/'OWNERS.json.gz');journal=rd(a.search);calls=collections.defaultdict(dict);used=collections.Counter();families=collections.defaultdict(set);fields=('owner_replica','child','port','copy','family')
def bk(z):return z['owner_replica'],z['child'],z['port']
def bounds(k):return plan['windows'][f'{k[0]},{k[1]}']
for z in roles:calls[z['time']][z['helper']]=z;used[bk(z)]+=z['width'];families[z['time']].add(z['family'])
base_dispatch={c['time']:c['provider'] for c in plan['provider_calls']};new=set(journal['selected_times'])-{t for t,p in base_dispatch.items() if p=='extra'};targets=[h for h,(x,y) in enumerate(zip(plan['provider_registry']['gauge44']['widths'],plan['provider_registry']['extra']['widths'])) if x!=y];changes=collections.defaultdict(list)
for t,h,ty,hy in journal['moves']:changes[t].append((h,ty,hy))
assert set(changes)<=new
for t in list(changes)+sorted(new-set(changes)):
 for h,ty,hy in changes[t]:
  x,y=calls[t][h],calls[ty][hy];kx,ky=bk(x),bk(y);assert x['width']==y['width']==4 and bounds(ky)[0]-used[ky]==1;assert t in bounds(ky)[1] and ty in bounds(kx)[1];assert y['family'] not in families[t] and x['family'] not in families[ty]
  fx,fy=x['family'],y['family'];oldx={f:x[f] for f in fields};oldy={f:y[f] for f in fields};x.update(oldy);y.update(oldx);families[t].remove(fx);families[t].add(fy);families[ty].remove(fy);families[ty].add(fx)
 for h in targets:
  x=calls[t][h];k=bk(x);assert x['width']==4 and bounds(k)[0]-used[k]==1;x['width']+=1;used[k]+=1
bins=collections.defaultdict(list)
for z in roles:bins[bk(z)].append(z)
for k,zs in bins.items():
 off=0
 for z in sorted(zs,key=lambda z:(z['time'],z['helper'])):z['offset']=off;off+=z['width']
 assert off==used[k]<=bounds(k)[0]
idle=collections.Counter()
for key,(cap,ts) in plan['windows'].items():
 r,ch=map(int,key.split(','))
 for port in range(112):
  rem=cap-used[r,ch,port]
  if rem:idle[rem]+=1
profile=collections.Counter(idle);dispatch=[]
for t,(s,r) in enumerate(plan['order']):
 p='extra' if t in journal['selected_times'] else 'gauge44';dispatch.append([s,r,p]);reg=plan['provider_registry'][p];profile.update({int(k):v for k,v in reg['actual_paid_profile'].items()})
 for h,z in calls[t].items():assert z['width']==reg['widths'][h] and t in bounds(bk(z))[1]
assert len(roles)==sum(len(x) for x in calls.values());assert sum(r*n for r,n in profile.items())==plan['M']*plan['live']-plan['deficit'];wr('OWNERS.json.gz',roles);wr('PROFILE.json',dict(profile));wr('DISPATCH.json',dispatch);print('REBUILT',len(roles),dict(idle),flush=True)
