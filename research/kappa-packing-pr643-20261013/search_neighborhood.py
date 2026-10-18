"""Bounded CP-SAT owner search. Chi Zhao with substantial OpenAI Codex assistance. Apache-2.0."""
from ortools.sat.python import cp_model
from pathlib import Path
from collections import defaultdict,Counter
import json,gzip,random,time,hashlib,math
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--base-data',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
p=json.loads((args.base_data/'PLAN.json').read_text());rows=json.loads(gzip.decompress((args.base_data/'OWNERS.json.gz').read_bytes()));bins=defaultdict(list)
for i,r in enumerate(rows):bins[r['owner_replica'],r['child'],r['port']].append(i)
cap=lambda b:p['windows'][f'{b[0]},{b[1]}'][0]
allow=lambda b:set(p['windows'][f'{b[0]},{b[1]}'][1])
gap=lambda b:cap(b)-sum(rows[i]['width']for i in bins[b])

for key in p['windows']:
 r,ch=map(int,key.split(','))
 for port in range(112):bins[r,ch,port]
partial=[b for b in bins if 0<gap(b)<48]
targets=[b for b in bins if cap(b)==48 and gap(b)==0 ]

donors=[b for b in bins if gap(b)==0 ]

uniq={}
for b in donors:
 key=(tuple(sorted(allow(b))),tuple((rows[i]['time'],rows[i]['width'])for i in bins[b]))
 uniq.setdefault(key,b)
donors=list(uniq.values())

empty48=[];wins=set()
for b in bins:
 if cap(b)==48 and gap(b)==48 and b[:2]not in wins:empty48.append(b);wins.add(b[:2])
rng=random.Random(123);print('partials',partial,'donors',len(donors),flush=True)
for trial in range(24):
 target=next(b for b in partial if gap(b)==12);pool=[b for b in donors if b!=target];chosen=partial+empty48+rng.sample(pool,min(40+trial//3*20,len(pool))); items=[i for b in chosen for i in bins[b]];m=cp_model.CpModel();x={}
 for i in items:
  poss=[]
  for b in chosen:
   if rows[i]['time']in allow(b):x[i,b]=m.NewBoolVar(f'x{i}_{b}');poss.append(x[i,b]);m.AddHint(x[i,b],int(i in bins[b]))
  m.Add(sum(poss)==1)
 for b in chosen:
  m.Add(sum(rows[i]['width']*x[i,b] for i in items if(i,b)in x)==(4 if b==target else (48*m.NewBoolVar(f'occupied{b}')if cap(b)==48 else cap(b))))
  for t in {rows[i]['time']for i in items}:m.Add(sum(x[i,b]for i in items if rows[i]['time']==t and(i,b)in x)<=1)
 solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=3;solver.parameters.num_search_workers=4;s=solver.Solve(m);print(trial,len(chosen),solver.StatusName(s),flush=True)
 if s not in(cp_model.FEASIBLE,cp_model.OPTIMAL):continue
 for b in chosen:
  contents=[i for i in items if(i,b)in x and solver.Value(x[i,b])];offset=0;r,ch,port=b;family=r*896+(2*p['pairs'][str(ch)]+p['sides'][str(ch)])*112+port
  for i in sorted(contents,key=lambda i:(rows[i]['time'],rows[i]['helper'])):
   rows[i].update(owner_replica=r,child=ch,port=port,copy=r*112+port,family=family,offset=offset);offset+=rows[i]['width']
 rem=Counter();allbins=defaultdict(list)
 for r in rows:allbins[r['owner_replica'],r['child'],r['port']].append(r)
 seen=defaultdict(set)
 for key,(c,ts)in p['windows'].items():
  rep,ch=map(int,key.split(','))
  for port in range(112):
   entries=allbins[rep,ch,port];used=0
   for r in sorted(entries,key=lambda r:r['offset']):
    assert r['offset']==used and r['time']in ts and r['family']not in seen[r['time']];seen[r['time']].add(r['family']);used+=r['width']
   assert used<=c
   if c-used:rem[c-used]+=1
 profile=Counter()
 for c in p['provider_calls']:profile.update({int(r):n for r,n in p['provider_registry'][c['provider']]['actual_paid_profile'].items()})
 profile.update(rem);assert sum(r*n for r,n in profile.items())==520704
 out=args.out;out.mkdir();rows.sort(key=lambda r:(r['time'],r['helper']));packed=gzip.compress(json.dumps(rows,sort_keys=True,separators=(',',':')).encode(),mtime=0);(out/'OWNERS.json.gz').write_bytes(packed);p['assignment_sha256']=hashlib.sha256(packed).hexdigest();p['profile']={str(r):n for r,n in sorted(profile.items())};(out/'PROVISIONAL-PLAN.json').write_text(json.dumps(p,indent=2)+'\n');print('WINNER',dict(rem),flush=True);break
