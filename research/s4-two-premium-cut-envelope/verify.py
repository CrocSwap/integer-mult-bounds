#!/usr/bin/env python3
"""Exact five-point obstruction and sharp permutation-cut invoice.

Prepared for Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
Default replay is read-only; --write explicitly regenerates RESULT.json.
"""
import argparse
from collections import deque
from fractions import Fraction
import hashlib
import heapq
from itertools import permutations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def compose(a, b):
    return tuple(a[b[i]] for i in range(len(a)))


def inverse(a):
    return tuple(a.index(i) for i in range(len(a)))


def inversion(a):
    return sum(a[i] > a[j] for i in range(len(a)) for j in range(i + 1, len(a)))


def source_checks():
    source = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for row in source['files']:
        if row['usage'] == 'input':
            require(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                    'changed external source: ' + row['path'])
    for name, digest in source['public_predecessor']['retained_files'].items():
        require(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest,
                'changed public predecessor: ' + name)


def scalar_words(group, generators):
    """Lexicographic Dijkstra: minimize (all calls, exterior calls)."""
    identity = tuple(range(4))
    best = {identity: (0, 0)}
    words = {identity: ()}
    queue = [(0, 0, identity)]
    while queue:
        length, exterior, g = heapq.heappop(queue)
        if (length, exterior) != best[g]:
            continue
        for i, s in enumerate(generators):
            h = compose(s, g)
            score = (length + 1, exterior + (i != 1))
            if score < best.get(h, (100, 100)):
                best[h] = score
                words[h] = words[g] + (i,)
                heapq.heappush(queue, (*score, h))
    require(len(best) == 24, 'incomplete S4')
    # Separate 0/1 shortest paths minimize exterior calls without a length limit.
    outer = {identity: 0}
    pending = deque([identity])
    while pending:
        g = pending.popleft()
        for i, s in enumerate(generators):
            h = compose(s, g)
            cost = outer[g] + (i != 1)
            if cost < outer.get(h, 100):
                outer[h] = cost
                (pending.appendleft if i == 1 else pending.append)(h)
    for g in group:
        require(best[g] == (inversion(g), outer[g]), 'no simultaneous attaining word')
        for i, s in enumerate(generators):
            h = compose(s, g)
            require(best[h][0] <= best[g][0] + 1, 'unit shortest-path dual')
            require(best[h][1] <= best[g][1] + (i != 1), 'outer shortest-path dual')
    return best, words


def crossing(action, subset, g):
    return sum(action(g, x) not in subset for x in subset)


def pentagon(matrix):
    positive = [(0, 1), (0, 2), (1, 2), (3, 4)]
    negative = [(i, j) for i in range(3) for j in (3, 4)]
    return sum(matrix[i][j] for i, j in positive) - sum(matrix[i][j] for i, j in negative)


def left_label(bits, s, group, index):
    result = 0
    for k, g in enumerate(group):
        if bits >> k & 1:
            result ^= 1 << index[compose(s, g)]
    return result


def formal_word(word, group, generators, targets, gauge=False):
    """Literal group-algebra rows, including two arbitrary dirty spectators."""
    count = len(targets) + 2
    index = {g: i for i, g in enumerate(group)}
    unit = 1 << index[tuple(range(4))]
    state = [[unit if i == j else 0 for j in range(count)] for i in range(count)]
    scalar = [1 << i for i in range(count)]
    scalar_inverse = scalar[:]
    operations = [(0, count - 1), (count - 1, 1)]
    for dst, src in operations:
        scalar[dst] ^= scalar[src]
    for dst, src in reversed(operations):
        scalar_inverse[dst] ^= scalar_inverse[src]
    if gauge:
        for dst, src in operations:
            state[dst] = [a ^ b for a, b in zip(state[dst], state[src])]
    for role, label in word:
        u = sum(((scalar[i] >> role) & 1) << i for i in range(count)) if gauge else 1 << role
        v = scalar_inverse[role] if gauge else 1 << role
        require((u & v).bit_count() % 2 == 1, 'non-idempotent paid projector')
        donor = [0] * count
        for i in range(count):
            if v >> i & 1:
                donor = [a ^ b for a, b in zip(donor, state[i])]
        delta = [x ^ left_label(x, generators[label], group, index) for x in donor]
        for i in range(count):
            if u >> i & 1:
                state[i] = [a ^ b for a, b in zip(state[i], delta)]
    if gauge:
        for dst, src in reversed(operations):
            state[dst] = [a ^ b for a, b in zip(state[dst], state[src])]
    wanted = [[0] * count for _ in range(count)]
    for i in range(count):
        wanted[i][i] = 1 << index[targets[i] if i < len(targets) else tuple(range(4))]
    return state == wanted


