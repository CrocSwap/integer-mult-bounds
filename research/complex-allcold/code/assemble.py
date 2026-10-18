"""Hardened all72 one-cold three-provider 0/4/8 assembly with the native exact-complex moment.

Prepared with OpenAI Codex assistance. The rational engines and outer
constraints are retained from PR547/PR548 and their preserved ancestry.
The bit operator is the cited unchanged PR543 supplier. The complex owner
and invoice inputs must be freshly emitted by the packaged physical replay.
All conservative admission guards and conservative moment/outer witnesses run
before the PR559 native-complex correction. The bit surcharge is retained.
"""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal, localcontext
import argparse,json,hashlib,importlib.util
from collections import Counter
assert __debug__, 'Assertions required'
P=Path(__file__).resolve().parent.parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hash_ok=lambda x:isinstance(x,str) and len(x)==64 and all(t in '0123456789abcdef'for t in x)
digest=lambda x:hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
def load(n):
 s=importlib.util.spec_from_file_location(n,P/'engines'/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M,B,A=[load(n)for n in ('moment','base_two_moment','outer')]
def dec(x):
 with localcontext()as ctx:ctx.prec=70;return str(Decimal(x.numerator)/Decimal(x.denominator))
PROVIDERS={'rank5_zero_cold': {'semantic_phase_sha256': 'cc8ef5d8b6814b3c7ce241c5eabb9b79ca342248a9df5e985b15575ea899be93', 'promoted': 0, 'width_digest': '9384652a1b9e5138ae337e329f6ffbf9d7c2a0a93e120d21ea5fec663198959b', 'program_hashes': {'forward': '2e6c329a14d95ad5d22a9672bb3a9136b96c0f0997d9cdb7bb5f0f0d05e17504', 'backward': '3edefeeeeed2f234ae0c72483363c38af87efbd415547425692e851cee69dc0f'}, 'artifacts': {'CANONICAL-WORD.json.gz': 'cfaaf0e6e033641e29ef926a1150b670f339a95993ebd7d8b37b24f58d5e7eb5', 'LOCAL-PROGRAMS.json.gz': '17bf7294e3ba34b52c134f54eca352eb3200843c51c230d048957b6164ffee27', 'LOCAL-CHECKS.json': 'a79876ab82fc3156d0542e002001a958fe0653f05f40d8b302b296da1f05216b', 'INDEPENDENT-LOCAL-REPLAY.json': '718a0b5c406c282f35b882df3451fdb6865c8bac6a038660422ecc316a493eb6', 'CLIFFORD-RECIPES.json': '95d12229b708f96864d7d226ff1f393c107fe9488b6019a298313028b8f5a2ed', 'RESIDUAL-ADAPTERS.json': 'e4fce8ca73ad20a86711837dd6fe1efad5a335689352791a635969e4d1be4391'}}, 'rank5_four_cold': {'semantic_phase_sha256': 'b1ad37b19dba3c211a18201820d6579c51b1c5f815745cdbe259651698111c63', 'promoted': 4, 'width_digest': '51d98570282ed066bd61bc60601681b44bb790ecd6dd2491b6b9e29b1b2eb693', 'program_hashes': {'forward': 'ed1ec8bc7f62806188df0b8f1516a958709c4cf7064c925b328f9a0240a9f321', 'backward': 'cd5fd9340f3064053b39e65fa053447e2a9f3545c038c073e328d2158469aca5'}, 'artifacts': {'CANONICAL-WORD.json.gz': 'd8b15de893feb4f0c93b456341a43e34aea7ffd0b3044a6d5ad44ac9efaa6d72', 'LOCAL-PROGRAMS.json.gz': '0b18cf4e24ba9f46ea24bb430e0cc9892ea3fe0a6a7586ff991e8d2ca22c1b82', 'LOCAL-CHECKS.json': 'd8ea70e258c5abb286784d493198173426be22635e1bc8f7c523a64614e4373f', 'INDEPENDENT-LOCAL-REPLAY.json': '736d39d98cb94aa40d10a0973f6375c28d29272e3c2f43f3b0e5776c0ac856fa', 'CLIFFORD-RECIPES.json': '6a6656fa6a3fdc0f081798a1a5d2303188c8f6d772e197253770926a044cc15e', 'RESIDUAL-ADAPTERS.json': 'ddeab3b37b16eca2c90c2a8d4afa124e86b611319c8f0a9632bfefbaa7667a0e'}}, 'rank5_eight_cold': {'semantic_phase_sha256': '2375b30733b9b2227b8a98a479c9000a77c1e40c98a4f1d97060a1506950ba0f', 'promoted': 8, 'width_digest': '6d7a577752c16fc59a21ae1b51dbf7e817b7c12172c5553da059aac8a48513af', 'program_hashes': {'forward': '81cb6a56eff79171f44cf2ab23e3d7288a5c0f44496c28f1d430e9276142f221', 'backward': 'a08413a5c1118477fc4c4b0e441248bb1bbc66f76a14c5d1d7a50feda94e2bb4'}, 'artifacts': {'CANONICAL-WORD.json.gz': '6bf22cadf4a4669458bfd9e8dd7dab80d8502595e52fc36acb60e9148f9fe93f', 'LOCAL-PROGRAMS.json.gz': '0179812f9f23ed4d89621c2c8355ca76ca226688090b32c02bf31e6d765de9f9', 'LOCAL-CHECKS.json': 'c06fda3e9e4232200f6ac4a7955b556b112f830f38457f65255b9753ac68bbba', 'INDEPENDENT-LOCAL-REPLAY.json': '898af46c5c47d35eb193adeb422fa464e67d7d7be43c8cf0657e59f282868ef0', 'CLIFFORD-RECIPES.json': '0e1f804db8521a62f2a8a4b52a697fb27d86b78f453207c316e5d77502f3c2bc', 'RESIDUAL-ADAPTERS.json': 'baafef737acc16dafbe1150896feb16744f3d669fa123bb2bff19ecc4e71b275'}}}
DISPATCH={(0, 0): 'rank5_eight_cold', (0, 1): 'rank5_eight_cold', (1, 0): 'rank5_eight_cold', (0, 2): 'rank5_eight_cold', (1, 1): 'rank5_eight_cold', (2, 0): 'rank5_eight_cold', (0, 3): 'rank5_eight_cold', (1, 2): 'rank5_eight_cold', (2, 1): 'rank5_eight_cold', (3, 0): 'rank5_eight_cold', (0, 4): 'rank5_eight_cold', (1, 3): 'rank5_eight_cold', (2, 2): 'rank5_eight_cold', (3, 1): 'rank5_eight_cold', (4, 0): 'rank5_eight_cold', (0, 5): 'rank5_eight_cold', (1, 4): 'rank5_eight_cold', (2, 3): 'rank5_eight_cold', (3, 2): 'rank5_eight_cold', (4, 1): 'rank5_eight_cold', (5, 0): 'rank5_eight_cold', (0, 6): 'rank5_eight_cold', (1, 5): 'rank5_eight_cold', (2, 4): 'rank5_eight_cold', (3, 3): 'rank5_eight_cold', (4, 2): 'rank5_eight_cold', (5, 1): 'rank5_eight_cold', (0, 7): 'rank5_eight_cold', (6, 0): 'rank5_eight_cold', (1, 6): 'rank5_eight_cold', (2, 5): 'rank5_eight_cold', (3, 4): 'rank5_eight_cold', (4, 3): 'rank5_eight_cold', (5, 2): 'rank5_eight_cold', (6, 1): 'rank5_eight_cold', (1, 7): 'rank5_eight_cold', (7, 0): 'rank5_eight_cold', (2, 6): 'rank5_eight_cold', (3, 5): 'rank5_eight_cold', (4, 4): 'rank5_eight_cold', (5, 3): 'rank5_eight_cold', (6, 2): 'rank5_zero_cold', (7, 1): 'rank5_eight_cold', (2, 7): 'rank5_eight_cold', (8, 0): 'rank5_eight_cold', (3, 6): 'rank5_zero_cold', (4, 5): 'rank5_four_cold', (5, 4): 'rank5_eight_cold', (6, 3): 'rank5_eight_cold', (7, 2): 'rank5_zero_cold', (8, 1): 'rank5_eight_cold', (3, 7): 'rank5_eight_cold', (4, 6): 'rank5_zero_cold', (5, 5): 'rank5_zero_cold', (6, 4): 'rank5_eight_cold', (7, 3): 'rank5_eight_cold', (8, 2): 'rank5_zero_cold', (4, 7): 'rank5_zero_cold', (5, 6): 'rank5_eight_cold', (6, 5): 'rank5_eight_cold', (7, 4): 'rank5_zero_cold', (8, 3): 'rank5_zero_cold', (5, 7): 'rank5_zero_cold', (6, 6): 'rank5_eight_cold', (7, 5): 'rank5_four_cold', (8, 4): 'rank5_zero_cold', (6, 7): 'rank5_zero_cold', (7, 6): 'rank5_zero_cold', (8, 5): 'rank5_zero_cold', (7, 7): 'rank5_eight_cold', (8, 6): 'rank5_eight_cold', (8, 7): 'rank5_zero_cold'}
CALL_ORDER=[(0, 0), (0, 1), (1, 0), (0, 2), (1, 1), (2, 0), (0, 3), (1, 2), (2, 1), (3, 0), (0, 4), (1, 3), (2, 2), (3, 1), (4, 0), (0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0), (0, 6), (1, 5), (2, 4), (3, 3), (4, 2), (5, 1), (0, 7), (6, 0), (1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (1, 7), (7, 0), (2, 6), (3, 5), (4, 4), (5, 3), (6, 2), (7, 1), (2, 7), (8, 0), (3, 6), (4, 5), (5, 4), (6, 3), (7, 2), (8, 1), (3, 7), (4, 6), (5, 5), (6, 4), (7, 3), (8, 2), (4, 7), (5, 6), (6, 5), (7, 4), (8, 3), (5, 7), (6, 6), (7, 5), (8, 4), (6, 7), (7, 6), (8, 5), (7, 7), (8, 6), (8, 7)]
def assemble(owner,invoice,owner_sha,invoice_sha):
 # These are admission receipts, not optional collections of successful rows.
 # Require both orientations and every finite check before pricing anything.
 assert owner['status']=='PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE'
 assert invoice['status']=='PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE'
 assert all(hash_ok(x)for x in (owner_sha,invoice_sha,owner['template_sha256'],owner['controller_audit_sha256'],invoice['parent_template_sha256']))
 checks={'local_primitive_bound','logical','router','literal','mass','precision','tape','row','halving'}
 assert set(invoice['strict_checks'])==checks
 assert all(invoice['strict_checks'][name] is True for name in checks)
 assert set(invoice['providers'])==set(PROVIDERS)
 assert invoice['provider_counts']=={'rank5_eight_cold':55,'rank5_zero_cold':15,'rank5_four_cold':2}
 assert owner['all_live_owners_per_call_distinct'] is True
 assert owner['owners_per_call']==728 and owner['actual_helper_owner_charts']==36288
 assert owner['rank_mass']==520704
 assert owner['actual_73column_sigmas']==2962 and owner['cross_replica_helper_roles']==29514
 assert owner['explicit_idle_remainder_children']==4204
 assert invoice['complete_invocation_sweeps']==invoice['bridge_sweeps']==72
 assert invoice['live']==owner['live'] and invoice['physical']==owner['physical']
 assert invoice['helpers']==504 and invoice['centres']==8
 assert invoice['physical_stock_identity']==dict(data_and_owner_families=7168,local_helpers=504,private_centres=8,coefficient_work=2)
 assert sum(invoice['physical_stock_identity'].values())==invoice['physical']
 assert invoice['controller_audit_sha256']==owner['controller_audit_sha256']
 for pid,p in invoice['providers'].items():
  promoted=PROVIDERS[pid]['promoted']
  assert set(p['local'])=={'forward','backward'}
  assert p['helpers']==504 and p['centres']==8 and p['n']==728 and p['v']==112 and p['h']==9
  assert p['entering_helpers']==213 and p['entrance_rank']==381+promoted
  assert p['width_inventory']=={str(r):n for r,n in {4:promoted,5:56-promoted,8:157,9:291}.items()if n}
  assert all(type(w) is int and 0<w<=9 for w in p['widths'])
  assert Counter(p['widths'])==Counter({int(r):n for r,n in p['width_inventory'].items()})
  assert sum(p['widths'])==9*504-p['entrance_rank'] and len(p['widths'])==504
  assert digest(p['widths'])==PROVIDERS[pid]['width_digest'] and p['widths'][270]==8
  assert p['paid_profile']=={'1':2301+2*promoted,'2':442-2*promoted,'3':470-promoted,'4':184+promoted,'5':56,'6':56,'8':8}
  assert p['children']==sum(p['paid_profile'].values())
  expected_hashes=PROVIDERS[pid]['program_hashes']
  assert p['program_hashes']==expected_hashes
  for name in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json','RESIDUAL-ADAPTERS.json'):
   assert hash_ok(p['artifacts'][name]) and p['artifacts'][name]==owner['source_artifacts']['providers/'+pid+'/'+name]
   if name!='CLIFFORD-REVIEW.json':assert p['artifacts'][name]==PROVIDERS[pid]['artifacts'][name]
  assert p['semantic_artifact_sha256']=={'CLIFFORD-REVIEW.json':PROVIDERS[pid]['semantic_phase_sha256']}
  assert owner['provider_phase_semantic_sha256'][pid]==invoice['provider_phase_semantic_sha256'][pid]==PROVIDERS[pid]['semantic_phase_sha256']
  for name,primitives,coefficient_work in [('forward',161308,79874),('backward',161356,79906)]:
   z=p['local'][name]
   assert z['all_dirty_helper_columns_restored'] is True and z['private_centres_and_coefficient_work_cleared'] is True
   assert z['all_exact_columns']==728 and z['dirty_helper_columns']==504
   assert z['events']==21486 and z['macros']==16291
   assert z['real_component_primitives']==primitives and z['coefficient_work_primitive_count']==coefficient_work
   assert z['pre_wrappers']==z['post_wrappers']==213
   assert 0<z['prefix_bits']<=192 and 0<Q(z['prefix_l1'])<2**192
   peak=Q(z['prefix_l1']);assert z['prefix_bits']==peak.numerator.bit_length()-peak.denominator.bit_length()+1
   assert peak==Q(88876257700 if name=='forward' else 1044730572396)
  assert p['compiler']==64*74**3
  assert p['local_adapters']==16*(max(z['macros']for z in p['local'].values())+p['children']+728+8)+64*73
  assert p['local_primitive_bound']==max(z['real_component_primitives']for z in p['local'].values())+p['local_adapters']*p['compiler']
 calls=invoice['selected_calls'];assert len(calls)==72
 assert [(c['stage'],c['replica'])for c in calls]==CALL_ORDER
 assert {(c['stage'],c['replica']) for c in calls}=={(s,r) for s in range(9) for r in range(8)}
 for c in calls:
  pid=DISPATCH[c['stage'],c['replica']]
  assert c['provider_id']==pid
  # The retained nine-stage recipe alternates its two reflected shears.
  assert c['orientation']==('forward' if c['stage']%2==0 else 'backward')
  p=invoice['providers'][pid];z=p['local'][c['orientation']]
  assert c['program_sha256']==p['program_hashes'][c['orientation']]
  for name in ('events','macros','real_component_primitives','coefficient_work_primitive_count','pre_wrappers','post_wrappers'):
   assert c[name]==z[name]
  assert c['entering_helpers']==p['entering_helpers'] and c['entrance_rank']==p['entrance_rank']
 assert invoice['selected_real_component_primitives']==sum(c['real_component_primitives'] for c in calls)
 assert invoice['selected_coefficient_work_primitive_count']==sum(c['coefficient_work_primitive_count'] for c in calls)
 assert invoice['selected_scalar_macros']==sum(c['macros'] for c in calls)==72*16291
 assert invoice['factors_per_wrapper']==144
 assert invoice['wrapper_elementary_factors_charged']==sum(c['pre_wrappers']+c['post_wrappers'] for c in calls)*144
 paid=Counter()
 for c in calls:paid.update({int(r):n for r,n in invoice['providers'][c['provider_id']]['paid_profile'].items()})
 assert dict(paid)=={int(r):n for r,n in invoice['selected_local_paid_profile'].items()}
 paid.update({3:2364,7:172,48:1668})
 assert dict(paid)=={int(r):n for r,n in owner['paid_profile'].items()}
 assert invoice['compiler']==64*74**3
 assert invoice['local_adapters']==max(p['local_adapters']for p in invoice['providers'].values())
 assert invoice['local_primitive_bound']==max(p['local_primitive_bound']for p in invoice['providers'].values())
 # Recount the retained dedicated-bank envelope independently. Its geometry
 # stays fixed, while every local primitive and wrapper comes from the actual
 # selected provider/orientation sums above.
 parent_live,parent_physical,parent_idle=11704,12218,16128
 assert owner['source_idle_children_charged']==parent_idle
 bridges,shifts=2*112*72,4*112*8;moves=2*shifts
 nonlocal_items=(4*112*8*9+2*112*8*9+2*72*504+parent_idle+9*504+bridges+shifts+moves+parent_live+parent_physical+invoice['wrapper_elementary_factors_charged'])
 outside=8*nonlocal_items+64*73
 pervertex=(invoice['selected_real_component_primitives']+bridges+shifts+moves+parent_live+(72*invoice['local_adapters']+outside)*invoice['compiler']+64*parent_physical)
 rebased=pervertex+65*(invoice['physical']-parent_physical)+(invoice['live']-parent_live)
 assert invoice['unhosted_pervertex']==pervertex and invoice['hosted_rebased_pervertex']==rebased
 used=max(pervertex,rebased)
 prior=invoice['retained_prior_overcharge']
 if prior is not None:
  assert hash_ok(prior['sha256']) and type(prior['previous_pervertex_allowance']) is int and prior['previous_pervertex_allowance']>0
  assert prior['added_complete_new_pervertex']==pervertex
  assert prior['policy']=='Retain old allowance and add entire fresh mixed recount.'
  used=max(used,prior['previous_pervertex_allowance']+pervertex)
 assert invoice['conservative_pervertex_used']==used
 finite=invoice['finite']
 assert 0<finite['physical_row_coefficient']<finite['retained_row_coefficient']==20161
 assert 0<finite['required_C0_bits']<finite['C0_exponent']==210000
 assert finite['G_exponent']==30000 and finite['E_exponent']==100000
 assert finite['halving_integer_inequality']==[5329,4608]
 assert 0<invoice['global_prefix_bits']<=invoice['charged_prefix_bits']==512
 assert invoice['row_prefix_extra']==1024
 assert invoice['global_prefix_bits']==max(z['prefix_bits']for p in invoice['providers'].values()for z in p['local'].values())+37+72+72+4
 group=2**(36*36)
 for j in range(1,37):group*=2**(2*j)-1
 stock=group*invoice['physical'];streamed_mass=group*owner['rank_mass']
 logical=group*used+64;router=invoice['compiler']*(logical+1)*(stock+1)**2
 literal=2*2**30000*stock**2+8*streamed_mass+4*stock+4+32*73
 total_mass=streamed_mass+2**100000
 assert finite['physical_stock_bits']==stock.bit_length() and finite['router_bits']==router.bit_length() and finite['literal_bits']==literal.bit_length()
 assert finite['physical_row_coefficient']==2*stock.bit_length()+9909+252+1024
 assert finite['required_C0_bits']==(32*73*total_mass*total_mass).bit_length()
 actual_checks=dict(local_primitive_bound=invoice['local_primitive_bound']<2**48,logical=logical<2**6050,router=router<2**30000,literal=literal<2**100000,mass=total_mass<2**100001,precision=32*73*total_mass*total_mass<2**210000,tape=2*total_mass+18<2**210000,row=finite['physical_row_coefficient']<20161,halving=73*73>2*48*48)
 assert actual_checks==invoice['strict_checks'] and all(actual_checks.values())
 bit_path=P/'inputs/PR543-EXPECTED.json';bit_data=bit_path.read_bytes()
 assert hashlib.sha1(b'blob '+str(len(bit_data)).encode()+b'\0'+bit_data).hexdigest()=='b61d859826246e0c3dabbe096e57ad7015eadfd5'
 bit=json.loads(bit_data)['nine']
 c=Q(bit['bit_lower']);conservative_b=Q('0.001595676281828849775453');b=Q('0.001595676284575998624254')
 expected={1:166568,2:30928,3:35756,4:13696,5:4032,6:4032,7:172,8:576,48:1668}
 H={int(r):n for r,n in owner['paid_profile'].items()};assert H==expected
 assert owner['template_sha256']==invoice['template_sha256'] and owner_sha==invoice['owner_audit_sha256']
 assert owner['live']==7168 and owner['physical']==7682 and owner['deficit']==2560
 assert owner['hosted_residuals']==36288 and owner['banked_residuals']==0
 def check_moment(side,h,m,W,lower,deficit,bad):
  assert m*W-sum(r*n for r,n in h.items())==deficit and m*m>2*max(h)**2
  rows=[]
  for z,accept in [(lower,True),(lower+Q(1,10**24),False)]:
   l,u=M.moment(h,m,W,z,bad);ll,uu=B.moment(m,W,list(h.items()),z)
   if bad:
    fl,fu=B.moment(m,W,[(1,32*m*m*sum(h.values()))],z);ll+=fl/10**16;uu+=fu/10**16
   assert (u<1 and uu<1)if accept else(l>1 and ll>1)
   rows.append(dict(side=side,surcharge=bad,endpoint=str(z),accept=accept,mercator=[str(l-1),str(u-1)],base_two=[str(ll-1),str(uu-1)]))
  return rows
 bitH={int(r):n for r,n in bit['profile'].items()}
 bit_moments=check_moment('bit',bitH,64,bit['bit']['live'],c,9984,True)
 conservative_moments=check_moment('conservative_complex',H,73,owner['live'],conservative_b,2560,True)
 assert bit['bit']['two_level_coefficient_bits']<bit['bit']['charged_two_level_coefficient_bits']==512 and bit['bit']['row_coefficient']<20161
 def outer_witness(bb):
  eta=beta=Q(1,10**24);s=min(c,(1-beta)*bb)-Q(1,10**27);assert 0<s<c and s<(1-beta)*bb
  chain=[Q(384599,10**10)];cuts=[]
  for _ in range(7):
   old=chain[-1];a=(1-s)*s+s*old;gap=min(s-a,1-a-s,1-a-s*(1-old),1-s);assert old<a<s<1-a and gap>0
   ceil=lambda x:-(-x.numerator//x.denominator);cut=max(ceil(36/gap**2),ceil(2*(4+512)/gap));assert cut*gap**2>=36 and cut*gap>=2*(4+512)
   cuts.append(dict(exponent=str(a),gap=str(gap),cutoff_log2=str(cut)));chain.append(a)
  q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin*10**18;k=Q((ticks.numerator-1)//ticks.denominator,10**18)
  bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
  outer=A.assembly(chain[-1],bb,bridge,k,eta=eta,beta=beta);assert len(outer['strict_constraints'])==47 and all(v>0 for v in outer['strict_constraints'].values())
  controls=[]
  for name,kk,ee,be in [('next_grid',k+Q(1,10**18),eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),('unit_beta',k,eta,Q(1))]:
   try:A.assembly(chain[-1],bb,bridge,kk,eta=ee,beta=be)
   except AssertionError:controls.append(name)
   else:raise AssertionError(name)
  return k,cuts,outer,controls
 conservative_k,conservative_cuts,conservative_outer,conservative_controls=outer_witness(conservative_b)
 assert conservative_k==Q('0.001593134155443237')
 # Only after every conservative supplier/admission/outer check succeeds is
 # the reviewed native exact-complex recurrence selected. Bit charge stays.
 native_moments=check_moment('complex',H,73,owner['live'],b,2560,False)
 k,cuts,outer,controls=outer_witness(b)
 assert k==Q('0.001593134158181640')
 assert M.moment(H,73,owner['live'],b,True)[0]>1
 assert M.moment(bitH,64,bit['bit']['live'],c+Q(1,10**24),False)[1]<1
 model_controls=['native_complex_endpoint_rejected_with_old_surcharge','omitting_bit_surcharge_would_fail_next_endpoint_rejection']
 moments=bit_moments+native_moments
 input_hashes={'owner_audit':owner_sha,'fresh_invoice':invoice_sha,'inputs/PR543-EXPECTED.json':sha(bit_path)}
 input_hashes.update({'engines/'+name+'.py':sha(P/'engines'/(name+'.py'))for name in ('moment','base_two_moment','outer')})
 return dict(status='PASS_FRESH_MIXED_048_ALLCOLD_NATIVE_EXACT_ASSEMBLY',kappa=str(k),kappa_decimal=dec(k),complex_lower=str(b),complex_decimal=dec(b),bit_lower=str(c),bit_decimal=dec(c),binding='complex',gain_over_pinned558_percent=dec(100*(k/Q('0.001592517889315014')-1)),complex_profile=H,provider_counts=invoice['provider_counts'],surcharge_model={'complex':False,'bit':True},conservative_complex_lower=str(conservative_b),conservative_complex_decimal=dec(conservative_b),conservative_kappa=str(conservative_k),conservative_kappa_decimal=dec(conservative_k),conservative_moments=conservative_moments,conservative_bootstrap=conservative_cuts,conservative_outer={n:str(v)for n,v in conservative_outer['strict_constraints'].items()},conservative_controls=conservative_controls,model_controls=model_controls,native_correction_gain=dec(k-conservative_k),template_sha256=owner['template_sha256'],input_sha256=input_hashes,bit_supplier=dict(pr=543,repository='eumemic/integer-mult-bounds',commit='2065fe4f72a914d907f1046603f5a36f17018535',path='research/e8-bit-r420/EXPECTED.json',git_blob_sha1='b61d859826246e0c3dabbe096e57ad7015eadfd5',replay_scope='Cited unchanged supplier; this assembly reprices its full profile and does not rebuild its bit circuit.'),moments=moments,bootstrap=cuts,outer={n:str(v)for n,v in outer['strict_constraints'].items()},controls=controls,scope='Conditional native exact-complex witness after complete conservative admission, moment and outer checks; PR559 exact-cover recurrence correction only, bit bad-residue surcharge and H1-H5 retained. Three fixed one-cold per-invocation providers composed with cited unchanged PR543 bit supplier. All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape and analytic transfer remain assumptions. No unconditional theorem or full Lean certification.')
if __name__=='__main__':
 import sys
 package,C,out=map(Path,sys.argv[1:4]);assert package.resolve()==P and not out.exists()
 owner_path=C/'audit/OWNERS-AND-PROFILE.json';invoice_path=C/'audit/PREFIX-AND-INVOICE.json'
 owner,invoice=read(owner_path),read(invoice_path)
 assert owner['template_sha256']==read(C/'hosted/HOSTED.json')['template_sha256']
 r=assemble(owner,invoice,sha(owner_path),sha(invoice_path));out.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['kappa_decimal'])
