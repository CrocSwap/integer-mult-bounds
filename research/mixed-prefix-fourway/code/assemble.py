# Adapted PR572: all four verified provider contracts and literal call selection frozen.
# Adapted PR569 assembly with immutable composed-provider contracts and fresh literal57-call owner fixtures.
"""Hardened 57 width-seven and 15 plain eight-cold provider assembly with the native exact-complex moment.

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
import argparse,json,hashlib,importlib.util,os,sys
from collections import Counter
assert __debug__, 'Assertions required'
P=Path(sys.argv[1] if __name__=='__main__' else os.environ['GAIN_PR564_SOURCE']).resolve()
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hash_ok=lambda x:isinstance(x,str) and len(x)==64 and all(t in '0123456789abcdef'for t in x)
digest=lambda x:hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
def load(n):
 s=importlib.util.spec_from_file_location(n,P/'engines'/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M,B,A=[load(n)for n in ('moment','base_two_moment','outer')]
def dec(x):
 with localcontext()as ctx:ctx.prec=70;return str(Decimal(x.numerator)/Decimal(x.denominator))
PROVIDERS={'plain_four': {'artifact_semantic_sha256': {'CANONICAL-WORD.json.gz': '12c85e9ddef0ff565207b6ecc198e9f154423736b14d62567b2f9c1545dc6539', 'LOCAL-PROGRAMS.json.gz': 'a2c3bd0e38b598eea185d2b56b257815802b739cf6fcd2af769817abc31ddeb4', 'LOCAL-CHECKS.json': '6220c00ac6b561c2d8c794aeb48b24c7420042cbc4e15a9ab541181eb4aff887', 'INDEPENDENT-LOCAL-REPLAY.json': 'f62751047d19673d4b209f7b2999e875074f73e36f73adceeb6fd17619df8f4b', 'CLIFFORD-RECIPES.json': '9f7b1d5bfcd937fb25778402cda7e71ccc1ae0e0e7f2b65a380dc231ad6f36fa', 'CLIFFORD-REVIEW.json': '66e70f02def7215e9d56e1346b72376b9374c9920626a0e9909564b058c5e976', 'RESIDUAL-ADAPTERS.json': '538c4a1fd46a44575c17d30586fe773d50b5f857be8c81aed37ffcbbec3a995c'}, 'semantic_phase_sha256': '66e70f02def7215e9d56e1346b72376b9374c9920626a0e9909564b058c5e976', 'artifacts': {'LOCAL-CHECKS.json': 'a66926b91a1d383b056e58c9c72024d228e710dae7c28af8514f1a2761e31f2a', 'CLIFFORD-RECIPES.json': '9f7b1d5bfcd937fb25778402cda7e71ccc1ae0e0e7f2b65a380dc231ad6f36fa', 'RESIDUAL-ADAPTERS.json': 'baafef737acc16dafbe1150896feb16744f3d669fa123bb2bff19ecc4e71b275'}}, 'plain_eight': {'artifact_semantic_sha256': {'CANONICAL-WORD.json.gz': '4bd83a3946bf7f5f4d0c1fee1ce5cc23749fbe1d1c2e39b94b749eac93f44e13', 'LOCAL-PROGRAMS.json.gz': 'f6c3816f94d7a3140550fa01001d6fa2b86ad94011588ccc2596202baa7ddd0e', 'LOCAL-CHECKS.json': 'becd709ef7328b5e45036c3691499028c1f03471cdea9b82e3b513a3d2452347', 'INDEPENDENT-LOCAL-REPLAY.json': '4c404ae021e507934ab5f0f2a39ceb4260fe2faa0e7f6ab0b59cb2423baf591b', 'CLIFFORD-RECIPES.json': 'b32e904cac5f4ac2b9a80a50dfd112ced1e44a2eab1ee24149c501f0d6979748', 'CLIFFORD-REVIEW.json': 'b877cf8e80b1940512d272d027871deca0ca8a876db23751dfc4844272b2ad2a', 'RESIDUAL-ADAPTERS.json': '538c4a1fd46a44575c17d30586fe773d50b5f857be8c81aed37ffcbbec3a995c'}, 'semantic_phase_sha256': 'b877cf8e80b1940512d272d027871deca0ca8a876db23751dfc4844272b2ad2a', 'artifacts': {'LOCAL-CHECKS.json': '57b8a93866ebfb23b81225264229742a980ab60b7dd6ff1df014ba43c8d0ead8', 'CLIFFORD-RECIPES.json': 'b32e904cac5f4ac2b9a80a50dfd112ced1e44a2eab1ee24149c501f0d6979748', 'RESIDUAL-ADAPTERS.json': 'baafef737acc16dafbe1150896feb16744f3d669fa123bb2bff19ecc4e71b275'}}, 'width7_eight': {'artifact_semantic_sha256': {'CANONICAL-WORD.json.gz': '7dd0eb8f3100a1b444cf64c78cf542731993cc7b59a875c9f4fc914aa9d9f02a', 'LOCAL-PROGRAMS.json.gz': 'e9c9e720f4b199c3e32175f4043333a90f30a57770385f9906a83bfac7a4bf30', 'LOCAL-CHECKS.json': '9374807e98eec6ec5bab0a42771d35e479f0741610c44bba6a6be9c10f3ffbdf', 'INDEPENDENT-LOCAL-REPLAY.json': '6bb8841989f5d185df36d2b42757b2f3e778a1fea5572d7b41ff87c172b429aa', 'CLIFFORD-RECIPES.json': 'd6dd182cb81d8b962b1ba6e6a04352309c38de894fa601634781220f6115ab8a', 'CLIFFORD-REVIEW.json': '7209672a038afa8ea8a17b8cc4a9be3f1b5df93560826b17fba4dae0212b35d9', 'RESIDUAL-ADAPTERS.json': '68cfb6a4924ca512fdf9d678618b7dfa420e90ec0e5b559e20358cd5a2bfe602'}, 'semantic_phase_sha256': '7209672a038afa8ea8a17b8cc4a9be3f1b5df93560826b17fba4dae0212b35d9', 'artifacts': {'LOCAL-CHECKS.json': '43c49979bcf3f29f575c10022c3052bfb9846860b13227b3d08cf90a37c382a1', 'CLIFFORD-RECIPES.json': 'd6dd182cb81d8b962b1ba6e6a04352309c38de894fa601634781220f6115ab8a', 'RESIDUAL-ADAPTERS.json': 'f2f7587e065fc14a5c6de4529a038b2dd0eb9aae820bfe928dca3e8d29561978'}}, 'prefix_width7_eight': {'artifact_semantic_sha256': {'CANONICAL-WORD.json.gz': '72310df524313ca91e7dd0de0c1a2772a4437a79b5f8d34222234c35159b495b', 'LOCAL-PROGRAMS.json.gz': 'a946b6da61abc8cd9443f4fd4ea591e6462070fb5c7ad6ab521d27ebdf6c9809', 'LOCAL-CHECKS.json': '943e6ef6c31405fd033192406856f444e2d9058e1b03e24532540751b9f7ece8', 'INDEPENDENT-LOCAL-REPLAY.json': '53680341eb55288af90cbf346ed94ac930ec2c8d5df622e335a1757c509172de', 'CLIFFORD-RECIPES.json': '3323144380012a59c59e56348dd56d17da0f93e7783415efdaabe6fd5d3edadc', 'CLIFFORD-REVIEW.json': '695a862d36f9912c4b090b3e0d3b2682308dfe5759fb9fbea21ffbb156759631', 'RESIDUAL-ADAPTERS.json': '608eca0714d2bab99178c3ae3cb9da3eaedd955bcc82eb878128e7ce8d5ede71'}, 'semantic_phase_sha256': '695a862d36f9912c4b090b3e0d3b2682308dfe5759fb9fbea21ffbb156759631', 'artifacts': {'LOCAL-CHECKS.json': '66a2f5d82e13179626dec71bb5a4b49bcae32f91e4812fa4056fe1f3c3ecadcb', 'CLIFFORD-RECIPES.json': '3323144380012a59c59e56348dd56d17da0f93e7783415efdaabe6fd5d3edadc', 'RESIDUAL-ADAPTERS.json': 'b55f994f7cad5b0be48084362f1461f7587689eb35ad4bb253de138792b1c526'}}}
CONTRACT_PATH=Path(__file__).resolve().parents[1]/'CONTRACTS.json'
assert sha(CONTRACT_PATH)=='8833f4746fd3bfb3dd6da79fee92180d4e30226fc9e3923f3ba16ad6aeb88957'
CONTRACTS=read(CONTRACT_PATH)
DISPATCH={(0, 0): 'width7_eight', (0, 1): 'width7_eight', (1, 0): 'width7_eight', (0, 2): 'width7_eight', (1, 1): 'width7_eight', (2, 0): 'width7_eight', (0, 3): 'width7_eight', (1, 2): 'width7_eight', (2, 1): 'plain_eight', (3, 0): 'prefix_width7_eight', (0, 4): 'prefix_width7_eight', (1, 3): 'prefix_width7_eight', (2, 2): 'prefix_width7_eight', (3, 1): 'plain_eight', (4, 0): 'prefix_width7_eight', (0, 5): 'prefix_width7_eight', (1, 4): 'prefix_width7_eight', (2, 3): 'prefix_width7_eight', (3, 2): 'prefix_width7_eight', (4, 1): 'prefix_width7_eight', (5, 0): 'prefix_width7_eight', (0, 6): 'prefix_width7_eight', (1, 5): 'prefix_width7_eight', (2, 4): 'prefix_width7_eight', (3, 3): 'prefix_width7_eight', (4, 2): 'prefix_width7_eight', (5, 1): 'prefix_width7_eight', (0, 7): 'prefix_width7_eight', (6, 0): 'prefix_width7_eight', (1, 6): 'prefix_width7_eight', (2, 5): 'prefix_width7_eight', (3, 4): 'prefix_width7_eight', (4, 3): 'prefix_width7_eight', (5, 2): 'prefix_width7_eight', (6, 1): 'prefix_width7_eight', (1, 7): 'prefix_width7_eight', (7, 0): 'prefix_width7_eight', (2, 6): 'prefix_width7_eight', (3, 5): 'prefix_width7_eight', (4, 4): 'prefix_width7_eight', (5, 3): 'plain_four', (6, 2): 'plain_eight', (7, 1): 'plain_eight', (2, 7): 'prefix_width7_eight', (8, 0): 'prefix_width7_eight', (3, 6): 'prefix_width7_eight', (4, 5): 'plain_four', (5, 4): 'prefix_width7_eight', (6, 3): 'prefix_width7_eight', (7, 2): 'prefix_width7_eight', (8, 1): 'prefix_width7_eight', (3, 7): 'prefix_width7_eight', (4, 6): 'prefix_width7_eight', (5, 5): 'prefix_width7_eight', (6, 4): 'prefix_width7_eight', (7, 3): 'prefix_width7_eight', (8, 2): 'prefix_width7_eight', (4, 7): 'prefix_width7_eight', (5, 6): 'prefix_width7_eight', (6, 5): 'prefix_width7_eight', (7, 4): 'prefix_width7_eight', (8, 3): 'prefix_width7_eight', (5, 7): 'prefix_width7_eight', (6, 6): 'prefix_width7_eight', (7, 5): 'prefix_width7_eight', (8, 4): 'prefix_width7_eight', (6, 7): 'prefix_width7_eight', (7, 6): 'prefix_width7_eight', (8, 5): 'prefix_width7_eight', (7, 7): 'prefix_width7_eight', (8, 6): 'prefix_width7_eight', (8, 7): 'prefix_width7_eight'}
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
 assert invoice['provider_counts']=={'width7_eight': 8, 'plain_eight': 4, 'prefix_width7_eight': 58, 'plain_four': 2}
 assert owner['all_live_owners_per_call_distinct'] is True
 assert owner['owners_per_call']==728 and owner['actual_helper_owner_charts']==36288
 assert owner['rank_mass']==520704
 assert owner['actual_73column_sigmas']==6222 and owner['cross_replica_helper_roles']==28407
 assert owner['explicit_idle_remainder_children']==3038
 assert invoice['complete_invocation_sweeps']==invoice['bridge_sweeps']==72
 assert invoice['live']==owner['live'] and invoice['physical']==owner['physical']
 assert invoice['helpers']==504 and invoice['centres']==8
 assert invoice['physical_stock_identity']==dict(data_and_owner_families=7168,local_helpers=504,private_centres=8,coefficient_work=2)
 assert sum(invoice['physical_stock_identity'].values())==invoice['physical']
 assert invoice['controller_audit_sha256']==owner['controller_audit_sha256']
 for pid,p in invoice['providers'].items():
  # Complete frozen numerical contract from the independently admitted provider;
  # no scalar, prefix, width, orientation, profile or cost field is projected out.
  assert {k:v for k,v in p.items()if k!='artifacts'}==CONTRACTS[pid]
  for name in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json','RESIDUAL-ADAPTERS.json'):
   assert hash_ok(p['artifacts'][name]) and p['artifacts'][name]==owner['source_artifacts']['providers/'+pid+'/'+name]
   if name in PROVIDERS[pid]['artifacts']:assert p['artifacts'][name]==PROVIDERS[pid]['artifacts'][name]
  assert p['semantic_artifact_sha256']==PROVIDERS[pid]['artifact_semantic_sha256']
  assert owner['provider_artifact_semantic_sha256'][pid]==p['semantic_artifact_sha256']
  assert owner['provider_phase_semantic_sha256'][pid]==invoice['provider_phase_semantic_sha256'][pid]==PROVIDERS[pid]['semantic_phase_sha256']
  for z in p['local'].values():
   assert z['all_dirty_helper_columns_restored']is True and z['private_centres_and_coefficient_work_cleared']is True
   assert z['all_exact_columns']==728 and z['dirty_helper_columns']==504
   assert 0<z['prefix_bits']<=192 and 0<Q(z['prefix_l1'])<2**192
   peak=Q(z['prefix_l1']);assert z['prefix_bits']==peak.numerator.bit_length()-peak.denominator.bit_length()+1
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
 assert invoice['selected_scalar_macros']==sum(c['macros'] for c in calls)==sum(CONTRACTS[c['provider_id']]['local'][c['orientation']]['macros']for c in calls)
 assert invoice['factors_per_wrapper']==144
 assert invoice['wrapper_elementary_factors_charged']==sum(c['pre_wrappers']+c['post_wrappers'] for c in calls)*144
 paid=Counter()
 for c in calls:paid.update({int(r):n for r,n in invoice['providers'][c['provider_id']]['paid_profile'].items()})
 assert dict(paid)=={int(r):n for r,n in invoice['selected_local_paid_profile'].items()}
 paid.update({2: 27, 3: 1191, 7: 3, 48: 1817})
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
 c=Q(bit['bit_lower']);conservative_b=Q('1603415350469063711949/1000000000000000000000000');b=Q('320683070652636948893/200000000000000000000000')
 expected={1: 169296, 2: 41043, 3: 25943, 4: 13824, 5: 4032, 6: 4032, 7: 3, 8: 576, 48: 1817}
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
 assert conservative_k==Q('160084852536971/100000000000000000')
 # Only after every conservative supplier/admission/outer check succeeds is
 # the reviewed native exact-complex recurrence selected. Bit charge stays.
 native_moments=check_moment('complex',H,73,owner['live'],b,2560,False)
 k,cuts,outer,controls=outer_witness(b)
 assert k==Q('400212132038723/250000000000000000')
 assert M.moment(H,73,owner['live'],b,True)[0]>1
 assert M.moment(bitH,64,bit['bit']['live'],c+Q(1,10**24),False)[1]<1
 model_controls=['native_complex_endpoint_rejected_with_old_surcharge','omitting_bit_surcharge_would_fail_next_endpoint_rejection']
 moments=bit_moments+native_moments
 input_hashes={'owner_audit':owner_sha,'fresh_invoice':invoice_sha,'inputs/PR543-EXPECTED.json':sha(bit_path)}
 input_hashes.update({'engines/'+name+'.py':sha(P/'engines'/(name+'.py'))for name in ('moment','base_two_moment','outer')})
 return dict(status='PASS_FRESH_MIXED_048_ALLCOLD_NATIVE_EXACT_ASSEMBLY',kappa=str(k),kappa_decimal=dec(k),complex_lower=str(b),complex_decimal=dec(b),bit_lower=str(c),bit_decimal=dec(c),binding='complex',gain_over_pinned564_percent=dec(100*(k/Q('0.001593134158181640')-1)),complex_profile=H,provider_counts=invoice['provider_counts'],surcharge_model={'complex':False,'bit':True},conservative_complex_lower=str(conservative_b),conservative_complex_decimal=dec(conservative_b),conservative_kappa=str(conservative_k),conservative_kappa_decimal=dec(conservative_k),conservative_moments=conservative_moments,conservative_bootstrap=conservative_cuts,conservative_outer={n:str(v)for n,v in conservative_outer['strict_constraints'].items()},conservative_controls=conservative_controls,model_controls=model_controls,native_correction_gain=dec(k-conservative_k),template_sha256=owner['template_sha256'],input_sha256=input_hashes,bit_supplier=dict(pr=543,repository='eumemic/integer-mult-bounds',commit='2065fe4f72a914d907f1046603f5a36f17018535',path='research/e8-bit-r420/EXPECTED.json',git_blob_sha1='b61d859826246e0c3dabbe096e57ad7015eadfd5',replay_scope='Cited unchanged supplier; this assembly reprices its full profile and does not rebuild its bit circuit.'),moments=moments,bootstrap=cuts,outer={n:str(v)for n,v in outer['strict_constraints'].items()},controls=controls,scope='Conditional native exact-complex witness after complete conservative admission, moment and outer checks; PR559 exact-cover recurrence correction only, bit bad-residue surcharge and H1-H5 retained. Four fixed plain/width-seven/joint-prefix per-invocation providers composed with cited unchanged PR543 bit supplier. All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape and analytic transfer remain assumptions. No unconditional theorem or full Lean certification.')
if __name__=='__main__':
 import sys
 package,C,out=map(Path,sys.argv[1:4]);assert package.resolve()==P and not out.exists()
 owner_path=C/'audit/OWNERS-AND-PROFILE.json';invoice_path=C/'audit/PREFIX-AND-INVOICE.json'
 owner,invoice=read(owner_path),read(invoice_path)
 assert owner['template_sha256']==read(C/'hosted/HOSTED.json')['template_sha256']
 r=assemble(owner,invoice,sha(owner_path),sha(invoice_path));out.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['kappa_decimal'])