def build_report():
    group = list(permutations(range(4)))
    generators = [(1, 0, 2, 3), (0, 2, 1, 3), (0, 1, 3, 2)]
    best, words = scalar_words(group, generators)
    pairs = [(i, j) for i in range(4) for j in range(4) if i != j]
    order_cut = {x for x in pairs if x[0] < x[1]}
    pair_action = lambda g, x: (g[x[0]], g[x[1]])
    natural_action = lambda g, x: g[x]
    cut_values = {}
    for g in group:
        inv = crossing(pair_action, order_cut, g)
        outer = sum(crossing(natural_action, set(range(p)), g) for p in (1, 3))
        require(inv == inversion(g), 'ordered-pair charge is not inversion count')
        cut_values[g] = (inv, outer)
    require([cut_values[g] for g in generators] == [(1, 1), (1, 0), (1, 1)],
            'wrong generator invoice')
    points = [(0, 1, 2, 3), (1, 0, 3, 2), (1, 3, 0, 2),
              (0, 1, 3, 2), (1, 0, 2, 3)]
    relative = [[compose(a, inverse(b)) for b in points] for a in points]
    units = [[best[g][0] for g in row] for row in relative]
    premiums = [[best[g][1] for g in row] for row in relative]
    require(pentagon(units) == 0 and pentagon(premiums) == 1, 'no strict symbolic separation')
    binary_slacks = []
    for mask in range(32):
        bits = [mask >> i & 1 for i in range(5)]
        matrix = [[abs(a - b) for b in bits] for a in bits]
        signed = sum(bits[:3]) - sum(bits[3:])
        require(pentagon(matrix) == signed * (1 - signed) <= 0, 'invalid cut inequality')
        binary_slacks.append(-pentagon(matrix))
    targets = [relative[i][j] for i, j in [(0, 1), (0, 2), (1, 2), (3, 4)]]
    display = lambda g: ''.join(str(x + 1) for x in g)
    require(list(map(display, targets)) == ['2143', '3142', '4231', '2143'],
            'wrong four-target tuple')
    direct = tuple(sum(best[g][i] for g in targets) for i in range(2))
    cut_bill = tuple(sum(cut_values[g][i] for g in targets) for i in range(2))
    require(direct == (12, 9) and cut_bill == (12, 8), 'sharp invoice mismatch')
    negative_terms = [relative[i][j] for i in range(3) for j in (3, 4)]
    require(tuple(sum(best[g][i] for g in negative_terms) for i in range(2)) == cut_bill,
            'upper and lower method certificates do not meet')
    full_word = [(role, letter) for role, g in enumerate(targets) for letter in words[g]]
    require(formal_word(full_word, group, generators, targets), 'direct formal endpoint')
    require(formal_word(full_word, group, generators, targets, True), 'gauged dirty endpoint')
    for k in range(len(full_word)):
        require(not formal_word(full_word[:k] + full_word[k + 1:], group, generators, targets, True),
                'call omission escaped literal dirty endpoint')
    for g in group:
        require(formal_word([(0, letter) for letter in words[g]], group, generators, [g], True),
                'scalar attaining word')
    prices = [(Fraction(1), Fraction(1)), (Fraction(1), Fraction(2)),
              (Fraction(2), Fraction(3)), (Fraction(0), Fraction(1)),
              (Fraction(1, 3), Fraction(7, 5))]
    invoices = [{'alpha': str(a), 'beta': str(b), 'direct': str(12*a + 9*(b-a)),
                 'best_coordinate_cut': str(12*a + 8*(b-a)), 'gap': str(b-a)} for a, b in prices]
    return {'schema_version': 1, 'status': 'SHARP_COORDINATE_CUT_METHOD_GAP_ONLY',
            'points': list(map(display, points)), 'unit_distance_matrix': units,
            'exterior_distance_matrix': premiums, 'binary_cut_slacks': binary_slacks,
            'targets': list(map(display, targets)), 'direct_alpha_gamma': list(direct),
            'sharp_cut_alpha_gamma': list(cut_bill), 'price_controls': invoices,
            'scalar_table': [{'target': display(g), 'unit': best[g][0], 'exterior': best[g][1],
                              'word': [i + 1 for i in words[g]],
                              'attaining_cut': list(cut_values[g])} for g in group],
            'formal_roles': 6, 'omission_controls': len(full_word),
            'scope': 'All nonnegative role-uniform coordinate-cut combinations on finite S4 permutation modules; not arbitrary subspace cuts, word optimality or a supplier.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    source_checks()
    report = build_report()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    require(path.read_text(encoding='utf-8') == json.dumps(report, indent=2) + '\n', 'receipt mismatch')
    print('PASS_S4_CUT_ENVELOPE direct=21 cut=20 gap=beta-alpha binary_cuts=32 no_new_kappa')


if __name__ == '__main__':
    main()
