from pathlib import Path
from collections import defaultdict,Counter
from fractions import Fraction
import json,hashlib,sys
from quaternion_route import construct,orthogonalize
from audit_rational_route import check
R=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text())
w=read(sys.argv[1]);flow=read(sys.argv[2]);audit=read(sys.argv[3]);out=Path(sys.argv[4]);out.mkdir(exist_ok=False)
pivots=set(audit['new_pivots']if 'new_pivots'in audit else [x['pivot']for x in audit['new_entries']]);T=flow['T'];L=flow['L'];m=flow['m'];assert T%2==0
widths={h:8-len(orthogonalize([w['lines'][i]for i in w['frames'][w['start'][h]]]))for h in range(240,955)}
assert all(widths[h]==7 for h in pivots)
registry={}
for h in sorted(pivots):
 f=w['start'][h]
 if f not in registry:
  basis=[w['lines'][i]for i in w['frames'][f]]
  route=construct(w['lines'],[],copies=2,basis=basis);check(route)
  assert all(Fraction(x).denominator in (1,2)for row in route['route']for x in row)
  registry[f]=route
pool=defaultdict(list)
for s in range(L):
 for rep in range(T):
  for h in range(240,955):
   if h not in pivots:pool[s,widths[h]].append([(rep,h)])
 for rep in range(0,T,2):
  for h in sorted(pivots):pool[s,14].append([(rep,h),(rep+1,h)])
win={int(i):(p,r,set(ss))for i,(p,r,ss)in flow['windows'].items()};slots=defaultdict(list);used={};pair_slots=Counter()
for i,(pair,r,ss)in sorted(win.items()):
 cp=0
 for ii,pat,nn in flow['patterns']:
  if ii!=i:continue
  for _ in range(nn):
   rep,loc=divmod(cp,240);fam=rep*1200+(2*pair+loc//120)*120+loc%120;off=0
   for width in pat:slots[i,width].append((fam,off));off+=width
   used[i,fam]=off;cp+=1
 assert cp==240*T
pcs={};pairs=[];cursor=Counter()
for i,width,s,count in flow['stages']:
 assert s in win[i][2]
 for _ in range(count):
  fam,off=slots[i,width].pop();roles=pool[s,width][cursor[s,width]];cursor[s,width]+=1
  if width==14:
   r=win[i][1];spectator=r+2*pair_slots[i,fam];pair_slots[i,fam]+=1;assert spectator+2<=m
   coords=list(range(off,off+14))+[spectator,spectator+1]
   assert len(set(coords))==16 and max(coords)<m
   pairid=len(pairs);f=w['start'][roles[0][1]]
   pairs.append(dict(stage=s,window=i,family=fam,active_offset=off,active_width=14,route_registry_frame=f,output_coordinates=coords,roles=[list(z)for z in roles]))
   for copy,(rep,h)in enumerate(roles):pcs[s,rep,h]=dict(kind='paired-rational-whole',window=i,family=fam,pair=pairid,copy=copy,width=7)
  else:
   assert len(roles)==1;rep,h=roles[0];pcs[s,rep,h]=dict(kind='coordinate-whole',window=i,family=fam,offset=off,width=width)
assert len(pcs)==L*T*715 and all(not q for q in slots.values())
assert all(cursor[k]==len(v)for k,v in pool.items())
# Exact capacity and interval audit; pair projectors individually checked by registry.
bywin=defaultdict(list)
for (s,rep,h),z in pcs.items():
 if z['kind']=='coordinate-whole':bywin[z['window'],z['family']].append((z['offset'],z['offset']+z['width']))
for z in pairs:bywin[z['window'],z['family']].append((z['active_offset'],z['active_offset']+14))
for (i,f),ints in bywin.items():
 ints.sort();assert all(0<=a<b<=win[i][1]for a,b in ints)
 assert all(b<=c for (a,b),(c,d)in zip(ints,ints[1:]))
# For each pair j, sigma_j = placement * (G directsum I) * swap(block0,blockj).
# This determines all m*m entries uniquely, with inverse equal to transpose.
# Active-projector inequality proves the pair's two owner matrices are distinct.
record=dict(status='PASS_EXACT_PAIRED_WHOLE_OWNER_ALLOCATION',source_word_sha256=hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),source_flow_sha256=hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest(),m=m,stages=L,replicas=T,new_pivots=sorted(pivots),registry=registry,pairs=pairs,owners=[[s,rep,h,z]for (s,rep,h),z in sorted(pcs.items())],route_definition='sigma_j = actual_pending_basis(window,port) * placement(output_coordinates) * (G directsum I) * swap(first8,copyj8). Complete output placement extends by increasing unused coordinates. One whole owner family; inverse transpose.',windows=flow['windows'],profile=flow['profile'],rank_mass=flow['rank_mass'],deficit=flow['deficit'],max_same_family_pairs=max(pair_slots.values()),maximum_spectator_dimensions=2*max(pair_slots.values()),numeric_saving_nomination=flow['numeric_saving'])
(out/'PAIRED-OWNERS.json').write_text(json.dumps(record,separators=(',',':'))+'\n')
print(json.dumps({k:v for k,v in record.items()if k not in ['owners','registry','pairs','windows','new_pivots']},indent=2));print('pair_count',len(pairs),'individual_whole_residuals',len(pcs),'route_frames',len(registry))
