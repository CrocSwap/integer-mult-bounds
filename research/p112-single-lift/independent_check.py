"""Independent finite-premise audit: no imports from geometry.py or verify.py.

Checks integer minors and binary ranks with Bareiss and set elimination.
The written all-real-parameter argument in PROOF.md remains a separate proof.
Apache-2.0; substantial OpenAI Codex assistance, no human-only review claimed.
"""

from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise ValueError(message)


def bits(value):
    return {i for i, c in enumerate(reversed(bin(value)[2:])) if c == '1'}


def rank(rows):
    basis = {}
    for original in rows:
        row = set(original)
        while row:
            pivot = min(row)
            if pivot in basis:
                row.symmetric_difference_update(basis[pivot])
            else:
                basis[pivot] = row
                break
    return len(basis)


def determinant(matrix):
    a = [list(row) for row in matrix]
    previous, sign = 1, 1
    for k in range(len(a) - 1):
        pivot = next((i for i in range(k, len(a)) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        value = a[k][k]
        for i in range(k + 1, len(a)):
            for j in range(k + 1, len(a)):
                numerator = a[i][j] * value - a[i][k] * a[k][j]
                check(numerator % previous == 0, 'Bareiss exact division')
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = value
    return sign * a[-1][-1]


def pair(a, b):
    return len(a & b) % 2


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def canonical(root):
    return tuple(root if next(v for v in root if v) > 0 else [-v for v in root])


def main():
    certificate = json.loads((HERE / 'RESULTS.json').read_text(encoding='utf-8'))
    raw = (HERE / 'reference-geometry.json').read_bytes()
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    check(sha256(raw).hexdigest() == sources['local_inputs']['reference-geometry.json'], 'geometry hash')
    data = json.loads(raw)
    x, roots = data['X'], data['roots']
    labels, duals = list(map(bits, data['labels'])), list(map(bits, data['duals']))
    root_lines = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[i], root[j] = 2, 2 * sign
            root_lines.add(tuple(root))
    root_lines.update(canonical(list(s)) for s in product((-1, 1), repeat=8)
                      if sum(v < 0 for v in s) % 2 == 0)
    frame = []
    for i in range(0, 8, 2):
        for sign in (1, -1):
            root = [0] * 8
            root[i], root[i + 1] = 2, 2 * sign
            frame.append(root)
    check(data['frame'] == frame, 'deleted frame')
    check(len(roots) == 112 and {canonical(r) for r in roots}
          == root_lines - {tuple(r) for r in frame}, 'independent root construction')
    check(rank(labels) == rank(duals) == 9, 'ambient span')
    for i in range(112):
        check(x[i] == [dot(roots[i], f) // 4 for f in frame], 'frame coordinates')
        for j in range(112):
            g4 = dot(roots[i], roots[j])
            check(g4 % 4 == 0 and pair(duals[i], labels[j]) == (1 + g4 // 4) % 2,
                  'independent pairing check')
            check(dot(x[i], x[j]) == g4 // 2, 'independent scalar identity')

    support = certificate['support_certificates']
    check([c['functional'] for c in support] == list(range(1, 512)), 'functional coverage')
    minor_values, exceptional = [], []
    for item in support:
        q = bits(item['functional'])
        indices = [i for i in range(112) if pair(q, duals[i])]
        zero_columns = [j for j in range(8) if all(x[i][j] == 0 for i in indices)]
        check(zero_columns == item['zero_columns'], 'all-port nullspace support')
        selected = item['basis_ports']
        check(len(set(selected)) == len(selected) == item['rank']
              and set(selected) <= set(indices), 'minor port membership')
        columns = [j for j in range(8) if j not in zero_columns]
        check(len(columns) == len(selected) in (7, 8), 'square minor size')
        value = determinant([[x[i][j] for j in columns] for i in selected])
        check(value != 0, 'nonsingular support minor')
        minor_values.append(value)
        if zero_columns:
            exceptional.extend(zero_columns)
    check(sorted(exceptional) == list(range(8)), 'eight exact coordinate exceptions')

    spaces = [[bits(v) for v in row] for row in certificate['reader_spaces']]
    for j, space in enumerate(spaces):
        actual = [duals[i] for i in range(112) if x[i][j]]
        check(len(space) == rank(space) == rank(actual) == rank(actual + space) == 8,
              'reader span certificate')
        check(rank([{k for k, q in enumerate(space) if pair(q, labels[i])}
                    for i in range(112) if x[i][j]]) == 8, 'baseline cost')
    evaluations = [[{k for k, q in enumerate(spaces[j]) if pair(q, label)}
                    for j in range(8)] for label in labels]
    expected = {c for c in product((-1, 0, 1), repeat=8)
                if sum(v != 0 for v in c) >= 2 and next(v for v in c if v) == 1}
    observed = [tuple(c['signs']) for c in certificate['cases']]
    check(len(observed) == len(set(observed)) == 3272 and set(observed) == expected,
          'all sign cases, no duplicates')
    kernels = 0
    for case in certificate['cases']:
        coefficients = case['signs']
        active = [j for j, v in enumerate(coefficients) if v]
        rows = []
        for i in range(112):
            for sign in (-1, 1):
                rows.append({8 * block + bit for block, j in enumerate(active)
                             if x[i][j] * coefficients[j] == sign
                             for bit in evaluations[i][j]})
        actual_rank = rank(rows)
        check(actual_rank == case['rank'] == (8 * len(active) if len(active) < 8 else 63),
              'independent sign rank')
        integer_rows = [sum(1 << b for b in row) for row in rows]
        encoded = json.dumps(integer_rows, sort_keys=True, separators=(',', ':')).encode()
        check(sha256(encoded).hexdigest() == case['rows_sha256'], 'constraint digest')
        if len(active) == 8:
            kernels += 1
            vector = bits(int(case['kernel'], 16))
            check(vector and max(vector) < 64 and all(not pair(row, vector) for row in rows),
                  'independent nullvector')
            qs = []
            for j in range(8):
                q = set()
                for b, normal in enumerate(spaces[j]):
                    if 8 * j + b in vector:
                        q.symmetric_difference_update(normal)
                qs.append(q)
            bad = [i for i in range(112)
                   if len({x[i][j] * coefficients[j] for j in range(8)
                           if pair(qs[j], labels[i])}) > 1]
            check(bad == case['conflict_ports'] and len(bad) == 56, 'actual kernel conflicts')
    check(kernels == 128, 'kernel coverage')

    # Direct adverse controls on the independent arithmetic implementation.
    check(determinant([[1, 2], [2, 4]]) == 0, 'singular-minor control')
    check(determinant([[0, 1], [1, 0]]) == -1, 'row-swap sign control')
    check(rank([{0, 1}, {1, 2}, {0, 2}]) == 2, 'binary dependence control')
    check(any(pair(row, {0}) for row in rows), 'corrupted-kernel control')
    print('PASS_P112_SINGLE_LIFT_INDEPENDENT: 511 nonzero integer minors; '
          '3272 set-rank replays; 128 incompatible kernels; 4 arithmetic controls')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print('FAIL_P112_SINGLE_LIFT_INDEPENDENT: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
