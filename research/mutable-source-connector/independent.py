#!/usr/bin/env python3
"""Separate Walsh census and dense F2 oracle; imports no primary checker code."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(value, message):
    if not value:
        raise ValueError(message)


def walsh(values):
    out = list(values)
    stride = 1
    while stride < 32:
        for block in range(0, 32, 2 * stride):
            for offset in range(stride):
                a, b = block + offset, block + offset + stride
                out[a], out[b] = out[a] + out[b], out[a] - out[b]
        stride *= 2
    return out


def coverage(points):
    indicator = [int(j in points) for j in range(32)]
    autocorrelation = walsh([v * v for v in walsh(indicator)])
    check(all(v >= 0 and v % 32 == 0 for v in autocorrelation), 'integer autocorrelation')
    return sum(v > 0 for v in autocorrelation)


def independent_census():
    anchors = [0, 1, 2, 4, 8, 16]
    choices = [j for j in range(32) if j not in anchors]
    histogram = Counter()
    # Explicit increasing-index DFS, rather than primary combinations/pair sets.
    stack = [(0, [])]
    while stack:
        start, tail = stack.pop()
        if len(tail) == 3:
            histogram[str(coverage(anchors + tail))] += 1
        else:
            for j in range(start, len(choices) - (2 - len(tail))):
                stack.append((j + 1, tail + [choices[j]]))
    return dict(histogram)


def query_word(certificate):
    points = certificate['points']
    slots = [[] for _ in points]
    for m, pair in enumerate(certificate['readout_pairs'], 1):
        check(len(pair) == 2 and pair[0] < pair[1] and points[pair[0]] ^ points[pair[1]] == m,
              'readout pair')
        for s in pair:
            slots[s].append(m)
    word = []
    for boundary, masks in enumerate(slots):
        word += [('A', m, 36, m + 4) for m in masks]
        if boundary < 10:
            step = points[boundary] ^ points[boundary + 1]
            pivot = (step & -step).bit_length() - 1
            donors = [j for j in range(pivot + 1, 5) if step & 2 ** j]
            word += [('X', -1, j, pivot) for j in donors]
            word += [('B', 0, pivot, 36)]
            word += [('X', -1, j, pivot) for j in donors[::-1]]
    return word


def emit(word):
    gates = []
    nodes = 0
    for kind, index, source, target in word:
        if kind == 'X':
            gates.append((-1, source, target))
            continue
        stack = [(tuple(range(index * 5, index * 5 + 5)), source, target, (37, 38, 39), False)]
        while stack:
            fs, src, dst, space, inverse = stack.pop()
            if len(fs) == 1:
                gates.append((fs[0], src, dst))
                continue
            nodes += 1
            middle = len(fs) // 2
            right = (fs[:middle], src, space[0], space[1:])
            left = (fs[middle:], space[0], dst, space[1:])
            order = [(right, False), (left, False), (right, True), (left, True)]
            if inverse:
                order = [(left, False), (right, False), (left, True), (right, True)]
            for args, rev in order[::-1]:
                stack.append((*args, rev))
    return gates, nodes


def action(matrix, vector):
    return sum(((row & vector).bit_count() % 2) << j for j, row in enumerate(matrix))


def run(gates, matrices, inputs):
    rows = list(inputs)
    for op, src, dst in gates:
        rows[dst] ^= rows[src] if op < 0 else action(matrices[op], rows[src])
    return rows


def desired(matrices, inputs):
    rows = list(inputs)
    common = []
    for value in rows[:5]:
        for f in range(5):
            value = action(matrices[f], value)
        common.append(value)
    for mask in range(1, 32):
        value = 0
        for j in range(5):
            if mask & (1 << j):
                value ^= common[j]
        for f in range(5 * mask, 5 * mask + 5):
            value = action(matrices[f], value)
        rows[4 + mask] ^= value
    return rows


def main():
    cert = json.loads((HERE / 'CERTIFICATE.json').read_text(encoding='utf-8'))
    check(independent_census() == cert['nine_point_histogram'], 'complete Walsh census disagrees')
    check(coverage(cert['points']) == 32, 'positive difference basis')
    word = query_word(cert)
    gates, nodes = emit(word)
    digest = lambda x: hashlib.sha256(json.dumps(x, separators=(',', ':')).encode()).hexdigest()
    check(digest(word) == cert['word_sha256'] and digest(gates) == cert['primitive_sha256'], 'emission differs')
    check(nodes == 648 and len(gates) == 2028 and Counter(w[0] for w in word) == {'A': 62, 'B': 10, 'X': 12},
          'independent invoice')
    reference = json.loads((ROOT / 'research/universal-connector-boundary/CERTIFICATE.json').read_text(encoding='utf-8'))
    words = [gates]
    for name in ('five_extra_source', 'five_extra_output'):
        root = [('B', 0, j, 36) if k == 'B' else ('A', j + 1, 36, j + 5)
                for k, j in reference['schedules'][name]['word']]
        primitive, internal = emit(root)
        check(len(primitive) == 2072 and internal == 666, 'reference invoice')
        words.append(primitive)
    cases = 0
    probes = 0
    rng = random.Random(20261013)
    for width in (1, 2, 3):
        for bank in range(2):
            matrices = [[rng.randrange(1 << width) for _ in range(width)] for _ in range(160)]
            inputs = [[0] * row + [1 << bit] + [0] * (39 - row) for row in range(40) for bit in range(width)]
            inputs += [[rng.randrange(1 << width) for _ in range(40)] for _ in range(4)]
            probes += 4
            for initial in inputs:
                expected = desired(matrices, initial)
                for program in words:
                    check(run(program, matrices, initial) == expected, 'dense forward map')
                    check(run(program[::-1], matrices, initial) == expected, 'dense inverse map')
                    cases += 2
    # Concrete common-map failure: all maps I, then change one B leaf to zero.
    matrices = [[1]] * 160
    bad_matrices = list(matrices)
    bad_matrices[159] = [0]
    damaged = list(gates)
    first = next(i for i, (op, _, _) in enumerate(damaged) if op == 0)
    damaged[first] = (159, damaged[first][1], damaged[first][2])
    concrete = [1] * 40
    check(run(damaged, bad_matrices, concrete) != desired(bad_matrices, concrete), 'common-B counterexample')
    # I and a nilpotent shift are noncommuting, so swapping their order matters.
    p, q = [2, 0], [0, 1]
    check(action(p, action(q, 1)) != action(q, action(p, 1)), 'noncommuting factor control')
    check(cert['unit_complete_tariff'] == {'candidate': len(gates) + nodes + len(word),
                                         'reference': 2072 + 666 + 74, 'saving': 52}, 'complete tariff')
    print(f'PASS_MUTABLE_SOURCE_ORACLE census=2600 dense_cases={cases} dirty_probes={probes} complete_tariff=2760_vs_2812')


if __name__ == '__main__':
    main()
