#!/usr/bin/env python3
"""Independently replay the two columns of every recorded cleanup minor."""

import argparse
import gzip
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path


SOURCE = Path('research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/CANONICAL-WORD.json.gz')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def apply(gate, column, inverse=False):
    if gate[0] == 'add':
        q = Fraction(gate[3], gate[4])
        column[gate[1]] += (-q if inverse else q) * column[gate[2]]
    elif gate[0] == 'scale':
        q = Fraction(gate[2], gate[3])
        require(q != 0, 'noninvertible middle scale')
        column[gate[1]] *= 1 / q if inverse else q
    else:
        raise ValueError('unexpected cleanup gate')


def difference_column(word, i, j, column_index, n):
    column = [Fraction(0) for _ in range(n)]
    column[column_index] = Fraction(1)
    for gate in reversed(word[i + 1:j]):
        apply(gate, column, inverse=True)
    for gate in word[i:j + 1]:
        apply(gate, column)
    column[column_index] -= 1
    return column


def dual_gate(gate):
    if gate[0] == 'add':
        return ['add', gate[2], gate[1], -gate[3], gate[4], gate[5]]
    return ['scale', gate[1], gate[3], gate[2], gate[4]]


def self_check():
    add = ['add', 0, 1, 1, 1, 1]
    middle = ['add', 1, 0, 1, 1, 1]
    word = [add, middle, add]
    require(difference_column(word, 0, 2, 0, 2) == [-2, -1], 'rank-two control column 0')
    require(difference_column(word, 0, 2, 1, 2) == [3, 1], 'rank-two control column 1')
    dual = [dual_gate(gate) for gate in word]
    require(difference_column(dual, 0, 2, 0, 2) == [1, -3], 'dual control column 0')
    require(difference_column(dual, 0, 2, 1, 2) == [1, -2], 'dual control column 1')
    word = [add, ['scale', 1, 2, 1, 1], add]
    require(difference_column(word, 0, 2, 0, 2) == [0, 0], 'scale control column 0')
    require(difference_column(word, 0, 2, 1, 2) == [Fraction(3, 2), 0], 'scale control column 1')


def verify(root, certificate):
    self_check()
    with gzip.open(Path(root) / SOURCE, 'rt') as stream:
        source = json.load(stream)
    word = source['cleanup']
    n = 2 * source['v'] + source['R']
    groups = {}
    for index, gate in enumerate(word):
        require(gate[0] in ('add', 'scale'), 'unexpected cleanup gate')
        require(len(gate) == (6 if gate[0] == 'add' else 5), 'unexpected gate shape')
        registers = gate[1:3] if gate[0] == 'add' else gate[1:2]
        require(all(type(r) is int and 0 <= r < n for r in registers), 'invalid register')
        require(gate[-1] == 1, 'cleanup gate outside full frame')
        if gate[0] == 'add':
            require(gate[1] != gate[2] and Fraction(gate[3], gate[4]) != 0, 'invalid addition')
            groups.setdefault(tuple(gate[1:3]), []).append(index)
        else:
            require(Fraction(gate[2], gate[3]) != 0, 'noninvertible scale')
    expected = sorted(pair for group in groups.values() for pair in combinations(group, 2))
    pairs = certificate['pairs']
    require(sorted((p['i'], p['j']) for p in pairs) == expected, 'incomplete or duplicated pair coverage')
    words = (word, [dual_gate(gate) for gate in word])
    for pair in pairs:
        i, j = pair['i'], pair['j']
        for record, oriented_word in zip((pair, pair['dual']), words):
            first, last = oriented_word[i], oriented_word[j]
            t, s = record['t'], record['s']
            require(first[1:3] == last[1:3] == [t, s], 'endpoint registers differ')
            require(Fraction(record['a']) == Fraction(first[3], first[4]), 'first coefficient differs')
            require(Fraction(record['b']) == Fraction(last[3], last[4]), 'last coefficient differs')
            rows, columns = record['rows'], record['columns']
            require(len(rows) == len(columns) == 2, 'minor must be two by two')
            require(rows[0] == t and columns[0] == s, 'minor anchor differs')
            require(rows[1] != t and columns[1] != s, 'minor indices repeat')
            require(all(type(r) is int and 0 <= r < n for r in rows + columns), 'invalid minor index')
            replayed = [difference_column(oriented_word, i, j, c, n) for c in columns]
            minor = [[replayed[c][r] for c in range(2)] for r in rows]
            declared = [[Fraction(value) for value in row] for row in record['minor']]
            require(minor == declared, f'minor entries differ for pair {i}, {j}')
            determinant = minor[0][0] * minor[1][1] - minor[0][1] * minor[1][0]
            require(determinant != 0, f'zero minor for pair {i}, {j}')
            require(determinant == Fraction(record['determinant']), f'determinant differs for pair {i}, {j}')
            # Direct columns check the minor, not the conjugation-vector support counts.
    return 4 * len(pairs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', nargs='?', type=Path, default=Path(__file__).with_name('CERTIFICATE.json'))
    arguments = parser.parse_args()
    with arguments.certificate.open() as stream:
        certificate = json.load(stream)
    count = verify(Path(__file__).resolve().parents[2], certificate)
    print(f'PASS independent direct-column replay: {count // 4} pairs, {count} columns, {2 * count} minor entries in both orientations')
