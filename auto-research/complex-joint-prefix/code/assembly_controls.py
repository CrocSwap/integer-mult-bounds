"""Independent admission controls for the two-provider width-seven native-complex assembly.

Prepared with OpenAI Codex assistance; Apache-2.0. Mutation receipts are
rebound to their new owner digest, so unrelated stale hashes cannot conceal
an incomplete width, provider, orientation, paid-profile or finite check.
The fresh physical replay remains a separate prerequisite.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path

if not __debug__:raise RuntimeError('Assertions required; refusing optimized admission controls')
P = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
digest = lambda x: hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def verify(owner_path, invoice_path, source_package):
    from assemble import assemble
    owner = json.loads(owner_path.read_text())
    invoice = json.loads(invoice_path.read_text())
    baseline = assemble(owner, invoice, sha(owner_path), sha(invoice_path))

    def empty_maps(o, i):
        i['strict_checks'] = {}
        i['providers'] = {}

    def missing_backward(o, i):
        del i['providers']['eightcold_eight']['local']['backward']

    def understated_stock(o, i):
        o['physical'] -= 1
        i['physical'] -= 1
        i['physical_stock_identity']['coefficient_work'] -= 1

    def changed_profile(o, i):
        o['paid_profile']['1'] += 2
        o['paid_profile']['2'] -= 1

    def changed_widths(o, i):
        widths = i['providers']['width7_eight']['widths']
        a, b = widths.index(4), widths.index(9)
        widths[a] += 1
        widths[b] -= 1

    def permuted_widths(o, i):
        widths = i['providers']['width7_eight']['widths']
        a, b = widths.index(4), widths.index(9)
        widths[a], widths[b] = widths[b], widths[a]

    def compensating_profiles(o, i):
        # Preserve the weighted aggregate for any nominated two-provider mix.
        from math import gcd
        p, q = i['providers']['width7_eight'], i['providers']['eightcold_eight']
        a,b=i['provider_counts']['width7_eight'],i['provider_counts']['eightcold_eight']
        common=gcd(a,b)
        p['paid_profile']['1'] += b//common
        q['paid_profile']['1'] -= a//common
        p['children'] += b//common
        q['children'] -= a//common

    def wrong_orientation(o, i):
        c = next(c for c in i['selected_calls'] if c['stage'] == 0)
        c['orientation'] = 'backward'
        p = i['providers'][c['provider_id']]
        z = p['local']['backward']
        c['program_sha256'] = p['program_hashes']['backward']
        for name in ('events', 'macros', 'real_component_primitives',
                     'coefficient_work_primitive_count', 'pre_wrappers', 'post_wrappers'):
            c[name] = z[name]
        i['selected_real_component_primitives'] = sum(c['real_component_primitives'] for c in i['selected_calls'])
        i['selected_coefficient_work_primitive_count'] = sum(c['coefficient_work_primitive_count'] for c in i['selected_calls'])

    def forged_program_hash(o, i):
        i['providers']['eightcold_eight']['program_hashes']['forward'] = '0' * 64
        for c in i['selected_calls']:
            if c['provider_id'] == 'eightcold_eight':
                c['program_sha256'] = '0' * 64

    def wrong_selected_call(o, i):
        c, d = next((c,d) for c in i['selected_calls'] for d in i['selected_calls']
                    if c['provider_id']=='eightcold_eight' and d['provider_id']=='width7_eight'
                    and c['replica']!=d['replica'])
        c['replica'], d['replica'] = d['replica'], c['replica']

    def understated_prefix(o, i):
        for p in i['providers'].values():
            for z in p['local'].values():
                z['prefix_bits'], z['prefix_l1'] = 1, '1'
        i['global_prefix_bits'] = 1 + 37 + 72 + 72 + 4

    def stale_plain_program(o, i):
        p = i['providers']['eightcold_eight']
        p['program_hashes'] = copy.deepcopy(i['providers']['width7_eight']['program_hashes'])
        for c in i['selected_calls']:
            if c['provider_id'] == 'eightcold_eight':
                c['program_sha256'] = p['program_hashes'][c['orientation']]

    def moved_providers(o, i):
        a = next(c for c in i['selected_calls'] if c['provider_id'] == 'eightcold_eight')
        b = next(c for c in i['selected_calls'] if c['provider_id'] == 'width7_eight')
        a['provider_id'], b['provider_id'] = b['provider_id'], a['provider_id']
        for c in (a, b):
            p = i['providers'][c['provider_id']]
            c['program_sha256'] = p['program_hashes'][c['orientation']]
            c['entering_helpers'], c['entrance_rank'] = p['entering_helpers'], p['entrance_rank']
            for name in ('events','macros','real_component_primitives','coefficient_work_primitive_count','pre_wrappers','post_wrappers'):
                c[name] = p['local'][c['orientation']][name]

    def reordered_calls(o, i):
        i['selected_calls'][0], i['selected_calls'][1] = i['selected_calls'][1], i['selected_calls'][0]

    def permuted_plain_widths(o, i):
        widths = i['providers']['eightcold_eight']['widths']
        a, b = widths.index(4), widths.index(5)
        widths[a], widths[b] = widths[b], widths[a]

    def stale_plain_profile(o, i):
        p = i['providers']['eightcold_eight']
        p['paid_profile'] = copy.deepcopy(i['providers']['width7_eight']['paid_profile'])
        p['children'] = sum(p['paid_profile'].values())

    controls = [
        ('empty_certification_maps', empty_maps),
        ('missing_provider_backward_orientation', missing_backward),
        ('failed_invoice_status', lambda o, i: i.__setitem__('status', 'FAIL')),
        ('nonboolean_precision_check', lambda o, i: i['strict_checks'].__setitem__('precision', 'true')),
        ('wrong_owner_role_count', lambda o, i: o.__setitem__('actual_helper_owner_charts', 36287)),
        ('understated_physical_stock', understated_stock),
        ('changed_profile_same_rank_mass', changed_profile),
        ('insufficient_finite_C0', lambda o, i: i['finite'].__setitem__('required_C0_bits', 210001)),
        ('unpaid_scalar_primitive', lambda o, i: i['providers']['eightcold_eight']['local']['forward'].__setitem__('real_component_primitives', i['providers']['eightcold_eight']['local']['forward']['real_component_primitives']-8)),
        ('wrong_local_artifact_binding', lambda o, i: i['providers']['eightcold_eight']['artifacts'].__setitem__('LOCAL-PROGRAMS.json.gz', '0' * 64)),
        ('false_dirty_restoration', lambda o, i: i['providers']['eightcold_eight']['local']['backward'].__setitem__('all_dirty_helper_columns_restored', False)),
        ('missing_finite_check', lambda o, i: i['strict_checks'].pop('halving')),
        ('width_inventory_wrong_same_total', changed_widths),
        ('width_order_wrong_same_inventory', permuted_widths),
        ('compensating_false_provider_profiles', compensating_profiles),
        ('wrong_reflected_orientation_selfconsistent_totals', wrong_orientation),
        ('forged_provider_and_call_program_hash', forged_program_hash),
        ('plain_provider_at_wrong_call', wrong_selected_call),
        ('wrong_declared_provider_count', lambda o, i: i['provider_counts'].__setitem__('eightcold_eight', i['provider_counts']['eightcold_eight']+1)),
        ('missing_selected_call', lambda o, i: i['selected_calls'].pop()),
        ('wrong_selected_primitive_sum', lambda o, i: i.__setitem__('selected_real_component_primitives', i['selected_real_component_primitives'] - 1)),
        ('wrong_selected_coefficient_work_sum', lambda o, i: i.__setitem__('selected_coefficient_work_primitive_count', i['selected_coefficient_work_primitive_count'] - 1)),
        ('unpaid_wrapper_factors', lambda o, i: i.__setitem__('wrapper_elementary_factors_charged', i['wrapper_elementary_factors_charged'] - 144)),
        ('wrong_local_compiler', lambda o, i: i['providers']['eightcold_eight'].__setitem__('compiler', 1)),
        ('wrong_global_compiler', lambda o, i: i.__setitem__('compiler', 1)),
        ('wrong_local_adapter_charge', lambda o, i: i['providers']['eightcold_eight'].__setitem__('local_adapters', 1)),
        ('wrong_global_adapter_maximum', lambda o, i: i.__setitem__('local_adapters', 1)),
        ('wrong_local_primitive_bound', lambda o, i: i['providers']['eightcold_eight'].__setitem__('local_primitive_bound', 1)),
        ('understated_exact_prefix_and_global_sum', understated_prefix),
        ('wrong_global_prefix_sum', lambda o, i: i.__setitem__('global_prefix_bits', 224)),
        ('wrong_row_prefix_reserve', lambda o, i: i.__setitem__('row_prefix_extra', 0)),
        ('wrong_parent_geometry_charge', lambda o, i: i.__setitem__('unhosted_pervertex', 1)),
        ('wrong_rebased_geometry_charge', lambda o, i: i.__setitem__('hosted_rebased_pervertex', 1)),
        ('wrong_complete_pervertex_envelope', lambda o, i: i.__setitem__('conservative_pervertex_used', 1)),
        ('wrong_prior_added_complete_invoice', lambda o, i: i['retained_prior_overcharge'].__setitem__('added_complete_new_pervertex', 1)),
        ('wrong_finite_router_bits', lambda o, i: i['finite'].__setitem__('router_bits', 1)),
        ('wrong_finite_literal_bits', lambda o, i: i['finite'].__setitem__('literal_bits', 1)),
        ('wrong_finite_physical_stock_bits', lambda o, i: i['finite'].__setitem__('physical_stock_bits', 1)),
        ('wrong_finite_row_coefficient', lambda o, i: i['finite'].__setitem__('physical_row_coefficient', 1)),
    ]
    controls.extend([
        ('missing_plain_provider', lambda o, i: i['providers'].pop('eightcold_eight')),
        ('missing_width7_provider_backward', lambda o, i: i['providers']['width7_eight']['local'].pop('backward')),
        ('stale_plain_program_and_consistent_selected_hashes', stale_plain_program),
        ('stale_plain_profile_with_consistent_child_total', stale_plain_profile),
        ('reordered_complete_calls', reordered_calls),
        ('relocated_plain_and_width7_providers_same_counts', moved_providers),
        ('plain_provider_widths_permuted_same_inventory', permuted_plain_widths),
        ('understated_explicit_idle_remainders', lambda o, i: o.__setitem__('explicit_idle_remainder_children', o['explicit_idle_remainder_children']-1)),
        ('understated_actual_chart_types', lambda o, i: o.__setitem__('actual_73column_sigmas', o['actual_73column_sigmas']-1)),
        ('wrong_cross_replica_role_count', lambda o, i: o.__setitem__('cross_replica_helper_roles', o['cross_replica_helper_roles']-1)),
    ])
    def cold_width_permutation(o, i):
        w = i['providers']['eightcold_eight']['widths']
        j = w.index(9)
        w[270], w[j] = w[j], w[270]
    def no_cold_wrappers(o, i):
        for p in i['providers'].values():
            p['entering_helpers'] = 212
            for z in p['local'].values():z['pre_wrappers'] = z['post_wrappers'] = 212
        for c in i['selected_calls']:
            c['entering_helpers'] = c['pre_wrappers'] = c['post_wrappers'] = 212
        i['wrapper_elementary_factors_charged'] = 72*424*144
    def synchronized_forged_recipe(o, i):
        pid = 'eightcold_eight';name = 'CLIFFORD-RECIPES.json'
        i['providers'][pid]['artifacts'][name] = '0'*64
        o['source_artifacts']['providers/'+pid+'/'+name] = '0'*64
    def synchronized_forged_phase_semantics(o, i):
        pid = 'eightcold_eight'
        i['providers'][pid]['semantic_artifact_sha256']['CLIFFORD-REVIEW.json'] = '0'*64
        o['provider_artifact_semantic_sha256'][pid]['CLIFFORD-REVIEW.json'] = '0'*64
        o['provider_phase_semantic_sha256'][pid] = i['provider_phase_semantic_sha256'][pid] = '0'*64
    controls.extend([
        ('synchronized_forged_phase_review_semantics', synchronized_forged_phase_semantics),
        ('cold_helper_width_permuted_same_inventory', cold_width_permutation),
        ('old_no_cold_wrapper_counts_selfconsistent', no_cold_wrappers),
        ('synchronized_forged_source_recipe_hash', synchronized_forged_recipe),
    ])
    for helper in (271, 282, 283, 294, 295, 306, 307):
        def move_extra_width(o, i, helper=helper):
            widths = i['providers']['width7_eight']['widths']
            other = widths.index(9)
            widths[helper], widths[other] = widths[other], widths[helper]
        controls.append(('extra_kernel_width_swap_' + str(helper), move_extra_width))
    for helper in [262, 263, 264, 265, 274, 275, 276, 277, 310, 311, 312, 313, 314, 315, 316, 317, 322, 323, 324, 325, 326, 327, 328, 329, 338, 339, 340, 341, 350, 351, 352, 353]:
        def swap_width7(o, i, helper=helper):
            widths = i['providers']['width7_eight']['widths']
            other = widths.index(8)
            widths[helper], widths[other] = widths[other], widths[helper]
        controls.append(('width7_entrance_width_swap_' + str(helper), swap_width7))
    rejected = []
    for name, mutate in controls:
        o, i = copy.deepcopy(owner), copy.deepcopy(invoice)
        mutate(o, i)
        oh = digest(o)
        i['owner_audit_sha256'] = oh
        try:
            assemble(o, i, oh, digest(i))
        except (AssertionError, KeyError):
            rejected.append(name)
        else:
            raise AssertionError('Invalid admission receipt accepted: ' + name)
    try:
        assemble(owner, invoice, '0' * 64, sha(invoice_path))
    except AssertionError:
        rejected.append('wrong_owner_receipt_hash')
    else:
        raise AssertionError('Wrong owner digest accepted')
    assert len(rejected) == 93
    assert baseline['controls'] == ['next_grid', 'zero_eta', 'zero_beta', 'unit_beta']
    assert baseline['conservative_controls'] == baseline['controls']
    assert baseline['surcharge_model'] == {'complex': False, 'bit': True}
    assert len(baseline['model_controls']) == 2
    return dict(
        status='PASS_EXACT_MIXED_048_ALLCOLD_NATIVE_ASSEMBLY_ADMISSION_NEGATIVE_CONTROLS',
        valid_receipt_kappa=baseline['kappa'],
        input_sha256=baseline['input_sha256'],
        assembler_sha256=sha(P / 'assemble.py'),
        rejected_controls=rejected,
        exact_outer_controls=baseline['controls'],
        conservative_outer_controls=baseline['conservative_controls'],
        recurrence_model_controls=baseline['model_controls'],
        scope='Complete receipt schema; ordered widths and both reflected providers; exact program, work and paid-profile binding; independently recounted compiler, conservative envelope and finite inequalities. Does not replace fresh physical replay.',
    )


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-package', type=Path, default=P.parent)
    ap.add_argument('--owner', type=Path, required=True)
    ap.add_argument('--invoice', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    assert not a.out.exists()
    result = verify(a.owner, a.invoice, a.source_package)
    a.out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], len(result['rejected_controls']))
