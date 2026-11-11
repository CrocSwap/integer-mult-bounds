"""Separate full changed-obligation arithmetic for a bounded PR275 candidate.

Imports only our newly authored bridge/norm programs and pure arithmetic.
Upstream source remains inert JSON/text. Original104-bit comparison is retained
as false when an explicitly reviewed fixed112-bit candidate bound is used.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib,importlib.util,json,sys
import reproduce_pr275 as base
from source_data import OUTPUT
import review_payload_cap
from price_candidate import price
from bank_receipt_binding import bind_banks
from check_candidate_charts import run as charts_run

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def ceil(x):return -((-x.numerator)//x.denominator)

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module

def invoice(stock,calls,added):
    pins=base.read('expected/kernel-pins.json');m=120;v=1760;R=pins['physical_R'];T=60;N=240;d=m*m
    E=T*calls;weighted=T*(5*(pins['scalar_events']+added)+6*v);unit=T*(5*(pins['literal_unit_additions']+added)+6*v)
    J=T*(24*v+10*R);good=8*m*m+8;high=16*(d+1)**2;K=600*((stock-1)+R*120*815)
    coefficient=unit+J*high+J*(stock+24)+E*good+E*(128*N**3)+16*m**3+120*T+E+K+1
    assert coefficient<2**80 and K<2**40 and stock+24<2**80 and 2*m**3*10**16<2**80
    return dict(literal_stock=stock,literal_children=E,gross_added_scalar_events_per_stage=added,
        weighted_additions_upper=weighted,unit_additions_upper=unit,route_families=J,
        normalizer_factor_bound=815,selector_calls_bound=K,displayed_finite_coefficient=coefficient,
        coefficient_bits=coefficient.bit_length(),coefficient_cap=2**80,coefficient_cap_strict_gap=2**80-coefficient,
        no_credit_taken_for_omitted_reads=True,primitive_chart_and_all_size_admission_replayed=False)

def run(label,candidate_path,bridge_dir,bank_receipt,bank_table):
    base.verify_sources();candidate_path=Path(candidate_path);bridge_dir=Path(bridge_dir)
    witness=json.loads(candidate_path.read_text());n=len(witness['entries'])
    import check_bridge as bridge_module,check_scalar_bounds as norm_module
    from cases import CASES
    case=next(k for k,v in CASES.items()if v['sha256']==digest(candidate_path))
    bridge_module.configure(case)
    assert Path(bridge_module.CAND).resolve()==candidate_path.resolve()
    code_hashes={name:digest(base.HERE/name)for name in('check_bridge.py','check_scalar_bounds.py')}
    bridge=bridge_module.run();norm=norm_module.run(candidate_path)
    assert code_hashes=={name:digest(base.HERE/name)for name in code_hashes}
    assert bridge['head']==witness['source_head']==base.HEAD and bridge['selected_pivots']==n
    assert bridge['all_column_formal_composition_forward_inverse'] and bridge['omitted_setup_and_restore_rejected'] and bridge['final_full_endpoints_checked']
    H=base.histogram(bridge['local_histogram_delta']);R=base.histogram(bridge['residual_family_delta'])
    assert dict(R)=={24:-n,23:n} and base.mass(H)==-n
    result=price(H,R,{23:n},label=label+' bound to freshly rerun exact bridge/norm; no final12')
    result['status']='PASS_PR275_CHANGED_OBLIGATIONS_UNDER_DECLARED_INTERFACES'
    result['source_head']=base.HEAD;result['candidate_sha256']=digest(candidate_path)
    result['bridge_code_sha256']=code_hashes;result['bridge_status']=bridge['status'];result['bridge_scope']=bridge['scope']
    result['role_bank_binding']=bind_banks(result,Path(bank_receipt),Path(bank_table),'PASS_PR275_SHARED_KERNEL_ROLE_BANK_ASSIGNMENT')
    chart=charts_run(candidate_path,bridge,result['literal_stock'])
    assert chart['candidate_sha256']==result['candidate_sha256'] and chart['pivot_residual_demands']==n
    assert len(chart['role_chart_uses'])==2*bridge['selected_streams']
    assert chart['max_changed_chart_factors']<=576 and chart['combined_normalizer_factor_bound']==815
    assert chart['max_factor_numerator']<2**80 and chart['max_factor_denominator']<2**80
    from source_data import OUTPUT
    chart_path=OUTPUT/(label+'-charts-receipt.json');chart_path.write_text(json.dumps(base.ae.serial(chart),separators=(',',':'))+'\n')
    result['changed_charts']={k:v for k,v in chart.items()if k not in('factor_programs','role_chart_uses')}
    result['changed_chart_receipt_sha256']=digest(chart_path)
    pins=base.read('expected/kernel-pins.json');setup=sum(len(e['donors'])for e in witness['entries'])
    assert setup==norm['setup_restore_pairs'] and norm['status']=='PASS_CONSERVATIVE_SCALAR_PREFIX_BOUNDS'
    for direction,key in [('forward','forward_max_row_l1'),('inverse','inverse_max_row_l1')]:
        row=norm[direction];assert row['inherited_bound']==pins[key] and row['max_added_source']==0
        assert row['certified_new_bound']==row['inherited_bound']+row['max_added_majorant']
    forward=norm['forward']['certified_new_bound'];inverse=norm['inverse']['certified_new_bound'];payload=64*forward**3*inverse**2
    assert payload==norm['payload_bound'] and payload.bit_length()==norm['payload_bits']
    if case=='166':
        assert not payload<2**104 and norm['retained_payload_cap_2_to104'] is False
        cap=review_payload_cap.run(forward,inverse,112)
        assert cap['payload']==payload and cap['original_cap_satisfied'] is False and cap['explicit_candidate_cap_satisfied']
        result['payload_cap_review']=cap
        cap_bits=112
    else:
        assert payload<2**104 and norm['retained_payload_cap_2_to104'] is True
        cap_bits=104
    assert norm['target_majorant_edges']==681 and norm['target_majorant_acyclic_vertices']==908 and norm['actual_sink_redirects']==14
    result['norm_review']=dict(forward=forward,inverse=inverse,payload=payload,payload_bits=payload.bit_length(),
        original_cap_bits=104,original_cap_satisfied=payload<2**104,explicit_candidate_cap_bits=cap_bits,
        explicit_candidate_cap_satisfied=True,explicit_candidate_cap_gap=2**cap_bits-payload,fresh_norm_receipt=norm)
    baseline=invoice(pins['literal_stock'],pins['priced_five_stage_calls'],0);assert baseline['displayed_finite_coefficient']==90322316339049601
    finite=invoice(result['literal_stock'],result['calls'],2*setup)
    assert finite['selector_calls_bound']==chart['selector_calls_bound']
    literal_mass=60*result['rank_mass'];assert 120*result['literal_stock']-literal_mass==264000
    finite.update(literal_rank_mass=literal_mass,max_bank_block_scalar=max(len(row['widths'])for row in result['packing_patterns']),
        normalizer_status='All changed chart programs freshly certified below retained576; exact normalizer815 bound retained.',
        baseline_displayed_coefficient=baseline['displayed_finite_coefficient'])
    assert finite['max_bank_block_scalar']==40
    formula=base.SOURCE/'finite_check.py.txt';assert 'coefficient=unit+J*high+J*(stock+24)+E*good+E*(128*N**3)+16*m**3+120*T+E+K+1'in formula.read_text()
    finite['pinned_finite_formula_sha256']=digest(formula)
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
    result['finite_arithmetic']=finite
    result['scope']='All changed obligations represented here are independently recomputed and bound to the fixed candidate: alias/prefix/frame bridge, charts, role banks, conservative norm, explicit case-specific numeric payload bound, displayed finite formula, moment and47 rational inequalities. Original104 comparison is retained explicitly, and fails for166. Unchanged full physical decoder, compiler and all-size interfaces remain assumptions; no upstream program executed.'
    return result

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    label,candidate,bridge,banks,table=sys.argv[1:]
    result=run(label,candidate,bridge,banks,table)
    (OUTPUT/(label+'-bound-receipt.json')).write_text(json.dumps(base.ae.serial(result),indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],kappa=result['assembly']['kappa_decimal'],charts=result['changed_charts']['charts'],
        finite_coefficient=result['finite_arithmetic']['displayed_finite_coefficient'],payload_bits=result['norm_review']['payload_bits'],
        old104=result['norm_review']['original_cap_satisfied'],new112=result['norm_review']['explicit_candidate_cap_satisfied']),indent=2))
