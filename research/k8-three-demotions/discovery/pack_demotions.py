"""Assign widened local helpers to existing one-rank gaps by integral max flow."""
import json,gzip,copy,argparse
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow
P=Path(__file__).resolve().parent;ROOT=P.parents[2];PRE=ROOT/'research/k8-eight-ends-t16'
ap=argparse.ArgumentParser();ap.add_argument('--groups',type=int,default=3);a=ap.parse_args()
rd=lambda f:json.loads(gzip.decompress(f.read_bytes()) if f.suffix=='.gz' else f.read_bytes())
plan=rd(PRE/'PLAN.json.gz');roles=rd(PRE/'OWNERS.json.gz');word=(rd(P.parent/'FULL-WORD.json.gz') if a.groups==3 else rd(P/f'demote-first-{a.groups}.json.gz'));base=rd(ROOT/'research/k8-eight-ends/FULL-WORD.json.gz')
widths=[len(word['helper_final'].get(str(h),[0]*9))-len(word['start_extra'].get(str(h),[])) for h in range(224,704)]
oldwidth=[len(base['helper_final'].get(str(h),[0]*9))-len(base['start_extra'].get(str(h),[])) for h in range(224,704)]
changed=[h for h in range(480) if widths[h]!=oldwidth[h]];assert len(changed)==4*a.groups and all((oldwidth[h],widths[h])==(4,5) for h in changed)
used=Counter();occupants=defaultdict(list);calls=defaultdict(list)
for j,z in enumerate(roles):
 key=z['owner_replica'],z['child'],z['port'];used[key]+=z['width'];occupants[key].append(j);calls[z['time']].append(j)
gaps=[key for key,n in used.items() if plan['windows'][f'{key[0]},{key[1]}'][0]-n==1]
rr=[];cc=[];vals=[];sink=145+len(gaps)
for t in range(144):rr.append(0);cc.append(1+t);vals.append(len(changed))
edge={}
for k,key in enumerate(gaps):
 node=145+k;rr.append(node);cc.append(sink);vals.append(1)
 for j in occupants[key]:
  z=roles[j]
  if z['width']==4:rr.append(1+z['time']);cc.append(node);vals.append(1);edge[z['time'],node]=j
net=csr_matrix((np.array(vals,dtype=np.int64),(rr,cc)),shape=(sink+1,sink+1));f=maximum_flow(net,0,sink);print('flow',f.flow_value,'required',144*len(changed),flush=True);assert f.flow_value==144*len(changed)
expanded=defaultdict(list)
for (t,node),j in edge.items():
 if f.flow[1+t,node]:expanded[t].append(j)
out=copy.deepcopy(roles)
for t,js in calls.items():
 targetslots=set(expanded[t]);changedroles=[j for j in js if roles[j]['helper'] in changed]
 otherroles=[j for j in js if roles[j]['width']==4 and j not in changedroles]
 otherslots=[j for j in js if roles[j]['width']==4 and j not in targetslots]
 for source,slot in zip(changedroles+otherroles,sorted(targetslots)+otherslots):
  for field in ['owner_replica','child','port','copy','family']:out[source][field]=roles[slot][field]
 for j in js:out[j]['width']=widths[out[j]['helper']]
offset=Counter();families=defaultdict(set)
for z in out:
 key=z['owner_replica'],z['child'],z['port'];z['offset']=offset[key];offset[key]+=z['width'];cap,times=plan['windows'][f'{key[0]},{key[1]}'];assert offset[key]<=cap and z['time'] in times;assert z['family'] not in families[z['time']];families[z['time']].add(z['family'])
idle=Counter()
for key,(cap,times) in plan['windows'].items():
 rep,ch=map(int,key.split(','))
 for port in range(112):
  rem=cap-offset[rep,ch,port]
  if rem:idle[rem]+=1
H=Counter({int(r):144*n for r,n in word['report']['local_profile'].items()});H.update(idle);plan['profile']={str(r):n for r,n in sorted(H.items())};plan['provider_registry']['gauge44']['widths']=widths;plan['provider_registry']['gauge44']['actual_paid_profile']=word['report']['local_profile']
for c in plan['per_call_widths']:c['widths']=widths
outdir=P/f'packed-{a.groups}';outdir.mkdir(exist_ok=True);(outdir/'OWNERS.json.gz').write_bytes(gzip.compress(json.dumps(out,sort_keys=True,separators=(',',':')).encode(),mtime=0));(outdir/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');(outdir/'PACKING.json').write_text(json.dumps(dict(status='INTEGER_FEASIBLE_NOMINATION',changed_helpers=changed,unit_gaps_consumed=int(f.flow_value),idle=dict(sorted(idle.items())),profile=plan['profile']),indent=2)+'\n');print(dict(idle),plan['profile'])
