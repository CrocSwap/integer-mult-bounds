"""Independent finite schedule/phase/owner readback, without price search."""
from pathlib import Path
import json,gzip,hashlib,copy
from collections import Counter,defaultdict
P=Path('pr378-donor-screen');BASE=Path('pr378-complex-screen/compressed/work/complex-nine-native')
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=gzip.decompress((P/'prefix-gauge-complete-template.json.gz').read_bytes());old=json.loads(raw)
phasebytes=(BASE/'DATA-PHASES.json').read_bytes();phase=json.loads(phasebytes)
rraw=gzip.decompress((P/'prefix-gauge-routes.json.gz').read_bytes());routes=json.loads(rraw)
c=json.load(gzip.open(P/'prefix-donor-candidate.json.gz'));ext=dict(c['ext']);h=c['h'];m=old['m'];v=c['v'];n=2*v+c['R'];basis=json.load(open(P/'best-bank-geometry.json'))['orthonormal_complement']
def mv(rows,x):return sum(((r&x).bit_count()%2)<<i for i,r in enumerate(rows))
def trans(rows):return [sum(((rows[i]>>j)&1)<<i for i in range(len(rows))) for j in range(len(rows))]
def scalar(events):
 a=[[int(i==j) for j in range(8)] for i in range(8)]
 def add(t,s,q):a[t]=[x+q*y for x,y in zip(a[t],a[s])]
 for e in events:
  if e['kind']=='local':
   x=2*e['pair'];y=x+1
   add(x,y,-1) if e['reverse'] else add(y,x,1)
  elif e['kind']=='bridge':
   i,j,q=e['dst'],e['src'],e['coefficient'];add(2*i,2*j,q);add(2*j+1,2*i+1,-q)
  elif e['kind']=='terminal':
   b=copy.deepcopy(a)
   for j in range(4):a[2*j]=b[2*j+1];a[2*j+1]=[-z for z in b[2*j]]
 return a
