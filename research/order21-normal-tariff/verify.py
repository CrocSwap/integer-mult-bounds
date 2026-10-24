#!/usr/bin/env python3
"""Exact corroboration of the normal-C7 call tariff; standard library only."""

import hashlib
import itertools
import json
from pathlib import Path

MAX_DIM = 128


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    require(1 <= n <= MAX_DIM, 'matrix dimension outside fixed replay limit')
    return tuple(1 << i for i in range(n))


def xor(a, b):
    require(len(a) == len(b), 'matrix sum dimensions')
    return tuple(x ^ y for x, y in zip(a, b))


def multiply(a, b):
    n = len(a)
    require(1 <= n <= MAX_DIM and len(b) == n, 'matrix product dimensions')
    require(all(0 <= row < 1 << n for row in a + b), 'matrix row range')
    out = []
    for row in a:
        value = 0
        for j in range(n):
            if row >> j & 1:
                value ^= b[j]
        out.append(value)
    return tuple(out)


def rank(rows):
    require(1 <= len(rows) <= MAX_DIM, 'rank dimension')
    pivots = [0] * MAX_DIM
    answer = 0
    for row in rows:
        require(0 <= row < 1 << MAX_DIM, 'rank row range')
        value = row
        for j in range(MAX_DIM - 1, -1, -1):
            if value >> j & 1:
                if pivots[j]:
                    value ^= pivots[j]
                else:
                    pivots[j] = value
                    answer += 1
                    break
    return answer


def outer(x, y, n):
    require(0 < x < 1 << n and 0 < y < 1 << n, 'outer vector range')
    return tuple(y if x >> i & 1 else 0 for i in range(n))


def kron(a, b):
    n, d = len(a), len(b)
    require(1 <= n * d <= MAX_DIM, 'tensor dimension')
    return tuple(sum((b[u] << (j * d)) for j in range(n) if a[i] >> j & 1)
                 for i in range(n) for u in range(d))


def field_multiply(x, y):
    require(0 <= x < 8 and 0 <= y < 8, 'F8 element range')
    result = 0
    for _ in range(3):
        if y & 1:
            result ^= x
        y >>= 1
        x <<= 1
        if x & 8:
            x ^= 0b1011
    return result


def group_multiply(g, h):
    require(0 <= g < 21 and 0 <= h < 21, 'group label range')
    i, j = g % 7, g // 7
    k, ell = h % 7, h // 7
    return (i + (1 << j) * k) % 7 + 7 * ((j + ell) % 3)


def representation(g):
    i, j = g % 7, g // 7
    coefficient = 1
    for _ in range(i):
        coefficient = field_multiply(coefficient, 2)
    columns = []
    for bit in range(3):
        value = 1 << bit
        for _ in range(j):
            value = field_multiply(value, value)
        columns.append(field_multiply(coefficient, value))
    return tuple(sum(((columns[c] >> r) & 1) << c for c in range(3))
                 for r in range(3))


def check_group():
    matrices = tuple(representation(g) for g in range(21))
    a, b = (4, 5, 2), (1, 4, 6)
    require(matrices[1] == a and matrices[7] == b, 'generator matrices')
    require(len(set(matrices)) == 21, 'representation is faithful')
    for g, h in itertools.product(range(21), repeat=2):
        require(multiply(matrices[g], matrices[h]) == matrices[group_multiply(g, h)],
                'representation multiplication')
    deltas = tuple(rank(xor(m, identity(3))) for m in matrices)
    require(deltas == (0,) + (3,) * 6 + (2,) * 14, 'represented delta ranks')
    return matrices, deltas


def check_factors(matrices, deltas):
    count = 0
    for n in (4, 5):
        for x, y in itertools.product(range(1, 1 << n), repeat=2):
            if (x & y).bit_count() % 2 == 0:
                continue
            coupling = outer(x, y, n)
            require(multiply(coupling, coupling) == coupling, 'idempotent')
            require(rank(coupling) == 1, 'scalar coupling rank')
            for g in range(1, 21):
                delta = kron(coupling, xor(matrices[g], identity(3)))
                require(rank(delta) == deltas[g], 'paid represented rank')
                count += 1
    return count


def zero_coefficients(n):
    require(1 <= n <= 14, 'formal role limit')
    return [(0,) * n for _ in range(21)]


def endpoint(labels):
    result = zero_coefficients(len(labels))
    for i, g in enumerate(labels):
        require(0 <= g < 21, 'endpoint group label')
        rows = list(result[g])
        rows[i] ^= 1 << i
        result[g] = tuple(rows)
    return tuple(result)


def execute(word, n, left=None, right=None):
    require(len(word) <= 12, 'formal call limit')
    result = zero_coefficients(n)
    result[0] = identity(n) if left is None else left
    for g, coupling in word:
        require(1 <= g < 21 and len(coupling) == n, 'paid call dimensions')
        require(rank(coupling) == 1, 'paid scalar rank')
        require(multiply(coupling, coupling) == coupling, 'paid idempotence')
        updated = list(result)
        for h in range(21):
            delta = multiply(result[h], coupling)
            updated[h] = xor(updated[h], delta)
            target = group_multiply(h, g)
            updated[target] = xor(updated[target], delta)
        result = updated
    if right is not None:
        result = [multiply(coefficient, right) for coefficient in result]
    return tuple(result)


