"""Price whole-fibre lower-rank, axis-aligned splits at one literal BIT pair."""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path

PINS = {
    'EFREE-CALLER.json.gz': '757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b',
    'EFREE-RESULT.json': 'a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b',
    'independent/interval_gate.py': '8dc2bc4c64cba3f83c664373984a075f1a14b4d53958084091345c8cab189dec',
    'retained/inputs/BIT-NATIVE-WORD.json.gz': '51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78',
}
TARGET = Fraction('0.0040075385047236')
RAW = Fraction('0.004008162992724')


def authenticate(root, key):
    path = root / key
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PINS[key]:
        raise ValueError(f'SHA-256 mismatch: bit/{key}')
    return raw


def contacts(event):
    if event[0] == 'LOCAL':
        return event[2:]
    if event[0] == 'IDLE_ONE':
        return event[1:2]
    if event[0] in ('ADD', 'SWAP', 'QUERY'):
        return event[1:]
    raise ValueError(event[0])


def axes(stages):
    return tuple(a for stage in stages for a in range(1 + 7 * (stage - 1), 1 + 7 * stage))


def rank_binary(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def control(s):
    addresses = list(product(range(s), repeat=2))
    states = list(product(range(2), addresses))
    order = {state: i for i, state in enumerate(states)}

    def reflect(state, flip):
        role, point = state
        return role, tuple((-x if i in flip else x) % s for i, x in enumerate(point))

    target = {state: reflect(state, {0, 1}) for state in states}
    assert all(reflect(reflect(x, {0}), {1}) == target[x] for x in states)
    assert all(reflect(target[x], {0, 1}) == x for x in states)
    assert sum(reflect(x, {0}) != target[x] for x in states) == 2 * s * (s - 1)
    controls = []
    for axis in (0, 1):
        edges = [(a, b) for a, b in target.items() if a[1][axis] < b[1][axis]]
        edges.sort(key=lambda edge: (edge[0][1][axis], order[edge[0]]))
        grade_zero_reference = {
            state: target[state] if state[1][axis] == 0 else state
            for state in states
        }
        assert all(grade_zero_reference[x][1][axis] == x[1][axis] for x in states)
        assert sum(target[x] != grade_zero_reference[x] for x in states) == 2 * len(edges)
        same_grade = {
            state: (1 - state[0], reflect(state, {1 - axis})[1])
            for state in states
        }
        assert all(same_grade[x] != x and same_grade[x][1][axis] == x[1][axis] for x in states)
        selected_minor = [
            sum(
                ((target[b] == a) ^ (same_grade[b] == a)) << j
                for j, (_, b) in enumerate(edges)
            )
            for a, _ in edges
        ]
        assert len(edges) == s * (s - 1)
        assert rank_binary(selected_minor) == len(edges)
        assert rank_binary([(1 << i) ^ (1 << i) for i in range(len(edges))]) == 0
        swap_grade = sum((p[0] != p[1]) for _, p in states)
        controls.append({'coordinate': axis, 'cross_minor_size_and_rank': len(edges),
                         'nonidentity_grade_preserving_control_columns': len(states),
                         'grade_swapping_right_matcher_moved_labels': swap_grade,
                         'true_address_changing_reference_rank': 0})
    return {'digit_cardinality': s, 'field_volume_each': len(addresses),
            'exact_basis_columns': len(states), 'missing_split_mutation_failures': 2 * s * (s - 1),
            'grades': controls}


def run(root):
    data = {key: authenticate(root, key) for key in PINS}
    caller = json.loads(gzip.decompress(data['EFREE-CALLER.json.gz']))
    native = json.loads(gzip.decompress(data['retained/inputs/BIT-NATIVE-WORD.json.gz']))
    invoice = json.loads(data['EFREE-RESULT.json'])
    path = root / 'independent/interval_gate.py'
    spec = spec_from_file_location('interval_gate', path)
    gate = module_from_spec(spec)
    spec.loader.exec_module(gate)

    stages = tuple(range(2, 10))
    first, second = 19, 24
    roles = (2, 21)
    events = caller['events']
    assert [events[i] for i in (first, second)] == [
        ['IDLE_ONE', role, list(stages)] for role in roles
    ]
    assert all(not (set(contacts(e)) & set(roles)) for e in events[first + 1:second])
    assert (caller['ambient_rank'], caller['body_rank'], caller['ports']) == (127, 7, 111)
    n = caller['ports']
    head, body = native['start'][0], native['final'][n]
    assert (head, body) == (2, 525)
    frame = native['frames'][str(body)]
    unit = [[int(i == j) for i in range(8)] for j in range(8)]
    assert native['frames'][str(head)] == {'dim': 1, 'B': unit[:1], 'A': unit[1:]}
    assert frame == {'dim': 7, 'B': unit[1:], 'A': unit[:1]}
    left, right = axes(stages[:4]), axes(stages[4:])
    assert len(left) == len(right) == 28 and not set(left) & set(right)
    assert left + right == axes(stages)

    old = Counter({int(k): v for k, v in invoice['targets'].items()})
    old.subtract({int(k): v for k, v in invoice['paid'].items()})
    pair_stock = sum(e[0] == 'IDLE_ONE' and len(e[2]) == 8 for e in events) * n // 2
    assert pair_stock == 222
    prices = {}
    for k in (TARGET, RAW):
        h = {r: gate.power(r, k) for r in (28, 49, 55, 56)}
        old_pair = gate.smul(h[56], 2)
        new_pair = gate.smul(h[28], 4)
        surcharge = gate.sub(new_pair, old_pair)
        smaller = {r: gate.sub(gate.smul(h[r], Fraction(112, r)), old_pair) for r in (49, 55)}
        assert surcharge[0] > 0 and all(x[0] > 0 for x in smaller.values())
        deficit = gate.smul(gate.moment(old, k), -1)
        fair_share = gate.smul(deficit, Fraction(1, pair_stock))
        # Fraction of the total selected-minor rank that the modified references
        # must cover, allowing every available pair the same optimistic credit.
        cap49 = gate.smul(h[49], Fraction(112, 49))
        reference = gate.sub(gate.exact(1), gate.div(gate.sub(old_pair, fair_share), cap49))
        assert deficit[0] > 0 and reference[0] > 0
        prices[str(k)] = {'old_pair_tariff': gate.show(old_pair), 'literal_four_rank28_tariff': gate.show(new_pair),
                          'literal_split_surcharge': gate.show(surcharge),
                          'proper_rank_surcharge_lowers_by_cap': {r: gate.show(v) for r, v in smaller.items()},
                          'complete_old_raw_deficit': gate.show(deficit),
                          'credit_per_pair_over_all_222_to_cover_deficit': gate.show(fair_share),
                          'rank49_min_reference_minor_rank_fraction_over_222': gate.show(reference)}
    return {
        'source_pins': {f'bit/{key}': val for key, val in PINS.items()},
        'literal_pair': {'old_events': [first, second], 'roles': roles, 'port': 0, 'rank': 56,
                         'head_chart': head, 'body_chart': body, 'body_stages': stages,
                         'intervening_contacts_to_pair': 0, 'equal_complete_volume_each': 'V',
                         'orthogonal_projector_axes': [left, right]},
        'literal_pilot': {'paid_profile': {28: 4}, 'replaced_paid_profile': {56: 2},
                          'changed_scalar_operations': 0, 'new_owned_lifetimes': 0,
                          'new_productive_helpers': 0, 'new_spectator_rows': 0,
                          'new_physical_compiler_or_tape_run': False},
        'all_width_aligned_lower': 'sum(V_i*r_i) >= 112V for the exact two-field target',
        'directed_prices_per_original_volume': prices,
        'finite_controls': [control(s) for s in (3, 5, 9)],
        'build': 'REJECTED_AT_PAID_GATE',
    }


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run with assertions enabled')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bit-package', type=Path, required=True)
    print(json.dumps(run(p.parse_args().bit_package), sort_keys=True, indent=2))
