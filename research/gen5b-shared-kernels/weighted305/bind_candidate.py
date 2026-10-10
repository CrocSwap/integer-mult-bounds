"""Bind exact PR305 pricing to independently produced changed-obligation receipts.

The bridge/norm certificates are fresh products of our separate authored
checkers; they are loaded as JSON and cross-checked here. No upstream program
is imported or executed. Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,sys
import reproduce_pr305 as base
from source_data import OUTPUT
import review_payload_cap
from price_witness import witness_delta
from price_candidate import price
from bank_receipt_binding import bind_banks
from check_candidate_charts import run as charts_run
from finite_bill import bind as finite_bind

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(label,candidate_path,bridge_path,norm_path,bank_receipt,bank_table):
    candidate_path=Path(candidate_path);base.verify_sources();c=json.loads(candidate_path.read_text())
    h,counts=witness_delta(candidate_path);n=counts['pivots'];sha=digest(candidate_path)
    bridge=json.loads(Path(bridge_path).read_text());norm=json.loads(Path(norm_path).read_text())
    assert bridge['status']=='PASS_PR305_SHARED_KERNEL_ALIAS_AND_PREFIX_BRIDGE'
    assert bridge['head']==c['source_head']==base.HEAD and bridge['candidate_sha256']==sha
    assert norm['head']==base.HEAD and norm['candidate_sha256']==sha
    assert bridge['source_pins_sha256']==digest(base.HERE/'inputs.json')
    assert norm['bridge_checker_sha256']==bridge['checker_sha256']
    assert bridge['selected_pivots']==n and bridge['selected_distinct_donors']==counts['distinct_donors'] and bridge['selected_streams']==counts['active_roles']
    assert bridge['all_column_formal_composition_forward_inverse'] and bridge['omitted_setup_and_restore_rejected'] and bridge['final_full_endpoints_checked']
    assert base.clean(base.histogram(bridge['local_histogram_delta']))==h and dict(base.histogram(bridge['residual_family_delta']))=={24:-n,23:n}
    result=price(h,{24:-n,23:n},{23:n},label=label+' bound to fresh independent PR305 bridge and norm receipts')
    result.update(status='PASS_PR305_CHANGED_OBLIGATIONS_UNDER_DECLARED_INTERFACES',source_head=base.HEAD,candidate_sha256=sha,
        witness_counts=counts,bridge_status=bridge['status'],bridge_scope=bridge['scope'],bridge_receipt_sha256=digest(bridge_path),norm_receipt_sha256=digest(norm_path),
        bridge_checker_source_sha256=bridge['checker_sha256'],norm_checker_source_sha256=norm['checker_sha256'])
    result['role_bank_binding']=bind_banks(result,Path(bank_receipt),Path(bank_table),'PASS_PR305_SHARED_KERNEL_ROLE_BANK_ASSIGNMENT')
    chart=charts_run(candidate_path,bridge,result['literal_stock'])
    assert chart['candidate_sha256']==sha and chart['pivot_residual_demands']==n
    assert len(chart['role_chart_uses'])==2*counts['active_roles']
    assert chart['max_changed_chart_factors']<=576 and chart['combined_normalizer_factor_bound']==815
    assert chart['max_factor_numerator']<2**80 and chart['max_factor_denominator']<2**80
    chart_path=OUTPUT/(label+'-charts-receipt.json');chart_path.write_text(json.dumps(base.ae.serial(chart),separators=(',',':'))+'\n')
    result['changed_charts']={k:v for k,v in chart.items()if k not in('factor_programs','role_chart_uses')};result['changed_chart_receipt_sha256']=digest(chart_path)
    pins=base.read('expected/kernel-pins.json');setup=counts['setup_pairs']
    assert setup==norm['setup_restore_pairs']==bridge['setup_adds']==bridge['restore_adds'] and norm['status']=='PASS_CONSERVATIVE_SCALAR_PREFIX_BOUNDS'
    for direction,key in [('forward','forward_max_row_l1'),('inverse','inverse_max_row_l1')]:
        row=norm[direction];assert row['inherited_bound']==pins[key] and row['max_added_source']==0
        assert row['certified_new_bound']==row['inherited_bound']+row['max_added_majorant']
    forward=norm['forward']['certified_new_bound'];inverse=norm['inverse']['certified_new_bound'];payload=64*forward**3*inverse**2
    assert payload==norm['payload_bound'] and payload.bit_length()==norm['payload_bits']
    assert not payload<2**104 and norm['retained_payload_cap_2_to104'] is False
    cap=review_payload_cap.run(forward,inverse,112)
    assert cap['payload']==payload and cap['original_cap_satisfied'] is False and cap['explicit_candidate_cap_satisfied']
    result['payload_cap_review']=cap
    assert norm['target_majorant_edges']==684 and norm['target_majorant_acyclic_vertices']==912
    assert norm['actual_sink_redirects']==16 and norm['sink_literal_words_verified']==8
    assert set(norm['sink_roles'])=={r['role']for r in base.read('sink-selection.json')['sinks']}
    result['norm_review']=dict(forward=forward,inverse=inverse,payload=payload,payload_bits=payload.bit_length(),original_cap_bits=104,original_cap_satisfied=False,
        explicit_candidate_cap_bits=112,explicit_candidate_cap_satisfied=True,explicit_candidate_cap_gap=2**112-payload,fresh_norm_receipt=norm)
    finite=finite_bind(result,setup);assert finite['selector_calls_bound']==chart['selector_calls_bound']
    finite['normalizer_status']='All changed chart programs freshly certified below retained576; exact normalizer815 bound retained.'
    result['finite_arithmetic']=finite
    result['scope']='All represented changed obligations are bound to this fixed candidate: fresh independent alias/prefix/frame bridge and conservative norm, exact constructed charts, re-enumerated role banks, explicit112-bit payload review, displayed finite formula, moment and47 rational inequalities. Original104 comparison is explicitly false. Unchanged full physical decoder, compiler and all-size interfaces remain assumptions. No upstream program executed.'
    return result

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    result=run(*sys.argv[1:]);label=sys.argv[1]
    (OUTPUT/(label+'-bound-receipt.json')).write_text(json.dumps(base.ae.serial(result),indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],kappa=result['assembly']['kappa_decimal'],charts=result['changed_charts']['charts'],finite_coefficient=result['finite_arithmetic']['displayed_finite_coefficient'],payload_bits=result['norm_review']['payload_bits'],old104=result['norm_review']['original_cap_satisfied'],new112=result['norm_review']['explicit_candidate_cap_satisfied']),indent=2))
