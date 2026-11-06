#!/usr/bin/env python3
"""Exact finite controls for the written algebraic-flag proof.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
No finite test below claims to prove the universal lower bound.
"""
from fractions import Fraction as F
import json

# An address scalar is a Gaussian rational a+b*i. Register coefficients
# remain F_2; the two kinds of arithmetic must never be conflated.
ZERO, ONE, I = (F(0), F(0)), (F(1), F(0)), (F(0), F(1))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def q(value):
    return tuple(map(F, value)) if isinstance(value, tuple) else (F(value), F(0))


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def neg(a):
    return -a[0], -a[1]


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def total(values):
    result = ZERO
    for value in values:
        result = add(result, value)
    return result


def mat(rows):
    return tuple(tuple(q(value) for value in row) for row in rows)


def plus(a, b):
    return tuple(tuple(add(x, y) for x, y in zip(ar, br)) for ar, br in zip(a, b))


def scale(a, value):
    return tuple(tuple(times(q(value), x) for x in row) for row in a)


def mm(a, b):
    return tuple(tuple(total(times(a[i][h], b[h][j]) for h in range(len(b)))
                       for j in range(len(b[0]))) for i in range(len(a)))


def det(a):
    check(len(a) == len(a[0]) == 2, 'determinant control is two-dimensional')
    return add(times(a[0][0], a[1][1]), neg(times(a[0][1], a[1][0])))


def rank_one(a):
    return det(a) == ZERO and any(x != ZERO for row in a for x in row)


def encode(a):
    return tuple(c for row in a for x in row for c in x)


