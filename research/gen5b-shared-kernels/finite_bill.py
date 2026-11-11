"""Original changed-obligation check for the retained finite bill.

Constants and formulas are independently transcribed from pinned PR299.
Unchanged all-size interfaces and original norm bounds remain hypotheses.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib
import source_data as sd

def ceil(x):return -((-x.numerator)//x.denominator)
def cutoff(delta,C):
    assert 0<delta<=1 and type(C)is int and C>0
    return max(1,ceil(36/delta**2),ceil(F(2*(4+(C-1).bit_length()),1)/delta))

def serial(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):serial(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [serial(v)for v in x]
    return x

def run(chart,norm,math):
    pins=sd.read_json('expected/kernel-pins.json')
    assert chart['charts']==18 and chart['max_changed_chart_factors']==142
    assert norm['status']=='PASS_EXACT_SCALAR_NORM_TRANSPORT'
    m=120;R=pins['physical_R'];v=1760;T=60;stock=math['literal_stock'];d=m*m;N=2*m
    assert R==15427 and stock==1229735
    E=T*math['calls'];mass=T*math['rank_mass'];assert m*stock-mass==264000
    assert math['calls']==482665 and math['rank_mass']==2455070
    weighted=T*(5*pins['scalar_events']+6*v)
    unit=T*(5*pins['literal_unit_additions']+6*v)
    J=T*(24*v+10*R);good=8*m*m+8;high=16*(d+1)**2
    K=600*((stock-1)+R*120*chart['combined_normalizer_factor_bound'])
    assert K==chart['selector_calls_bound']==905994200400<2**40
    coefficient=unit+J*high+J*(stock+24)+E*good+E*(128*N**3)+16*m**3+120*T+E+K+1
    assert coefficient<2**80 and 2*m**3*10**16<2**80 and stock+24<2**80
    # Use the independent conservative factor-two norm transport, even though
    # the bridge worker separately checks the stronger unchanged majorant.
    payload=64*(2*pins['forward_max_row_l1'])**3*(2*pins['inverse_max_row_l1'])**2
    assert payload==norm['payload_upper']<2**104
    c=F(math['root_bracket'][0]);moment_upper=F(math['moment_interval'][1])
    delta_tau=1-moment_upper
    delta_linear=1-F(mass,m*stock)-F(32*m*E,10**16*stock)
    assert delta_tau>0 and delta_linear>0
    chain=[F(384599,10**10)];gaps=[]
    for stage in range(3):
        prior=chain[-1];a=(1-c)*c+c*prior
        ds=dict(atom=c-a,borrowing=1-a-c,remainder=1-a-c*(1-prior),stock=1-c)
        delta=min(ds.values());assert prior<a<c<1-a and delta>0
        L=cutoff(delta,coefficient)
        assert F(L)*delta**2>=36 and F(L)*delta>=2*(4+(coefficient-1).bit_length())
        gaps.append(dict(stage=stage+1,slacks=ds,minimum=delta,cutoff_log2_at_displayed_coefficient=L))
        chain.append(a)
    assert chain==list(map(F,math['assembly']['bootstrap_chain']))
    # Pure rank-2 banks introduce sixty block-separation scalar choices.
    max_bank_scalar=max(len(p['widths'])for p in math['packing']['patterns'])
    assert max_bank_scalar==60<=m
    return dict(status='PASS_CHANGED_FINITE_OBLIGATIONS_UNDER_RETAINED_INTERFACES',
      scalar_weighted_additions=weighted,scalar_unit_additions=unit,literal_children=E,
      literal_rank_mass=mass,literal_stock=stock,route_families=J,
      new_chart_count=18,max_changed_chart_factors=142,max_changed_chart_numerator=11,max_changed_chart_denominator=9,
      new_bank_block_scalars_up_to=max_bank_scalar,
      scalar_unit_reason='Every block+1 scalar is at most60; chart factor numerators≤11 and denominators≤9. All are units in retained prime characteristic q>2^80.',
      normalizer_factor_bound=815,bank_selector_calls=K,displayed_finite_coefficient=coefficient,
      coefficient_bits=coefficient.bit_length(),retained_coefficient_cap_bits=80,
      conservative_payload_upper=payload,payload_bits=payload.bit_length(),retained_payload_cap_bits=104,
      bad_fallback_per_child=32*m*m,internal_row_coefficient=14401,external_row_coefficient=20161,
      ordinary_degree_gap=F(10**6)-F(51*20161,25),delta_tau_lower=delta_tau,delta_linear=delta_linear,
      bootstrap_chain=chain,bootstrap_gaps=gaps,
      cutoff_scope='Displayed fixed bill only. The retained theorem rule uses C_full including inherited primitive, wrapper and earlier ordinary-level constants; this check does not assign those unknown constants a value.',
      source_head=sd.HEAD,source_pins_sha256=sd.MANIFEST['files']['expected/kernel-pins.json']['sha256'])

