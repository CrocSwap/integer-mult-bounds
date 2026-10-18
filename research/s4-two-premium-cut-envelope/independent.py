#!/usr/bin/env python3
"""Separate Floyd-Warshall and literal-set corroboration; imports no producer.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check(ok, text):
    if not ok:
        raise ValueError(text)


def swapped(p, i):
    p = list(p)
    p[i], p[i + 1] = p[i + 1], p[i]
    return tuple(p)


def floyd(vertices, prices):
    # Right adjacent swaps, unlike the producer's left multiplication.
    positions = {p: i for i, p in enumerate(vertices)}
    distance = [[Fraction(10000)] * 24 for _ in vertices]
    for i, p in enumerate(vertices):
        distance[i][i] = Fraction(0)
        for k in range(3):
            distance[i][positions[swapped(p, k)]] = prices[k]
    for middle in range(24):
        for left in range(24):
            for right in range(24):
                distance[left][right] = min(distance[left][right],
                    distance[left][middle] + distance[middle][right])
    return distance


def run():
    identity = (1, 2, 3, 4)
    vertices = [identity]
    for p in vertices:
        for i in range(3):
            q = swapped(p, i)
            if q not in vertices:
                vertices.append(q)
    check(len(vertices) == 24, 'group coverage')
    ix = {p: i for i, p in enumerate(vertices)}
    unit = floyd(vertices, [1, 1, 1])
    outer = floyd(vertices, [1, 0, 1])
    receipt = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
    scalar = {tuple(map(int, row['target'])): row for row in receipt['scalar_table']}
    # Undeduplicated words, not shortest-path predecessor data: all 1,093 words
    # through length six. Keep every simultaneous unit/exterior witness.
    simultaneous = {}
    traversed = 0
    for length in range(7):
        for letters in product(range(3), repeat=length):
            p = identity
            for letter in letters:
                p = swapped(p, letter)
            exterior = sum(letter != 1 for letter in letters)
            traversed += 1
            if length == unit[0][ix[p]] and exterior == outer[0][ix[p]]:
                simultaneous.setdefault(p, letters)
    check(traversed == 1093 and len(simultaneous) == 24, 'simultaneous scalar words')
    for p in vertices:
        check((scalar[p]['unit'], scalar[p]['exterior']) ==
              (unit[0][ix[p]], outer[0][ix[p]]), 'scalar table disagreement')
    points = [tuple(map(int, p)) for p in receipt['points']]
    inverse_points = [tuple(p.index(i) + 1 for i in range(1, 5)) for p in points]
    for row, oracle in [('unit_distance_matrix', unit), ('exterior_distance_matrix', outer)]:
        actual = [[int(oracle[ix[a]][ix[b]]) for b in inverse_points] for a in inverse_points]
        check(actual == receipt[row], 'five-point matrix disagreement')
    positive = [(0, 1), (0, 2), (1, 2), (3, 4)]
    negative = [(i, j) for i in range(3) for j in (3, 4)]
    pattern_slacks = []
    for bits in product((0, 1), repeat=5):
        inside = sum(bits[i] != bits[j] for i, j in positive)
        across = sum(bits[i] != bits[j] for i, j in negative)
        check(inside <= across, 'binary pentagon')
        pattern_slacks.append(across - inside)
    check(sorted(pattern_slacks) == sorted(receipt['binary_cut_slacks']), 'binary slacks')
    samples = [(Fraction(r['alpha']), Fraction(r['beta'])) for r in receipt['price_controls']]
    comparisons = 0
    for alpha, beta in samples:
        table = floyd(vertices, [beta, alpha, beta])
        for p in vertices:
            check(table[0][ix[p]] == alpha * unit[0][ix[p]] +
                  (beta - alpha) * outer[0][ix[p]], 'real-cone distance control')
            comparisons += 1
        matrix = [[table[ix[a]][ix[b]] for b in inverse_points] for a in inverse_points]
        lhs = sum(matrix[i][j] for i, j in positive)
        rhs = sum(matrix[i][j] for i, j in negative)
        check(lhs - rhs == beta - alpha, 'symbolic price gap')
        # Independently count ordered-pair inversions and natural cut crossings
        # for the four relative permutations; no receipt cut counts are used.
        targets = [tuple(map(int, p)) for p in receipt['targets']]
        count_order = sum(p[a] > p[b] for p in targets for a in range(4) for b in range(a + 1, 4))
        count_natural = sum(sum(p[i] > cut for i in range(cut))
                            for p in targets for cut in (1, 3))
        check((count_order, count_natural) == (12, 8), 'attaining cut profile')
        check(alpha * count_order + (beta - alpha) * count_natural == rhs,
              'sharp upper/lower method agreement')
    # A nonconstant five-point semimetric need not be L1: these scalar distances
    # obey every triangle but violate the pentagon at ratio two.
    ratio_two = floyd(vertices, [2, 1, 2])
    check(all(ratio_two[a][c] <= ratio_two[a][b] + ratio_two[b][c]
              for a in range(24) for b in range(24) for c in range(24)), 'triangle control')
    check(receipt['direct_alpha_gamma'] == [12, 9] and
          receipt['sharp_cut_alpha_gamma'] == [12, 8], 'invoice control')
    print('PASS_INDEPENDENT_S4_CUT_ENVELOPE words=1093 scalar_comparisons=' + str(comparisons))


if __name__ == '__main__':
    run()
