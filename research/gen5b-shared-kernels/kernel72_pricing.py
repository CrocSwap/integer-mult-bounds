"""Exact portable pricing of the admitted union72 plus final12 changes.

Only independently authored helpers and byte-pinned PR299 JSON are used.
Physical bank admission and inherited all-size interfaces remain separate.
"""
from collections import Counter
from fractions import Fraction as F

import check_coretime
import check_suffix_frames
import reprice
import source_data as sd


def integer_map(values):
    result = {}
    for rank, count in values.items():
        if isinstance(rank, str):
            if not rank.isdecimal():
                raise ValueError('Invalid histogram rank')
            rank = int(rank)
        if type(rank) is not int or type(count) is not int or rank <= 0:
            raise ValueError('Histogram requires positive integer ranks and integer counts')
        if count:
            if rank in result:
                raise ValueError('Duplicate histogram rank')
            result[rank] = count
    return result


def measured_kernel_delta(bridge):
    """Bind the price to the full measured entrance ledger, not a copied delta."""
    assert bridge['status'] == 'PASS_SHARED_DONOR_CHANGED_STAGE_COMPOSITION'
    assert bridge['selection'] == 'union72' and bridge['source_head'] == sd.HEAD
    assert bridge['formal_forward_and_inverse_equal']
    assert bridge['arbitrary_source_target_dirty_inputs']
    paths = bridge['paths']
    assert len(paths) == bridge['members'] == 165
    assert len({p['role'] for p in paths}) == len({p['stream'] for p in paths}) == len(paths)
    assert Counter(p['kind'] for p in paths) == {'pivot': 72, 'donor': 93}
    assert bridge['pivots'] == 72 and bridge['distinct_donors'] == 93
    assert bridge['setup_adds'] == bridge['restore_adds'] == 473
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
    assert delta == {1: 93, 2: 144, 3: -144, 4: 19, 5: -17, 6: -2}
    residual = {24: -72, 23: 72}
    assert integer_map(bridge['residual_family_delta']) == residual
    assert sum(r * n for r, n in delta.items()) == -72
    return delta, residual


