"""Exact portable kernel70 + final12 pricing on the separately pinned PR300 case.

PR299 raw inputs and declared PR300 descent2 delta remain byte-pinned. The
composition checker binds changed role paths; inherited source admission and
all-size interfaces remain conditional. The kernel72 fallback is unchanged.
"""
from collections import Counter
from fractions import Fraction as F

import source_data as sd
import check_coretime
import check_suffix_frames
import reprice
from kernel72_pricing import integer_map, patterns

PR300_HEAD = 'fd516176fd068e4fa7af14b40cd878ce8c305296'


def measured_kernel_delta(bridge):
    """Bind the price to the full measured entrance ledger, not a copied delta."""
    assert bridge['status'] == 'PASS_SHARED_DONOR_CHANGED_STAGE_COMPOSITION'
    assert bridge['selection'] == 'candidate70' and bridge['source_head'] == sd.HEAD
    assert bridge['formal_forward_and_inverse_equal']
    assert bridge['arbitrary_source_target_dirty_inputs']
    paths = bridge['paths']
    assert len(paths) == bridge['members'] == 157
    assert len({p['role'] for p in paths}) == len({p['stream'] for p in paths}) == len(paths)
    assert Counter(p['kind'] for p in paths) == {'pivot': 70, 'donor': 87}
    assert bridge['pivots'] == 70 and bridge['distinct_donors'] == 87
    assert bridge['setup_adds'] == bridge['restore_adds'] == 601
    assert {tuple(p['line']) for p in paths} == {(6, 7), (16, 17), (2, 3)}
    delta = Counter()
    for p in paths:
        d = p['first_dimension']
        assert type(d) is int and 1 < d <= 24
        assert p['old_dimensions'][0] == d and p['old_dimensions'][-1] == 24
        assert len(p['old_frames']) == len(p['old_dimensions'])
        assert all(a <= b for a, b in zip(p['old_dimensions'], p['old_dimensions'][1:]))
        paid = [d - 1] if p['kind'] == 'pivot' else [1, d - 1]
        assert p['new_paid_entrance_dimensions'] == paid
        assert p['new_initial_dimension'] == (1 if p['kind'] == 'pivot' else 0)
        delta[d] -= 1
        delta.update(paid)
    delta = {r: n for r, n in delta.items() if n}
    assert delta == integer_map(bridge['local_paid_histogram_delta'])
    assert delta == {1: 87, 2: 137, 3: -137, 4: 18, 5: -16, 6: -2}
    residual = {24: -70, 23: 70}
    assert integer_map(bridge['residual_family_delta']) == residual
    assert sum(r * n for r, n in delta.items()) == -70
    return delta, residual



def verify_composition(composition, combined_delta=None):
    assert composition['status'] == 'PASS_ROLE_DISJOINT_PR300_COMPOSITION'
    assert composition['baseline_head'] == sd.HEAD
    assert composition['source_head'] == PR300_HEAD
    pin = sd.MANIFEST['files']['pr300/descent2-selection.json']
    assert pin['commit'] == PR300_HEAD
    assert composition['input_sha256']['pr300/descent2-selection.json'] == pin['sha256']
    assert composition['paid_ledgers_additive']
    assert composition['new_descent_gate_count'] == 89
    assert composition['rational_new_frame_ranks_and_nondegeneracy_checked'] == 89
    assert composition['final12_broader_scalar_closure'] == 84
    assert composition['kernel70_streams'] == 157
    assert composition['descent2_overlap_final12'] == composition['descent2_overlap_kernel70'] == []
    assert composition['scalar_majorants_unchanged_by_descent2']
    assert composition['source_operand_columns_unchanged_by_new_kernel']
    assert composition['common_kernel_cut_and_final_restore_order_unchanged']
    assert composition['final12_and_kernel70_source_response_unchanged']
    assert composition['unchanged_restore_entries'] == 440 and composition['unchanged_sink_entries'] == 7
    if combined_delta is not None:
        assert integer_map(composition['combined_local_histogram_delta_over299']) == integer_map(combined_delta)
    return pin


def run(bridge=None, final12_frames=None, final12_local=None, composition=None):
    sd.verify_all()
    if bridge is None:
        import check_kernel70
        bridge = check_kernel70.run()
    if final12_frames is None:
        final12_frames = check_suffix_frames.run()
    if final12_local is None:
        final12_local = check_coretime.run(minimal=True)
    if composition is None:
        import check_pr300_kernel70_composition
        composition = check_pr300_kernel70_composition.run()
    H, D = measured_kernel_delta(bridge)
    assert final12_frames['status'] == 'PASS_MEASURED_AFFECTED_SUFFIX_FRAME_LEDGER'
    assert final12_frames['source_head'] == sd.HEAD and final12_frames['both_reflected_ledgers']
    finalH = integer_map(final12_frames['local_histogram_delta'])
    assert finalH == {1: 18, 2: -12}
    assert final12_local['selected'] == 12 and final12_local['undone_old_restorations'] == 6
    finalD = integer_map(final12_local['residual_rank_count_delta'])
    assert finalD == {2: 12, 3: -18, 4: 6}
    extraH = integer_map(sd.read_json('pr300/descent2-selection.json')['expected_local_histogram_delta'])
    assert sum(r*n for r,n in extraH.items()) == 0 and sum(extraH.values()) == 65
    combinedH = Counter(H); combinedH.update(finalH); combinedH.update(extraH)
    combinedD = Counter(D); combinedD.update(finalD)
    pin = verify_composition(composition, combinedH)
    result = reprice.reprice(dict(combinedH), dict(combinedD), patterns(70, finalD))
    assert result['packing']['optimal'] and result['packing']['unused_coordinate_capacity'] == 0
    assert result['literal_stock'] == 1229560
    assert result['calls'] == 483425 and result['rank_mass'] == 2454720
    assert result['deficit'] == 4400 and result['packing']['feasible_bins'] == 161432
    assert result['kappa'] == F(749940157923873, 10**18)
    result.update(status='PASS_KERNEL70_PR300_FINAL12_EXACT_PRICING', selection='candidate70',
                  with_final12=True, on_PR300=True, source_head=sd.HEAD,
                  additional_source=dict(pin), composition_status=composition['status'],
                  kernel_histogram_delta=H, final12_histogram_delta=finalH,
                  pr300_histogram_delta=extraH, kernel_residual_delta=D,
                  final12_residual_delta=finalD, pivots=70, distinct_donors=87,
                  scalar_setup_gates=601, scalar_restore_gates=601,
                  fallback_kernel72_kappa=F(749936120273400, 10**18),
                  kappa_gain_over_kernel72=result['kappa']-F(749936120273400, 10**18),
                  binding='Measured candidate70 first-frame ledger plus measured final12 chronological suffix delta and pinned PR300 descent2 delta, bound to role-disjoint composition.',
                  scope='Exact arithmetic and optimal inventory under the changed composition certificates. PR300 chronological/source-span admission and unchanged compiler, prime, routing and all-size interfaces remain inherited.')
    return result
