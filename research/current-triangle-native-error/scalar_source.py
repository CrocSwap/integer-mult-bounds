#!/usr/bin/env python3
"""Check the exact rounded scalar law of the pinned three-field repair."""
from fractions import Fraction as F
from hashlib import sha1, sha256
from itertools import product
import gzip
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLES = (236, 544, 1000)
SOURCE = '3dd1199d95291ee96e6c0aeb6f55f86244a569b1d4975840bf0207e2dcf9c025'
CANDIDATE = 'ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d'
MATRIX = ((F(0), F(1, 2), F(1, 4)), (F(-2), F(1), F(0)), (F(-4), F(2), F(1)))
PERIODS = ((1, 0, 0), (0, 2, 0), (0, 0, 4))


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sources():
    for row in json.loads((HERE / 'VENDORED.json').read_text())['files']:
        raw = (HERE / row['path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'copied source hash')
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'copied source Git blob')
    old = json.loads(gzip.decompress((HERE / 'source/data/K372-2-WORD.json.gz').read_bytes()))
    edit = json.loads((HERE / 'source/EDIT.json').read_text())
    need(sha256(encoded(old)).hexdigest() == SOURCE == edit['source'], 'complete source identity')
    cursor, program = 0, []
    for block in edit['edits']:
        start, stop = block['start'], block['stop']
        need(cursor <= start <= stop <= len(old['program']), 'ordered source edit')
        need(old['program'][start:stop] == block['before'], 'exact edit preimage')
        program.extend(old['program'][cursor:start])
        program.extend(block['after'])
        cursor = stop
    program.extend(old['program'][cursor:])
    new = dict(old, program=program)
    need(sha256(encoded(new)).hexdigest() == CANDIDATE == edit['candidate'], 'complete candidate identity')
    before, after = old['program'][97747:97753], program[97842:97851]
    build = json.loads((HERE / 'source/evidence/BUILD.json').read_text())
    need(before == build['old_local_events'] and after == build['replacement_local_events'], 'literal local source tapes')
    next_event = ['ADD', 544, 972, '1/2', 927]
    need(old['program'][97753] == program[97851] == next_event, 'first later external operand')
    need([[str(x) for x in row] for row in MATRIX] == build['exact_local_matrix'], 'source rational matrix')
    return before, after, {'source_sha256': SOURCE, 'candidate_sha256': CANDIDATE,
                           'source_window': [97747, 97753], 'candidate_window': [97842, 97851],
                           'first_later_event': next_event,
                           'frames': {str(k): old['frames'][k] for k in (265, 751, 927)},
                           'old_events': before, 'new_events': after}


def core(events):
    result = []
    for event in events:
        need(event[0] in ('ADD', 'MOVE'), 'scalar core operation')
        need(event[1] in ROLES, 'local output role')
        if event[0] == 'ADD':
            need(event[2] in ROLES, 'local input role')
            result.append((ROLES.index(event[1]), ROLES.index(event[2]), F(event[3])))
    return result


def rational_run(tape, point, mode='exact'):
    state = list(map(F, point))
    exact = True
    for dest, source, coefficient in tape:
        value = state[dest] + coefficient * state[source]
        exact &= value.denominator == 1
        if mode == 'floor':
            value = F(value.numerator // value.denominator)
        elif mode == 'truncate':
            value = F(int(value))
        state[dest] = value
    return tuple(state), exact


def integer_run(tape, point):
    state = list(point)
    for dest, source, coefficient in tape:
        state[dest] += coefficient.numerator * state[source] // coefficient.denominator
    return tuple(state)


def expected(point):
    x, y, z = point
    old = ((2 * y + z) // 4, y - 2 * x, z + 2 * y - 4 * x)
    h = (z % 4) // 2
    new = (old[0], old[1] + h, old[2] + 2 * h)
    return old, new


def matrix(tape):
    columns = [rational_run(tape, [int(i == j) for i in range(3)])[0] for j in range(3)]
    return tuple(tuple(columns[j][i] for j in range(3)) for i in range(3))


def squared(values):
    return sum(x * x for x in values)


def verify_point(old, new, point):
    a, exact_a = rational_run(old, point, 'floor')
    b, exact_b = rational_run(new, point, 'floor')
    need((a, b) == expected(point), 'complete rounded residue law')
    need(a == integer_run(old, point) and b == integer_run(new, point), 'independent integer arithmetic')
    x, y, z = point
    need(exact_a == ((2 * y + z) % 4 == 0), 'old exactness lattice')
    need(exact_b == (z % 4 == 0 and y % 2 == 0), 'new exactness lattice')
    exact = tuple(sum(row[i] * point[i] for i in range(3)) for row in MATRIX)
    old_error = squared([a[i] - exact[i] for i in range(3)])
    new_error = squared([b[i] - exact[i] for i in range(3)])
    difference = squared([a[i] - b[i] for i in range(3)])
    need(old_error <= F(9, 16) and new_error <= F(89, 16) and difference <= 5, 'sharp local error bounds')
    return {'input': list(point), 'old': list(map(int, a)), 'new': list(map(int, b)),
            'old_exact': exact_a, 'new_exact': exact_b,
            'squared_old_error': str(old_error), 'squared_new_error': str(new_error),
            'squared_difference': str(difference)}


def controls(old, new):
    results = []
    for label, index, coefficient in [('wrong first quarter', 0, F(1, 2)),
                                       ('wrong middle sign', 3, F(-2)),
                                       ('wrong final half', 5, F(-1, 2))]:
        changed = list(new)
        dest, source, _ = changed[index]
        changed[index] = (dest, source, coefficient)
        need(matrix(changed) != MATRIX, 'arithmetic mutation changes matrix')
        witness = next((point for point in product(range(-2, 3), repeat=3)
                        if rational_run(changed, point, 'floor')[0] != expected(point)[1]), None)
        need(witness is not None, 'actual arithmetic mutation detected')
        results.append({'fault': label, 'witness': list(witness)})
    witness = next((point for point in product(range(-2, 3), repeat=3)
                    if rational_run(new, point, 'truncate')[0] != expected(point)[1]), None)
    need(witness is not None, 'signed truncation differs from floor')
    results.append({'fault': 'truncate signed fractions toward zero', 'witness': list(witness)})
    need(rational_run(old, (0, 1, 2), 'floor')[0] != rational_run(new, (0, 1, 2), 'floor')[0], 'exact matrix does not imply rounded equality')
    return results


def main():
    before, after, binding = sources()
    old, new = core(before), core(after)
    need(len(old) == 3 and len(new) == 6 and matrix(old) == matrix(new) == MATRIX, 'exact rational identity')
    prefixes = []
    for name, tape in [('old', old), ('new', new)]:
        for length in range(len(tape) + 1):
            shifts = [rational_run(tape[:length], period)[0] for period in PERIODS]
            need(all(x.denominator == 1 for shift in shifts for x in shift), 'every prefix has integral period shifts')
            prefixes.append({'tape': name, 'prefix_length': length, 'shifts': [list(map(int, shift)) for shift in shifts]})
    residues = [verify_point(old, new, (0, y, z)) for y in range(2) for z in range(4)]
    for point in product(range(-9, 10), repeat=3):
        verify_point(old, new, point)
    need(max(F(row['squared_old_error']) for row in residues) == F(9, 16), 'old bound attained')
    need(max(F(row['squared_new_error']) for row in residues) == F(89, 16), 'new bound attained')
    need(max(F(row['squared_difference']) for row in residues) == 5, 'difference bound attained')
    need(sum(row['old_exact'] for row in residues) == 2 and sum(row['new_exact'] for row in residues) == 1, 'exactness indices four and eight')
    paths = []
    for point in ((0, 1, 2), (0, 0, 3)):
        for name, tape in [('old', old), ('new', new)]:
            states = [list(map(int, rational_run(tape[:i], point, 'floor')[0])) for i in range(len(tape) + 1)]
            need(all(-8 <= value <= 7 for state in states for value in state), 'four-bit witness has no stored overflow')
            paths.append({'input': list(point), 'tape': name, 'states': states})
    result = {'binding': binding, 'scope': 'common-coordinate scalar core; native MOVE transports are not rounded here',
              'matrix': [[str(x) for x in row] for row in MATRIX],
              'period_generators': PERIODS, 'integral_prefix_shifts': prefixes,
              'residues': residues, 'signed_box_cases': 19 ** 3,
              'four_bit_paths': paths,
              'old_exact_new_inexact': verify_point(old, new, (0, 1, 2)),
              'worst_new_error': verify_point(old, new, (0, 0, 3)),
              'controls': controls(old, new)}
    file = HERE / 'RESULT.json'
    if sys.argv[1:] == ['--write']:
        need(not file.exists(), 'do not replace checked receipt')
        file.write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(not sys.argv[1:], 'unexpected arguments')
        need(encoded(result) == encoded(json.loads(file.read_text())), 'complete result receipt')
    print('PASS_CURRENT_TRIANGLE_ROUNDED_CONTRACT ' + json.dumps({'residues': 8, 'signed_cases': 19 ** 3,
          'old_exactness_index': 4, 'new_exactness_index': 8, 'new_squared_error': '89/16',
          'squared_difference': 5, 'controls': len(result['controls'])}, sort_keys=True))


if __name__ == '__main__':
    main()
