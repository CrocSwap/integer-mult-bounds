"""Unified changed finite bill for the 70-pivot union plus final12.

Closes changed chart, selector, scalar-cost and sink-aware payload obligations.
Original compiler, primitive, weighted-chart, routing and all-size contracts
remain explicit assumptions; their unspecified constants are not set to zero.
"""
from collections import Counter
from fractions import Fraction as F

import finite_bill as base
import source_data as sd
import bank_binding
from kernel70_pricing import integer_map, measured_kernel_delta, verify_composition


def run(chart, norm, math, bridge, banks=None, suffix=None, composition=None):
    sd.verify_all()
    measured_kernel_delta(bridge)
    assert chart['status'] == 'PASS_KERNEL70_PR300_FINAL12_CHANGED_CHARTS'
    assert chart['selection'] == math['selection'] == 'candidate70'
    assert chart['with_final12'] and math['with_final12']
    assert chart['source_head'] == math['source_head'] == sd.HEAD
    assert math['status'] == 'PASS_KERNEL70_PR300_FINAL12_EXACT_PRICING'
    if composition is None:
        import check_pr300_kernel70_composition
        composition = check_pr300_kernel70_composition.run()
    verify_composition(composition, math['local_histogram_delta'])
    assert math['additional_source']['sha256'] == sd.MANIFEST['files']['pr300/descent2-selection.json']['sha256']
    assert chart['first_frame_quotient_demands'] == bridge['members'] == 157
    assert chart['pivot_residual_demands'] == bridge['pivots'] == 70
    assert chart['donor_line_entrance_demands'] == bridge['distinct_donors'] == 87
    assert chart['final12_charts'] == 18
    programs = {p['program_id']: p for p in chart['factor_programs']}
    assert len(programs) == chart['charts']
    expected = {(p['role'], p['stream'], 'first_frame_quotient', p['first_dimension'] - 1)
                for p in bridge['paths']}
    expected.update((p['role'], p['stream'], 'pivot_residual' if p['kind'] == 'pivot' else 'donor_line_entrance',
                     23 if p['kind'] == 'pivot' else 1) for p in bridge['paths'])
    uses = chart['role_chart_uses']
    assert len(uses) == len(expected) == 314
    assert {(u['role'], u['stream'], u['kind'], u['rank']) for u in uses} == expected
    for u in uses:
        assert programs[u['program_id']]['residual_rank'] == u['rank']
    assert norm['status'] == 'PASS_CONSERVATIVE_SCALAR_PREFIX_BOUNDS'
    assert norm['selection'] in ('candidate70',)
    assert norm['setup_restore_pairs'] == bridge['setup_adds'] == bridge['restore_adds'] == 601
    pins = sd.read_json('expected/kernel-pins.json')
    forward = norm['forward']; inverse = norm['inverse']
    assert forward['reverse'] is False and inverse['reverse'] is True
    assert forward['inherited_bound'] == pins['forward_max_row_l1'] == 77985
    assert inverse['inherited_bound'] == pins['inverse_max_row_l1'] == 2475558
    for row in (forward, inverse):
        assert row['certified_new_bound'] == row['inherited_bound'] + row['max_added_majorant']
        assert row['max_added_source'] == 0
    assert forward['certified_new_bound'] == 191659 and inverse['certified_new_bound'] == 5356455
    # These guards specifically reject the superseded target-only majorant.
    sinks = sd.read_json('sink-selection.json')['sinks']
    assert norm['actual_sink_redirects'] == sum(s['forward_writes'] for s in sinks) == 14
    assert norm['target_majorant_edges'] == 681 and norm['target_majorant_acyclic_vertices'] == 908
    payload = 64 * forward['certified_new_bound']**3 * inverse['certified_new_bound']**2
    assert payload == norm['payload_bound'] == 12927738210344389271740351838400
    assert payload.bit_length() == norm['payload_bits'] == 104
    assert norm['retained_payload_cap_2_to104'] and payload < 2**104
    assert 2**104 - payload == 7354671393307281152206899447616
    if suffix is None:
        import check_complete_suffix
        suffix = check_complete_suffix.run()
    assert suffix['status'] == 'PASS_COMPLETE_SUFFIX_ALL_COLUMN_EQUALITY'
    assert suffix['source_head'] == sd.HEAD and suffix['unchanged_scalar_multiset']
    assert suffix['original_suffix_adds'] == suffix['modified_suffix_adds']
    if banks is None:
        import check_kernel70_bank_assignment
        banks = check_kernel70_bank_assignment.run()
    assert banks['status'] == 'PASS_UNIFIED_KERNEL70_CORETIME12_BANK_ASSIGNMENT'
    assert banks['new_shared_kernel_pivots'] == 70 and banks['helper_roles'] == pins['physical_R']
    assert banks['all_banks_full'] and banks['stages_have_disjoint_bank_namespaces']
    assert integer_map(banks['family_counts']) == {r: n // 60 for r, n in integer_map(math['packing']['demand']).items()}
    assert banks['banks_per_stage'] == math['packing']['feasible_bins'] == 161432
    bank_binding.check(banks, math)
    m = 120; R = pins['physical_R']; v = 1760; T = 60; d = m*m; N = 2*m
    stock = math['literal_stock']
    assert R == 15427 and stock == chart['literal_stock'] == banks['literal_stock'] == 1229560
    assert F(banks['unreplicated_stock']) == F(math['unreplicated_stock']) == F(stock, 60)
    assert math['calls'] == 483425 and math['rank_mass'] == 2454720
    E = T * math['calls']; mass = T * math['rank_mass']
    assert m * stock - mass == 264000
    # All 601 setup and 601 restore additions are charged. The 860 omitted
    # old compensation reads are deliberately not subtracted from this bound.
    added = bridge['setup_adds'] + bridge['restore_adds']
    weighted = T * (5 * (pins['scalar_events'] + added) + 6*v)
    unit = T * (5 * (pins['literal_unit_additions'] + added) + 6*v)
    J = T * (24*v + 10*R); good = 8*m*m + 8; high = 16*(d+1)**2
    bound = chart['combined_normalizer_factor_bound']
    assert bound == 815 and chart['max_changed_chart_factors'] <= pins['max_chart_factors'] == 576
    K = 600 * ((stock-1) + R*120*bound)
    assert K == chart['selector_calls_bound'] < 2**40
    coefficient = unit + J*high + J*(stock+24) + E*good + E*(128*N**3) + 16*m**3 + 120*T + E + K + 1
    assert coefficient == 90466979917115701
    assert coefficient < 2**80 and 2*m**3*10**16 < 2**80 and stock+24 < 2**80
    c = F(math['root_bracket'][0]); moment_upper = F(math['moment_interval'][1])
    delta_tau = 1 - moment_upper
    delta_linear = 1 - F(mass, m*stock) - F(32*m*E, 10**16*stock)
    assert delta_tau > 0 and delta_linear > 0
    chain = [F(384599, 10**10)]; gaps = []
    for stage in range(3):
        prior = chain[-1]; a = (1-c)*c + c*prior
        slacks = dict(atom=c-a, borrowing=1-a-c, remainder=1-a-c*(1-prior), stock=1-c)
        delta = min(slacks.values()); assert prior < a < c < 1-a and delta > 0
        L = base.cutoff(delta, coefficient)
        assert F(L)*delta**2 >= 36 and F(L)*delta >= 2*(4+(coefficient-1).bit_length())
        gaps.append(dict(stage=stage+1, slacks=slacks, minimum=delta,
                         cutoff_log2_at_displayed_coefficient=L))
        chain.append(a)
    assert chain == list(map(F, math['assembly']['bootstrap_chain']))
    max_bank_scalar = max(len(p['widths']) for p in math['packing']['patterns'])
    assert max_bank_scalar == banks['maximum_block_scalar'] == 60 <= m
    result = dict(status='PASS_UNIFIED_PR300_KERNEL70_FINAL12_FINITE_OBLIGATIONS_UNDER_RETAINED_INTERFACES',
                source_head=sd.HEAD, selection='candidate70', with_final12=True,
                gross_added_scalar_events_per_stage=added,
                omitted_reads_not_credited=bridge['prefix_compensation_reads_removed'],
                scalar_weighted_additions_upper=weighted, scalar_unit_additions_upper=unit,
                literal_children=E, literal_rank_mass=mass, literal_stock=stock,
                route_families=J, changed_chart_programs=chart['charts'],
                changed_role_chart_uses=314, pivot_residual_demands=70,
                max_changed_chart_factors=chart['max_changed_chart_factors'],
                max_changed_chart_numerator=chart['max_factor_numerator'],
                max_changed_chart_denominator=chart['max_factor_denominator'],
                normalizer_factor_bound=bound, bank_selector_calls=K,
                displayed_finite_coefficient=coefficient, coefficient_bits=coefficient.bit_length(),
                retained_coefficient_cap_bits=80,
                sink_aware_forward_norm=forward['certified_new_bound'],
                sink_aware_inverse_norm=inverse['certified_new_bound'],
                conservative_payload_upper=payload, payload_bits=payload.bit_length(),
                retained_payload_cap_bits=104, payload_strict_gap=2**104-payload, actual_sink_redirects=14,
                target_majorant_edges=681, target_majorant_acyclic_vertices=908,
                new_bank_block_scalars_up_to=max_bank_scalar,
                scalar_unit_reason='All chart factor numerators and denominators, and every block+1 scalar, are nonzero and smaller than the retained prime characteristic q>2^80.',
                bad_fallback_per_child=32*m*m, internal_row_coefficient=14401,
                external_row_coefficient=20161, ordinary_degree_gap=F(10**6)-F(51*20161,25),
                delta_tau_lower=delta_tau, delta_linear=delta_linear,
                bootstrap_chain=chain, bootstrap_gaps=gaps,
                cutoff_scope='Displayed fixed bill only. The retained theorem rule uses C_full, including inherited primitive, wrapper and earlier ordinary-level constants, whose values are not supplied or replaced by this check.',
                inherited_assumptions=[
                    'Pinned PR299 full unchanged bit decoder, original scalar bounds and stage admission.',
                    'Retained weighted-chart, prime-field, routing, cover, bank-normalizer and finite-compiler contracts.',
                    'Inherited setup, primitive, wrapper and earlier ordinary-level constants inside C_full.',
                    'Inherited all-size theorem and outer positive literal-gap and row-gap interfaces.'
                ], full_inherited_admission_replayed=False, all_size_theorem_verified=False)
    result['additional_source_head'] = composition['source_head']
    result['additional_source_pins'] = composition['input_sha256']
    result['pr300_composition_status'] = composition['status']
    result['inherited_assumptions'].append(
        'Pinned PR300 second-descent chronological/source-span admission and its unchanged chart/finite-compiler contracts; only the new composition is independently checked here.')
    return result
