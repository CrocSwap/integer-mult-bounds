"""Finite bill for the literal 60-replica banked five-stage gen5 word (source527 finite bill, rebound).
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
Retains PR234exact-tape/prime/ordinary-leaf hypotheses, and pays bankroutes.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util,json
HERE=Path(__file__).resolve().parent
THEOREM_PINS={
 'proof/three-stage-cover-bit.tex':'47123a756f823c83a0d48cca2bf5add6472cd88410b13aed345e70c8834fb511',
 'proof/three-stage-cover-rows.tex':'6ad97a5cd7d6aecf978a81226e1c2763d37840caca130c61f3bf5c4ac111c5c8',
 'proof/copied-centers-lemma.tex':'d0ce6d3d504996aadb098227885224e48df46101daec8893523a0a8b7364d8fe'}
def ceilq(x):return -((-x.numerator)//x.denominator)

def cutoff_log2(delta,C):
    assert 0<delta<=1 and isinstance(C,int) and C>=1
    return max(1,ceilq(36/delta**2),ceilq(2*(4+(C-1).bit_length())/delta))

def hist(x):return Counter({int(k):v for k,v in x.items()if v})

def route_template():
    """Recompute the actual 48-dimensional rational route, not its receipt."""
    h=24
    I=lambda n:[[Q(i==j)for j in range(n)]for i in range(n)]
    q=[int(i<3)for i in range(h)]
    P=[[Q(q[i])*(Q(q[j])-Q(1,3))/2 for j in range(h)]for i in range(h)]
    K=[[Q(i==j)-P[i][j]for j in range(h)]for i in range(h)]
    rho=[P[i]+K[i]for i in range(h)]+[K[i]+P[i]for i in range(h)]
    a=[r[:]for r in rho];factors=[]
    for j in range(2*h):
        p=next(i for i in range(j,2*h)if a[i][j])
        if p!=j:a[j],a[p]=a[p],a[j];factors.append(('swap',j,p,None))
        if a[j][j]!=1:
            c=1/a[j][j];a[j]=[c*x for x in a[j]];factors.append(('scale',j,None,c))
        for i in range(2*h):
            if i!=j and a[i][j]:
                c=-a[i][j];a[i]=[x+c*y for x,y in zip(a[i],a[j])];factors.append(('add',i,j,c))
    assert a==I(2*h)
    def replay(omit=None):
        a=I(2*h)
        for z in reversed(range(len(factors))):
            if z==omit:continue
            kind,i,j,c=factors[z]
            if kind=='swap':a[i],a[j]=a[j],a[i]
            elif kind=='scale':a[i]=[x/c for x in a[i]]
            else:a[i]=[x-c*y for x,y in zip(a[i],a[j])]
        return a
    assert replay()==rho
    assert replay(next(i for i,f in enumerate(factors)if f[0]=='add'))!=rho
    counts=dict(Counter(f[0]for f in factors));denoms=sorted({c.denominator for kind,i,j,c in factors if c is not None})
    assert counts==dict(scale=27,add=195,swap=44) and denoms==[1,2,3,6]
    serialization=[[kind,i,j,None if c is None else str(c)]for kind,i,j,c in factors]
    return dict(factors=len(factors),factor_counts=counts,denominators=denoms,
        factor_program_sha256=sha256(json.dumps(serialization,separators=(',',':')).encode()).hexdigest(),
        exact_inverse_reconstruction=True,missing_addition_rejected=True)

def run(raw,physical,scalar,prime_result,math_result,banks,banked_result,global_result):
 for name,h in THEOREM_PINS.items():assert sha256((HERE/name).read_bytes()).hexdigest()==h,('changed theorem',name)
 bit=(HERE/'proof/three-stage-cover-bit.tex').read_text();rows=(HERE/'proof/three-stage-cover-rows.tex').read_text();copied=(HERE/'proof/copied-centers-lemma.tex').read_text()
 for s in ('constants are independent of $w,n$ and ancestor values','absorbed by the complete $q^w$ target fiber','spectator counters','32m^2','only units are inverted'):assert s in bit
 for s in ('W(w)^{D(n)}','padding factor is less than two','below $q^2$'):assert s in rows
 assert 'Copying, pointwise reads and erasure are linear'in copied and'fixed work stream'in copied
 assert raw['physical_R']==15434 and raw['v']==1760 and raw['h']==24 and raw['source_aliases']==0
 assert scalar['forward']['event_sha256']==physical['scalar_projection_sha256']==global_result['scalar_projection_sha256']
 assert physical['tagged_scalar_sha256']==global_result['local_tagged_sha256']
 f,b=scalar['forward'],scalar['inverse'];n=2*raw['v']+raw['physical_R'];assert n==18954
 for row in(f,b):
  assert row['all_source_and_dirty_restored']and row['arbitrary_target_contents_preserved']and row['all_formal_columns']==n
  assert row['weighted_additions']==physical['weighted_scalar_events']==753692
  assert hist(row['coefficient_counts'])==hist(physical['coefficient_histogram'])
  assert row['literal_unit_additions']==sum(c*v for c,v in hist(row['coefficient_counts']).items())==757212
 assert f['max_intermediate_row_l1']==55241 and b['max_intermediate_row_l1']==2360074
 assert raw['parity_transform']['both_reflected_ledgers'] and raw['parity_transform']['remaining_payload_additions']==753472
 assert raw['parity_transform']['removed_even_add_count']==1586240
 assert physical['copied_centers']==24 and len(physical['copied_center_blocks'])==24
 assert all(z['rank']==22 and z['scatter_reads']==220 for z in physical['copied_center_blocks'])
 assert hist(physical['paid_histogram'])==hist(raw['one_stage_helper_histogram_including_copies'])
 assert prime_result['all_remaining_factors_below_2_power_80']and prime_result['physical_inventory_bound']
 assert prime_result['independent_entrances']==2234 and prime_result['bundled_unique_bases']==250
 assert hist(prime_result['entrance_rank_counts'])==hist(raw['auxiliary_entrance_rank_histogram'])
 assert banks['conservative_extra_selector_calls']==736388225400 and banks['normalizer_factor_bound']==662
 assert banks['physical_replicas']==60 and banks['literal_stock']==1236750 and banks['assignments']==4630200
 assert banked_result['all_assignments_match']and banked_result['all_logical_helpers_bound']and banked_result['independent_completions_removed']==2234
 m=120;v=raw['v'];R=raw['physical_R'];T=banks['physical_replicas'];stock=banks['literal_stock'];d=m*m;N=2*m
 H=hist(raw['five_stage_profile']['histogram']);assert H==hist(global_result['paid_histogram'])
 for a,cnt in hist(raw['auxiliary_entrance_rank_histogram']).items():assert H.pop(5*a)==cnt
 literal=Counter({r:T*cnt for r,cnt in H.items()});E=sum(literal.values());mass=sum(r*cnt for r,cnt in literal.items())
 assert m*stock-mass==264000 and max(literal)==50 and Q(max(literal),m)<Q(1,2)
 assert hist(banked_result['literal_paid_histogram'])==literal and banked_result['literal_stock']==stock
 mathematics=math_result['mathematics'];bp=mathematics['bit_profile'];assert bp['literal_stock']==stock and bp['literal_children']==E and bp['literal_rank_mass']==mass
 weighted=T*(5*f['weighted_additions']+6*v);unit=T*(5*f['literal_unit_additions']+6*v)
 assert weighted==T*global_result['total_weighted_additions']
 # Preserve alloriginalroutes/bridges, paidcopies and finiteprimitiveovercharges.
 # The actual physicalstock and60replicas enter this bill; normalizedmomentW doesnot.
 J=T*(24*v+10*R);good=8*m*m+8;high=16*(d+1)**2;K=banks['conservative_extra_selector_calls']
 payload=64*f['max_intermediate_row_l1']**3*b['max_intermediate_row_l1']**2;payloadbits=payload.bit_length();assert payload<2**104
 fallback=6*N*(N-1)+3*N+6*(N-1);assert fallback==346314<32*m*m==460800
 coefficient=unit+J*high+J*(stock+24)+E*good+E*(128*N**3)+16*m**3+120*T+E+K+1
 assert coefficient<2**80 and 2*m**3*10**16<2**80 and 0<K<2**40
 # Internal borrowed rows are restored; the external complex row reserve is
 # independently regenerated in portable_complex and bound by verify.py.
 assert stock+24 < 2**80
 row_reserve=dict(internal_coefficient=d+1,halving_degree=1,
     bound='14401*w*ceil(log2(n)) + inherited ordinary-leaf reserve',
     restored=True,physical_stock_less_than_prime=True,external_complex_coefficient=20161)
 assert row_reserve['internal_coefficient']==14401
 route=route_template();spec=importlib.util.spec_from_file_location('bankedfinite_moment',HERE/'moment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 c=Q(mathematics['bit_coarse']);lo,hi=mod.moment(dict(literal),m,stock,c,True)
 assert list(map(Q,mathematics['bit_moment_interval']))==[lo,hi]
 delta_tau=1-hi;delta1=1-Q(mass,m*stock)-Q(1,10**16)*32*m*E/stock;assert delta_tau>0 and delta1>0
 chain=[Q(384599,10**10)];gaps=[]
 for j in range(3):
  old=chain[-1];a=(1-c)*c+c*old;ds=dict(atom=c-a,borrowing=1-a-c,remainder=1-a-c*(1-old),stock=1-c);assert old<a<c<1-a and min(ds.values())>0
  delta=min(ds.values());L=cutoff_log2(delta,coefficient);assert Q(L)*delta**2>=36 and Q(L)*delta>=2*(4+(coefficient-1).bit_length())
  gaps.append(dict(stage=j+1,gaps={k:str(x)for k,x in ds.items()},minimum_gap=str(delta),cutoff_log2_at_charged_coefficient=str(L),full_cutoff_rule='Apply cutoff_log2(delta, C_full), where C_full bounds the displayed coefficient times every inherited primitive, wrapper and preceding ordinary-level constant.'));chain.append(a)
 assert list(map(Q,mathematics['ordinary_bootstrap_chain']))==chain
 controls=[]
 for name,test in [('zero cutoff gap',lambda:cutoff_log2(Q(0),coefficient)),('negative constant',lambda:cutoff_log2(Q(1,2),0))]:
  try:test()
  except AssertionError:controls.append(name)
  else:raise AssertionError('bad finitecutoff accepted')
 return dict(status='PASS_LITERAL_PARITY_FUSED_BANKED_FIVE_STAGE_GEN5_FINITE_BILL',theorem_pins=THEOREM_PINS,source_binding=dict(event=physical['scalar_projection_sha256'],tagged=physical['tagged_scalar_sha256'],global_program=global_result['program_sha256']),paid_inventory=dict(m=m,literal_stock=stock,physical_replicas=T,positive_rank_children=E,rank_mass=mass,weighted_additions=weighted,unit_expanded_additions=unit,bridge_additions=T*6*v,route_families=J,terminal_exchange_stream_movements=T*4*v,high_affine_factors=J*high,low_transposition_coefficient=J*(stock+24),generic_wrappers=E*good,matrix_preparation=E*128*N**3,copy_erase_episodes=120*T,fallback_per_child=32*m*m,extra_bank_selector_calls=K,normalizer_factor_bound=banks['normalizer_factor_bound'],simultaneous_extra_work_streams=1,payload_prefix_upper=payload,payload_prefix_bits=payloadbits),q_power_bound=dict(coefficient=coefficient,low_matrix_power=14400,strict_upper='q^14401'),rational_route=route,row_reserve=row_reserve,moment=dict(coarse=str(c),tau=str(1-c),delta_tau_lower=str(delta_tau),delta_linear=str(delta1),fallback_added_in_full=True),recurrence=dict(bound='A*(n+n^(1-c)*w^(1-a_j))',A='C*(1+1/delta_linear+1/delta_tau)',halving_degree=1,one_level_histogram=True),bootstrap=dict(chain=list(map(str,chain)),ordinary=str(chain[-1]),gaps=gaps),rejected_controls=controls,scope='Actual60replicas/literalbankstock andallfixedbanknormalizerschargedbefore finiteordinaryleaf absorption. Inheritedweightedcompiler,commonancestorchart,restoredrow,routing,prime,recoveryandanalyticinterfacesremainconditional.')
