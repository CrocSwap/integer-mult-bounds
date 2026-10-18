"""Hardened 63 width-seven (#571 prefix word) and 9 plain eight-cold (#568 E8) provider assembly with the native exact-complex moment.

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
from witness import DISPATCH,CALL_ORDER,COUNTS,PIDS,X,DISCOVER,pin


def assemble(owner,invoice,owner_sha,invoice_sha):
 # These are admission receipts, not optional collections of successful rows.
 # Require both orientations and every finite check before pricing anything.
 assert owner['status']=='PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE'
 assert invoice['status']=='PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE'
 assert all(hash_ok(x)for x in (owner_sha,invoice_sha,owner['template_sha256'],owner['controller_audit_sha256'],invoice['parent_template_sha256']))
 checks={'local_primitive_bound','logical','router','literal','mass','precision','tape','row','halving'}
 assert set(invoice['strict_checks'])==checks
 assert all(invoice['strict_checks'][name] is True for name in checks)
 assert set(invoice['providers'])==set(PIDS)
 assert invoice['provider_counts']==COUNTS
 assert owner['all_live_owners_per_call_distinct'] is True
 assert owner['owners_per_call']==728 and owner['actual_helper_owner_charts']==owner['hosted_residuals']==pin('expected.hosted_residuals',owner['hosted_residuals'])
 pin('expected.rank_mass',owner['rank_mass'])
 pin('expected.actual_73column_sigmas',owner['actual_73column_sigmas']);pin('expected.cross_replica_helper_roles',owner['cross_replica_helper_roles'])
 pin('expected.idle_remainders',owner['explicit_idle_remainder_children'])
 assert invoice['complete_invocation_sweeps']==invoice['bridge_sweeps']==72
 assert invoice['live']==owner['live'] and invoice['physical']==owner['physical']
 assert invoice['helpers']==504 and invoice['centres']==8
 assert invoice['physical_stock_identity']==dict(data_and_owner_families=7168,local_helpers=504,private_centres=8,coefficient_work=2)
 assert sum(invoice['physical_stock_identity'].values())==invoice['physical']
 assert invoice['controller_audit_sha256']==owner['controller_audit_sha256']
 for pid,p in invoice['providers'].items():
  assert set(p['local'])=={'forward','backward'}
  assert p['helpers']==504 and p['centres']==8 and p['n']==728 and p['v']==112 and p['h']==9
  K='providers.'+pid+'.';pin(K+'entering',p['entering_helpers']);pin(K+'entrance',p['entrance_rank'])
  pin(K+'inventory',p['width_inventory'])
  assert all(type(w) is int and 0<w<=9 for w in p['widths'])
  assert Counter(p['widths'])==Counter({int(r):n for r,n in p['width_inventory'].items()})
  assert sum(p['widths'])==9*504-p['entrance_rank']-p['terminal_codimension'] and len(p['widths'])==504   # HPE: widths |final|-|start|
  pin(K+'width_digest',digest(p['widths']));assert all(p['widths'][h]==8 for h in (270,282,294,306))
  pin(K+'expected_profile',p['paid_profile'])
  assert p['children']==sum(p['paid_profile'].values())
  pin(K+'program_hashes',p['program_hashes'])
  for name in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json','RESIDUAL-ADAPTERS.json'):
   assert hash_ok(p['artifacts'][name]) and p['artifacts'][name]==owner['source_artifacts']['providers/'+pid+'/'+name]
   if name in ('LOCAL-CHECKS.json','CLIFFORD-RECIPES.json','RESIDUAL-ADAPTERS.json'):pin(K+'artifacts.'+name,p['artifacts'][name])
  pin(K+'artifact_semantic_sha256',p['semantic_artifact_sha256'])
  pin(K+'complete_contract',{k:v for k,v in p.items()if k!='artifacts'})
  assert owner['provider_artifact_semantic_sha256'][pid]==p['semantic_artifact_sha256']
  pin(K+'semantic_phase_sha256',p['semantic_artifact_sha256']['CLIFFORD-REVIEW.json'])
  assert owner['provider_phase_semantic_sha256'][pid]==invoice['provider_phase_semantic_sha256'][pid]==p['semantic_artifact_sha256']['CLIFFORD-REVIEW.json']
  for name in ('forward','backward'):
   z=p['local'][name];pinned=pin(K+'expected_local.'+name,{k:z[k]for k in('events','macros','real_component_primitives','prefix_l1','coefficient_work_primitive_count')});primitives=pinned['real_component_primitives'];coefficient_work=pinned['coefficient_work_primitive_count']
   assert z['all_dirty_helper_columns_restored'] is True and z['private_centres_and_coefficient_work_cleared'] is True
   assert z['all_exact_columns']==728 and z['dirty_helper_columns']==504
   assert z['events']==pinned['events'] and z['macros']==pinned['macros']
   assert z['real_component_primitives']==primitives and z['coefficient_work_primitive_count']==coefficient_work
   assert z['pre_wrappers']==z['post_wrappers']==p['entering_helpers'];pin(K+'wrappers',z['pre_wrappers'])
   assert 0<z['prefix_bits']<=192 and 0<Q(z['prefix_l1'])<2**192
   peak=Q(z['prefix_l1']);assert z['prefix_bits']==peak.numerator.bit_length()-peak.denominator.bit_length()+1
   assert peak==Q(pinned['prefix_l1'])
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
 assert invoice['selected_scalar_macros']==sum(c['macros'] for c in calls)==sum(invoice['providers'][c['provider_id']]['local'][c['orientation']]['macros'] for c in calls)
 assert invoice['factors_per_wrapper']==144
 assert invoice['wrapper_elementary_factors_charged']==sum(c['pre_wrappers']+c['post_wrappers'] for c in calls)*144
 paid=Counter()
 for c in calls:paid.update({int(r):n for r,n in invoice['providers'][c['provider_id']]['paid_profile'].items()})
 assert dict(paid)=={int(r):n for r,n in invoice['selected_local_paid_profile'].items()}
 idle=Counter({int(r):n for r,n in owner['paid_profile'].items()});idle.subtract(paid);assert all(n>=0 for n in idle.values())
 idle=+idle;assert sum(idle.values())==owner['explicit_idle_remainder_children']
 pin('expected.idle_remainder_profile',{str(r):n for r,n in sorted(idle.items())})
 paid.update(idle)
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
 c=Q(bit['bit_lower'])
 H={int(r):n for r,n in owner['paid_profile'].items()};pin('expected.global_profile',owner['paid_profile'])
 # Claimed lower endpoints come from the spec; discovery derives them with the same certified moment engine.
 # Either way they are verified below (accepted at b, rejected at b+1e-24).
 if DISCOVER:b=Q(M.certify(H,73,owner['live'],False)['lower']);conservative_b=Q(M.certify(H,73,owner['live'],True)['lower'])
 else:b=Q(X['complex_lower']);conservative_b=Q(X['conservative_complex_lower'])
 assert owner['template_sha256']==invoice['template_sha256'] and owner_sha==invoice['owner_audit_sha256']
 pin('expected.live',owner['live']);pin('expected.physical',owner['physical']);assert owner['deficit']==2560
 assert owner['banked_residuals']==0
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
 pin('expected.conservative_kappa_decimal',dec(conservative_k))
 # Only after every conservative supplier/admission/outer check succeeds is
 # the reviewed native exact-complex recurrence selected. Bit charge stays.
 native_moments=check_moment('complex',H,73,owner['live'],b,2560,False)
 k,cuts,outer,controls=outer_witness(b)
 pin('expected.kappa_decimal',dec(k))
 assert M.moment(H,73,owner['live'],b,True)[0]>1
 assert M.moment(bitH,64,bit['bit']['live'],c+Q(1,10**24),False)[1]<1
 model_controls=['native_complex_endpoint_rejected_with_old_surcharge','omitting_bit_surcharge_would_fail_next_endpoint_rejection']
 moments=bit_moments+native_moments
 input_hashes={'owner_audit':owner_sha,'fresh_invoice':invoice_sha,'inputs/PR543-EXPECTED.json':sha(bit_path)}
 input_hashes.update({'engines/'+name+'.py':sha(P/'engines'/(name+'.py'))for name in ('moment','base_two_moment','outer')})
 return dict(status='PASS_FRESH_MIXED_048_ALLCOLD_NATIVE_EXACT_ASSEMBLY',kappa=str(k),kappa_decimal=dec(k),complex_lower=str(b),complex_decimal=dec(b),bit_lower=str(c),bit_decimal=dec(c),binding='complex',gain_over_pinned569_percent=dec(100*(k/Q(X['gain_baseline_kappa'])-1)),complex_profile=H,provider_counts=invoice['provider_counts'],surcharge_model={'complex':False,'bit':True},conservative_complex_lower=str(conservative_b),conservative_complex_decimal=dec(conservative_b),conservative_kappa=str(conservative_k),conservative_kappa_decimal=dec(conservative_k),conservative_moments=conservative_moments,conservative_bootstrap=conservative_cuts,conservative_outer={n:str(v)for n,v in conservative_outer['strict_constraints'].items()},conservative_controls=conservative_controls,model_controls=model_controls,native_correction_gain=dec(k-conservative_k),template_sha256=owner['template_sha256'],input_sha256=input_hashes,bit_supplier=dict(pr=543,repository='eumemic/integer-mult-bounds',commit='2065fe4f72a914d907f1046603f5a36f17018535',path='research/e8-bit-r420/EXPECTED.json',git_blob_sha1='b61d859826246e0c3dabbe096e57ad7015eadfd5',replay_scope='Cited unchanged supplier; this assembly reprices its full profile and does not rebuild its bit circuit.'),moments=moments,bootstrap=cuts,outer={n:str(v)for n,v in outer['strict_constraints'].items()},controls=controls,scope='Conditional native exact-complex witness after complete conservative admission, moment and outer checks; PR559 exact-cover recurrence correction only, bit bad-residue surcharge and H1-H5 retained. The frozen PR582 plain-joint-prefix, added-kernel and entrance-promoted provider dispatch with the new frame coalescences composed with cited unchanged PR543 bit supplier. All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape and analytic transfer remain assumptions. No unconditional theorem or full Lean certification.')
if __name__=='__main__':
 import sys
 package,C,out=map(Path,sys.argv[1:4]);assert package.resolve()==P and not out.exists()
 owner_path=C/'audit/OWNERS-AND-PROFILE.json';invoice_path=C/'audit/PREFIX-AND-INVOICE.json'
 owner,invoice=read(owner_path),read(invoice_path)
 assert owner['template_sha256']==read(C/'hosted/HOSTED.json')['template_sha256']
 r=assemble(owner,invoice,sha(owner_path),sha(invoice_path));out.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['kappa_decimal'])