def coordinate_word(labels):
    n = len(labels)
    return tuple((g, outer(1 << i, 1 << i, n))
                 for i, g in enumerate(labels) if g)


def scalar_mix(n):
    shear_list = []
    for i in range(n - 1):
        for row, column in ((i, n - 1), (n - 1, i)):
            shear = list(identity(n))
            shear[row] ^= 1 << column
            shear_list.append(tuple(shear))
    forward = reverse = identity(n)
    for shear in shear_list:
        forward = multiply(forward, shear)
    for shear in reversed(shear_list):
        reverse = multiply(reverse, shear)
    require(multiply(forward, reverse) == identity(n), 'inverse scalar mixes')
    return forward, reverse


def regular_operator(coefficients):
    n = len(coefficients[0])
    require(n <= 5, 'faithful regular replay role limit')
    out = [0] * (21 * n)
    for g, scalar in enumerate(coefficients):
        for i, row in enumerate(scalar):
            for j in range(n):
                if row >> j & 1:
                    for h in range(21):
                        out[21 * i + group_multiply(g, h)] ^= 1 << (21 * j + h)
    return tuple(out)


def check_witnesses():
    count = 0
    digest = hashlib.sha256()
    for exponents in itertools.product(range(1, 7), repeat=4):
        labels = exponents + (0,)
        actual = execute(coordinate_word(labels), len(labels))
        require(actual == endpoint(labels), 'four-target full formal endpoint')
        digest.update(json.dumps(actual, separators=(',', ':')).encode())
        count += 1
    for width, dirty in itertools.product((5, 8, 12), (0, 2)):
        labels = tuple(1 + i % 6 for i in range(width)) + (0,) * dirty
        require(execute(coordinate_word(labels), len(labels)) == endpoint(labels),
                'additional full formal endpoint')
        count += 1
    return count, digest.hexdigest()


def check_mixing():
    labels = (1, 2, 4, 1, 0)
    n = len(labels)
    forward, reverse = scalar_mix(n)
    word = tuple((g, multiply(multiply(forward, p), reverse))
                 for g, p in coordinate_word(labels))
    actual = execute(word, n, reverse, forward)
    require(actual == endpoint(labels), 'dirty-mixed full formal endpoint')
    literal = kron(reverse, identity(21))
    for g, coupling in word:
        permutation = tuple(1 << group_multiply(g, h) for h in range(21))
        # The row encoding of left multiplication is the transpose of this column list.
        action = tuple(sum(((permutation[c] >> r) & 1) << c for c in range(21))
                       for r in range(21))
        call = xor(identity(21 * n), kron(coupling, xor(action, identity(21))))
        literal = multiply(literal, call)
    literal = multiply(literal, kron(forward, identity(21)))
    require(literal == regular_operator(actual), 'faithful full operator comparison')
    return labels, word, forward, reverse


def reject_check(predicate, message):
    try:
        require(predicate, message)
    except ValueError:
        return message
    raise ValueError('control was not rejected: ' + message)


def check_controls(labels, word, forward, reverse, matrices):
    controls = []
    n = len(labels)
    target = endpoint(labels)
    for i in range(4):
        changed = word[:i] + word[i + 1:]
        controls.append(reject_check(execute(changed, n, reverse, forward) == target,
                                     'omitted call ' + str(i)))
    controls.append(reject_check(execute(word, n, None, forward) == target,
                                 'omitted entry scalar map'))
    controls.append(reject_check(execute(word, n, reverse, None) == target,
                                 'omitted exit scalar map'))
    controls.append(reject_check(endpoint(labels[:-1] + (1,)) == target,
                                 'unrestored dirty operator'))
    controls.append(reject_check(endpoint((2,) + labels[1:]) == target,
                                 'wrong target exponent'))
    bad_b = multiply(matrices[7], matrices[7])
    controls.append(reject_check(multiply(bad_b, matrices[1]) ==
                                 multiply(matrices[2], bad_b), 'reversed Frobenius'))
    controls.append(reject_check(rank(xor(matrices[7], identity(3))) == 3,
                                 'order-three call charged rank three'))
    return controls


def main():
    matrices, deltas = check_group()
    factors = check_factors(matrices, deltas)
    witnesses, digest = check_witnesses()
    labels, word, forward, reverse = check_mixing()
    controls = check_controls(labels, word, forward, reverse, matrices)
    represented_target = kron(identity(5), (0, 0, 0))
    for i, g in enumerate(labels):
        projector = outer(1 << i, 1 << i, 5)
        represented_target = xor(represented_target,
                                 kron(projector, xor(matrices[g], identity(3))))
    require(rank(represented_target) == 12, 'four-target represented rank')
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in ('README.md', 'PROOF.md', 'TASK.json', 'SOURCES.json',
                 'VERIFY.json', 'verify.py'):
        content = (package / name).read_bytes()
        require(len(content) <= 1 << 20, 'package file size limit')
        hashes[name] = hashlib.sha256(content).hexdigest()
    print(json.dumps({'status': 'PASS_ORDER21_NORMAL_TARIFF',
                      'group_products': 441, 'paid_factors': factors,
                      'formal_witnesses': witnesses, 'mixed_regular_witnesses': 1,
                      'four_target_delta_rank': rank(represented_target),
                      'controls': controls, 'four_target_stream_sha256': digest,
                      'source_sha256': hashes}, sort_keys=True))


if __name__ == '__main__':
    main()