def patterns(pivots, final12_residual):
    """Exact mixed-bin exchange: 4*23 + 24 + 4 = 120, with 60 replicas."""
    if type(pivots) is not int or pivots <= 0 or pivots % 2:
        raise ValueError('An even positive pivot count is required')
    out = reprice.pure_retile(final12_residual)
    for widths, change in (([23] * 4 + [24, 4], 15 * pivots),
                           ([24] * 5, -15 * pivots),
                           ([4] * 30, -pivots // 2)):
        row = next((r for r in out if r['widths'] == widths), None)
        if row is None or row['count'] + change < 0:
            raise ValueError('Mixed packing exchange is unavailable')
        row['count'] += change
    return [row for row in out if row['count']]


def run(bridge=None, final12_frames=None, final12_local=None):
    sd.verify_all()
    if bridge is None:
        import check_shared_kernel
        bridge = check_shared_kernel.run(selection='union72')
    if final12_frames is None:
        final12_frames = check_suffix_frames.run()
    if final12_local is None:
        final12_local = check_coretime.run(minimal=True)
    H, D = measured_kernel_delta(bridge)
    assert final12_frames['status'] == 'PASS_MEASURED_AFFECTED_SUFFIX_FRAME_LEDGER'
    assert final12_frames['source_head'] == sd.HEAD and final12_frames['both_reflected_ledgers']
    finalH = integer_map(final12_frames['local_histogram_delta'])
    assert finalH == {1: 18, 2: -12}
    assert final12_local['selected'] == 12 and final12_local['undone_old_restorations'] == 6
    finalD = integer_map(final12_local['residual_rank_count_delta'])
    assert finalD == {2: 12, 3: -18, 4: 6}
    combinedH = Counter(H); combinedH.update(finalH)
    combinedD = Counter(D); combinedD.update(finalD)
    result = reprice.reprice(dict(combinedH), dict(combinedD), patterns(72, finalD))
    assert result['packing']['optimal'] and result['packing']['unused_coordinate_capacity'] == 0
    assert result['literal_stock'] == 1229555
    assert result['calls'] == 483130 and result['rank_mass'] == 2454710
    assert result['deficit'] == 4400
    assert result['kappa'] == F(749917402998347, 10**18)
    result.update(status='PASS_UNION72_FINAL12_EXACT_PRICING', selection='union72',
                  with_final12=True, source_head=sd.HEAD,
                  kernel_histogram_delta=H, final12_histogram_delta=finalH,
                  kernel_residual_delta=D, final12_residual_delta=finalD,
                  pivots=72, distinct_donors=93, scalar_setup_gates=473,
                  scalar_restore_gates=473,
                  prior_final12_kappa=F(749906929903449, 10**18),
                  kappa_gain_over_final12=result['kappa'] - F(749906929903449, 10**18),
                  binding='Measured union72 first-frame ledger plus measured final12 chronological suffix delta; exact residual inventory.',
                  scope='Exact arithmetic and optimal inventory under separately checked changed-stage certificates. Literal bank assignment, unchanged PR299 admission, finite compiler and all-size theorem remain separate.')
    return result


def price_additional_histogram(base_receipt, selection_bytes, pin):
    """Separate conditional case; byte-pin an extra declared local histogram.

    This does not certify the extra transformation's chronological admission,
    compatibility, scalar norms or finite bill. The base receipt is untouched.
    """
    import hashlib
    import json
    import re
    assert base_receipt['status'] == 'PASS_UNION72_FINAL12_EXACT_PRICING'
    assert base_receipt['source_head'] == sd.HEAD
    assert isinstance(selection_bytes, bytes)
    assert pin['repository'] and pin['path']
    assert re.fullmatch('[0-9a-f]{40}', pin['commit'])
    assert re.fullmatch('[0-9a-f]{40}', pin['git_blob'])
    assert re.fullmatch('[0-9a-f]{64}', pin['sha256'])
    if hashlib.sha256(selection_bytes).hexdigest() != pin['sha256']:
        raise ValueError('Additional histogram source SHA-256 mismatch')
    blob = hashlib.sha1(b'blob ' + str(len(selection_bytes)).encode() + b'\0' + selection_bytes).hexdigest()
    if blob != pin['git_blob']:
        raise ValueError('Additional histogram source Git blob mismatch')
    data = json.loads(selection_bytes)
    extra = integer_map(data['expected_local_histogram_delta'])
    if sum(rank * count for rank, count in extra.items()):
        raise ValueError('This overlay requires unchanged total rank and bank inventory')
    H = Counter(integer_map(base_receipt['local_histogram_delta'])); H.update(extra)
    D = integer_map(base_receipt['role_rank_count_delta'])
    result = reprice.reprice(dict(H), D, base_receipt['packing']['patterns'])
    assert result['literal_stock'] == base_receipt['literal_stock']
    assert result['rank_mass'] == base_receipt['rank_mass']
    assert result['calls'] == base_receipt['calls'] + 5 * sum(extra.values())
    result.update(status='CONDITIONAL_PINNED_ADDITIONAL_HISTOGRAM_ARITHMETIC',
                  source_head=sd.HEAD, selection='union72', with_final12=True,
                  additional_source=dict(pin),
                  additional_declared_local_histogram_delta=extra,
                  preceding_kappa=F(base_receipt['kappa']),
                  gain_over_preceding_case=result['kappa']-F(base_receipt['kappa']),
                  extra_chronology_and_interactions_verified=False,
                  updated_finite_bill_verified=False,
                  scope='Separate declared-histogram arithmetic with verified source bytes; does not replace the union72+final12 receipt or certify extra admission, composition, scalar norms, or finite bounds.')
    return result