I=[[int(i==j) for j in range(8)] for i in range(8)]
def schedule(t):
 assert t['data_phase_binding']['sha256']==sha(phasebytes)
 assert t['route_table_sha256']==sha(rraw)
 stages={e['stage']:e for e in t['recipe'] if e['kind']=='local'};levels=[-1]*4;seen=[];children=[];reconstructed=[];terminal=False;padding=False
 for e in t['execution_schedule']:
  k=e['kind']
  if k=='local_cover_sweep':
   s=e['stage'];a=stages[s];p=a['pair'];assert levels[p]==s-1
   assert e['entry_exit_phase_adapters']==dict(recipe='DATA-PHASES',stage=s,entry=['entry_X','entry_Y'],exit=['exit_X','exit_Y'])
   assert e['local_call_indices']==[i for i,x in enumerate(t['calls']) if x['stage']==s]
   assert e['replicas']==list(range(8));levels[p]=s;seen.append(s);reconstructed.append(a)
  elif k=='idle_cover_sweep':
   p=e['pair'];assert levels[p]==e['from_level']<=e['to_level'];assert e['apply_translation_after_child'] is True
   for idx in e['child_indices']:
    assert all(idx<len(r['idle_children']) for r in phase['recipes']);children.append(idx)
   levels[p]=e['to_level']
  elif k=='bridge':assert levels[e['src']]==levels[e['dst']];reconstructed.append(e)
  elif k=='terminal_Y_translations':assert levels==[8]*4;assert e['phase_recipe_field']=='terminal_Y_translation';terminal=True
  elif k=='terminal':assert terminal and levels==[8]*4;reconstructed.append(e)
  elif k=='bank_padding_cover_sweep':assert terminal;assert e['blocks']==t['bank_padding'];padding=True
  elif k=='translate_every_live_family':assert padding;assert e==t['cover_final_correction'] and e['families']==[0,t['live']]
  else:raise AssertionError(k)
 assert seen==list(stages) and reconstructed==t['recipe'];assert sorted(children)==list(range(len(phase['recipes'][0]['idle_children'])))
 assert scalar(reconstructed)==I
 # Every nonzero idle child is paid exactly with its literal phase recipe.
 want={(r['port'],i):x['rank'] for r in phase['recipes'] for i,x in enumerate(r['idle_children']) if x['rank']}
 got={(x['port'],x['child']):x['rank'] for x in t['idle_children']}
 assert want==got and len(got)==len(t['idle_children']);assert all(x['replicas']==8 for x in t['idle_children'])
 # Source-bound data owners, including right factors and exact local hash.
 for call in t['calls']:
  s,r,p=call['stage'],call['replica'],call['pair'];assert p==stages[s]['pair'];assert call['orientation']==('backward' if stages[s]['reverse'] else 'forward')
  assert call['local_program_sha256']==sha(json.dumps(t['local_programs'][call['orientation']],sort_keys=True,separators=(',',':')).encode())
  for z,(fam,route) in enumerate(call['owners'][:2*v]):assert fam==r*8*v+(2*p+z//v)*v+z%v and route==[1,s,z%v]
 return len(children)
def owners(rr,t):
 lookup={(a['replica'],a['helper']):a for a in rr};assert len(lookup)==len(rr)==8*c['R']
 blocks=defaultdict(list)
 for a in rr:
  A=a['map_local_to_bank_rows'];inv=a['owner_right_factor_rows'];assert inv==trans(A)
  assert all(mv(inv,mv(A,1<<i))==1<<i for i in range(m))
  b=basis if a['helper'] in ext else [1<<i for i in range(h)]
  assert len(b)==len(a['residual_axes'])
  for x,j in zip(b,a['residual_axes']):assert mv(inv,1<<j)==x and mv(A,x)==1<<j
  blocks[a['bank']].extend(a['residual_axes'])
 bankcount=len(blocks)
 for call in t['calls']:
  used=set()
  for z in range(2*v,n):
   a=lookup[call['replica'],z];expected=[8*8*v+call['stage']*bankcount+a['bank'],['orthogonal_inverse_route',call['replica'],z]];assert call['owners'][z]==expected
   # Complete-cover right multiplication is bijective. Within one call,
   # actual helper streams are distinct, including helpers sharing banks.
   owner=(expected[0],tuple(a['owner_right_factor_rows']));assert owner not in used;used.add(owner)
 for b,axes in blocks.items():assert len(axes)==len(set(axes))
 for stage in range(9):
  for b,axes in blocks.items():
   fam=8*8*v+stage*bankcount+b;pad=next((x['axes'] for x in t['bank_padding'] if x['family']==fam),[])
   assert sorted(axes+pad)==list(range(m))
 return bankcount
# Preserve the first emitted artifact and record its concrete admission gap.
try:schedule(old)
except (KeyError,AssertionError) as e:initial=dict(status='REJECTED_UNBOUND_DATA_PHASE_SCHEDULE',template_sha256=sha(raw),error=str(e))
else:raise AssertionError('v2 unexpectedly complete')
(P/'complete-schedule-v2-rejection.json').write_text(json.dumps(initial,indent=2))
t=copy.deepcopy(old);t['version']='prefix-donor-gauge-bound-schedule-v3';t['data_phase_binding']=dict(path=str(BASE/'DATA-PHASES.json'),sha256=sha(phasebytes),semantics='Per port entry adapters before local word, exit adapters after local word; translations after every idle child; terminal Y translation before exchange.')
for e in t['execution_schedule']:
 if e['kind']=='local_cover_sweep':e['entry_exit_phase_adapters']=dict(recipe='DATA-PHASES',stage=e['stage'],entry=['entry_X','entry_Y'],exit=['exit_X','exit_Y'])
 elif e['kind']=='idle_cover_sweep':e['apply_translation_after_child']=True
 elif e['kind']=='terminal_Y_translations':e['phase_recipe_field']='terminal_Y_translation'
t['scope']='Finite schedule and explicit route audit; local normalization and Clifford interfaces are source-bound. No unconditional theorem or new kappa; independent ambient Gaussian integration remains a separate obligation.'
for call in t['calls']:call['local_program_sha256']=sha(json.dumps(t['local_programs'][call['orientation']],sort_keys=True,separators=(',',':')).encode())
t['local_program_hash_encoding']='JSON sorted keys, compact separators, UTF-8'
childcount=schedule(t);banks=owners(routes,t);controls=[]
mutations=[('missing_entry_exit_phase',lambda z:z['execution_schedule'][0].pop('entry_exit_phase_adapters')),('missing_idle_translation',lambda z:next(e for e in z['execution_schedule'] if e['kind']=='idle_cover_sweep').__setitem__('apply_translation_after_child',False)),('wrong_idle_level',lambda z:next(e for e in z['execution_schedule'] if e['kind']=='idle_cover_sweep').__setitem__('from_level',0)),('omit_local_call',lambda z:z['execution_schedule'][0]['local_call_indices'].pop()),('omit_terminal_translation',lambda z:z['execution_schedule'].pop(next(i for i,e in enumerate(z['execution_schedule']) if e['kind']=='terminal_Y_translations'))),('omit_cover_family',lambda z:z['cover_final_correction']['families'].__setitem__(1,z['live']-1)),('wrong_data_owner',lambda z:z['calls'][0]['owners'][0].__setitem__(1,[1,1,0]))]
for name,fn in mutations:
 bad=copy.deepcopy(t);fn(bad)
 try:schedule(bad)
 except (KeyError,AssertionError):controls.append(name)
 else:raise AssertionError('accepted '+name)
for i,e in enumerate(t['recipe']):
 if e['kind']=='bridge':assert scalar(t['recipe'][:i]+t['recipe'][i+1:])!=I
bad=copy.deepcopy(routes);a=next(x for x in bad if x['map_local_to_bank_rows']!=x['owner_right_factor_rows']);a['owner_right_factor_rows']=a['map_local_to_bank_rows']
try:owners(bad,t)
except AssertionError:controls.append('wrong_inverse_route')
else:raise AssertionError('wrong route accepted')
blob=json.dumps(t,sort_keys=True,separators=(',',':')).encode();(P/'prefix-gauge-bound-template.json.gz').write_bytes(gzip.compress(blob,mtime=0))
result=dict(status='PASS_SCOPED_BOUND_SCHEDULE_AND_INVERSE_OWNER_AUDIT',template_sha256=sha(blob),data_phase_sha256=sha(phasebytes),routes=len(routes),banks_per_stage=banks,stages=9,scheduled_idle_children_per_port=childcount,nonzero_paid_idle_children=len(t['idle_children']),structural_controls_rejected=controls,bridge_omission_controls=9,scope=t['scope'],prior_v2_rejected=initial)
(P/'bound-schedule-audit.json').write_text(json.dumps(result,indent=2));print(result)
