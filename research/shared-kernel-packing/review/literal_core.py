# SPDX-License-Identifier: Apache-2.0
"""Independent literal owner/provider audit. No constructor or solver imports."""
import argparse,collections,copy,gzip,hashlib,json,os
from pathlib import Path

def need(p,m):
 if not p:raise AssertionError(m)
def rd(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def chronology(template,order,T):
 schedule=template['execution_schedule'];need(len(schedule)==32,'source schedule length');blocks={};s=None
 for j,e in enumerate(schedule[:30]):
  if e['kind']=='local_cover_sweep':s=e['stage'];blocks[s]=[]
  need(s is not None,'source starts with local call');blocks[s].append((j,e))
 need(set(blocks)==set(range(9))and [e['kind']for e in schedule[30:]]==['bank_padding_cover_sweep','translate_every_live_family'],'nine source blocks and final routes')
 stages={e['stage']:e['pair']for e in template['recipe']if e['kind']=='local'};caps={e['child']:e['rank']for e in template['idle_children']};pairs={};sides={};last={};bounds={};clock=0;times=[];projection=collections.defaultdict(list)
 for s,r in order:
  for j,e in blocks[s]:
   projection[r].append(j)
   if e['kind']=='local_cover_sweep':times.append(clock);last[r,stages[s]]=clock
   elif e['kind']=='bridge':last[r,e['src']]=clock;last[r,e['dst']]=clock
   elif e['kind']=='idle_cover_sweep':
    for side,ch in enumerate(e['child_indices']):
     
     if ch not in caps:
      need(e['from_level']==e['to_level'],'omitted positive-rank source child');continue
     pairs[ch]=e['pair'];sides[ch]=side;bounds[r,ch]=(last.get((r,e['pair']),-1),clock)
   else:need(e['kind']in('terminal','terminal_Y_translations'),'unknown source event')
   clock+=1
 need(set(projection)==set(range(T))and all(v==list(range(30))for v in projection.values()),'every actual source event once per replica')
 need(set(pairs)==set(caps)and len(times)==9*T,'all source child intervals')
 return caps,pairs,sides,bounds,times,stages

def audit(fill,order,dispatch,providers,context,T):
 caps,pairs,sides,bounds,times,stages=context;need(fill['columns']==['time','helper','owner_replica','child','port','offset']and fill['dispatch_overrides']==[],'literal fill schema/no hidden dispatch')
 occupied={};families=[set()for _ in order];helper_masks=[0 for _ in order];rows=fill['rows']
 for row in rows:
  need(isinstance(row,list)and len(row)==6 and all(type(x)is int for x in row),'integer role descriptor')
  t,h,o,c,p,off=row;need(0<=t<len(order)and 0<=h<408 and 0<=o<T and c in caps and 0<=p<112 and off>=0,'role coordinate range')
  pid=dispatch[tuple(order[t])];w=providers[pid]['widths'][h];need(1<=w<=9 and off+w<=caps[c],'actual width and capacity')
  need(bounds[o,c][0]<times[t]<bounds[o,c][1],'strict actual event window')
  s,r=order[t];f=896*o+112*(2*pairs[c]+sides[c])+p
  need(not(o==r and 224*stages[s]<=f-896*r<224*(stages[s]+1)),'helper aliases active data')
  need(f not in families[t],'duplicate physical family');families[t].add(f)
  need(not(helper_masks[t]>>h&1),'duplicate logical helper');helper_masks[t]|=1<<h
  key=o,c,p;bits=((1<<w)-1)<<off;need(not(occupied.get(key,0)&bits),'overlapping paid slices');occupied[key]=occupied.get(key,0)|bits
 need(len(rows)==len(order)*408 and all(x==(1<<408)-1 for x in helper_masks),'every helper at every invocation')
 idle=collections.Counter()
 for o in range(T):
  for c,cap in caps.items():
   for p in range(112):
    mask=occupied.get((o,c,p),0);need(mask&(mask+1)==0,'literal used prefix');left=cap-mask.bit_count()
    if left:idle[left]+=1
 H=collections.Counter(idle)
 for call in order:H.update({int(r):n for r,n in providers[dispatch[tuple(call)]]['actual_paid_profile'].items()})
 need(sum(r*n for r,n in H.items())==65088*T,'exact paid mass')
 return dict(sorted(H.items())),dict(sorted(idle.items()))

