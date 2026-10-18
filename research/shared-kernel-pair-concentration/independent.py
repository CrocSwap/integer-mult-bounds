#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent event/role audit of the doubled PR2857 allocation. Codex-assisted.
No inherited engine is imported. Full native and analytic admission is separate.
"""
import argparse,collections,copy,gzip,hashlib,json
from pathlib import Path

def need(ok,s):
 if not ok:raise ValueError(s)
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def main():
 import sys
 if sys.flags.optimize:raise SystemExit("assertions must be enabled")
 ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('candidate',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 order=read(a.candidate/'ORDER.json');oldorder=read(a.source/'ORDER.json');need(order==[[s,r+37*k] for s,r in oldorder for k in range(2)],'exact interleaved chronology')
 providers=read(a.source/'PROVIDERS.json');need(providers==read(a.candidate/'PROVIDERS.json'),'unchanged inventory')
 olddispatch=read(a.source/'DISPATCH.json');dispatchrows=read(a.candidate/'DISPATCH.json');need(dispatchrows==[[s,r+37*k,p] for s,r,p in olddispatch for k in range(2)],'unchanged dispatch in both copies')
 dispatch={(s,r):p for s,r,p in dispatchrows};template=read(a.source/'sources/PR2833-T37-TEMPLATE.json.gz');plan=read(a.source/'sources/PR2833-PLAN.json.gz')
 blocks=collections.defaultdict(list);stage=None
 for idx,e in enumerate(template['execution_schedule']):
  if e['kind'] in ('bank_padding_cover_sweep','translate_every_live_family'):continue
  if e['kind']=='local_cover_sweep':stage=e['stage']
  need(stage is not None,'stage');blocks[stage].append((idx,e))
 pairs={e['stage']:e['pair'] for e in template['recipe'] if e['kind']=='local'};rank={e['child']:e['rank'] for e in template['idle_children']};last={};windows={};clocks=[];clock=0;projections=collections.defaultdict(list)
 for t,(s,r) in enumerate(order):
  for idx,e in blocks[s]:
   projections[r].append(idx)
   if e['kind']=='local_cover_sweep':last[r,pairs[s]]=clock;clocks.append(clock)
   elif e['kind']=='bridge':last[r,e['src']]=clock;last[r,e['dst']]=clock
   elif e['kind']=='idle_cover_sweep':
    for child in e['child_indices']:
     if child in rank:windows[r,child]=(last.get((r,e['pair']),-1),clock)
   clock+=1
 need(set(projections)==set(range(74)) and all(v==list(range(30)) for v in projections.values()),'complete original block event projections')
 def audit(rows):
  need(len(rows)==666*408,'all roles');seen=collections.defaultdict(set);families=collections.defaultdict(set);bins=collections.defaultdict(list)
  for row in rows:
   need(len(row)==6 and all(type(v)is int for v in row),'integer role')
   t,h,r,ch,port,off=row;need(0<=t<666 and 0<=h<408 and 0<=r<74 and ch in rank and 0<=port<112 and off>=0,'role ranges')
   lo,hi=windows[r,ch];need(lo<clocks[t]<hi,'chronological window')
   need(h not in seen[t],'duplicate helper');seen[t].add(h)
   family=r*896+(2*plan['pairs'][str(ch)]+plan['sides'][str(ch)])*112+port
   need(family not in families[t],'physical family collision');families[t].add(family)
   w=providers[dispatch[tuple(order[t])]]['widths'][h];need(off+w<=rank[ch],'capacity');bins[r,ch,port].append((off,w))
  need(all(seen[t]==set(range(408)) for t in range(666)),'role coverage')
  idle=collections.Counter()
  for r in range(74):
   for ch,cap in rank.items():
    for port in range(112):
     used=0
     for off,w in sorted(bins[r,ch,port]):need(off==used,'overlap or gap');used+=w
     if used<cap:idle[cap-used]+=1
  profile=collections.Counter(idle)
  for sr in order:profile.update({int(r):n for r,n in providers[dispatch[tuple(sr)]]['actual_paid_profile'].items()})
  need(sum(r*n for r,n in profile.items())==65088*74,'rank mass')
  return profile,idle
 original=read(a.source/'FILL.json.gz');candidate=read(a.candidate/'FILL.json.gz');rows=candidate['rows'];expected=[]
 for t,h,r,ch,port,off in original['rows']:
  for k in range(2):expected.append([2*t+k,h,r+37*k,ch,port,off])
 expected.sort(key=lambda r:r[:2]);before,_=audit(expected)
 target=next(r for r in expected if r[:2]==[658,297]);need(target==[658,297,35,16,37,0],'transfer source');target[2]=72;target[5]=7
 need(rows==expected,'one declared transfer only')
 after,idle=audit(rows);delta={r:after[r]-before[r] for r in after.keys()|before.keys() if after[r]!=before[r]};need(delta=={2:1,9:-2,16:1},'exact idle delta')
 need(dict(after)=={int(r):n for r,n in read(a.candidate/'PROFILE.json').items()},'full profile')
 controls=[]
 for name,change in [('overlap',lambda z:z.__setitem__(5,0)),('capacity',lambda z:z.__setitem__(5,16)),('port',lambda z:z.__setitem__(4,112)),('time',lambda z:z.__setitem__(0,666))]:
  mutant=copy.deepcopy(rows);row=next(r for r in mutant if r[:2]==[658,297]);change(row)
  try:audit(mutant)
  except ValueError as e:controls.append({'name':name,'rejection':str(e)})
  else:raise ValueError('accepted mutant '+name)
 report={'status':'PASS_INDEPENDENT_INTERLEAVED_TRANSFER','calls':666,'roles':len(rows),'replicas':74,'live':66304,'physical':66794,'profile':dict(sorted(after.items())),'idle':dict(sorted(idle.items())),'profile_delta_from_double':delta,'controls':controls,'input_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for d in [a.source,a.candidate] for n in ['FILL.json.gz','ORDER.json','DISPATCH.json','PROVIDERS.json'] if (p:=d/n).exists()},'scope':'Literal complete roles, source event chronology, windows, disjoint families, no-gap capacities, complete profile. Native operations, interfaces and analytic transfer are retained dependencies, not established here.'}
 a.out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['profile'])
if __name__=='__main__':main()
