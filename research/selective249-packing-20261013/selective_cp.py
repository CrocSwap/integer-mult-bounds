"""Selective native helper25 end, bounded exact integer packing nomination. Chi Zhao / Codex."""
import json,gzip,time,hashlib,argparse
from collections import defaultdict,Counter
from pathlib import Path
from ortools.sat.python import cp_model
ap=argparse.ArgumentParser();ap.add_argument('--base-data',type=Path,required=True);ap.add_argument('--extra',type=int,default=0);ap.add_argument('--seconds',type=float,default=60);ap.add_argument('--out',required=True);a=ap.parse_args()
p=json.load(open(a.base_data/'PLAN.json'));rows=json.load(gzip.open(a.base_data/'OWNERS.json.gz'));keys=[];lookup={};caps=[];allow=[];bins=[]
for key,(cap,ts)in p['windows'].items():
 r,ch=map(int,key.split(','))
 for port in range(112):lookup[r,ch,port]=len(keys);keys.append((r,ch,port));caps.append(cap);allow.append(set(ts));bins.append([])
where=[]
for i,r in enumerate(rows):b=lookup[r['owner_replica'],r['child'],r['port']];bins[b].append(i);where.append(b)
gap=[caps[b]-sum(rows[i]['width']for i in items)for b,items in enumerate(bins)];target=next(b for b in range(len(bins))if gap[b]==36)
shrink=[i for i,r in enumerate(rows)if r['helper']==25 and r['time']!=5];selected={where[i]for i in shrink}|{target}
# Add a few representative full bins of each window with diverse widths.
for win in p['windows']:
 r,ch=map(int,win.split(','));choices=[lookup[r,ch,port]for port in range(112)if lookup[r,ch,port]not in selected and gap[lookup[r,ch,port]]==0]
 choices.sort(key=lambda b:(-len({rows[i]['width']for i in bins[b]}),b))
 selected.update(choices[:a.extra])
selected=sorted(selected);items=[i for b in selected for i in bins[b]];dest=[b for b in selected if b!=target]
print('scope',len(selected),'bins',len(items),'roles',flush=True)
m=cp_model.CpModel();xx={};rolevars=defaultdict(list);bincells=defaultdict(list);bin_times=defaultdict(list);activation=defaultdict(list);shrink=set(shrink)
for i in items:
 row=rows[i];t=row['time'];w=row['width']
 for b in dest:
  if t not in allow[b]:continue
  for v in ([w,8]if i in shrink else[w]):
   if v>caps[b]:continue
   x=m.new_bool_var(f'x{i}_{b}_{v}');xx[i,b,v]=x;rolevars[i].append(x);bincells[b].append(v*x);bin_times[b,t].append(x)
   if i in shrink and v==8:activation[t].append(x)
for i in items:m.add(sum(rolevars[i])==1)
for b in dest:m.add(sum(bincells[b])==caps[b])
for variables in bin_times.values():m.add(sum(variables)<=1)
m.add(sum(v for vv in activation.values()for v in vv)==12)
m.add(sum(activation[0])==0)
for orient in ['forward','backward']:
 m.add(sum(v for t,vv in activation.items()if p['provider_calls'][t]['orientation']==orient for v in vv)>=1)
# Feasibility; prefer original owners as hints only.
for (i,b,v),x in xx.items():m.add_hint(x,int(where[i]==b and v==rows[i]['width']))
s=cp_model.CpSolver();s.parameters.max_time_in_seconds=a.seconds;s.parameters.num_search_workers=8;s.parameters.random_seed=37
status=s.solve(m);print('status',s.status_name(status),'time',s.wall_time,flush=True)
if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):raise SystemExit(2)
activated=set()
for (i,b,v),x in xx.items():
 if s.value(x):
  row=rows[i];r,ch,port=keys[b];row.update(owner_replica=r,child=ch,port=port,copy=r*112+port,family=r*896+(2*p['pairs'][str(ch)]+p['sides'][str(ch)])*112+port,width=v)
  if i in shrink and v==8:activated.add(row['time'])
newbins=defaultdict(list)
for row in rows:newbins[row['owner_replica'],row['child'],row['port']].append(row)
for vv in newbins.values():
 off=0
 for row in sorted(vv,key=lambda r:(r['time'],r['helper'])):row['offset']=off;off+=row['width']
import copy
p['provider_registry']['j249']=copy.deepcopy(p['provider_registry']['jp8']);p['provider_registry']['j249']['widths'][25]=8;p['provider_registry']['j249']['actual_paid_profile']={'1':2528,'2':397,'3':448,'4':169,'5':63,'6':4,'8':8}
for t in activated:p['provider_calls'][t]['provider']='j249';p['per_call_widths'][t]['widths']=p['provider_registry']['j249']['widths'][:]
prof=Counter()
for call in p['provider_calls']:prof.update({int(r):n for r,n in p['provider_registry'][call['provider']]['actual_paid_profile'].items()})
prof[48]+=2230;p['profile']={str(k):v for k,v in sorted(prof.items())};p['provider_bindings_pending']=True
out=Path(a.out);out.mkdir(parents=True,exist_ok=True);rows.sort(key=lambda r:(r['time'],r['helper']));data=gzip.compress(json.dumps(rows,sort_keys=True,separators=(',',':')).encode(),mtime=0);data=data[:9]+b'\xff'+data[10:];p['assignment_sha256']=hashlib.sha256(data).hexdigest();(out/'OWNERS.json.gz').write_bytes(data);(out/'PROVISIONAL-PLAN.json').write_text(json.dumps(p,indent=2)+'\n');(out/'SEARCH.json').write_text(json.dumps({'status':s.status_name(status),'seconds':s.wall_time,'activated_times':sorted(activated),'scope_bins':len(selected),'roles':len(items)},indent=2)+'\n');print('activated',sorted(activated),flush=True)
