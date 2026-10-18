#!/usr/bin/env python3
"""Finite dyadic butterfly families; exact full-map replay, no random search.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
Credits: Alluri's PR #681 factory resynthesis and Jeremy Kothe's PR #622
112-port construction. Common exact circuit operations are source-pinned below.

Run with --write to regenerate SEARCH.json and candidate.json; default execution
replays the complete prespecified domain and compares the checked-in receipts.
The losing candidate is evidence about this domain, not a proposed replacement.
"""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREDECESSOR = HERE.parent / 'complex-factory5-resynthesis'
PINS = {
    'search.py': '67f9a86e7d29c96edf685b0f30757b99457599c305b1ac6f7326adc4505ce57e',
    'CIRCUIT.json': 'f64a9e88491af13fe564f0512e8455eb268d1732a978b1b4fe3b93e601b59f71',
}
for name, expected in PINS.items():
    if hashlib.sha256((PREDECESSOR / name).read_bytes()).hexdigest() != expected:
        raise ValueError('source pin mismatch: ' + name)
spec = importlib.util.spec_from_file_location('factory_predecessor', PREDECESSOR / 'search.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
C = json.loads((PREDECESSOR / 'CIRCUIT.json').read_text())
M = s.matrix(C['original'])
FRAME = C['frame']
MATCHINGS = [[(0, 1), (2, 3)], [(0, 2), (1, 3)], [(0, 3), (1, 2)]]


def canonical(value):
    return json.dumps(value, separators=(',', ':'), sort_keys=True).encode()


def add(i, j, q):
    q = F(q)
    return ['add', i, j, q.numerator, q.denominator, FRAME]


def scale(i, q):
    q = F(q)
    return ['scale', i, q.numerator, q.denominator, FRAME]


def current_cost(ops):
    """PR #696 pricing: cleared work register included for every scalar add."""
    return sum((2 if abs(F(e[3], e[4])) == 1 else s.primitive_cost([e]) - 1)
               if e[0] == 'add' else s.primitive_cost([e]) for e in ops)


def normal_row(values, exponent):
    mask = 0
    for x in values:
        mask |= abs(x)
    shift = min(exponent, (mask & -mask).bit_length() - 1) if mask else exponent
    return ([x >> shift for x in values], exponent - shift)


def exact_dyadic_map(ops):
    """Eight dirty basis vectors, using integer row numerators and binary exponents."""
    rows = [([int(i == j) for j in range(8)], 0) for i in range(8)]
    for e in ops:
        target = e[1]
        old, old_exp = rows[target]
        num, den = e[3:5] if e[0] == 'add' else e[2:4]
        if den < 0:
            num, den = -num, -den
        if den <= 0 or den & (den - 1):
            raise ValueError('non-dyadic denominator')
        power = den.bit_length() - 1
        if e[0] == 'add':
            source, source_exp = rows[e[2]]
            exponent = max(old_exp, source_exp + power)
            values = [(x << (exponent-old_exp)) + num*(y << (exponent-source_exp-power))
                      for x, y in zip(old, source)]
        else:
            if not num or abs(num) & (abs(num)-1):
                raise ValueError('non-binary scale')
            exponent = old_exp + power
            values = [num*x for x in old]
        rows[target] = normal_row(values, exponent)
    return [(tuple(values), exponent) for values, exponent in rows]


TARGET = exact_dyadic_map(C['original'])
TARGET_SHA = hashlib.sha256(canonical(TARGET)).hexdigest()
if [[F(x, 1 << exponent) for x in values] for values, exponent in TARGET] != M:
    raise AssertionError('source full map mismatch between Fraction and integer engines')


def reduce(a, initial, mode):
    """One of four fixed minimum-fill rules; ties use ascending row then column."""
    a, ops, done = copy.deepcopy(a), copy.deepcopy(initial), set()

    def emit(e):
        s.apply(a, e)
        ops.append(e)

    for _ in range(8):
        options = []
        for c in range(8):
            if c in done:
                continue
            for r in range(8):
                pivot = a[r][c]
                if r in done or not pivot or not s.power2(abs(pivot.numerator)) or not s.power2(pivot.denominator):
                    continue
                nr = sum(bool(x) for x in a[r])
                nc = sum(bool(a[k][c]) for k in range(8))
                swap = int(r != c)
                scores = ((nr-1)*(nc-1)+3*swap, nr+nc+3*swap,
                          nr+2*nc+4*swap, 2*nr+nc+4*swap)
                options.append((scores[mode], r, c))
        if not options:
            return None
        _, r, c = min(options)
        if r != c:
            for e in (add(c, r, 1), add(r, c, -1), add(c, r, 1), scale(r, -1)):
                emit(e)
        if a[c][c] != 1:
            emit(scale(c, 1/a[c][c]))
        for r in range(8):
            if r != c and a[r][c]:
                emit(add(r, c, -a[r][c]))
        done.add(c)
    if a != s.identity():
        raise AssertionError('residual elimination did not reach the identity')
    return s.collect(s.inverse(ops))


def butterfly(i, j, form):
    """(u,v)->(u+v,u-v), optionally halving either or both output rows."""
    ops = [add(i, j, 1), scale(j, -2), add(j, i, 1)]
    if form & 1:
        ops.append(scale(i, F(1, 2)))
    if form & 2:
        ops.append(scale(j, F(1, 2)))
    return ops


def input_pair(i, j, form):
    """Seven explicit weighted or triangular two-register prefixes; see SEARCH.json."""
    return ([add(j, i, F(-1, 2)), add(i, j, 1), scale(j, -1)],
            [add(i, j, -2), add(j, i, F(1, 2)), scale(i, F(1, 2))],
            [add(j, i, F(-1, 2)), add(i, j, 1)],
            [add(i, j, -2), add(j, i, F(1, 2))],
            [add(j, i, F(-1, 2))], [add(i, j, -2)], [])[form]


def right_inverse(matrix, ops):
    """If prefix matrix is P, return M P^-1 by exact elementary column operations."""
    a = copy.deepcopy(matrix)
    for e in ops:
        if e[0] == 'add':
            target, source, q = e[1], e[2], F(e[3], e[4])
            for row in a:
                row[source] -= q*row[target]
        else:
            for row in a:
                row[e[1]] /= F(e[2], e[3])
    return a


def enumerate_family(name, input_forms, pairings, lower_masks):
    counts = {'attempted': 0, 'no_binary_pivot': 0, 'exact_full_map_passed': 0}
    stream, words = hashlib.sha256(), hashlib.sha256()
    best, best_spec, best_key = None, None, None
    for po in input_forms:
        prefix = [] if po is None else input_pair(1, 7, po[0]) + input_pair(2, 5, po[1])
        base = right_inverse(M, prefix)
        for pairing in pairings:
            for orientations in itertools.product(range(2), repeat=len(pairing)):
                for forms in itertools.product(range(4), repeat=len(pairing)):
                    for bottom_mask in lower_masks:
                        ops = []
                        for (i, j), orientation, form in zip(pairing, orientations, forms):
                            ops += butterfly(j, i, form) if orientation else butterfly(i, j, form)
                        if bottom_mask & 1:
                            ops.append(add(6, 5, -1))
                        if bottom_mask & 2:
                            ops.append(add(7, 5, -1))
                        a = copy.deepcopy(base)
                        for e in ops:
                            s.apply(a, e)
                        for mode in range(4):
                            specification = [po, pairing, orientations, forms, bottom_mask, mode]
                            counts['attempted'] += 1
                            tail = reduce(a, ops, mode)
                            if tail is None:
                                counts['no_binary_pivot'] += 1
                                stream.update(canonical([specification, 'no_binary_pivot']) + b'\n')
                                continue
                            candidate = s.collect(prefix + tail)
                            result = exact_dyadic_map(candidate)
                            if result != TARGET:
                                raise AssertionError(('full dirty-map failure', name, specification))
                            counts['exact_full_map_passed'] += 1
                            key = (current_cost(candidate), len(candidate))
                            stream.update(canonical([specification, key, result]) + b'\n')
                            words.update(canonical([specification, candidate]) + b'\n')
                            if best_key is None or key < best_key:
                                best, best_spec, best_key = candidate, specification, key
    return {
        'family': name, 'counts': counts, 'best_current_primitives': best_key[0],
        'best_scalar_gates': best_key[1], 'best_specification': best_spec,
        'cost_and_exact_map_stream_sha256': stream.hexdigest(),
        'candidate_word_stream_sha256': words.hexdigest(),
        'best_replacement': best,
    }


def run():
    families = [enumerate_family('output-pair-butterflies', [None], MATCHINGS, range(4)),
                enumerate_family('weighted-input-pairs-and-output-butterflies',
                                 itertools.product(range(7), repeat=2), [[]] + MATCHINGS, [0, 3])]
    best = min(families, key=lambda f: (f['best_current_primitives'], f['best_scalar_gates']))
    planned = [3072, 75656]
    for family, expected in zip(families, planned):
        family['planned_parameter_tuples'] = expected
        counts = family['counts']
        if counts['attempted'] != expected or counts['exact_full_map_passed'] + counts['no_binary_pivot'] != expected:
            raise AssertionError('incomplete declared family')
    if best['best_current_primitives'] < current_cost(C['replacement']):
        raise AssertionError('negative-result conclusion invalidated by an improvement')
    receipt = {
        'format': 'finite-butterfly-enumeration-v1', 'assignment_seed': 21,
        'seed_role': 'track assignment; no stochastic search',
        'base_commit': '91a2094f2e022930069e8cfdc810a3ea1b81cd09',
        'source_pins_sha256': PINS, 'target_map_sha256': TARGET_SHA,
        'stopping_rule': 'Enumerate both complete Cartesian products exactly once; no restart or adaptive extension.',
        'counting_unit': 'Parameter tuples, not distinct circuits. Families overlap and may nominate identical words.',
        'objective': 'Minimize current PR #696 primitive count, then scalar-gate count; retain the first tuple on a complete tie.',
        'improvement_test': 'Strictly fewer current primitives than the incumbent 81.',
        'domain': {
            'output_pairings': MATCHINGS,
            'output_orientations_per_pair': [0, 1],
            'output_halving_masks_per_pair': [0, 1, 2, 3],
            'lower_difference_masks_first_family': [0, 1, 2, 3],
            'lower_difference_masks_second_family': [0, 3],
            'input_pairs_second_family': [[1, 7], [2, 5]],
            'input_prefix_maps_on_u_v_in_order': [
                ['u/2+v', 'u/2-v'], ['u/2-v', 'u/2'],
                ['u/2+v', 'v-u/2'], ['u-2v', 'u/2'],
                ['u', 'v-u/2'], ['u-2v', 'v'], ['u', 'v']],
            'second_family_allows_no_output_butterfly': True,
            'residual_rules': ['(nr-1)*(nc-1)+3*swap', 'nr+nc+3*swap',
                               'nr+2*nc+4*swap', '2*nr+nc+4*swap'],
            'residual_tie_break': 'ascending row, then ascending column',
            'scope_limit': 'Only these prefixes, output butterflies, and four deterministic residual rules; not all block or butterfly factorizations.',
        },
        'baseline_scalar_gates': len(C['replacement']),
        'baseline_current_primitives': current_cost(C['replacement']),
        'families': families,
        'conclusion': 'No strict current-primitive improvement in these finite families; no global optimality or impossibility claim.',
    }
    candidate = {
        'format': 'exact-factory-butterfly-negative-witness-v1',
        'status': 'nearest losing witness, not a proposed construction improvement',
        'assignment_seed': 21, 'base_commit': receipt['base_commit'],
        'contributors': ['Ross Richardson'],
        'assistance': 'Substantial OpenAI Codex assistance in algebra, implementation, and verification.',
        'predecessors': ['Alluri PR #681', 'Jeremy Kothe PR #622', 'current lowering PR #696'],
        'source_pins_sha256': PINS,
        **{key: C[key] for key in ('frame', 'entry_frames', 'exit_frames', 'matrix')},
        'replacement': best['best_replacement'], 'family': best['family'],
        'specification': best['best_specification'],
        'scalar_gates': best['best_scalar_gates'],
        'current_real_primitives': best['best_current_primitives'],
        'historical_real_primitives': s.primitive_cost(best['best_replacement']),
    }
    return receipt, candidate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='replace only local SEARCH.json and candidate.json')
    args = parser.parse_args()
    receipt, candidate = run()
    for filename, value in [('SEARCH.json', receipt), ('candidate.json', candidate)]:
        if args.write:
            (HERE / filename).write_text(json.dumps(value, indent=2) + '\n')
        elif json.loads((HERE / filename).read_text()) != json.loads(json.dumps(value)):
            raise AssertionError('replay receipt mismatch: ' + filename)
    for family in receipt['families']:
        print(f"PASS {family['family']} attempted={family['counts']['attempted']} "
              f"exact={family['counts']['exact_full_map_passed']} "
              f"best={family['best_current_primitives']} primitives/{family['best_scalar_gates']} gates")
    print('PASS finite-family negative result; baseline=81 primitives/34 gates')


if __name__ == '__main__':
    main()