def rational_rank(rows):
    a = [list(map(F, row)) for row in rows]
    pivot = 0
    for col in range(len(a[0])):
        found = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        divisor = a[pivot][col]
        a[pivot] = [x / divisor for x in a[pivot]]
        for i in range(len(a)):
            if i != pivot:
                value = a[i][col]
                a[i] = [x - value * y for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def binary_rank(vectors):
    basis = {}
    for vector in vectors:
        value = sum(b << i for i, b in enumerate(vector))
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def exp_add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def identity(n, zero):
    return [[{zero} if i == j else set() for j in range(n)] for i in range(n)]


def product(calls, project=encode):
    """Expand the ordered formal product; sets are polynomial supports in F_2."""
    check(bool(calls), 'controls supply a nonempty word')
    n = len(calls[0][1])
    zero = (F(0),) * len(project(calls[0][0]))
    result = identity(n, zero)
    for frame, x, y in calls:
        check(len(x) == len(y) == n, 'scalar-vector size mismatch')
        check(all(b in (0, 1) for b in x + y), 'nonbinary scalar vector')
        check(sum(a * b for a, b in zip(x, y)) % 2 == 1, 'nonidempotent call')
        exponent = project(frame)
        # Right multiplication by I+([frame]+1)xy^T uses the old P*x column.
        columns = []
        for row in result:
            value = set()
            for p, active in zip(row, x):
                if active:
                    value ^= p
            columns.append(value)
        result = [[p ^ ({exp_add(e, exponent) for e in columns[i]} ^ columns[i])
                   if y[j] else set(p)
                   for j, p in enumerate(row)] for i, row in enumerate(result)]
    return result


def expected(targets, helpers, project=encode):
    zero = (F(0),) * len(project(targets[0]))
    exponents = [project(a) for a in targets] + [zero] * helpers
    n = len(exponents)
    return [[{exponents[i]} if i == j else set() for j in range(n)] for i in range(n)]


def coordinate_calls(parts, helpers):
    n = len(parts) + helpers
    result = []
    for role, frames in enumerate(parts):
        vector = tuple(int(i == role) for i in range(n))
        result.extend((frame, vector, vector) for frame in frames)
    return result


def transform(calls, left, right):
    return [(mm(mm(left, a), right), x, y) for a, x, y in calls]


def flag_count(calls, targets, helpers):
    t, n = len(targets), len(targets) + helpers
    check(all(a[0][1] == ZERO and det(a) != ZERO for a in targets), 'target flag absent')
    check(all(rank_one(a) for a, _, _ in calls), 'non-rank-one block frame')
    upper = [(a, x, y) for a, x, y in calls if a[0][1] != ZERO]
    check(product(calls, lambda a: a[0][1]) == identity(n, (F(0), F(0))),
          'upper-entry projection is not identity')
    rx = binary_rank([x for _, x, _ in upper])
    ry = binary_rank([y for _, _, y in upper])
    check(rx + ry <= len(upper), 'cancellation span inequality failed')
    lower_counts = []
    for i in range(2):
        project = lambda a, i=i: a[i][i]
        check(product(calls, project) == expected(targets, helpers, project),
              'diagonal projected identity failed')
        check(sum(a[i][i] != ZERO for a in targets) == t, 'diagonal output rank is not t')
        count = sum(a[0][1] == ZERO and a[i][i] != ZERO for a, _, _ in calls)
        lower_counts.append(count)
        check(t <= rx + count and t <= ry + count, 'diagonal scalar-span bound failed')
    check(sum(lower_counts) <= len(calls) - len(upper), 'lower-frame assignments overlap')
    check(len(calls) >= 2 * t, 'finite fixture contradicts the bound')
    return {'calls': len(calls), 'data': t, 'helpers': helpers, 'upper_calls': len(upper),
            'scalar_column_rank': rx, 'scalar_row_rank': ry, 'lower_counts': lower_counts}


def verify_case(name, parts, helpers, left, right):
    targets = [plus(frames[0], frames[1]) for frames in parts]
    calls = coordinate_calls(parts, helpers)
    check(all(rank_one(a) for a, _, _ in calls), name + ': illegal original frame')
    check(all(det(a) != ZERO for a in targets), name + ': singular data target')
    check(rational_rank([encode(a) for a, _, _ in calls]) == 3, name + ': wrong span')
    check(product(calls) == expected(targets, helpers), name + ': formal identity failed')
    check(det(left) != ZERO and det(right) != ZERO, name + ': singular address change')
    moved = transform(calls, left, right)
    moved_targets = [mm(mm(left, a), right) for a in targets]
    check(product(moved) == expected(moved_targets, helpers), name + ': field extension failed')
    record = flag_count(moved, moved_targets, helpers)
    record['case'] = name
    return record, calls, targets, moved_targets


def main():
    e1, e2 = mat([[1, 0], [0, 0]]), mat([[0, 0], [0, 1]])
    eye = plus(e1, e2)
    c = plus(e1, scale(e2, -1))
    d = mat([[0, 1], [1, 0]])
    j, h = mat([[1, 1], [1, 1]]), mat([[1, -1], [-1, 1]])
    left = mat([[F(1, 2), (0, F(1, 2))], [F(1, 2), (0, F(-1, 2))]])
    right = mat([[1, 1], [I, neg(I)]])
    pair_parts = [(e1, scale(e2, -1)), (scale(j, F(1, 2)), scale(h, F(-1, 2)))]
    results = []
    record, calls, targets, moved_targets = verify_case('irreducible_quadratic_pair', pair_parts, 1, left, right)
    results.append(record)
    check(targets == [c, d], 'wrong sharp targets')
    relative = mm(c, d)
    check(add(relative[0][0], relative[1][1]) == ZERO and det(relative) == ONE,
          'relative characteristic polynomial must be z^2+1')
    check(moved_targets == [eye, mat([[I, 0], [0, neg(I)]])], 'wrong Gaussian diagonalization')
    moved = transform(calls, left, right)
    check([a[0][1] for a, _, _ in moved] == [q(F(1, 2)), q(F(-1, 2))] * 2,
          'wrong upper-entry cancellation values')

    pencil_parts = pair_parts + [(j, scale(e2, -2))]
    record, _, pencil_targets, _ = verify_case('commuting_three_target_pencil', pencil_parts, 2, left, right)
    results.append(record)
    check(pencil_targets[2] == plus(c, d), 'third target escaped the pencil')
    u, v = mm(c, pencil_targets[1]), mm(c, pencil_targets[2])
    check(mm(u, v) == mm(v, u), 'pencil relatives do not commute')

    mixed_x, mixed_y = (1, 0, 1), (0, 0, 1)
    helper_word = calls + [(e1, mixed_x, mixed_y), (scale(e1, -1), mixed_x, mixed_y)]
    check(product(helper_word) == expected(targets, 1), 'helper restoration failed')
    helper_moved = transform(helper_word, left, right)
    record = flag_count(helper_moved, moved_targets, 1)
    record['case'] = 'helper_mixing_and_cleanup'
    results.append(record)
    broken = helper_word[:-1]
    check(product(broken) != expected(targets, 1), 'missing cleanup was accepted')
    check(product(transform(broken, left, right), lambda a: a[0][1]) != identity(3, (F(0), F(0))),
          'missing upper cancellation was accepted')
    bad_upper = [(a, x, y) for a, x, y in transform(broken, left, right) if a[0][1] != ZERO]
    check(binary_rank([x for _, x, _ in bad_upper]) + binary_rank([y for _, _, y in bad_upper])
          > len(bad_upper), 'missing-cancellation control did not violate the conditional rank bound')

    # A repeated-root relative matrix is not diagonalizable but retains a flag.
    jordan = mat([[1, 1], [0, 1]])
    jordan_parts = [(e1, e2), (e1, mat([[0, 1], [0, 1]]))]
    swap = mat([[0, 1], [1, 0]])
    record, _, jordan_targets, jordan_moved = verify_case('nondiagonalizable_jordan_pair', jordan_parts, 1, swap, swap)
    results.append(record)
    check(jordan_targets[1] == jordan and jordan != eye, 'Jordan control is scalar')
    nilpotent = plus(jordan, scale(eye, -1))
    check(mm(nilpotent, nilpotent) == scale(eye, 0), 'Jordan minimal polynomial is wrong')
    check(jordan_moved[1][1][0] == ONE, 'Jordan block was incorrectly diagonalized')

    # This feasible low-span triple has no common invariant line over Qbar.
    diagonal = mat([[1, 0], [0, 2]])
    symmetric = mat([[2, 1], [1, 2]])
    nonflag_parts = [(e1, e2), (e1, scale(e2, 2)),
                     (mat([[2, 1], [1, F(1, 2)]]), scale(e2, F(3, 2)))]
    nonflag = coordinate_calls(nonflag_parts, 1)
    check(all(rank_one(a) for a, _, _ in nonflag), 'nonflag fixture contains illegal frame')
    check(rational_rank([encode(a) for a, _, _ in nonflag]) == 3, 'nonflag span must be three')
    check(product(nonflag) == expected([eye, diagonal, symmetric], 1), 'nonflag direct word failed')
    commutator = plus(mm(diagonal, symmetric), scale(mm(symmetric, diagonal), -1))
    check(det(commutator) == ONE, 'no-common-line rejection certificate failed')
    check(not rank_one(symmetric), 'rank-two frame was wrongly accepted')

    # Formal exponent addition must not inherit multiplicative torsion of i.
    gaussian_call = (mat([[I]]), (1,), (1,))
    check(product([gaussian_call, gaussian_call]) == expected([mat([[(0, 2)]])], 0),
          'Gaussian exponent addition failed')
    check(product([gaussian_call, gaussian_call]) != identity(1, (F(0), F(0))),
          'algebraic multiplication was substituted for additive exponents')
    check(product([(e1, (1,), (1,)), (e1, (1,), (1,))]) != identity(1, (F(0),) * 8),
          'rational address entries were reduced modulo two')
    try:
        product([(e1, (1, 0), (0, 1))])
    except ValueError as error:
        check(str(error) == 'nonidempotent call', 'unexpected rejection reason')
    else:
        raise ValueError('nonidempotent scalar update was accepted')

    print(json.dumps({'status': 'PASS_EXACT_FINITE_CONTROLS', 'cases': results,
                      'nonflag_triple': {'calls': 6, 'data': 3, 'helpers': 1,
                                        'frame_span': 3, 'commutator_determinant': '1'},
                      'rejection_controls': ['missing_helper_cleanup', 'missing_upper_cancellation',
                                             'no_algebraic_common_line', 'rank_two_paid_frame',
                                             'multiplicative_torsion_alias', 'address_mod_two_alias',
                                             'nonidempotent_scalar_update'],
                      'scope': 'Finite exact corroboration; universal result is in PROOF.md.'}, indent=2))


if __name__ == '__main__':
    main()
