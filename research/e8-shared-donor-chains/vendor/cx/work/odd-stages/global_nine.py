"""Source-bound nine-stage IR, injective owner routes, and finite invoice.
The complete orthogonal cover is a symbolic finite loop, as in the frozen
supplier. This checks its route bijections, not an astronomical enumeration.
"""
import os,sys,json,gzip,hashlib,importlib.util,math,time
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from data_phases import rho,rank,mv,transpose
sys.set_int_max_str_digits(0)
ROOT=Path('work/native358/vendor/complex-reserve/upstream/pr352/code/complex').resolve();OUT=Path('work/complex-nine-native');t0=time.monotonic()
os.environ['CX_PINS']=str(ROOT/'pins-e8.json');os.environ.pop('CX_RECORD',None);sys.path.insert(0,str(ROOT/'code'))
s=importlib.util.spec_from_file_location('cx9_source_splice',ROOT/'code/complex_splice.py');S=importlib.util.module_from_spec(s);s.loader.exec_module(S)
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
c=json.load(gzip.open('work/pr361/complex/gcert1-e8-r783.json.gz'));raw=read(OUT/'local-admission/UPSTREAM-GUARD.json');audit=read(OUT/'local-admission/INDEPENDENT-AUDIT.json');phase=read(OUT/'DATA-PHASES.json');clifford=read(OUT/'CLIFFORD-REVIEW.json');candidate=read('work/odd-stages/COMPLEX-NINE-CANDIDATE.json')
assert raw['splice']['certificate_sha256']==sha('work/pr361/complex/gcert1-e8-r783.json.gz')==candidate['certificate_gzip_sha256']
assert audit['guard_receipt_sha256']==sha(OUT/'local-admission/UPSTREAM-GUARD.json')
for ori in ['forward','backward']:assert audit['scalar_words'][ori]['all_live_rows_correct'] and audit['scalar_words'][ori]['all_private_work_restored_zero']
h,v,R=9,120,783;k,L,T,m=4,9,8,73;live=14727;physical=live+R+h+1
assert phase['status']=='PASS_EXACT_Z4_DATA_ROUTE_IDLE_AND_TERMINAL_PHASES' and clifford['all_child_equalities_include_global_phase']
locals={};local_checks={}
for ori in ['forward','backward']:
 events=list(S.emit(c,ori));check=S.validate(events,c,ori,{'checks':raw['label_checks']},raw['scalar_bill']);assert check==raw['splice']['program'][ori]
 locals[ori]=events;local_checks[ori]=check
def bank_perm(slot):
 p=list(range(m))
 if slot:
  for i in range(h):p[i],p[slot*h+i]=p[slot*h+i],p[i]
 return tuple(1<<i for i in p)
