"""Portable fresh BIT finite bill under the pinned public exact-tape theorem.

API run(raw, physical, scalar, prime_result, math_result, global_result=None).
Inputs are the live outputs of portable_bit, scalar_check, prime_check and
math_check. No saved PASS receipt, historical path or workspace is read.
This check does not repeat their expensive source computation. Assisted with
ChatGPT; original public theorem files retain their original content.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

assert __debug__, 'Do not run exact checks under -O.'
HERE=Path(__file__).resolve().parent
HEAD='df95878d11190518e45ef9717c9ee05011f88ace'
EVENT='e74e43692685ad5f716b41b363acb8b443c2c90096634a55f0e3728980713944'
TAGGED='614f19da4288021cd5c10a575ec7759c069962a6030bf30edb047573ed76edf6'
PINS={
 'proof/three-stage-cover-bit.tex':'47123a756f823c83a0d48cca2bf5add6472cd88410b13aed345e70c8834fb511',
 'proof/three-stage-cover-rows.tex':'6ad97a5cd7d6aecf978a81226e1c2763d37840caca130c61f3bf5c4ac111c5c8',
 'proof/copied-centers-lemma.tex':'d0ce6d3d504996aadb098227885224e48df46101daec8893523a0a8b7364d8fe',
 'code/five_stage_bit_cost_20261009.py':'9d465c716c6b910ff66e1453e3bf0057608a787b5f5361be93781f42cb3370f7'}

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

def run(raw,physical,scalar,prime_result,math_result,global_result=None):
    for name,h in PINS.items():assert sha256((HERE/name).read_bytes()).hexdigest()==h,('changed theorem/code',name)
    bit=(HERE/'proof/three-stage-cover-bit.tex').read_text()
    rows=(HERE/'proof/three-stage-cover-rows.tex').read_text()
    copied=(HERE/'proof/copied-centers-lemma.tex').read_text()
    for s in ('constants are independent of $w,n$ and ancestor values','absorbed by the complete $q^w$ target fiber','spectator counters','32m^2','only units are inverted'):assert s in bit
    for s in ('W(w)^{D(n)}','padding factor is less than two','below $q^2$'):assert s in rows
    assert 'Copying, pointwise reads and erasure are linear' in copied and 'fixed work stream' in copied
    assert raw['source_head']==physical['source_head']==HEAD
    assert (raw['h'],raw['v'],raw['physical_R'])==(24,1760,16643)
    assert scalar['forward']['event_sha256']==physical['scalar_projection_sha256']==EVENT
    assert physical['tagged_scalar_sha256']==TAGGED
    f,b=scalar['forward'],scalar['inverse']
    assert f['weighted_additions']==b['weighted_additions']==physical['weighted_scalar_events']==2569626
    assert hist(f['coefficient_counts'])==hist(b['coefficient_counts'])==Counter({1:785130,2:1783176,3:1320})
    assert f['literal_unit_additions']==b['literal_unit_additions']==4355442
    assert f['max_intermediate_row_l1']==37623 and b['max_intermediate_row_l1']==9430154
    assert f['all_source_and_dirty_restored'] and b['all_source_and_dirty_restored']
    assert f['all_formal_columns']==b['all_formal_columns']==20163
    assert physical['temporary_streams_simultaneous']==1
    assert len(physical['copied_center_blocks'])==24
    assert all(z['rank']==22 and z['scatter_reads']==220 for z in physical['copied_center_blocks'])
    assert hist(physical['paid_histogram'])==hist(raw['one_stage_helper_histogram_including_copies'])
    assert hist(raw['paid_center_copy_histogram'])=={22:24}
    assert prime_result['unique_bases']==26380 and prime_result['current_frame_ids']==26750
    assert prime_result['all_remaining_factors_below_2_power_80']
    assert prime_result['prime_factors']==[2,3,5,7]
    assert prime_result['independent_entrances']==2279 and prime_result['bundled_unique_bases']==231
    assert hist(prime_result['entrance_rank_counts'])==hist(raw['auxiliary_entrance_rank_histogram'])
    m=5*raw['h'];v=raw['v'];R=raw['physical_R'];W=4*v+R;d=m*m
    H=hist(raw['five_stage_profile']['histogram']);E=sum(H.values());mass=sum(r*n for r,n in H.items())
    assert (m,W,E,mass,max(H))==(120,23683,495304,2837560,100)
    J=20*v+10*R+4*v;good=8*m*m+8;high=16*(d+1)**2;N=2*m
    weighted=5*f['weighted_additions']+6*v;unit=5*f['literal_unit_additions']+6*v
    payload=64*f['max_intermediate_row_l1']**3*b['max_intermediate_row_l1']**2
    assert payload==303094329841208644962256113408<2**98
    fallback=6*N*(N-1)+3*N+6*(N-1)
    assert fallback==346314<32*m*m==460800
    coefficient=unit+J*high+J*(W+24)+E*good+E*(128*N**3)+16*m**3+120+E+1
    assert coefficient==1568901757016837<2**80
    if global_result is not None:
        assert global_result['source_head']==HEAD
        assert global_result['scalar_projection_sha256']==EVENT and global_result['local_tagged_sha256']==TAGGED
        assert hist(global_result['paid_histogram'])==H and global_result['paid_calls']==E
        assert global_result['total_weighted_additions']==weighted and global_result['bridge_additions']==6*v
        assert global_result['terminal_exchange_stream_movements']==4*v
    route=route_template()
    p=HERE/'code/five_stage_bit_cost_20261009.py';spec=importlib.util.spec_from_file_location('portable_finite_moment',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    c=Q(704197288590873,10**18);lo,hi=mod.moment(dict(H),m,W,c,True)
    delta_tau=1-hi;delta1=1-Q(mass,m*W)-Q(1,10**16)*32*m*E/W
    assert delta_tau>Q(774,10**21) and delta1==Q(107421874442783,69383789062500000)>0
    assert Q(2*m**3,2**80)<Q(1,10**16) and Q(5,6)**3>Q(1,2)>Q(5,6)**4
    mathematics=math_result.get('mathematics',math_result)
    assert list(map(Q,mathematics['bit_moment_interval']))==[lo,hi]
    chain=[Q(384599,10**10)];gaps=[]
    for j in range(3):
        old=chain[-1];a=(1-c)*c+c*old
        ds=dict(atom=c-a,borrowing=1-a-c,remainder=1-a-c*(1-old),stock=1-c)
        assert old<a<c<1-a and min(ds.values())>0
        delta=min(ds.values());L=cutoff_log2(delta,1)
        assert Q(L)*delta**2>=36 and Q(L)*delta>=8
        gaps.append(dict(stage=j+1,gaps={k:str(x)for k,x in ds.items()},minimum_gap=str(delta),cutoff_log2_at_C_equals_1=str(L)))
        chain.append(a)
    assert list(map(Q,mathematics['ordinary_bootstrap_chain']))==chain
    controls=[]
    for name,test in [('zero cutoff gap',lambda:cutoff_log2(Q(0),1)),('negative primitive constant',lambda:cutoff_log2(Q(1,2),0))]:
        try:test()
        except AssertionError:controls.append(name)
        else:raise AssertionError('bad finite cutoff accepted')
    return dict(status='PASS_FRESH_PORTABLE_BIT_FINITE_ACCOUNTING_UNDER_RETAINED_PRIMITIVE_THEOREM',
        source_head=HEAD,public_theorem_and_code_pins=PINS,
        source_binding=dict(scalar_projection_sha256=EVENT,physical_tagged_sha256=TAGGED,global_lowering_checked=global_result is not None),
        primitive_contract=dict(q_fixed_before_width=True,eligible_prime='any fixed odd prime q>2^80',
            C_may_depend_on=['q','source_recipe','finite_bootstrap_level','retained_primitive_implementations'],
            C_independent_of=['n','w','ancestor_values','spectator_width_except_logical_volume'],
            exact_tapes='Complete high fibers batched; polynomial descriptor preparation amortized over q^w; spectator counters ripple; one extra copied work stream.',
            initialization_and_table_scans_charged=True,numeric_machine_constant_required=False),
        paid_inventory=dict(m=m,W=W,positive_rank_children=E,rank_mass=mass,weighted_additions=weighted,unit_expanded_additions=unit,
            bridge_additions=6*v,route_and_final_exchange_families=J,terminal_exchange_stream_movements=4*v,
            high_affine_factors=J*high,low_transposition_coefficient=J*(W+24),generic_wrappers=E*good,
            matrix_preparation_per_edge_per_low_class=128*N**3,copy_erase_episodes=120,copy_children_already_paid=True,
            fallback_children=32*m*m,physical_stock_roles=W+24,simultaneous_extra_work_streams=1,payload_prefix_upper=payload,payload_prefix_bits=98),
        rational_route=route,q_power_bound=dict(coefficient=coefficient,low_matrix_power=14400,strict_upper='q^14401',
            toll='C_primitive(q,source,j)*(1+B(q))*(n+w^(1-a_j))'),
        moment=dict(coarse=str(c),tau=str(1-c),delta_tau_lower=str(delta_tau),delta_linear=str(delta1),fallback_added_in_full=True),
        recurrence=dict(bound='A*(n+n^(1-c)*w^(1-a_j))',A='C*(1+1/delta_linear+1/delta_tau)',halving_degree=4,no_fourfold_moment_factor=True),
        bootstrap=dict(chain=list(map(str,chain)),ordinary=str(chain[-1]),gaps=gaps),
        finite_cutoff=dict(formula='e0(C)=2^ceil(max(1,36/delta^2,2*(4+ceil(log2(C)))/delta))',
            inequality='C*(1+log2(e))*e^(-delta)<=1/16 for e>=e0',
            next_constant='C_large+C_old*2^(L*(a_next-a_old))',small_widths='Use the previously completed ordinary supplier'),
        row_reserve=dict(log_q_bound='4*ceil(log2(max(2,n)))*(14400*w+1)+log_q(S_old_leaf)',coarse_coefficient=57604,
            outside_moment=True,restored_and_reused=True,one_outer_padding_factor_less_than=2,binary_padding_volume_factor_less_than='q^2'),
        rejected_controls=controls,scope='Fresh finite admission bill from current source outputs, under the pinned public exact-tape and completed-ordinary-leaf hypotheses; no numeric machine-time constant or hidden extra child.')
