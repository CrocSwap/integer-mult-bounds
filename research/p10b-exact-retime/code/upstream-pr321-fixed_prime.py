#!/usr/bin/env python3
"""Exact p10 fixed-prime/full-fallback arithmetic on freshly admitted PR320 outputs."""
assert __debug__, 'Assertions required'
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
import argparse,hashlib,importlib.util,json
from decimal import Decimal,ROUND_FLOOR,localcontext
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
GRID=10**27
PRIME=(1<<127)-1
ETA=Q(1,10**24)
BETA=Q(1,10**9)
BASE=Q(384599485948493,5*10**17)
INITIAL=Q(384599,10**10)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ld(p):return json.loads(p.read_text(encoding='utf-8'))
def serial(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):serial(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return list(map(serial,x))
 return x
def load(n,p):
 s=importlib.util.spec_from_file_location('p10_fixed_'+n,p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v);return v
def gridk(a,eta=ETA):
 q=a*(1-2*eta);v=(1-eta)*q/(1+q)*GRID
 return Q((v.numerator-1)//v.denominator,GRID)
def moment(H,m,W,a,cost,rho):
 lo,hi=cost.moment(H,m,W,a,False);l,u=cost.logarithm(Q(m));e,f=cost.exponential(a*l,a*u)
 w=Q(32*m*sum(H.values()),W)*rho
 return cost.floor(lo+w*e),cost.ceil(hi+w*f)
def second(H,m,W,a,other,rho):
 lo,hi=other.moment(m,W,list(H.items()),a);l,u=other.log_bounds(Q(m))
 w=Q(32*m*sum(H.values()),W)*rho
 return lo+w*other.exp_bounds(a*l)[0],hi+w*other.exp_bounds(a*u)[1]
def certify(H,m,W,cost,other,rho):
 with localcontext()as c:
  c.prec=90
  terms=[(Decimal(r*n)/Decimal(m*W),(Decimal(m)/Decimal(r)).ln())for r,n in H.items()]
  f=Decimal(32*m*sum(H.values()))/Decimal(W)*Decimal(rho.numerator)/Decimal(rho.denominator)
  lm=Decimal(m).ln();lo=Decimal(0);hi=Decimal('.003')
  for _ in range(270):
   a=(lo+hi)/2
   if sum(p*(a*l).exp()for p,l in terms)+f*(a*lm).exp()<1:lo=a
   else:hi=a
  a=Q(int(((lo+hi)/2*GRID).to_integral_value(rounding=ROUND_FLOOR)),GRID)
 b=a+Q(1,GRID);x=moment(H,m,W,a,cost,rho);y=moment(H,m,W,b,cost,rho);u=second(H,m,W,a,other,rho);v=second(H,m,W,b,other,rho)
 assert x[1]<1<y[0] and u[1]<1<v[0], 'Independent root brackets'
 return a,b,x,y,u,v
def ceilq(v):return -((-v.numerator)//v.denominator)
def cutoff(delta,C):
 assert 0<delta<=1 and type(C)is int and C>0
 return max(1,ceilq(36/delta**2),ceilq(2*(4+(C-1).bit_length())/delta))
def validate_invoice(i,bp,p):
 m=i['m'];T=i['physical_replicas'];stock=i['literal_stock'];E=i['positive_rank_children'];mass=i['rank_mass'];N=2*m
 assert(m,T)==(100,60) and bp['m']==m
 assert stock==bp['literal_stock']==5*bp['W'] and E==bp['literal_children']==5*bp['calls']
 assert mass==bp['literal_rank_mass']==5*bp['rank_mass'] and m*stock-mass==T*2040
 assert i['fallback_per_child']==32*m*m and i['simultaneous_extra_work_streams']==1
 assert i['generic_wrappers']==E*(8*m*m+8) and i['matrix_preparation']==E*128*N**3
 assert i['copy_erase_episodes']==5*20*T and i['bridge_additions']==T*6*960
 assert i['route_families']==T*(24*960+10*8223)
 assert i['high_affine_factors']==i['route_families']*16*(m*m+1)**2
 assert i['low_transposition_coefficient']==i['route_families']*(stock+20)
 C=i['unit_expanded_additions']+i['high_affine_factors']+i['low_transposition_coefficient']+i['generic_wrappers']+i['matrix_preparation']+16*m**3+i['copy_erase_episodes']+E+i['extra_bank_selector_calls']+1
 assert C==p['coefficient'] and C<2**80<PRIME and stock+20<PRIME
 assert i['payload_prefix_upper']<2**104<PRIME and 0<i['extra_bank_selector_calls']<2**40
 assert 0<i['normalizer_factor_bound']<2**80<PRIME
 return C
def run(replay,output,source=None):
 source=Path(source).resolve()if source else ROOT/'vendor/pr320-derived'
 pin=ld(ROOT/'SOURCE-PIN.json');vr=ld(replay/'verification.json');ma=ld(replay/'math.json')['mathematics'];fin=ld(replay/'finite.json');pr=ld(replay/'primes.json')
 assert vr['status']in('PASS_IMMUTABLE_P10_TRANSCRIPT_STAGES_FIVE_STAGE_BANKED_CONSTRUCTION','PASS_SOURCE_BOUND_NEW_FIVE_RANK1_KERNEL_P10_STRICT_AUDIT') and vr['inputs_unchanged']
 assert vr['manifest_sha256']==pin['supplier_manifest_sha256']==sha(source/'MANIFEST.json') and Q(vr['kappa'])==Q(pin['supplier_kappa'])
 required={'virtual','raw','bit','scalar','primes','banks','complex','math','finite','descent','target','kernel','restore','sink','reorder'}
 if vr['status']=='PASS_IMMUTABLE_P10_TRANSCRIPT_STAGES_FIVE_STAGE_BANKED_CONSTRUCTION':
  assert set(vr['fresh_stages'])==required;reuse={}
 else:
  assert vr['strict_pins'] and set(vr['fresh_stages'])==required-{'complex'} and set(vr['reused_stages'])=={'complex'}
  reuse=vr['reused_stages'];cr=reuse['complex'];dependencies={p.relative_to(source).as_posix():sha(p)for p in source.rglob('*')if p.is_file()and(p.name=='portable_complex.py'or p.relative_to(source).as_posix().startswith('code/complex')or p.relative_to(source).as_posix().startswith('inputs/complex'))}
  assert dependencies==cr['dependencies'] and not cr['fresh_in_this_candidate_process']
  um=ROOT/'provenance/pr320-upstream-MANIFEST.json';uv=ROOT/'receipts/complex-source-verification.json';uc=ROOT/'receipts/complex-source-receipt.json'
  assert sha(um)==pin['upstream_manifest_sha256']==cr['source_manifest_sha256'] and sha(uv)==cr['native_verification_sha256'] and sha(uc)==cr['complex_receipt_sha256']
  ov=ld(uv);assert ov['inputs_unchanged'] and ov['status']=='PASS_IMMUTABLE_P10_TRANSCRIPT_STAGES_FIVE_STAGE_BANKED_CONSTRUCTION'and'complex'in ov['fresh_stages']
  assert all(ld(um)['files'][name]==h for name,h in dependencies.items())
  assert ld(replay/'complex.json')==ld(uc), 'Complex receipt must equal freshly checked source-identical supplier'
 raw=ld(replay/'raw.json');assert raw['kernel_transform']['selected_entries']==780 and raw['physical_R']==8223
 census=ld(replay/'kernel.json');assert census['selected_entries']==780 and census['rank_drop']==975 and census['selected_pairs']==536
 selection=ld(source/'kernel-selection.json');assert len(selection['pairs'])+len(selection['families'])==780 and selection['total_entrance_rank']==975
 assert sha(source/'kernel-selection.json')==pin['new_kernel_selection_sha256']
 assert len(vr['negative_controls'])==15
 assert pr['all_remaining_factors_below_2_power_80'] and pr['physical_inventory_bound']
 assert pr['status']=='PASS_FRESH_ALL_ACTUAL_P10_BASIS_DETERMINANTS_AND_FIVEFOLD_BUNDLES'
 assert max(pr['prime_factors'])<=31 and len(pr['controls'])==6
 # Lucas-Lehmer with prime exponent127: finite arithmetic, no probabilistic primality test.
 assert all(127%d for d in range(2,12));ll=4
 for _ in range(125):ll=(ll*ll-2)%PRIME
 assert ll==0 and PRIME>2**80 and all(PRIME%d for d in(2,3,5,7,11,13,17,19,23,29,31))
 bp=ma['bit_profile'];H={int(k):int(n)for k,n in bp['histogram'].items()};m=bp['m'];W=bp['W'];rho=Q(2*m**3,PRIME)
 assert m==100 and sum(H.values())==bp['calls'] and sum(r*n for r,n in H.items())==bp['rank_mass']
 assert m*W-bp['rank_mass']==24480 and max(H)==42<m/2 and rho<Q(1,10**16)
 C=validate_invoice(fin['paid_inventory'],bp,fin['q_power_bound'])
 assert fin['row_reserve']['internal_coefficient']==10001 and fin['row_reserve']['external_complex_coefficient']==20161
 cost=load('moment',source/'moment.py');other=load('independent',source/'base_two_moment.py');outer=load('outer',source/'outer.py')
 baseline_leaf=Q(ma['ordinary_bootstrap_chain'][-1])
 assert list(map(Q,fin['bootstrap']['chain']))==list(map(Q,ma['ordinary_bootstrap_chain']))
 assert 0<INITIAL<baseline_leaf<Q(ma['bit_coarse']), 'Seed follows from freshly verified stronger baseline leaf'
 coarse,nextcoarse,x,y,u,v=certify(H,m,W,cost,other,rho)
 assert coarse>Q(ma['bit_root'])
 cap=gridk(coarse);chain=[INITIAL];gaps=[]
 for level in range(1,21):
  old=chain[-1];a=(1-coarse)*coarse+coarse*old
  ds=dict(atom=coarse-a,borrowing=1-a-coarse,remainder=1-a-coarse*(1-old),stock=1-coarse)
  assert old<a<coarse<1-a and min(ds.values())>0
  delta=min(ds.values());L=cutoff(delta,C)
  assert Q(L)*delta**2>=36 and Q(L)*delta>=2*(4+(C-1).bit_length())
  chain.append(a);gaps.append(dict(level=level,gaps=ds,minimum_gap=delta,cutoff_log2_at_charged_coefficient=L))
  if gridk(a)==cap:break
 else:raise AssertionError('Finite bootstrap budget20 exhausted')
 bridge=ma['finite_bridge'];bridge['rows']['degree_gap']=Q(bridge['rows']['degree_gap'])
 complex_saving=Q(ma['complex_coarse']);assert coarse<(1-BETA)*complex_saving
 assembly=outer.assembly(chain[-1],complex_saving,bridge,cap,eta=ETA,beta=BETA)
 assert len(assembly['strict_constraints'])==47 and len(assembly['margins'])==7 and min(assembly['strict_constraints'].values())>0 and cap>BASE
 controls=[]
 def reject(name,fn):
  try:fn()
  except(AssertionError,ValueError):controls.append(name)
  else:raise AssertionError('Mutationaccepted '+name)
 for a in(chain[-1],coarse):reject('adjacent kappa at '+('finite leaf'if a==chain[-1]else'coarse cap'),lambda a=a:outer.assembly(a,complex_saving,bridge,cap+Q(1,GRID),eta=ETA,beta=BETA))
 for key in('fallback_per_child','matrix_preparation','generic_wrappers','literal_stock','copy_erase_episodes','high_affine_factors','low_transposition_coefficient'):
  bad=dict(fin['paid_inventory']);bad[key]-=1
  reject('undercharged '+key,lambda bad=bad:validate_invoice(bad,bp,fin['q_power_bound']))
 reject('zero finite cutoff gap',lambda:cutoff(Q(0),C));reject('zero invoice coefficient',lambda:cutoff(Q(1,2),0))
 tau=1-x[1];linear=1-Q(bp['rank_mass'],m*W)-rho*Q(32*m*bp['calls'],W);assert tau>0 and linear>0
 oldeta=gridk(coarse,Q(1,10**12))
 result=dict(status='PASS_SOURCE_BOUND_FIVE_NEW_KERNELS_P10_PRIME_THRESHOLD_FULL_FALLBACK_BOOTSTRAP_OUTER47',kappa=cap,kappa_scientific=format(float(cap),'.17e'),baseline_kappa=BASE,candidate_native_kappa=Q(pin['supplier_kappa']),candidate_native_gain_over_public_parent=Q(pin['supplier_kappa'])-BASE,exact_gain=cap-BASE,additional_threshold_bootstrap_gain=cap-Q(pin['supplier_kappa']),binding='bit',conditional=True,lean_certificate=False,supplier_reused_stages=reuse,new_kernel_entries=5,kernel_entries_total=780,new_kernel_selection_sha256=pin['new_kernel_selection_sha256'],
  source=dict(public_pr=pin['public_pr'],public_parent_head=pin['public_parent_head'],derived_source=True,manifest_sha256=vr['manifest_sha256'],compressed_source_word_sha256=sha(source/'bitword/selected/bit/word_p10.json.gz'),emitted_global_program_sha256=fin['source_binding']['global_program'],local_tagged_word_sha256=fin['source_binding']['tagged'],replay_certificate_sha256=sha(replay/'certificate.json'),replay_verification_sha256=sha(replay/'verification.json'),source_unchanged_during_checked_replay=True),
  fixed_prime=dict(minimum_prime_threshold=PRIME,policy='Every prime q at least this threshold; retain the source all-size q-growth and prime-supply regime. No replacement by a constant-modulus machine.',uniform_density_upper_bound=True,exponent=127,lucas_lehmer_iterations=125,lucas_lehmer_residue=ll,density=rho,density_formula='2*m^3/q',actual_basis_inventory_sha256=pr['basis_inventory_sha256'],actual_unique_bases=pr['unique_bases'],retained_residual_upper=2**80,named_factors_upper=31),
  bit_profile=bp,whole_literal_invoice=fin['paid_inventory'],finite_coefficient=C,full_fallback_retained=True,
  root=dict(lower=coarse,upper=nextcoarse,first_lower=x,first_upper=y,second_lower=u,second_upper=v),
  complex_supplier_unchanged=ma['complex_coarse'],ordinary_bootstrap=dict(initial=INITIAL,seed_justification='The freshly verified baseline ordinary leaf is stronger than INITIAL; use its weaker admitted bound as the seed.',verified_baseline_leaf=baseline_leaf,seed_gap=baseline_leaf-INITIAL,levels=level,chain=chain,gaps=gaps,eta=ETA,beta=BETA,grid=GRID,coarse_grid_cap=cap,eta_1e_12_cap=oldeta),
  moment_gaps=dict(delta_tau=tau,delta_linear=linear),growing_prime_regime=dict(retained=True,all_primes_above_threshold=True,coefficient_below_threshold=C<PRIME,stock_and_centre_below_threshold=fin['paid_inventory']['literal_stock']+20<PRIME,normalizers_below_threshold=fin['paid_inventory']['normalizer_factor_bound']<PRIME,payload_prefix_below_threshold=fin['paid_inventory']['payload_prefix_upper']<PRIME,q_power_exponent=10001,argument='For every permitted growing q >= threshold, each exact basis denominator and bank-normalizer factor is a unit, rho(q)=2m^3/q <= the priced threshold envelope, and C*q^10000 < q^10001. The unchanged supplier prime-supply and asymptotic q regime are retained.'),assembly=assembly,finite_bridge=bridge,negative_controls=controls,
  scope='Conditional sufficient finite construction under the unchanged PR320 public all-size compiler, weighted-selector, common-ancestor-chart, restored-row, routing, prime-supply, recovery and complex analytic interfaces. The derived complete p10 word, regenerated banks, geometry and full finite invoice are freshly admitted; only the source-identical complex supplier is inherited unchanged. No universal machine or Lean certificate is asserted.',
  cutoff_scope='Displayed cutoffs use the freshly charged primitive coefficient. As in PR320, the full asymptotic cutoff also multiplies every inherited primitive, wrapper and preceding ordinary-level constant; those retained public interfaces remain conditions.')
 output.write_text(json.dumps(serial(result),indent=2,sort_keys=True)+'\n',encoding='utf-8');print(result['status'],str(cap),format(float(cap),'.17e'),'levels',level,flush=True)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('replay',type=Path);p.add_argument('output',type=Path);p.add_argument('--source',type=Path);a=p.parse_args();run(a.replay,a.output,a.source)
