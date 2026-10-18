#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent, bounded controls for the PR1598 finite-image successor review.

Andrey Mas with GPT-6 Pro mathematical assistance through ChatGPT.
This is new audit code, NOT the producer's unavailable checker, a Lean replay,
or a word search/BFS. It imports and executes no repository code.
Boolean rows are integers with input coordinate c at bit c; matrixAction
returns an integer whose output coordinate r is at bit r. All checks use
explicit exceptions and survive python -O.
"""
from itertools import product
import json


class AuditError(Exception):
    pass


def need(ok, message):
    if not ok:
        raise AuditError(message)


def identity(n):
    need(isinstance(n, int) and n >= 0, 'invalid dimension')
    return tuple(1 << r for r in range(n))


def action(matrix, x):
    n = len(matrix)
    need(0 <= x < (1 << n), 'input outside full Boolean domain')
    need(all(0 <= row < (1 << n) for row in matrix), 'invalid matrix row')
    return sum(((row & x).bit_count() % 2) << r
               for r, row in enumerate(matrix))


def transpose(matrix):
    return tuple(sum(((matrix[r] >> c) & 1) << r
                     for r in range(len(matrix)))
                 for c in range(len(matrix)))


def combination(generators, bits):
    # Like the Lean definition, totalized by truncation.
    row = 0
    for donor, bit in zip(generators, bits):
        need(type(bit) is bool, 'mask is not Boolean')
        if bit:
            row ^= donor
    return row


def measurements(generators, x):
    return tuple(bool((row & x).bit_count() % 2) for row in generators)


def scalar_combination(bits, values):
    value = False
    for bit, measurement in zip(bits, values):
        value ^= bit and measurement
    return value


def decode(masks, values):
    return sum(int(scalar_combination(mask, values)) << r
               for r, mask in enumerate(masks))


def bits_code(bits):
    # First list bit is least significant.
    code = 0
    for bit in reversed(bits):
        need(type(bit) is bool, 'code input is not Boolean')
        code = int(bit) + 2 * code
    return code


def bitlists(k):
    return tuple(product((False, True), repeat=k))


def input_code(generators, x):
    return bits_code(measurements(generators, x))


def check_certificate(matrix, generators, masks):
    n = len(matrix)
    need(len(masks) == n, 'wrong number of output masks')
    need(all(0 <= g < (1 << n) for g in generators), 'invalid donor row')
    for row, mask in zip(matrix, masks):
        need(len(mask) == len(generators), 'inexact mask length')
        need(combination(generators, mask) == row, 'wrong generated row')


def audit_factor(matrix, generators, masks):
    """Check all inputs and ALL choices of one preimage per actual output."""
    check_certificate(matrix, generators, masks)
    n, k = len(matrix), len(generators)
    fibers, seen_codes = {}, {}
    for x in range(1 << n):
        values = measurements(generators, x)
        need(len(values) == k, 'measurement length')
        out = action(matrix, x)
        need(out == decode(masks, values), 'factorization failure')
        code = input_code(generators, x)
        need(0 <= code < (1 << k), 'code outside finite ordinal')
        if code in seen_codes:
            other = seen_codes[code]
            need(values == measurements(generators, other), 'equal-code decoding')
            need(out == action(matrix, other), 'equal codes, unequal outputs')
        seen_codes[code] = x
        fibers.setdefault(out, []).append(x)
    need(len(fibers) <= (1 << k), 'actual image exceeds bound')
    outputs = sorted(fibers)
    sections = 0
    for witnesses in product(*(fibers[out] for out in outputs)):
        codes = [input_code(generators, x) for x in witnesses]
        need(len(codes) == len(set(codes)), 'chosen image code not injective')
        need(all(action(matrix, x) == out for out, x in zip(outputs, witnesses)),
             'selected input is not a preimage')
        sections += 1
    return {'inputs': 1 << n, 'image_size': len(fibers),
            'bound': 1 << k, 'all_preimage_sections_checked': sections}


def replay(n, target, word):
    """Concrete raw/projected scanner, checking each prefix invariant."""
    need(n > 0 and 0 <= target < n, 'no distinguished target')
    raw, projected = list(identity(n)), list(identity(n))
    donors = []
    masks = [() for _ in range(n)]

    def prefix_check():
        check_certificate(tuple(a ^ b for a, b in zip(raw, projected)),
                          tuple(donors), tuple(masks))
        total = 0
        for donor in donors:
            total ^= donor
        need(raw[target] == (1 << target) ^ total, 'target telescope failure')

    prefix_check()
    for dst, src in word:
        need(0 <= dst < n and 0 <= src < n and dst != src,
             'not a distinct-register gate')
        donor = raw[src]
        raw[dst] ^= donor
        if dst == target:
            donors.append(donor)
            masks = [mask + (r == target,) for r, mask in enumerate(masks)]
        else:
            projected[dst] ^= projected[src]
            masks[dst] = tuple(a ^ b for a, b in zip(masks[dst], masks[src]))
        prefix_check()
    return tuple(raw), tuple(projected), tuple(donors), tuple(masks)


def audit_restored_word(n, target, word):
    raw, projected, donors, masks = replay(n, target, word)
    need(raw == identity(n), 'full raw restoration required')
    defect = tuple(a ^ b for a, b in zip(identity(n), projected))
    m = len(donors)
    if m:
        kept = donors[1:]
        reduced = tuple(tuple(not b for b in mask[1:]) if mask[0]
                        else mask[1:] for mask in masks)
        need(len(kept) == m - 1, 'wrong retained occurrence length')
    else:
        need(projected == identity(n) and not any(defect), 'zero-write defect')
        kept, reduced = (), tuple(() for _ in range(n))
    result = audit_factor(defect, kept, reduced)
    need(result['bound'] == 1 << max(m - 1, 0), 'truncated exponent error')
    result.update({'registers': n, 'gates': len(word), 'target_writes': m,
                   'donors': donors, 'retained_donors': kept,
                   'reduced_masks': reduced, 'defect_rows': defect,
                   'prefix_invariants_checked': len(word) + 1})
    return result


def run():
    rejected = []

    def reject(name, fn):
        try:
            fn()
        except AuditError:
            rejected.append(name)
        else:
            raise AuditError('bad alternative accepted: ' + name)

    # A fixed finite algebra census, not a gate-word census:
    # all two-row generators in F2^2 and all 2-by-2 Boolean masks.
    totals = {'models': 0, 'inputs': 0, 'preimage_sections': 0}
    for generators in product(range(4), repeat=2):
        for masks in product(bitlists(2), repeat=2):
            matrix = tuple(combination(generators, mask) for mask in masks)
            result = audit_factor(matrix, generators, masks)
            totals['models'] += 1
            totals['inputs'] += result['inputs']
            totals['preimage_sections'] += result['all_preimage_sections_checked']
    need(totals['models'] == 256 and totals['inputs'] == 1024,
         'bounded factor census incomplete')
    empty = audit_factor((), (), ())
    need(empty['image_size'] == empty['bound'] == 1, 'dimension-zero factor')

    code_lists = 0
    for k in range(7):
        codes = [bits_code(bits) for bits in bitlists(k)]
        need(len(set(codes)) == len(codes), 'equal-length code collision')
        need(all(code < (1 << k) for code in codes), 'code range')
        code_lists += len(codes)
    need(code_lists == 127, 'bounded code census incomplete')

    feedback = ((1, 0), (0, 1)) * 3
    commutator = ((2, 0), (1, 2), (2, 0), (1, 2), (1, 0))
    specifications = {
        'feedback': (2, 1, feedback),
        'commutator': (3, 2, commutator),
        'repeated_donor_zero_defect': (2, 1, ((1, 0), (1, 0))),
        'nonempty_zero_writes': (3, 2, ((0, 2), (0, 2))),
        'one_register_empty': (1, 0, ()),
        'commutator_extra_dirty_spectator': (4, 2, commutator),
    }
    fixtures = {name: audit_restored_word(*args)
                for name, args in specifications.items()}
    f, c = fixtures['feedback'], fixtures['commutator']
    need(f['donors'] == (1, 2, 3) and f['retained_donors'] == (2, 3),
         'feedback donor occurrence mismatch')
    need(f['defect_rows'] == (2, 0) and c['defect_rows'] == (0, 1, 0),
         'orientation fixture mismatch')
    need(action(c['defect_rows'], 1) == 2, 'M e_a is not e_b')
    need(action(f['defect_rows'], 2) == 1, 'dirty target input not read')

    # Every individual choice of a preimage gives an injection; nevertheless
    # input codes are NOT functions of the output without a selection rule.
    need(action(f['defect_rows'], 0) == action(f['defect_rows'], 1) == 0,
         'equal-output control')
    need(input_code(f['retained_donors'], 0) == 0
         and input_code(f['retained_donors'], 1) == 2,
         'noncanonical measurement control')
    reject('equal_outputs_force_equal_input_codes', lambda: need(
        input_code(f['retained_donors'], 0) == input_code(f['retained_donors'], 1),
        'measurements need not be canonical'))
    reject('row_column_transposition', lambda: need(
        action(c['defect_rows'], 1) == action(transpose(c['defect_rows']), 1),
        'transpose changes actual image action'))
    reject('discard_dirty_target_input', lambda: need(
        action(f['defect_rows'], 2) == action(f['defect_rows'], 0),
        'cleaning target changes output'))
    reject('code_injectivity_without_equal_lengths', lambda: need(
        bits_code(()) != bits_code((False,)), 'padded zero collision'))
    reject('inexact_mask_length', lambda: check_certificate((0,), (1,), ((),)))
    reject('wrong_row_certificate', lambda: check_certificate((1,), (1,), ((False,),)))
    reject('remove_raw_restoration_zero_writes', lambda: audit_restored_word(
        2, 1, ((0, 1),)))
    reject('remove_raw_restoration_positive_writes', lambda: audit_restored_word(
        2, 1, ((1, 0), (0, 1))))
    reject('invent_target_in_dimension_zero', lambda: replay(0, 0, ()))
    reject('allow_same_register_gate', lambda: replay(1, 0, ((0, 0),)))

    # Show the two rejected nonrestoring words actually falsify the claimed
    # bound without hraw, rather than merely exercising a precondition.
    for word in (((0, 1),), ((1, 0), (0, 1))):
        raw, projected, donors, _ = replay(2, 1, word)
        defect = tuple(a ^ b for a, b in zip(identity(2), projected))
        need(raw != identity(2), 'bad missing-hraw example')
        image = {action(defect, x) for x in range(4)}
        need(len(image) == 2 > 1 << max(len(donors) - 1, 0),
             'missing restoration did not falsify bound')

    need(len(rejected) == 10, 'wrong negative-control count')
    return {'status': 'PASS_INDEPENDENT_FINITE_IMAGE_CONTROLS',
            'scope': 'Independent bounded Boolean checks only; no Lean, imported repository code, producer checker, BFS, or full word census.',
            'factor_census_n2_k2': totals, 'dimension_zero_factor': empty,
            'bitlists_checked_lengths_0_through_6': code_lists,
            'restored_word_fixtures': fixtures,
            'rejected_bad_alternatives': rejected,
            'negative_control_count': len(rejected)}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
