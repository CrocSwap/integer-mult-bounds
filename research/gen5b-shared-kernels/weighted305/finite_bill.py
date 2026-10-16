"""Independent displayed finite-bill accounting for pinned PR305 candidates.

This charges the displayed invoice. It does not instantiate inherited primitive,
wrapper, or analytic constants hidden in C_full. Upstream code remains inert.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as F
import hashlib
import reproduce_pr305 as base

def ceil(x):return -((-x.numerator)//x.denominator)

def invoice(stock,calls,added):
    pins=base.read('expected/kernel-pins.json');m=120;v=1760;R=pins['physical_R'];T=60;N=240;d=m*m
    E=T*calls;weighted=T*(5*(pins['scalar_events']+added)+6*v);unit=T*(5*(pins['literal_unit_additions']+added)+6*v)
    J=T*(24*v+10*R);good=8*m*m+8;high=16*(d+1)**2;K=600*((stock-1)+R*120*815)
    coefficient=unit+J*high+J*(stock+24)+E*good+E*(128*N**3)+16*m**3+120*T+E+K+1
    assert coefficient<2**80 and K<2**40 and stock+24<2**80 and 2*m**3*10**16<2**80
    formula=base.SOURCE/'finite_check.py.txt';raw=formula.read_bytes()
    assert 'coefficient=unit+J*high+J*(stock+24)+E*good+E*(128*N**3)+16*m**3+120*T+E+K+1'in raw.decode()
    assert hashlib.sha256(raw).hexdigest()==base.read('MANIFEST.json')['files']['finite_check.py']
    return dict(literal_stock=stock,literal_children=E,gross_added_scalar_events_per_stage=added,
        weighted_additions_upper=weighted,unit_additions_upper=unit,route_families=J,
        normalizer_factor_bound=815,selector_calls_bound=K,displayed_finite_coefficient=coefficient,
        coefficient_bits=coefficient.bit_length(),coefficient_cap=2**80,coefficient_cap_strict_gap=2**80-coefficient,
        no_credit_taken_for_omitted_reads=True,primitive_chart_and_all_size_admission_replayed=False,
        pinned_finite_formula_sha256=hashlib.sha256(raw).hexdigest())

def bind(result,setup_pairs):
    pins=base.read('expected/kernel-pins.json');baseline=invoice(pins['literal_stock'],pins['priced_five_stage_calls'],0)
    finite=invoice(result['literal_stock'],result['calls'],2*setup_pairs)
    literal_mass=60*result['rank_mass'];assert 120*result['literal_stock']-literal_mass==264000
    finite.update(literal_rank_mass=literal_mass,max_bank_block_scalar=max(len(row['widths'])for row in result['packing_patterns']),baseline_displayed_coefficient=baseline['displayed_finite_coefficient'])
    assert finite['max_bank_block_scalar']==40
    delta_tau=1-result['bit_root_bracket']['lower_moment'][1]
    delta_linear=1-F(literal_mass,120*result['literal_stock'])-F(32*120*finite['literal_children'],10**16*result['literal_stock'])
    assert delta_tau>0 and delta_linear>0
    chain=result['assembly']['bootstrap_chain'];coarse=result['bit_root_bracket']['lower'];gaps=[]
    for stage,(prior,a)in enumerate(zip(chain,chain[1:]),1):
        slacks=dict(atom=coarse-a,borrowing=1-a-coarse,remainder=1-a-coarse*(1-prior),stock=1-coarse);delta=min(slacks.values());assert delta>0
        coefficient=finite['displayed_finite_coefficient'];cutoff=max(1,ceil(36/delta**2),ceil(F(2*(4+(coefficient-1).bit_length()))/delta))
        assert cutoff*delta**2>=36 and cutoff*delta>=2*(4+(coefficient-1).bit_length())
        gaps.append(dict(stage=stage,slacks=slacks,minimum=delta,displayed_coefficient_cutoff_log2=cutoff))
    finite.update(delta_tau_lower=delta_tau,delta_linear=delta_linear,bootstrap_gap_checks=gaps,
        cutoff_scope='Displayed fixed bill only. C_full still includes unspecified inherited primitive, wrapper, setup and previous ordinary-level constants; none are set to zero or claimed numerically measured.')
    return finite
