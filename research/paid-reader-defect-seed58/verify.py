#!/usr/bin/env python3
"""Independent exact replay and bounded census. Standard library, Python 3.10+.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def execute(word, initial, envelope=None):
    """Literal row interpreter: applies instructions to all basis columns."""
    state = [list(row) for row in initial]
    size = len(state)
    if envelope is not None:
        envelope['row_l1_peak'] = max(sum(abs(x) for x in row) for row in state)
    for op in word:
        require(isinstance(op, tuple) and op, 'malformed instruction')
        if op[0] == 'A':
            require(len(op) == 4, 'bad ADD arity')
            _, t, s, a = op
            require(type(t) is int and type(s) is int and 0 <= t < size
                    and 0 <= s < size and t != s and type(a) is int
                    and a in (-1, 1), 'invalid ADD')
            state[t] = [x + a * y for x, y in zip(state[t], state[s])]
        elif op[0] == 'N':
            require(len(op) == 2 and type(op[1]) is int
                    and 0 <= op[1] < size, 'invalid NEG')
            state[op[1]] = [-x for x in state[op[1]]]
        else:
            raise ValueError('unknown opcode')
        if envelope is not None:
            envelope['row_l1_peak'] = max(envelope['row_l1_peak'],
                                           sum(abs(x) for x in state[op[1]]))
    return state


def eager_matrix(children):
    n = len(children[0].row)
    matrix = eye(n + 1)
    for child in children:
        for j, a in enumerate(child.row):
            matrix[0][j + 1] += a
    return matrix


def oracle_segment(children):
    """Dense whole-state composition; no production defect or word helpers."""
    n = len(children[0].row)
    state = eye(n + 1)
    for child in children:
        old = [r[:] for r in state]
        for j, a in enumerate(child.row):
            for col in range(n + 1):
                state[0][col] += a * old[j + 1][col]
        for j, index in enumerate(child.perm):
            state[j + 1] = [(1 if index > 0 else -1) * x
                            for x in old[abs(index)]]
    expected = eager_matrix(children)
    error = tuple(state[0][j + 1] - expected[0][j + 1] for j in range(n))
    permutation = []
    negative = 0
    for row in state[1:]:
        support = [j for j, a in enumerate(row[1:]) if a]
        require(len(support) == 1, 'oracle drift ceased to be a permutation')
        j = support[0]
        require(abs(row[j + 1]) == 1, 'oracle drift coefficient')
        permutation.append(j)
        negative += row[j + 1] < 0
    seen, cycles = set(), 0
    for start in range(n):
        if start not in seen:
            cycles += 1
            j = start
            while j not in seen:
                seen.add(j)
                j = permutation[j]
    # Canonical permutation inverse: n-cycles swaps, four instructions each,
    # then one NEG for each negative sign. Correction uses |coefficient| ADDs.
    return 4 * (n - cycles) + negative + sum(abs(a) for a in error), error


def all_cuts(k, required=()):
    for mask in range(1 << (k - 1)):
        cuts = tuple(j for j in range(1, k) if mask & (1 << (j - 1))) + (k,)
        if set(required).issubset(cuts):
            yield cuts


def oracle_plan(children, required=(), zero=False):
    costs = {}
    for a in range(len(children)):
        for b in range(a + 1, len(children) + 1):
            costs[a, b] = oracle_segment(children[a:b])
    choices = []
    for cuts in all_cuts(len(children), required):
        start, price, legal = 0, 0, True
        for end in cuts:
            cost, error = costs[start, end]
            legal = legal and (not zero or not any(error))
            price += cost
            start = end
        if legal:
            choices.append((price, cuts))
    require(choices, 'oracle found no legal partition')
    return min(choices)


def check_batch(children, required=()):
    n = len(children[0].row)
    results = []
    for zero in (False, True):
        got = model.plan(children, required, zero)
        expected = oracle_plan(children, required, zero)
        require(got == expected, 'partition optimum differs from dense oracle')
        word = model.batch_word(children, tuple(range(1, n + 1)), 0, got[1])
        matrix = execute(word, eye(n + 1))
        require(matrix == eager_matrix(children), 'batch differs on a dirty basis column')
        require(execute(model.reverse_word(word), matrix) == eye(n + 1), 'literal inverse failed')
        results.append(got)
    return results


def selected():
    rng = random.Random(58)
    n = 3 + 58 % 4
    row = tuple(rng.choice((-1, 0, 1)) for _ in range(n))
    signs = [1, 1, 1, -1, -1]
    rng.shuffle(signs)
    p = tuple(range(2, n + 1)) + (1,)
    children = tuple(model.Child(tuple(s * a for a in row), p) for s in signs)
    return row, tuple(signs), p, children


def finite_census():
    signed = tuple(tuple(s * a for s, a in zip(signs, p))
                   for p in itertools.permutations((1, 2))
                   for signs in itertools.product((-1, 1), repeat=2))
    alphabet = tuple(model.Child(row, p)
                     for row in itertools.product((-1, 0, 1), repeat=2)
                     for p in signed)
    stream = hashlib.sha256()
    cases = partitions = improvements = 0
    for k in (1, 2):
        for children in itertools.product(alphabet, repeat=k):
            result = check_batch(children)
            stream.update(canonical(result))
            cases += 1
            partitions += 1 << (k - 1)
            improvements += result[0][0] < result[1][0]
    rng = random.Random(58)
    noncommuting, seeded_improvements, constrained = 0, 0, 0
    for case in range(160):
        n, k = rng.randrange(3, 7), rng.randrange(3, 8)
        children = []
        for _ in range(k):
            p = list(range(1, n + 1))
            rng.shuffle(p)
            p = tuple(x * rng.choice((-1, 1)) for x in p)
            row = tuple(rng.randrange(-2, 3) for _ in range(n))
            children.append(model.Child(row, p))
        required = tuple(j for j in range(1, k) if case % 3 == 0 and j % 2 == 0)
        constrained += bool(required)
        result = check_batch(tuple(children), required)
        stream.update(canonical([n, k, required, result]))
        seeded_improvements += result[0][0] < result[1][0]
        noncommuting += any(model.compose(a.perm, b.perm) != model.compose(b.perm, a.perm)
                            for a, b in zip(children, children[1:]))
    return {'exhaustive_batches': cases, 'exhaustive_partitions_per_policy': partitions,
            'exhaustive_strict_improvements': improvements, 'seeded_batches': 160,
            'seeded_noncommuting': noncommuting, 'seeded_with_required_cuts': constrained,
            'seeded_strict_improvements': seeded_improvements, 'results_sha256': stream.hexdigest()}


def check_recursive(depth, row, p, signs, mode, echo):
    word, size = model.recursive_word(depth, row, p, signs, mode, echo)
    envelope = {}
    matrix = execute(word, eye(size), envelope)
    expected = eye(size)
    for j, a in enumerate(row):
        expected[0][j + 1] += a
    if not echo:
        for j, x in enumerate(p):
            expected[j + 1] = [int(col == abs(x)) * (1 if x > 0 else -1)
                               for col in range(size)]
    require(matrix == expected, 'recursive reader/echo dirty map failed')
    require(execute(model.reverse_word(word), matrix) == eye(size), 'recursive inverse failed')
    # Separate rational input with nonzero values in every private scratch port.
    probe = [[Fraction(j + 1, j + 2)] for j in range(size)]
    want = [[sum(a * probe[j][0] for j, a in enumerate(r))] for r in expected]
    require(execute(word, probe) == want, 'rational dirty probe failed')
    result = model.counts(word)
    result['integer_row_l1_peak'] = envelope['row_l1_peak']
    # Recount from raw instruction tuples, independently of counts().
    reads = writes = fields = 0
    for op in word:
        reads += len(op) // 2
        writes += 1
        fields += len(op)
    require((reads, writes, fields) == (result['data_reads'], result['data_writes'],
                                      result['descriptor_fields']), 'access invoice failed')
    # Complete recursive arithmetic recurrence, independent of word generation.
    child_cost = sum(abs(a) for a in row)
    drift = oracle_segment((model.Child((0,) * len(row), tuple(p)),))[0]
    current = child_cost + drift
    children = tuple(model.Child(tuple(s * a for a in row), p) for s in signs)
    if mode == 'eager':
        boundary = sum(oracle_segment((c,))[0] for c in children)
    else:
        boundary = oracle_plan(children, zero=(mode == 'zero'))[0]
    for _ in range(depth):
        current = 2 * len(signs) * current + 2 * len(row) + 2 * boundary + drift
    if echo:
        current -= drift
    require(result['instructions'] == current, 'full recursive recurrence failed')
    return result, size


def recursive_census():
    rng, cases, columns = random.Random(5801), 0, 0
    stream = hashlib.sha256()
    for n in range(2, 6):
        for k in (3, 5):
            row = tuple(rng.choice((-1, 0, 1)) for _ in range(n))
            p = list(range(1, n + 1))
            rng.shuffle(p)
            p = tuple(x * rng.choice((-1, 1)) for x in p)
            signs = tuple([1] * ((k + 1) // 2) + [-1] * ((k - 1) // 2))
            for depth in range(3):
                for mode in ('eager', 'zero', 'repair'):
                    for echo in ((False,) if depth == 0 else (False, True)):
                        count, size = check_recursive(depth, row, p, signs, mode, echo)
                        cases += 1
                        columns += size
                        stream.update(canonical([n, k, depth, mode, echo, count]))
    row, signs, p, children = selected()
    chosen = []
    for depth in (1, 2, 3):
        for mode in ('eager', 'zero', 'repair'):
            count, size = check_recursive(depth, row, p, signs, mode, True)
            chosen.append({'depth': depth, 'mode': mode, 'registers': size, **count})
    return {'generic_cases': cases, 'generic_basis_columns': columns,
            'results_sha256': stream.hexdigest(), 'selected_echoes': chosen}


def failure_witness(word, expected, name):
    actual = execute(word, eye(len(expected)))
    require(actual != expected, name + ': mutation did not fail')
    column = next(j for j in range(len(expected))
                  if any(a[j] != b[j] for a, b in zip(actual, expected)))
    return {'control': name, 'input_basis_column': column,
            'actual': [r[column] for r in actual], 'expected': [r[column] for r in expected]}


def controls():
    row, signs, p, children = selected()
    ports = tuple(range(1, 6))
    raw = tuple(op for c in children for op in
                model.add_word(c.row, ports, 0) + model.permutation_word(c.perm, ports))
    expected = eager_matrix(children)
    correction = model.boundary_word(children, ports, 0)
    ans = [failure_witness(raw, expected, 'omit_nonzero_defect_correction'),
           failure_witness(raw + model.reverse_word(correction), expected, 'reverse_correction_sign')]
    # A noncommuting, nonidentity final drift distinguishes repair order.
    different = (model.Child((1, 0, 1), (2, 1, 3)),
                 model.Child((0, 1, -1), (1, 3, 2)))
    ports3 = (1, 2, 3)
    raw3 = tuple(op for c in different for op in
                 model.add_word(c.row, ports3, 0) + model.permutation_word(c.perm, ports3))
    final_p, e = model.defect(different)
    restore = model.permutation_word(model.inverse(final_p), ports3)
    repair = model.add_word(tuple(-a for a in e), ports3, 0)
    ans.append(failure_witness(raw3 + repair + restore, eager_matrix(different),
                               'repair_before_restoring_entry_coordinates'))
    ans.append(failure_witness(raw3 + repair, eager_matrix(different), 'omit_workspace_restoration'))
    wrong_restore = tuple(op for c in different for op in
                          model.permutation_word(model.inverse(c.perm), ports3))
    ans.append(failure_witness(raw3 + wrong_restore + repair, eager_matrix(different),
                               'wrong_noncommuting_inverse_order'))
    batch = model.batch_word(children, ports, 0)
    # Explicit two-pass echo at depth one: X=1..5, W=6..10.
    work = tuple(range(6, 11))
    copy = tuple(('A', w, x, 1) for w, x in zip(work, ports))
    b = model.batch_word(children, work, 0)
    target = eye(11)
    for j, a in enumerate(row):
        target[0][j + 1] += a
    ans.append(failure_witness(copy + b + model.reverse_word(b), target, 'omit_source_uncopy'))
    ans.append(failure_witness(copy + b + model.reverse_word(copy), target, 'omit_second_batch'))
    # Zero-initialized W hides the defect, while a nonzero dirty column exposes it.
    require([r[0] for r in execute(raw, eye(6))] == [r[0] for r in expected],
            'zero-workspace control was not actually hidden')
    first_two = tuple(op for c in children[:2] for op in
                      model.add_word(c.row, ports, 0) + model.permutation_word(c.perm, ports))
    prefix_error = execute(first_two, eye(6))[0]
    require(prefix_error != eager_matrix(children[:2])[0], 'unsafe prefix unexpectedly agreed')
    # Correct full restoration at every observation removes the exhibited gain.
    forced = model.plan(children, tuple(range(1, 5)))
    require(forced[0] == 80 and forced[1] == (1, 2, 3, 4, 5), 'forced observation boundary')
    ans.append({'control': 'premature_output_observer', 'actual_row': prefix_error,
                'expected_row': eager_matrix(children[:2])[0], 'forced_boundary_cost': forced[0]})
    _, delta = model.defect(children)
    require(sum(abs(a) for a in delta) == 12 and sum(a != 0 for a in delta) == 4,
            'coefficient magnitude pricing control failed')
    ans.append({'control': 'nonunit_coefficients_are_not_free', 'paid_ADD': 12, 'nonzero_entries': 4})
    invalid = [lambda: model.Child((True, 0), (1, 2)),
               lambda: model.Child((1, 0), (1, 1)),
               lambda: model.plan(()),
               lambda: model.plan(children, (0,)),
               lambda: model.plan(children, (5,)),
               lambda: model.batch_word(children, ports, 0, (2, 4)),
               lambda: model.recursive_word(1, row, p, (1, 1)),
               lambda: execute((('A', 0, 0, 1),), eye(1))]
    for call in invalid:
        try:
            call()
        except ValueError:
            pass
        else:
            raise ValueError('invalid input accepted')
    return {'mathematical_controls': ans, 'invalid_inputs_rejected': len(invalid)}


def source_check():
    pins = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    for pin in pins['sources']:
        data = (HERE / pin['local_path']).read_bytes()
        require(digest(data) == pin['sha256'], 'source SHA256 mismatch')
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == pin['git_blob'], 'source Git blob mismatch')
    return {'base_commit': pins['base_commit'], 'source_notes': len(pins['sources']),
            'source_manifest_sha256': digest((HERE / 'SOURCE-PINS.json').read_bytes()),
            'model_sha256': digest((HERE / 'model.py').read_bytes()),
            'verifier_sha256': digest(Path(__file__).read_bytes())}


def certificate():
    provenance = source_check()  # Fail before the census if source bytes changed.
    row, signs, p, children = selected()
    every_partition = []
    for cuts in all_cuts(5):
        word = model.batch_word(children, tuple(range(1, 6)), 0, cuts)
        require(execute(word, eye(6)) == eager_matrix(children), 'selected partition map')
        every_partition.append({'cuts': cuts, 'instructions': len(word)})
    return {'format': 'paid-reader-defect-v1', 'assignment_seed': 58,
            'status': 'scoped exact recursive-interface construction; no new kappa',
            'provenance': provenance,
            'selected': {'row': row, 'signs': signs, 'drift': p,
                         'defect': model.defect(children)[1],
                         'repair_plan': model.plan(children),
                         'zero_defect_plan': model.plan(children, zero_defect_only=True),
                         'all_partitions': every_partition},
            'finite_census': finite_census(), 'recursive_census': recursive_census(),
            'controls': controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='print recomputed certificate; no writes')
    args = parser.parse_args()
    result = json.loads(json.dumps(certificate()))
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    expected = json.loads((HERE / 'CERTIFICATE.json').read_text())
    require(result == expected, 'certificate mismatch')
    c = result['finite_census']
    print('PASS_PAID_READER_DEFECT'
          f" batches={c['exhaustive_batches']} seeded={c['seeded_batches']}"
          ' echo=380->244 controls=9 kappa=unchanged')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print('FAIL_PAID_READER_DEFECT: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
