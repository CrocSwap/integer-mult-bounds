"""Hardened all72 two-cold three-provider 0/4/8 assembly with the native exact-complex moment.

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
if not __debug__:raise RuntimeError('Assertions required; refusing optimized assembly')
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
PROVIDERS={'rank5_zero_cold': {'semantic_phase_sha256': '14a1a00276831f11ac717a2684362a573f5bc80dbdb33109668bbc0db207287a', 'promoted': 0, 'width_digest': '813e5089e8e4cb6f6b9db01d8413113e94c23d083ec01febd5bd1033891e477a', 'program_hashes': {'forward': '1fa3d0e975559db13ca2297a8d42b2c623cd431c61539fa083b1d17e54734054', 'backward': '8fab9c5f0084d81f624361a2f2720887eed9677dde92350879550c585b488720'}, 'artifacts': {'CANONICAL-WORD.json.gz': '13b9e9b9209b2fb1b07413e0c8b368ceada61d0f8390da2b96fcd6af6d5d1948', 'LOCAL-PROGRAMS.json.gz': '0ef9c90936ef4cf130f28b00e02d7e54b574eadef57be0790a55ba11f0532874', 'LOCAL-CHECKS.json': '62136f7a66207f9fca41485ce0c421f0633dfe620a35fe0611d780ab98052e7e', 'INDEPENDENT-LOCAL-REPLAY.json': '11c6edf53cdc4c77fded1199f70c9a79d7104791d7d3dccf5c024938cc7d462a', 'CLIFFORD-RECIPES.json': 'eac4d4e78125b412a813f393ea5a76ae7e6790342ff2557a6031eeabbe01b3cd', 'RESIDUAL-ADAPTERS.json': 'e4fce8ca73ad20a86711837dd6fe1efad5a335689352791a635969e4d1be4391'}, 'artifact_semantic_sha256': {'CANONICAL-WORD.json.gz': '7ea9874316b12338ff06b0027cc811067c173e74774c9927025f16f8953576d7', 'LOCAL-PROGRAMS.json.gz': 'd75027db295c474cb8c93664550bfa9d312d66c26ba270db502aee58576652da', 'LOCAL-CHECKS.json': '59cf5b25723d87bbfb948d80ad7afd7fba79ec00434bc09d817092a2724a26d2', 'INDEPENDENT-LOCAL-REPLAY.json': '14bbf39af35c57239d7c1aa621aecbdb1f78f4eb6146657b05051a649d0a5a24', 'CLIFFORD-RECIPES.json': 'eac4d4e78125b412a813f393ea5a76ae7e6790342ff2557a6031eeabbe01b3cd', 'CLIFFORD-REVIEW.json': '14a1a00276831f11ac717a2684362a573f5bc80dbdb33109668bbc0db207287a', 'RESIDUAL-ADAPTERS.json': '4908148280db7dd4c996660c380bd3675320b21223664128c4914234213bb2af'}}, 'rank5_four_cold': {'semantic_phase_sha256': 'f65f37d3e3c231baaae5f7aff2ed52be42943d8310ba151137bb5568412528c9', 'promoted': 4, 'width_digest': 'da39a4f991710c97ef626f032f034c168794c3d90be509a3c5c1856e333a5324', 'program_hashes': {'forward': '1157d3f1056ff868df6d69cbbb9f4d0c6f915381e9e891b6481aadcab755633f', 'backward': '2dfebcaa39568c2b226123650d7b8ed566f7f8f429769086794d6f3fb58d1540'}, 'artifacts': {'CANONICAL-WORD.json.gz': '273d6219890b87b9000dcb940f4e0f0484af6750b35f0fc8aa21501285f64ded', 'LOCAL-PROGRAMS.json.gz': '8936c2313e6606a8d6a8172d64e06fbade307a7a70347c9d1bb4667570c6539f', 'LOCAL-CHECKS.json': '29a5faae75c20c2baa299740bf979e8622962a4726ed0a48c3d62ba8f342aee3', 'INDEPENDENT-LOCAL-REPLAY.json': '9cf2407e5133c2d5cc90396c79f8b01c258532d1f2c7cd9d8c6cffebb64e0460', 'CLIFFORD-RECIPES.json': '7625bcc9a939e5ca96034e96a46fda66b23a08b4049bd4b2cb1eb594935d4bd3', 'RESIDUAL-ADAPTERS.json': 'ddeab3b37b16eca2c90c2a8d4afa124e86b611319c8f0a9632bfefbaa7667a0e'}, 'artifact_semantic_sha256': {'CANONICAL-WORD.json.gz': '689a7a7e343b48cd40ca1ea7cca61e386fe46f94acdd5af6544101ee4d5d95ab', 'LOCAL-PROGRAMS.json.gz': '0a2414ae68d186a257caf8a5f8807f2b62bd1d02fca760d77da18414d17f06d1', 'LOCAL-CHECKS.json': '7894273957cf4f38ec150951c3e1e1cec48ca0174e266f217be7a2ccad1f43a0', 'INDEPENDENT-LOCAL-REPLAY.json': '2a8022cc5169213a22b49b316c6f91b44eaab65e93a77fbe5d230da7e1e72a88', 'CLIFFORD-RECIPES.json': '7625bcc9a939e5ca96034e96a46fda66b23a08b4049bd4b2cb1eb594935d4bd3', 'CLIFFORD-REVIEW.json': 'f65f37d3e3c231baaae5f7aff2ed52be42943d8310ba151137bb5568412528c9', 'RESIDUAL-ADAPTERS.json': '277af9a2e6c19185539c6ded7fd1f4674fa47781d53d4de60ccb41da5826b1ac'}}, 'rank5_eight_cold': {'semantic_phase_sha256': '57e10e37fdc346a609fbeca0f27fbfda8e4d05307a73348f170396a3e1c6078e', 'promoted': 8, 'width_digest': 'c494510893c42c1341e05769fca447645e119300132faf5b83a4192d5eb0833b', 'program_hashes': {'forward': 'dae271b3d6172075ebcb112e1bb2d2f40ace4bde735d10a9496652a5030f1ef7', 'backward': 'f1640f2c35e3ca74bc9ecb29f619eb9ee29361510e9d16172e7441ff4f381da3'}, 'artifacts': {'CANONICAL-WORD.json.gz': 'df2987d922a6df1fe7987d507de814881b7c847a8fdd91618257c465a338db0a', 'LOCAL-PROGRAMS.json.gz': 'c9564c0d800869a63e6ab009c0c9a6e5ad5e288a02fbffb7689c2613a9351058', 'LOCAL-CHECKS.json': '6454bfa447998a9e11131603ca83c5a57b1619958c266f1b85ff1fd8134cbf39', 'INDEPENDENT-LOCAL-REPLAY.json': '373c2530acdf7bb63cecebb993ff5fce487627ec9883580358ca642154f7593a', 'CLIFFORD-RECIPES.json': '34dd3b524399da7c365052ec369c40519b217cb3160c8d5ab2b50bba268d59a1', 'RESIDUAL-ADAPTERS.json': 'baafef737acc16dafbe1150896feb16744f3d669fa123bb2bff19ecc4e71b275'}, 'artifact_semantic_sha256': {'CANONICAL-WORD.json.gz': 'a39da1c3bf9cd5fe9eb8756c96cd4d6ba316fe33975b7025deb46959080ef773', 'LOCAL-PROGRAMS.json.gz': '66fa6a2706b58202ba65c04e47a99c8af236cb3557807dd3f2aae35f834a2897', 'LOCAL-CHECKS.json': '139bc5aae175f815bf67f24b987fff5086c364d36aec47c78caea709b02146ed', 'INDEPENDENT-LOCAL-REPLAY.json': 'ad4dded5594c09b368a65372feff2750805a2bf4e6c467f31b556c8859876513', 'CLIFFORD-RECIPES.json': '34dd3b524399da7c365052ec369c40519b217cb3160c8d5ab2b50bba268d59a1', 'CLIFFORD-REVIEW.json': '57e10e37fdc346a609fbeca0f27fbfda8e4d05307a73348f170396a3e1c6078e', 'RESIDUAL-ADAPTERS.json': '538c4a1fd46a44575c17d30586fe773d50b5f857be8c81aed37ffcbbec3a995c'}}}
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
 assert owner['actual_73column_sigmas']==2976 and owner['cross_replica_helper_roles']==29259
 assert owner['explicit_idle_remainder_children']==4168
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
  assert p['entering_helpers']==214 and p['entrance_rank']==382+promoted
  assert p['width_inventory']=={str(r):n for r,n in {4:promoted,5:56-promoted,8:158,9:290}.items()if n}
  assert all(type(w) is int and 0<w<=9 for w in p['widths'])
  assert Counter(p['widths'])==Counter({int(r):n for r,n in p['width_inventory'].items()})
  assert sum(p['widths'])==9*504-p['entrance_rank'] and len(p['widths'])==504
  assert digest(p['widths'])==PROVIDERS[pid]['width_digest'] and p['widths'][270]==p['widths'][294]==8
  assert p['paid_profile']=={'1':2302+2*promoted,'2':444-2*promoted,'3':468-promoted,'4':184+promoted,'5':56,'6':56,'8':8}
  assert p['children']==sum(p['paid_profile'].values())
  expected_hashes=PROVIDERS[pid]['program_hashes']
  assert p['program_hashes']==expected_hashes
  for name in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json','RESIDUAL-ADAPTERS.json'):
   assert hash_ok(p['artifacts'][name]) and p['artifacts'][name]==owner['source_artifacts']['providers/'+pid+'/'+name]
   if name in ('LOCAL-CHECKS.json','CLIFFORD-RECIPES.json','RESIDUAL-ADAPTERS.json'):assert p['artifacts'][name]==PROVIDERS[pid]['artifacts'][name]
  assert p['semantic_artifact_sha256']==PROVIDERS[pid]['artifact_semantic_sha256']
  assert owner['provider_artifact_semantic_sha256'][pid]==p['semantic_artifact_sha256']
  assert owner['provider_phase_semantic_sha256'][pid]==invoice['provider_phase_semantic_sha256'][pid]==PROVIDERS[pid]['semantic_phase_sha256']
  for name,primitives,coefficient_work in [('forward',161308,79874),('backward',161356,79906)]:
   z=p['local'][name]
   assert z['all_dirty_helper_columns_restored'] is True and z['private_centres_and_coefficient_work_cleared'] is True
   assert z['all_exact_columns']==728 and z['dirty_helper_columns']==504
   assert z['events']==21489 and z['macros']==16292
   assert z['real_component_primitives']==primitives and z['coefficient_work_primitive_count']==coefficient_work
   assert z['pre_wrappers']==z['post_wrappers']==214
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
 assert invoice['selected_scalar_macros']==sum(c['macros'] for c in calls)==72*16292
 assert invoice['factors_per_wrapper']==144
 assert invoice['wrapper_elementary_factors_charged']==sum(c['pre_wrappers']+c['post_wrappers'] for c in calls)*144
 paid=Counter()
 for c in calls:paid.update({int(r):n for r,n in invoice['providers'][c['provider_id']]['paid_profile'].items()})
 assert dict(paid)=={int(r):n for r,n in invoice['selected_local_paid_profile'].items()}
 paid.update({3:2356,7:136,12:1,48:1675})
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
 c=Q(bit['bit_lower']);conservative_b=Q('0.001596211544128909961969');b=Q('0.001596211546877366844000')
 expected={1:166640,2:31072,3:35604,4:13696,5:4032,6:4032,7:136,8:576,12:1,48:1675}
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
 assert conservative_k==Q('0.001593667713327391')
 # Only after every conservative supplier/admission/outer check succeeds is
 # the reviewed native exact-complex recurrence selected. Bit charge stays.
 native_moments=check_moment('complex',H,73,owner['live'],b,2560,False)
 k,cuts,outer,controls=outer_witness(b)
 assert k==Q('0.001593667716067094')
 assert k>Q('0.001593134158181640')
 assert M.moment(H,73,owner['live'],b,True)[0]>1
 assert M.moment(bitH,64,bit['bit']['live'],c+Q(1,10**24),False)[1]<1
 model_controls=['native_complex_endpoint_rejected_with_old_surcharge','omitting_bit_surcharge_would_fail_next_endpoint_rejection']
 moments=bit_moments+native_moments
 input_hashes={'owner_audit':owner_sha,'fresh_invoice':invoice_sha,'inputs/PR543-EXPECTED.json':sha(bit_path)}
 input_hashes.update({'engines/'+name+'.py':sha(P/'engines'/(name+'.py'))for name in ('moment','base_two_moment','outer')})
 return dict(status='PASS_FRESH_MIXED_048_DOUBLECOLD_NATIVE_EXACT_ASSEMBLY',kappa=str(k),kappa_decimal=dec(k),complex_lower=str(b),complex_decimal=dec(b),bit_lower=str(c),bit_decimal=dec(c),binding='complex',gain_over_pinned558_percent=dec(100*(k/Q('0.001592517889315014')-1)),gain_over_pr564_percent=dec(100*(k/Q('0.001593134158181640')-1)),complex_profile=H,provider_counts=invoice['provider_counts'],surcharge_model={'complex':False,'bit':True},conservative_complex_lower=str(conservative_b),conservative_complex_decimal=dec(conservative_b),conservative_kappa=str(conservative_k),conservative_kappa_decimal=dec(conservative_k),conservative_moments=conservative_moments,conservative_bootstrap=conservative_cuts,conservative_outer={n:str(v)for n,v in conservative_outer['strict_constraints'].items()},conservative_controls=conservative_controls,model_controls=model_controls,native_correction_gain=dec(k-conservative_k),template_sha256=owner['template_sha256'],input_sha256=input_hashes,bit_supplier=dict(pr=543,repository='eumemic/integer-mult-bounds',commit='2065fe4f72a914d907f1046603f5a36f17018535',path='research/e8-bit-r420/EXPECTED.json',git_blob_sha1='b61d859826246e0c3dabbe096e57ad7015eadfd5',replay_scope='Cited unchanged supplier; this assembly reprices its full profile and does not rebuild its bit circuit.'),moments=moments,bootstrap=cuts,outer={n:str(v)for n,v in outer['strict_constraints'].items()},controls=controls,scope='Conditional native exact-complex witness after complete conservative admission, moment and outer checks; PR559 exact-cover recurrence correction only, bit bad-residue surcharge and H1-H5 retained. Three fixed two-cold per-invocation providers composed with cited unchanged PR543 bit supplier. All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape and analytic transfer remain assumptions. No unconditional theorem or full Lean certification.')
if __name__=='__main__':
 import sys
 package,C,out=map(Path,sys.argv[1:4]);assert package.resolve()==P and not out.exists()
 owner_path=C/'audit/OWNERS-AND-PROFILE.json';invoice_path=C/'audit/PREFIX-AND-INVOICE.json'
 owner,invoice=read(owner_path),read(invoice_path)
 assert owner['template_sha256']==read(C/'hosted/HOSTED.json')['template_sha256']
 r=assemble(owner,invoice,sha(owner_path),sha(invoice_path));out.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['kappa_decimal'])