perms=[bank_perm(j) for j in range(8)];assert len(set(perms))==8
for P in perms:assert transpose(P,m)==P and all(mv(P,mv(P,1<<i))==1<<i for i in range(m))
def owners(stage,rep,pair):
 out=[]
 for r in range(2*v):out.append([rep*(2*k*v)+(2*pair+r//v)*v+r%v,[1,stage,r%v]])
 for r in range(R):
  z=rep*R+r;bank,slot=divmod(z,8);out.append([2*k*v*T+stage*R+bank,[2,slot]])
 return out
recipe=read('work/odd-stages/RECIPE-9.json');calls=[];paid=Counter();seen_assign=set();scalar_primitives=0;event_count=0
for e in recipe:
 if e['kind']!='local':continue
 stage,pair=e['stage'],e['pair'];ori='backward' if e['reverse'] else 'forward'
 for rep in range(T):
  mapping=owners(stage,rep,pair);keys=[(f,tuple(r)) for f,r in mapping]
  assert len(set(keys))==2*v+R and all(0<=f<live for f,r in mapping)
  for p,q in enumerate(c['ports']):
   d=rho(q,stage);assert all(mv(d,mv(d,1<<j))==1<<j for j in range(m))
  for r,(family,route) in enumerate(mapping[2*v:]):
   _,slot=route;P=perms[slot];assert {mv(P,1<<j) for j in range(h)}=={1<<j for j in range(slot*h,(slot+1)*h)}
   seen_assign.add((stage,rep,r,family,slot))
  # Every private scalar-only work stream is disjoint and cleared locally.
  private=list(range(live,physical));assert not set(f for f,r in mapping)&set(private)
  for ev in locals[ori]:
   if ev[0]=='climb':paid[ev[5]]+=1
   elif ev[0]=='center':paid[ev[4]]+=1
  scalar_primitives+=local_checks[ori]['real_component_primitives'];event_count+=len(locals[ori])
  calls.append(dict(stage=stage,replica=rep,pair=pair,orientation=ori,owners=mapping,window=dict(local_axes=list(range(h)),prefix_axes=list(range(h,h+stage*8))),local_program_sha256=local_checks[ori]['program_sha256']))
assert len(calls)==72 and len(seen_assign)==L*T*R
idle=[]
for p,z in enumerate(phase['recipes']):
 for j,x in enumerate(z['idle_children']):
  if x['rank']:paid[x['rank']]+=T;idle.append(dict(port=p,child=j,rank=x['rank'],replicas=T))
paid[1]+=L*R
assert dict(sorted(paid.items()))=={int(r):n for r,n in candidate['profile'].items()}
mass=sum(r*n for r,n in paid.items());assert m*live-mass==2496
bridges=[e for e in recipe if e['kind']=='bridge'];bridge_adds=2*v*T*len(bridges);terminal_shifts=k*v*T;terminal_movements=2*k*v*T
cover_corrections=live
assert phase['cover_correction']['mandatory'] is True
# Retain one extra centre slot, all R dirty-tableau slots and one coefficient
# slot. Calls, replicas and cover classes run sequentially; their clean work
# is reused only after the source-checked erasure events.
macros=max(raw['scalar_bill'][o]['totals']['scalar_macros'] for o in locals)
local_children=raw['label_checks']['invocation_calls'];assert local_children==3974
compiler=64*(m+1)**3
local_adapter_bound=16*(macros+local_children+(2*v+R)+h)+64*m
local_primitive=max(local_checks[o]['real_component_primitives'] for o in locals)
local_bound=local_primitive+local_adapter_bound*compiler
# Each changed route or child gets at least two full rank-zero compilations;
# factor eight also covers phases, inverse charts, selector and cleanup.
nonlocal_items=(4*v*T*L+2*v*T*L+2*L*T*R+len(idle)*T+L*R+bridge_adds+terminal_shifts+terminal_movements+cover_corrections+physical)
outside=8*nonlocal_items+64*m
pervertex=scalar_primitives+bridge_adds+terminal_shifts+terminal_movements+cover_corrections+(72*local_adapter_bound+outside)*compiler+64*physical
r=m//2;group=2**(r*r)*math.prod(2**(2*i)-1 for i in range(1,r+1));stock=group*live;physical_stock=group*physical;s_mass=group*mass;logical=group*pervertex+64;router=compiler*(logical+1)*(physical_stock+1)**2
G,E,C0=1<<30000,1<<100000,1<<210000;B=s_mass+E;literal=2*G*physical_stock**2+8*s_mass+4*physical_stock+4+32*m
maxchild=max(paid);depth=next(t for t in range(1,20) if m**t>2*maxchild**t);assert depth==2
induction=2*(m-maxchild)-1;assert 2*B*(m-maxchild)-s_mass-E==induction*B and induction>=1
assert local_bound<1<<48 and logical<1<<6050 and router<G and literal<E and B<1<<100001
assert 32*m*B*B<C0 and 2*B+18<C0
row=depth*physical_stock.bit_length()+9909+252;assert row<20161 and Q(10**6)-Q(51*20161,25)>0
for e in range(1,100001):
 f=e//m;assert (maxchild*(maxchild*f//m))*2<e if f else True
 # This explicit bound is only a finite control; m^2>2r^2 proves all e.
template=dict(version='independent-compressed-nine-v1',m=m,cover='all matrices d in O(73,2), in lexicographic row order',loop_order='For each recipe phase: replicas in increasing order, then every cover class d; each local invocation completes before the next.',live=live,physical=physical,recipe=recipe,local_programs=locals,calls=calls,bank_padding=dict(families=list(range(2*k*v*T,live)),axis=72,child_rank=1),idle_children=idle,exact_data_phase_recipe_sha256=sha(OUT/'DATA-PHASES.json'),exact_local_clifford_recipe_sha256=sha(OUT/'CLIFFORD-RECIPES.json'),private_namespace=dict(centers=[live,live+h],tableau=[live+h,live+h+R],coefficient=[physical-1,physical]),route_semantics={'data':'physical cover class d*rho(stage,port); rho is the exact orthogonal involution from data_phases.py','helper':'physical cover class d*Pi(slot)^(-1); Pi swaps the local nine coordinates with the assigned bank block','work':'private family at class d; every allocated work stream is erased before reuse'},adapter_policy='Use the exact rank-zero translations in DATA-PHASES.json, the explicit Gaussian monomial adapters in CLIFFORD-RECIPES.json, and the literal terminal X_q before signed exchange.')
template['cover_final_correction']=dict(kind='translate_every_live_family',formula='delta_i=(weight(row_i(g))-1)/2 mod 2',families=[0,live],must_follow_bank_padding_and_data_signed_exchange=True,charged_calls_per_cover=cover_corrections)
schedule=[]
for e in recipe:
 if e['kind']=='local':
  s=e['stage'];schedule.append(dict(kind='local_cover_sweep',stage=s,replicas=list(range(T)),entry_exit_phase_adapters='DATA-PHASES.recipes[port].stage_alignment[stage]'))
  if s in (1,3,5):
   j=(s+1)//2;schedule.append(dict(kind='idle_cover_sweep',pair=j,child_indices=[4*(j-1),4*(j-1)+2],from_level=-1,to_level=s))
  elif s in (2,4,6):
   j=s//2;schedule.append(dict(kind='idle_cover_sweep',pair=j,child_indices=[4*(j-1)+1,4*(j-1)+3],from_level=s-1,to_level=s))
  elif s==8:
   for j in range(4):schedule.append(dict(kind='idle_cover_sweep',pair=j,child_indices=[12+2*j,13+2*j],from_level=2*j+2,to_level=8))
 elif e['kind']=='bridge':schedule.append(dict(e))
 else:
  schedule.append(dict(kind='terminal_Y_translations',pairs=list(range(4)),vector='port q transported by its cover matrix g'))
  schedule.append(dict(e))
schedule.append(dict(kind='bank_padding_cover_sweep',families=[7680,live],axis=72,rank=1))
schedule.append(dict(template['cover_final_correction']))
template['execution_schedule']=schedule
blob=json.dumps(template,sort_keys=True,separators=(',',':')).encode();(OUT/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(blob,mtime=0))
invoice=dict(local_primitive_bound=local_bound,local_adapters=local_adapter_bound,compiler=compiler,scalar_primitives_all_invocations=scalar_primitives,outside_adapter_bound=outside,pervertex=pervertex,group_bits=group.bit_length(),live_stock_bits=stock.bit_length(),physical_stock_bits=physical_stock.bit_length(),logical_groups_bits=logical.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),required_C0_bits=(32*m*B*B).bit_length(),G_exponent=30000,E_exponent=100000,C0_exponent=210000,halving_degree=depth,halving_integer_inequality=[m**depth,2*maxchild**depth],induction_gap_multiple_B=induction,physical_row_coefficient=row,retained_row_coefficient=20161)
result=dict(status='PASS_NINE_STAGE_SOURCE_BOUND_TEMPLATE_OWNERS_PROFILE_AND_FINITE_INVOICE',m=m,live=live,physical=physical,invocations=72,local_source_events=event_count,paid_calls=sum(paid.values()),rank_mass=mass,deficit=2496,profile=dict(sorted(paid.items())),whole_residual_assignments=len(seen_assign),bank_padding_calls=L*R,bridge_additions=bridge_adds,terminal_shift_calls=terminal_shifts,terminal_complete_stream_movements=terminal_movements,work_lifetimes_freshly_revalidated=True,owner_injections=True,cover_route_bijections='Explicit invertible right factors; roles sharing a bank have different disjoint block images, hence different right factors.',template_sha256=hashlib.sha256(blob).hexdigest(),finite_invoice=invoice,source_hashes={str(p):sha(p) for p in [ROOT/'code/complex_splice.py',OUT/'local-admission/UPSTREAM-GUARD.json',OUT/'local-admission/INDEPENDENT-AUDIT.json',OUT/'CLIFFORD-REVIEW.json',OUT/'DATA-PHASES.json']},seconds=time.monotonic()-t0,scope='Finite source-bound global recipe, exact owner factors, paid histogram and conservative scalar/tape/precision/row invoice. Requires explicit mathematical integration of the compressed window lift and arbitrary-bank dirty composition; this is not a Lean proof or final multiplication exponent certificate.')
result['cover_correction_calls']=cover_corrections
(OUT/'GLOBAL-REVIEW.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
