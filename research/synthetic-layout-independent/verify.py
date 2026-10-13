#!/usr/bin/env python3
"""Bounded, exact, independent verification of the source's physical layout.

Standard-library only. Failures use exceptions, including under python -O.
The fixed finite domain is not a formal proof of an all-size complexity claim.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import physical
import reference


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':'), sort_keys=True).encode()).hexdigest()


def source_check(root=None):
    root = root or HERE.parents[1]
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for relative, expected in pins['sources'].items():
        require(hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected,
                'source drift: ' + relative)
    return pins


def configurations(max_ell, max_axes):
    for ell in range(2, max_ell + 1):
        for count in range(1, max_axes + 1):
            for flags in itertools.product((False, True), repeat=count):
                for width in range(1, ell):
                    yield ell, width, flags


def layout_checks():
    count = named_bits = basis_addresses = exact_configs = exact_addresses = rounds = 0
    categories = {}
    receipt = hashlib.sha256()
    for ell, width, flags in configurations(18, 5):
        schedule = physical.plan(ell, width, flags)
        slots = schedule['slots']
        n = len(slots)
        count += 1
        named_bits += n
        require(slots == reference.closed_form_slots(ell, width, flags), 'layout mismatch')
        require(set(slots) == set(schedule['original']) and len(set(slots)) == n, 'slot loss')
        b = (ell - 1) % width
        q = (ell - 1) // width
        require(schedule['prefix_moves'] <= len(flags) * (b + 1), 'prefix move invoice')
        for i in range(n):
            address = 1 << i
            moved = physical.layout_address(address, schedule)
            require(moved == reference.address_from_logical(address, ell, width, flags), 'basis address mismatch')
            require(physical.layout_address(moved, schedule, True) == address, 'inverse address mismatch')
            basis_addresses += 1
        positions = {slot: j for j, slot in enumerate(slots)}
        groups = []
        for h in range(ell - 2, b - 1, -1):
            rho = (h - b) % width
            selected = [positions[i, h] for i in range(len(flags))]
            group_start = selected[0] - (width - 1 - rho)
            expected = [group_start + i * width + width - 1 - rho for i in range(len(flags))]
            require(selected == expected, 'selected bits not at common offset in consecutive chunks')
            nP, nS = group_start, n - group_start - len(flags) * width
            require(nP >= 0 and nS >= 0 and nP + len(flags) * width + nS == n, 'Cartesian group coverage')
            # Every address bit appears exactly once in prefix, group, suffix.
            require(len(slots[:nP]) == nP and len(slots[nP:n-nS if nS else n]) == len(flags) * width,
                    'incomplete group partition')
            groups.append([h, rho, nP, nS])
            rounds += 1
        require(len(groups) == q * width, 'round count mismatch')
        if ell <= 7 and len(flags) <= 4 and n <= 12:
            exact_configs += 1
            key = 'b_positive=%s,q_multiple=%s' % (b > 0, q > 1)
            categories[key] = categories.get(key, 0) + 1
            seen = set()
            for address in range(1 << n):
                moved = physical.layout_address(address, schedule)
                require(moved == reference.address_from_logical(address, ell, width, flags), 'full address mismatch')
                require(physical.layout_address(moved, schedule, True) == address, 'full inverse mismatch')
                seen.add(moved)
                exact_addresses += 1
            require(len(seen) == 1 << n, 'address collision')
        receipt.update(bytes.fromhex(digest([ell, width, flags, slots, schedule['operations'], groups])))
    return {'configurations': count, 'named_slots': named_bits, 'basis_address_comparisons': basis_addresses,
            'complete_address_configurations': exact_configs, 'complete_addresses': exact_addresses,
            'complete_address_categories': categories, 'Cartesian_chunk_rounds': rounds,
            'sha256': receipt.hexdigest()}


def basis(M, r, record, coefficient=0):
    data = [[0] * r for _ in range(M)]
    data[record][coefficient] = 1
    return data


def first_difference(actual, expected):
    for i, (a, b) in enumerate(zip(actual, expected)):
        for j, (x, y) in enumerate(zip(a, b)):
            if x != y:
                return {'record': i, 'coefficient': j, 'actual_numerator': x, 'expected_numerator': y}
    return None


def arithmetic_checks():
    rng = random.Random(80)
    cases = list(configurations(4, 2)) + [(2, 1, (False, False, True))]
    receipts = []
    ring_columns = scalar_columns = entries = dense_cases = 0
    for ell, width, flags in cases:
        schedule = physical.plan(ell, width, flags)
        r, M = 1 << ell, 1 << sum(schedule['lengths'])
        case_hash = hashlib.sha256()
        all_coefficients = ell == 2 or (ell == 3 and width == 2 and len(flags) == 2 and flags[0] != flags[1])
        for coefficient in range(r if all_coefficients else 1):
            for record in range(M):
                data = basis(M, r, record, coefficient)
                for direction in ('forward', 'opposite'):
                    actual = physical.execute(data, schedule, opposite=direction == 'opposite')
                    expected = reference.direct_basis(ell, width, flags, record, coefficient, direction)
                    require(actual == expected, 'basis operator mismatch: ' + repr((ell, width, flags, record, coefficient, direction)))
                    case_hash.update(bytes.fromhex(digest(actual)))
                    entries += M * r
                    if coefficient == 0:
                        ring_columns += 1
                    else:
                        scalar_columns += 1
        data = [[rng.randrange(-5, 6) for _ in range(r)] for _ in range(M)]
        for direction in ('forward', 'opposite'):
            actual = physical.execute(data, schedule, opposite=direction == 'opposite')
            expected = reference.direct_transform(ell, width, flags, data, direction)
            require(actual == expected, 'dense operator mismatch')
            case_hash.update(bytes.fromhex(digest(actual)))
            dense_cases += 1
            entries += M * r
        forward = physical.execute(data, schedule)
        composite = physical.execute(forward, schedule, opposite=True)
        require(composite == [[M * x for x in row] for row in data], 'normalized opposite composition must be I/M')
        receipts.append({'ell': ell, 'K': width, 'long_axes': list(flags), 'M': M, 'r': r,
                         'all_scalar_columns': all_coefficients, 'sha256': case_hash.hexdigest()})
    illustration = physical.plan(6, 2, (True, False))
    illustration_hash = hashlib.sha256()
    illustration_columns = 0
    for record in (0, 1, 80, 2047):
        for coefficient in (0, 63):
            for direction in ('forward', 'opposite'):
                actual = physical.execute(basis(2048, 64, record, coefficient), illustration, opposite=direction == 'opposite')
                expected = reference.direct_basis(6, 2, (True, False), record, coefficient, direction)
                require(actual == expected, 'source illustration column mismatch')
                illustration_hash.update(bytes.fromhex(digest(actual)))
                illustration_columns += 1
                entries += 2048 * 64
    return {'configurations': len(cases), 'ring_basis_columns_both_directions': ring_columns,
            'additional_scalar_basis_columns_both_directions': scalar_columns,
            'dense_operator_cases': dense_cases, 'composition_cases': len(cases),
            'coefficient_comparisons': entries, 'cases': receipts,
            'source_illustration': {'columns_both_directions': illustration_columns, 'sha256': illustration_hash.hexdigest()}}


def controls():
    controls = []
    # A nontrivial mixed layout, with b>0, exposes use of physical low bits.
    ell, width, flags = 4, 2, (True, False)
    schedule = physical.plan(ell, width, flags)
    r, M = 1 << ell, 1 << sum(schedule['lengths'])
    rng = random.Random(80)
    data = [[rng.randrange(-3, 4) for _ in range(r)] for _ in range(M)]
    for fault, opposite in [('omit_long_round', False), ('include_branch_in_k', False),
                            ('physical_low_bits', False), ('cyclic_instead_of_negacyclic', False),
                            ('wrong_inverse_sign', True), ('inverse_twiddle_after_butterfly', True),
                            ('omit_layout_restoration', True)]:
        direction = 'opposite' if opposite else 'forward'
        expected = reference.direct_transform(ell, width, flags, data, direction)
        actual = physical.execute(data, schedule, opposite=opposite, fault=fault)
        difference = first_difference(actual, expected)
        require(difference is not None, 'insensitive control: ' + fault)
        controls.append({'mutation': fault, 'case': [ell, width, list(flags)], 'denominator': M, 'witness': difference})
    # Corrupt only movement; leave the final slot descriptor unchanged.
    for fault, config in [('omit_chunk_transpose', (3, 1, (True, False))),
                          ('omit_prefix_moves', (4, 2, (True, False))),
                          ('reverse_layout_direction', (2, 1, (False, False, True)))]:
        ell, width, flags = config
        schedule = physical.plan(ell, width, flags)
        mutated = dict(schedule)
        if fault == 'omit_chunk_transpose':
            mutated['operations'] = [op for op in schedule['operations'] if op[0] != 'swap']
        elif fault == 'omit_prefix_moves':
            mutated['operations'] = [op for op in schedule['operations'] if op[0] != 'move']
        else:
            mutated['operations'] = physical.inverse_operations(schedule['operations'])
        r, M = 1 << ell, 1 << sum(schedule['lengths'])
        data = [[i * r + j + 1 for j in range(r)] for i in range(M)]
        actual = physical.execute(data, mutated)
        expected = reference.direct_transform(ell, width, flags, data)
        difference = first_difference(actual, expected)
        require(difference is not None, 'insensitive movement control: ' + fault)
        controls.append({'mutation': fault, 'case': [ell, width, list(flags)], 'denominator': M, 'witness': difference})
    # Both normalized transforms compose to I/M, not I.
    schedule = physical.plan(2, 1, (True, False))
    data = basis(8, 4, 1, 3)
    composite = physical.execute(physical.execute(data, schedule), schedule, opposite=True)
    wrong = [[64 * x for x in row] for row in data]
    difference = first_difference(composite, wrong)
    require(difference is not None, 'insensitive normalization control')
    controls.append({'mutation': 'claim_opposite_is_unscaled_inverse', 'case': [2, 1, [True, False]],
                     'denominator': 64, 'witness': difference})
    return controls


def run():
    sources = source_check()
    return {'schema': 'synthetic-layout-independent/v1', 'status': 'independent finite verification; no new kappa',
            'base_commit': sources['base_commit'], 'sources': sources['sources'],
            'domain_sha256': hashlib.sha256((HERE / 'DOMAIN.json').read_bytes()).hexdigest(),
            'layouts': layout_checks(), 'arithmetic': arithmetic_checks(), 'negative_controls': controls()}


def check_receipt(result, path):
    require(result == json.loads(Path(path).read_text()), 'receipt mismatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='explicitly regenerate this package EXPECTED.json')
    parser.add_argument('--check', type=Path, default=HERE / 'EXPECTED.json')
    args = parser.parse_args()
    result = run()
    if args.write:
        (HERE / 'EXPECTED.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        check_receipt(result, args.check)
    print('PASS_SYNTHETIC_LAYOUT: %d layouts; %d complete addresses; %d ring columns; %d extra scalar columns; %d negative controls' %
          (result['layouts']['configurations'], result['layouts']['complete_addresses'],
           result['arithmetic']['ring_basis_columns_both_directions'], result['arithmetic']['additional_scalar_basis_columns_both_directions'],
           len(result['negative_controls'])))


if __name__ == '__main__':
    main()
