"""Independent admission controls for the N-provider native-complex assembly (per-provider controls).

Prepared with OpenAI Codex assistance; Apache-2.0. Mutation receipts are
rebound to their new owner digest, so unrelated stale hashes cannot conceal
an incomplete width, provider, orientation, paid-profile or finite check.
The fresh physical replay remains a separate prerequisite.
"""
import argparse
import copy
import itertools
import math
import hashlib
import json
import os
from pathlib import Path
import sys as _s,pathlib as _p;_s.path.insert(0,str(_p.Path(__file__).resolve().parent))
from witness import *

assert __debug__, 'Assertions required'
P = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
digest = lambda x: hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def verify(owner_path, invoice_path, source_package):
    os.environ['GAIN_PR564_SOURCE'] = str(source_package.resolve())
    from assemble import assemble
    owner = json.loads(owner_path.read_text())
    invoice = json.loads(invoice_path.read_text())
    baseline = assemble(owner, invoice, sha(owner_path), sha(invoice_path))

    def empty_maps(o, i):
        i['strict_checks'] = {}
        i['providers'] = {}

    def understated_stock(o, i):
        o['physical'] -= 1
        i['physical'] -= 1
        i['physical_stock_identity']['coefficient_work'] -= 1

    def changed_profile(o, i):
        o['paid_profile']['1'] += 2
        o['paid_profile']['2'] -= 1

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

    def understated_prefix(o, i):
        for p in i['providers'].values():
            for z in p['local'].values():
                z['prefix_bits'], z['prefix_l1'] = 1, '1'
        i['global_prefix_bits'] = 1 + 37 + 333 + 333 + 4

    def reordered_calls(o, i):
        i['selected_calls'][0], i['selected_calls'][1] = i['selected_calls'][1], i['selected_calls'][0]

    def no_cold_wrappers(o, i):
        for p in i['providers'].values():
            p['entering_helpers'] -= 4
            for z in p['local'].values():z['pre_wrappers'] = z['post_wrappers'] = p['entering_helpers']
        for c in i['selected_calls']:
            c['entering_helpers'] = c['pre_wrappers'] = c['post_wrappers'] = i['providers'][c['provider_id']]['entering_helpers']
        i['wrapper_elementary_factors_charged'] = sum(2*c['pre_wrappers'] for c in i['selected_calls'])*i['factors_per_wrapper']

    controls = [
        ('empty_certification_maps', empty_maps),
        ('failed_invoice_status', lambda o, i: i.__setitem__('status', 'FAIL')),
        ('nonboolean_precision_check', lambda o, i: i['strict_checks'].__setitem__('precision', 'true')),
        ('wrong_owner_role_count', lambda o, i: o.__setitem__('actual_helper_owner_charts', o['actual_helper_owner_charts'] - 1)),
        ('understated_physical_stock', understated_stock),
        ('changed_profile_same_rank_mass', changed_profile),
        ('insufficient_finite_C0', lambda o, i: i['finite'].__setitem__('required_C0_bits', 210001)),
        ('missing_finite_check', lambda o, i: i['strict_checks'].pop('halving')),
        ('wrong_reflected_orientation_selfconsistent_totals', wrong_orientation),
        ('missing_selected_call', lambda o, i: i['selected_calls'].pop()),
        ('wrong_selected_primitive_sum', lambda o, i: i.__setitem__('selected_real_component_primitives', i['selected_real_component_primitives'] - 1)),
        ('wrong_selected_coefficient_work_sum', lambda o, i: i.__setitem__('selected_coefficient_work_primitive_count', i['selected_coefficient_work_primitive_count'] - 1)),
        ('unpaid_wrapper_factors', lambda o, i: i.__setitem__('wrapper_elementary_factors_charged', i['wrapper_elementary_factors_charged'] - 144)),
        ('wrong_global_compiler', lambda o, i: i.__setitem__('compiler', 1)),
        ('wrong_global_adapter_maximum', lambda o, i: i.__setitem__('local_adapters', 1)),
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
        ('reordered_complete_calls', reordered_calls),
        ('understated_explicit_idle_remainders', lambda o, i: o.__setitem__('explicit_idle_remainder_children', o['explicit_idle_remainder_children']-1)),
        ('understated_actual_chart_types', lambda o, i: o.__setitem__('actual_73column_sigmas', o['actual_73column_sigmas']-1)),
        ('wrong_cross_replica_role_count', lambda o, i: o.__setitem__('cross_replica_helper_roles', o['cross_replica_helper_roles']-1)),
        ('old_no_cold_wrapper_counts_selfconsistent', no_cold_wrappers),
    ]

    def resync(i, c):
        p = i['providers'][c['provider_id']]
        c['program_sha256'] = p['program_hashes'][c['orientation']]
        c['entering_helpers'], c['entrance_rank'] = p['entering_helpers'], p['entrance_rank']
        for name in ('events','macros','real_component_primitives','coefficient_work_primitive_count','pre_wrappers','post_wrappers'):
            c[name] = p['local'][c['orientation']][name]

    # Every provider gets the full per-provider control set, substituting a partner provider where needed.
    for P in PIDS:
        Qp = partner(P) if len(PIDS)>1 else '__unregistered__'
        widths = invoice['providers'][P]['widths']

        def forged_program_hash(o, i, P=P):
            i['providers'][P]['program_hashes']['forward'] = '0' * 64
            for c in i['selected_calls']:
                if c['provider_id'] == P:
                    c['program_sha256'] = '0' * 64

        def wrong_selected_call(o, i, P=P):
            c = next(c for c in i['selected_calls'] if c['provider_id'] == P)
            d = next(d for d in i['selected_calls'] if d is not c and (d['provider_id'] != P or len(PIDS)==1) and (d['stage'] - c['stage']) % 2 == 0)
            c['stage'], d['stage'], c['replica'], d['replica'] = d['stage'], c['stage'], d['replica'], c['replica']

        def stale_program(o, i, P=P, Qp=Qp):
            p = i['providers'][P]
            p['program_hashes'] = copy.deepcopy(i['providers'][Qp]['program_hashes'])
            for c in i['selected_calls']:
                if c['provider_id'] == P:
                    c['program_sha256'] = p['program_hashes'][c['orientation']]

        def stale_profile(o, i, P=P, Qp=Qp):
            p = i['providers'][P]
            p['paid_profile'] = copy.deepcopy(i['providers'][Qp]['paid_profile'])
            p['children'] = sum(p['paid_profile'].values())

        def moved(o, i, P=P):
            a = next(c for c in i['selected_calls'] if c['provider_id'] == P)
            b = next(c for c in i['selected_calls'] if c['provider_id'] != P and c['orientation'] == a['orientation'])
            a['provider_id'], b['provider_id'] = b['provider_id'], a['provider_id']
            resync(i, a); resync(i, b)

        def compensating(o, i, P=P, Qp=Qp):
            # Two dishonest profiles that cancel exactly in the dispatch-weighted aggregate.
            g = math.gcd(COUNTS[P], COUNTS[Qp]); dp, dq = COUNTS[Qp] // g, COUNTS[P] // g
            p, q = i['providers'][P], i['providers'][Qp]
            p['paid_profile']['1'] += dp; q['paid_profile']['1'] -= dq
            p['children'] += dp; q['children'] -= dq

        def forged_recipe(o, i, P=P):
            name = 'CLIFFORD-RECIPES.json'
            i['providers'][P]['artifacts'][name] = '0'*64
            o['source_artifacts']['providers/'+P+'/'+name] = '0'*64

        def forged_phase(o, i, P=P):
            i['providers'][P]['semantic_artifact_sha256']['CLIFFORD-REVIEW.json'] = '0'*64
            o['provider_phase_semantic_sha256'][P] = i['provider_phase_semantic_sha256'][P] = '0'*64

        controls += [
            (P + ':missing_provider', lambda o, i, P=P: i['providers'].pop(P)),
            (P + ':missing_backward_orientation', lambda o, i, P=P: i['providers'][P]['local'].pop('backward')),
            (P + ':unpaid_scalar_primitive', lambda o, i, P=P: i['providers'][P]['local']['forward'].__setitem__('real_component_primitives', i['providers'][P]['local']['forward']['real_component_primitives'] - 1)),
            (P + ':wrong_local_artifact_binding', lambda o, i, P=P: i['providers'][P]['artifacts'].__setitem__('LOCAL-PROGRAMS.json.gz', '0' * 64)),
            (P + ':false_dirty_restoration', lambda o, i, P=P: i['providers'][P]['local']['backward'].__setitem__('all_dirty_helper_columns_restored', False)),
            (P + ':wrong_declared_provider_count', lambda o, i, P=P: i['provider_counts'].__setitem__(P, i['provider_counts'][P] + 1)),
            (P + ':wrong_local_compiler', lambda o, i, P=P: i['providers'][P].__setitem__('compiler', 1)),
            (P + ':wrong_local_adapter_charge', lambda o, i, P=P: i['providers'][P].__setitem__('local_adapters', 1)),
            (P + ':wrong_local_primitive_bound', lambda o, i, P=P: i['providers'][P].__setitem__('local_primitive_bound', 1)),
            (P + ':forged_provider_and_call_program_hash', forged_program_hash),
            (P + ':provider_at_wrong_call', wrong_selected_call),
            (P + ':stale_partner_program_consistent_call_hashes', stale_program),
            (P + ':stale_partner_profile_consistent_child_total', stale_profile),
            (P + ':relocated_against_partner_same_counts', moved),
            (P + ':compensating_false_profiles_with_' + Qp, compensating),
            (P + ':synchronized_forged_source_recipe_hash', forged_recipe),
            (P + ':synchronized_forged_phase_review_semantics', forged_phase),
        ]
        if len(PIDS)==1:
            # Cross-provider substitutions require a second actual supplier.
            # All single-provider program, phase, profile and dispatch bindings
            # retain their direct mutations above and in the controller audit.
            partner_only = {P+':stale_partner_program_consistent_call_hashes',
                            P+':stale_partner_profile_consistent_child_total',
                            P+':relocated_against_partner_same_counts',
                            P+':compensating_false_profiles_with_'+Qp}
            controls = [(name, fn) for name, fn in controls if name not in partner_only]
        # Width order and inventory: swap the first helper of every pair of distinct widths (same inventory),
        # and shift one unit between them (same total).
        first = {}
        for h, w in enumerate(widths):
            first.setdefault(w, h)
        for wa, wb in itertools.combinations(sorted(first), 2):
            def swap(o, i, P=P, a=first[wa], b=first[wb]):
                w = i['providers'][P]['widths']; w[a], w[b] = w[b], w[a]
            def shift(o, i, P=P, a=first[wa], b=first[wb]):
                w = i['providers'][P]['widths']; w[a] += 1; w[b] -= 1
            controls.append((P + ':width_order_swap_%d_%d' % (wa, wb), swap))
            controls.append((P + ':width_inventory_shift_%d_%d' % (wa, wb), shift))
        for h in SPOT:
            def cold_swap(o, i, P=P, h=h):
                w = i['providers'][P]['widths']; j = w.index(9 if w[h] != 9 else 8); w[h], w[j] = w[j], w[h]   # never the identity
            controls.append((P + ':cold_helper_width_swap_%d' % h, cold_swap))
    rejected = []
    accepted = []
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
            # Discovery has no pinned values to reject spec-only mutations; the strict run must reject every control.
            if not DISCOVER:
                raise AssertionError('Invalid admission receipt accepted: ' + name)
            accepted.append(name)
    try:
        assemble(owner, invoice, '0' * 64, sha(invoice_path))
    except AssertionError:
        rejected.append('wrong_owner_receipt_hash')
    else:
        raise AssertionError('Wrong owner digest accepted')
    pin('expected.assembly_controls_rejected', len(rejected))
    assert baseline['controls'] == ['next_grid', 'zero_eta', 'zero_beta', 'unit_beta']
    assert baseline['conservative_controls'] == baseline['controls']
    assert baseline['surcharge_model'] == {'complex': False, 'bit': True}
    assert len(baseline['model_controls']) == 2
    return dict(
        status='PASS_EXACT_MIXED_048_ALLCOLD_NATIVE_ASSEMBLY_ADMISSION_NEGATIVE_CONTROLS',
        valid_receipt_kappa=baseline['kappa'],
        input_sha256=baseline['input_sha256'],
        assembler_sha256=sha(Path(__file__).resolve().parent / 'assemble.py'),
        rejected_controls=rejected,
        discovery_accepted_controls=accepted,
        exact_outer_controls=baseline['controls'],
        conservative_outer_controls=baseline['conservative_controls'],
        recurrence_model_controls=baseline['model_controls'],
        scope='Complete receipt schema; ordered widths and both reflected providers; exact program, work and paid-profile binding; independently recounted compiler, conservative envelope and finite inequalities. Does not replace fresh physical replay.',
    )


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-package', type=Path, required=True)
    ap.add_argument('--owner', type=Path, required=True)
    ap.add_argument('--invoice', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    assert not a.out.exists()
    result = verify(a.owner, a.invoice, a.source_package)
    a.out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], len(result['rejected_controls']))
