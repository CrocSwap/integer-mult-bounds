#!/usr/bin/env python3
"""Source-bound prime-threshold and finite bootstrap on a fully replayed p10 T300 word.
Arithmetic enclosure primitives: PR321 c76247701762feb2c5bea5bcf302b010eb7d1bc3,
prepared with OpenAI Codex assistance. Literal-word rebinding and invoice reconstruction
prepared with OpenAI Codex assistance. Apache-2.0. All inherited hypotheses remain.
"""
import sys
assert __debug__
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import argparse,hashlib,importlib.util,json,struct
ROOT=Path(__file__).resolve().parent
P=(1<<127)-1; GRID=10**27; ETA=Q(1,10**24); BETA=Q(1,10**9); INITIAL=Q(384599,10**10)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def serial(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):serial(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return list(map(serial,x))
 return x

def census(path):
 H=Counter();adds=units=copies=erasures=records=0
 data=Path(path).read_bytes();assert len(data)%24==0
 for op,a,b,c,f,z in struct.iter_unpack('<6i',data):
  records+=1
  if op==0 and f:H[f]+=1
  elif op==1:adds+=1;units+=abs(c)
  elif op==2:H[z]+=1;copies+=1
  elif op==3:erasures+=1
  else:assert op==0
 assert copies==erasures==20
 return H,adds,units,records

def invoice(word,bank,columns,price,inv):
 m=100;h=20;v=960;T=bank['physical_replicas'];assert T>0 and T%5==0
 R=bank['actual_helper_roles'];stock=bank['literal_stock'];norm=bank['normalizer_factor_ceiling']
 assert bank['actual_role_replica_stage_assignments']==5*T*R
 assert stock==4*v*T+5*bank['banks_per_stage']==5*bank['normalized_stock']
 residual={int(r):n for r,n in bank['residual_families'].items()};used=Counter()
 for row in bank['bank_patterns']:
  assert sum(row['widths'])==m and row['count']>0
  for r in row['widths']:used[r]+=row['count']
 assert used=={r:T*n for r,n in residual.items()} and sum(residual.values())==R
 assert sum(row['count']for row in bank['bank_patterns'])==bank['banks_per_stage']
 H,adds,units,nrecords=census(word);literal=Counter({r:5*T*n for r,n in H.items()})
 for r in (4,19,38,42):literal[r]+=2*v*T
 E=sum(literal.values());mass=sum(r*n for r,n in literal.items())
 assert max(literal)==42 and m*stock-mass==2040*T
 assert dict(literal)=={int(r):int(n)for r,n in inv['literal_histogram'].items()}=={int(r):5*n for r,n in price['cohort_candidate']['histogram'].items()}
 assert price['adds']==adds and price['unit_adds']==units and price['local_rank_mass']==sum(r*n for r,n in H.items())
 assert dict(H)=={int(r):n for r,n in price['local_histogram'].items()}==dict(columns['local_raw_H'])
 assert columns['independent_dirty_registers']==R and columns['local_scalar_additions']==adds
 assert columns['fresh_center_copies']==100 and columns['copied_center_original_source_immutable']
 assert len(columns['negative_controls'])==6 and all(c['rejected']for c in columns['negative_controls'])
 N=2*m;d=m*m;J=T*(24*v+10*R);K=2*5*T*((stock-1)+R*m*norm)
 weighted=T*(5*adds+6*v);unit=T*(5*units+6*v)
 components=dict(unit_expanded_additions=unit,high_affine_factors=J*16*(d+1)**2,low_transposition_coefficient=J*(stock+h),generic_wrappers=E*(8*m*m+8),matrix_preparation=E*128*N**3,selector_preparation=16*m**3,copy_erase_episodes=5*h*T,paid_children=E,extra_bank_selector_calls=K,one_extra_work_stream=1)
 C=sum(components.values())
 assert norm==int(inv['normalizer_factor_bound']) and K==bank['selector_charge']==int(inv['extra_selector_calls'])
 assert T==inv['physical_replicas'] and stock==inv['literal_stock'] and 5*price['cohort_candidate']['stock']==stock
 assert E==int(inv['positive_rank_children']) and mass==int(inv['literal_rank_mass']) and inv['literal_deficit']==2040*T
 assert weighted==int(inv['global_weighted_additions']) and unit==int(inv['global_unit_expanded_additions']) and J==int(inv['route_families'])
 assert C==int(inv['full_counted_primitive_coefficient']) and C<2**80<P
 F,B=[int(r['cancellation_free_signed_row_l1_upper'])for r in columns['signed_lift_prefix']]
 payload=64*F**3*B**2;assert payload==int(inv['payload_signed_prefix_upper']) and payload.bit_length()==inv['payload_bits'] and payload<2**104<P
 assert inv['internal_row_coefficient']==m*m+1 and inv['external_complex_row_coefficient']==20161
 assert inv['simultaneous_extra_work_streams']==1 and stock+h<P and norm<P
 assert 6*N*(N-1)+3*N+6*(N-1)<32*m*m
 return dict(m=m,h=h,v=v,R=R,T=T,literal_stock=stock,literal_histogram=dict(literal),positive_rank_children=E,rank_mass=mass,components=components,coefficient=C,full_rank_one_fallback_calls=32*m*m*E,fallback_per_child=32*m*m,normalizer=norm,payload=payload,records=nrecords,adds=adds,units=units)

def compute(source,replay,expected_word,predecessor=None,require_frame_primes=False,math_root=None):
 """Exact arithmetic stage; enclosing verifier admits the bound structural receipts."""
 source=Path(source).resolve();replay=Path(replay).resolve()
 word=replay/'candidate/COHORT249-RECORDS.bin';assert sha(word)==expected_word
 price=read(replay/'PRICE.json');bank=read(replay/'BANK.json');columns=read(replay/'COLUMNS.json');inv=read(replay/'INVOICE.json')
 assert price['source_word_sha256']==expected_word
 native=Q(price['kappa'])
 assert price['full_fallback_retained'] and price['adjacent_rejected']
 assert bank['status']=='PASS_GENERIC_EXACT_CHARTS_ACTUAL_BANK_ALLOCATION' and bank['all_new_ordinary_annihilators_full_rank']
 assert max(int(bank[k])for k in ('max_intermediate_numerator','max_intermediate_denominator','normalizer_factor_ceiling'))<2**80<P
 assert int(bank['max_block_scalar'])<2**80 and bank['geometry_controls']
 parent=Path(predecessor).resolve()if predecessor else replay/'predecessor';pv=read(parent/'verification.json');pr=read(parent/'primes.json')
 assert pv['inputs_unchanged'] and 'primes'in pv['fresh_stages'] and 'complex'in pv['fresh_stages']
 assert pr['all_remaining_factors_below_2_power_80'] and pr['physical_inventory_bound'] and all(int(r)<P for r in pr['prime_factors'])
 assert read(parent/'complex.json')['precision_guard']['retained_row_coefficient']==20161
 assert all(127%d for d in range(2,12));ll=4
 for _ in range(125):ll=(ll*ll-2)%P
 assert ll==0
 bill=invoice(word,bank,columns,price,inv);m=bill['m'];C=bill['coefficient'];H={int(r):n for r,n in price['cohort_candidate']['histogram'].items()};W=price['cohort_candidate']['stock'];rho=Q(2*m**3,P)
 assert sum(H.values())==price['cohort_candidate']['calls'] and sum(r*n for r,n in H.items())==price['cohort_candidate']['rank_mass'] and m*W-sum(r*n for r,n in H.items())==2040*bill['T']//5
 mathsrc=Path(math_root).resolve()if math_root else source/'vendor/predecessor';cost=load('threshold_moment',mathsrc/'moment.py');other=load('threshold_base2',mathsrc/'base_two_moment.py');outer=load('threshold_outer',mathsrc/'outer.py');primitive=load('pr321_exact_arithmetic',ROOT/'upstream-pr321-fixed_prime.py')
 # Pin every consumed structural and arithmetic input, including inherited prime exclusions.
 consumed=['PRICE.json','BANK.json','COLUMNS.json','INVOICE.json','candidate/COHORT249-RECORDS.bin','candidate/COHORT249-FRAMES.json','candidate/frames.json','candidate/COHORT249-INITIAL.json','candidate/COHORT249-FINAL.json']
 if require_frame_primes:
  fp=read(replay/'FRAME-PRIMES.json');assert fp['status']=='PASS_EXACT_FRAME_AND_ANNIHILATOR_MINORS_FOR_ALL_PRIMES_ABOVE_2_POWER_80'
  assert fp['input_sha256']==sha(replay/'candidate/frames.json') and fp['zero_row_control_rejected']
  assert fp['basis_witnesses']==2*fp['frames']==len(fp['witnesses']) and 0<int(fp['max_abs_minor'])<2**80<P
  assert max(abs(int(r['determinant']))for r in fp['witnesses'])==int(fp['max_abs_minor'])
  assert all(0<abs(int(r['determinant']))<2**80<P for r in fp['witnesses'])
  consumed.append('FRAME-PRIMES.json')
 receipt_hashes={name:sha(replay/name)for name in consumed}
 for name in ('verification.json','primes.json','complex.json','math.json'):receipt_hashes['predecessor/'+name]=sha(parent/name)
 engine_hashes={name:sha(mathsrc/name)for name in ('moment.py','base_two_moment.py','outer.py')}
 engine_hashes['upstream-pr321-fixed_prime.py']=sha(ROOT/'upstream-pr321-fixed_prime.py')
 engine_hashes[Path(__file__).name]=sha(__file__)
 bitcoarse,nextcoarse,x,y,u,v=primitive.certify(H,m,W,cost,other,rho);assert bitcoarse>Q(price['bit_root'])
 complex_saving=Q(price['complex_saving']);complex_limit=(1-BETA)*complex_saving;limit_ticks=complex_limit*GRID;strict_complex_cap=Q((limit_ticks.numerator-1)//limit_ticks.denominator,GRID)
 coarse=min(bitcoarse,strict_complex_cap);admit_first=primitive.moment(H,m,W,coarse,cost,rho);admit_second=primitive.second(H,m,W,coarse,other,rho);assert admit_first[1]<1 and admit_second[1]<1 and coarse<complex_limit
 cap=primitive.gridk(coarse);chain=[INITIAL];gaps=[]
 assert INITIAL<Q(price['ordinary_chain'][-1])<coarse
 for level in range(1,21):
  old=chain[-1];a=(1-coarse)*coarse+coarse*old;ds=dict(atom=coarse-a,borrowing=1-a-coarse,remainder=1-a-coarse*(1-old),stock=1-coarse);assert old<a<coarse<1-a and min(ds.values())>0
  delta=min(ds.values());cut=primitive.cutoff(delta,C);assert cut*delta**2>=36 and cut*delta>=2*(4+(C-1).bit_length());chain.append(a);gaps.append(dict(level=level,gaps=ds,minimum_gap=delta,primitive_coefficient_cutoff_log2=cut))
  if primitive.gridk(a)==cap:break
 else:raise AssertionError('finite bootstrap budget exhausted')
 bridge=read(parent/'math.json')['mathematics']['finite_bridge'];bridge['rows']['degree_gap']=Q(bridge['rows']['degree_gap']);complex_saving=Q(price['complex_saving']);assert coarse<(1-BETA)*complex_saving
 assembly=outer.assembly(chain[-1],complex_saving,bridge,cap,eta=ETA,beta=BETA);assert len(assembly['strict_constraints'])==47 and len(assembly['margins'])==7 and min(assembly['strict_constraints'].values())>0
 controls=[]
 def reject(label,fn):
  try:fn()
  except(AssertionError,ValueError):controls.append(label)
  else:raise AssertionError('mutation accepted '+label)
 for leaf in (chain[-1],coarse):reject('adjacent kappa',lambda leaf=leaf:outer.assembly(leaf,complex_saving,bridge,cap+Q(1,GRID),eta=ETA,beta=BETA))
 for key in ('full_counted_primitive_coefficient','global_unit_expanded_additions','literal_stock','positive_rank_children','literal_rank_mass','extra_selector_calls','normalizer_factor_bound','payload_signed_prefix_upper'):
  bad=dict(inv);bad[key]=str(int(bad[key])-1)if isinstance(bad[key],str)else bad[key]-1
  reject('undercharged '+key,lambda bad=bad:invoice(word,bank,columns,price,bad))
 reject('zero cutoff gap',lambda:primitive.cutoff(Q(0),C));reject('zero coefficient',lambda:primitive.cutoff(Q(1,2),0))
 tau=1-admit_first[1];linear=1-Q(bill['rank_mass'],m*bill['literal_stock'])-rho*Q(32*m*bill['positive_rank_children'],bill['literal_stock']);assert tau>0 and linear>0
 external={}
 if price.get('complex_reserve'):
  cr=price['complex_reserve'];binding=cr['binding'];assert sha(Path(cr['package'])/'MANIFEST.json')==binding['manifest_sha256'];assert binding['inputs_unchanged'] and binding['all_supplier_stages_fresh'];engine_hashes['future_supplier.py']=sha(ROOT/'future_supplier.py');assert engine_hashes['future_supplier.py']==binding['adapter_sha256']
  for name,digest in binding['receipt_hashes'].items():
   path=Path(cr['proof'])/name;assert sha(path)==digest;external[str(path)]=digest
 result=dict(status='PASS_P10_PRIME_THRESHOLD_FULL_INVOICE_TWO_MOMENTS_FINITE_BOOTSTRAP_OUTER47',kappa=cap,kappa_decimal=format(float(cap),'.18e'),native_kappa=native,exact_gain=cap-native,source=dict(word_sha256=expected_word,external_receipt_hashes=external,receipt_hashes=receipt_hashes,engine_hashes=engine_hashes,arithmetic_source_pr='https://github.com/CrocSwap/integer-mult-bounds/pull/321',arithmetic_source_head='c76247701762feb2c5bea5bcf302b010eb7d1bc3',structural_admission='Consumed only; the enclosing full verifier must bind and admit these exact structural receipts.'),prime_threshold=dict(Q=P,lucas_lehmer_residue=ll,density=rho,growing_prime_regime_retained=True,all_permitted_primes_q_at_least_Q=True,current_frame_and_bank_exclusions_below_2_power_80=True),complete_literal_invoice=bill,bit_profile=dict(m=m,W=W,histogram=H),ordinary_saving=dict(value=coarse,complex_limit=complex_limit,strict_complex_cap=strict_complex_cap,complex_binds=coarse<bitcoarse,first_interval=admit_first,second_interval=admit_second),root=dict(lower=bitcoarse,upper=nextcoarse,first_lower=x,first_next=y,second_lower=u,second_next=v),bootstrap=dict(initial=INITIAL,admitted_native_leaf=Q(price['ordinary_chain'][-1]),levels=level,chain=chain,gaps=gaps,full_cutoff_rule='Replace the displayed primitive coefficient C by any C_full bounding it times all inherited primitive, wrapper, and preceding-level constants. The finite level count is fixed.'),eta=ETA,beta=BETA,grid=GRID,complex_saving=complex_saving,moment_gaps=dict(strict=tau,linear=linear),assembly=assembly,negative_controls=controls,scope='Conditional sufficient finite construction under the unchanged all-size compiler, weighted selector, common-ancestor chart, restored-row, routing, prime-supply, precision/recovery, complex-symbolic and analytic interfaces. Prime q still grows as in the admitted source; Q is only an eventual lower threshold. No fixed-modulus machine or unconditional theorem is claimed.')
 print(result['status'],str(cap),'levels',level,'gain',float(cap-native))
 return result
def run(source,replay,output,expected_manifest,expected_word,public_commit,require_frame_primes=False):
 source=Path(source).resolve();replay=Path(replay).resolve();output=Path(output).resolve();assert not output.exists()
 verifier=load('source_package_verifier',source/'verify.py');digest=verifier.integrity();assert digest==expected_manifest
 pin=read(source/'SOURCE.json');assert pin['final_word_sha256']==expected_word
 ver=read(replay/'VERIFICATION.json');cert=read(replay/'CERTIFICATE.json')
 assert ver['inputs_unchanged'] and ver['manifest_sha256']==digest
 assert ver['status']==cert['status'] and ver['status'].startswith('PASS_SOURCE_BOUND_')
 assert Q(ver['kappa'])==Q(cert['kappa'])==Q(pin['kappa']) and ver['word_sha256']==cert['word_sha256']==expected_word
 required={'BANK.json','COLUMNS.json','INVOICE.json','LEGALITY.json','PRICE.json','TILING.json','predecessor/verification.json','predecessor/complex.json'}
 if require_frame_primes:required.add('FRAME-PRIMES.json')
 assert required<=cert['fresh_receipt_hashes'].keys()
 for name,d in cert['fresh_receipt_hashes'].items():assert sha(replay/name)==d,('changed structural receipt',name)
 stages=[r['stage']for r in ver['fresh_stages']];assert len(stages)==len(set(stages))
 for stage in ('legality','columns','tiling','bank-frames-and-assignment','changed-charts','geometry-admission','price','finite-invoice','complete-admission'):assert stage in stages
 result=compute(source,replay,expected_word,require_frame_primes=require_frame_primes)
 assert Q(result['native_kappa'])==Q(ver['kappa']) and verifier.integrity()==digest
 result['status']='PASS_SOURCE_BOUND_'+result['status'][5:]
 result['source'].update(public_commit=public_commit,manifest_sha256=digest,verification_sha256=sha(replay/'VERIFICATION.json'),certificate_sha256=sha(replay/'CERTIFICATE.json'),structural_receipt_hashes=cert['fresh_receipt_hashes'],inputs_unchanged=True,structural_admission='All source stages successfully replayed and admitted by the pinned native verifier.')
 output.write_text(json.dumps(serial(result),sort_keys=True,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--replay',required=True);p.add_argument('--output',required=True);p.add_argument('--expected-manifest');p.add_argument('--expected-word',required=True);p.add_argument('--public-commit');p.add_argument('--require-frame-primes',action='store_true');p.add_argument('--arithmetic-stage',action='store_true');p.add_argument('--predecessor-replay');p.add_argument('--math-root');a=p.parse_args()
 if a.arithmetic_stage:
  assert not Path(a.output).exists();r=compute(a.source,a.replay,a.expected_word,a.predecessor_replay,a.require_frame_primes,a.math_root);Path(a.output).write_text(json.dumps(serial(r),sort_keys=True,indent=2)+'\n')
 else:
  assert a.expected_manifest and a.public_commit and not a.predecessor_replay
  run(a.source,a.replay,a.output,a.expected_manifest,a.expected_word,a.public_commit,a.require_frame_primes)
