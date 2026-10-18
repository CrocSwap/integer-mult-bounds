#!/usr/bin/env python3
"""Independent P112 masked tangent certificate (standard library only).

Constructs roots, splits the tangent equations by transpose symmetry, and uses
bit-sliced F3 elimination. Does not import the primary implementation or any
predecessor executable code. Exact integer kernel vectors give the upper rank
bound over Q/C; nonzero modular pivots give the matching lower bound.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import combinations, product
import hashlib
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def roots_and_readers():
    """Canonical doubled E8 lines, minus the adjacent-pair orthogonal frame."""
    roots = []
    for a, b in combinations(range(8), 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[a], root[b] = 2, 2 * sign
            roots.append(tuple(root))
    roots.extend(signs for signs in product((-1, 1), repeat=8)
                 if signs[0] == 1 and sum(x < 0 for x in signs) % 2 == 0)
    roots.sort()
    frame = []
    for a in range(0, 8, 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[a], root[a + 1] = 2, 2 * sign
            frame.append(tuple(root))
    need(len(roots) == len(set(roots)) == 120, '120 distinct root lines')
    need(all(sum(x * x for x in r) == 8 for r in roots), 'root norms')
    live = [r for r in roots if r not in frame]
    dot = lambda a, b: sum(x * y for x, y in zip(a, b))
    need(all(dot(f, g) == (8 if i == j else 0)
             for i, f in enumerate(frame) for j, g in enumerate(frame)),
         'orthogonal frame')
    need(all(dot(r, f) % 4 == 0 for r in live for f in frame),
         'integer frame coordinates')
    x = [tuple(dot(r, f) // 4 for f in frame) for r in live]
    need(len(live) == 112 and all(sum(v * v for v in r) == 4 for r in x),
         'P112 reader norms')
    need(all(2 * dot(x[i], x[j]) == dot(live[i], live[j])
             for i in range(112) for j in range(112)), 'XX transpose = 2G')
    need(all(sum(row[i] * row[j] for row in x) == (56 if i == j else 0)
             for i in range(8) for j in range(8)), 'exact left-inverse covariance')
    neighbors = [{j for j, other in enumerate(x) if j != i and dot(row, other)}
                 for i, row in enumerate(x)]
    need(all(len(adjacent) == 52 for adjacent in neighbors), 'odd graph degrees')
    visited, frontier = {0}, [0]
    while frontier:
        for vertex in neighbors[frontier.pop()]:
            if vertex not in visited:
                visited.add(vertex)
                frontier.append(vertex)
    need(len(visited) == 112, 'odd graph connected for orbit closedness')
    return live, x


def ternary_add(a, b):
    """Add vectors in F3 represented by disjoint +1 and -1 bit masks."""
    ap, am = a
    bp, bm = b
    az, bz = ~(ap | am), ~(bp | bm)
    return ((az & bp) | (ap & bz) | (am & bm),
            (az & bm) | (am & bz) | (ap & bp))


def ternary_encode(items):
    pos = neg = 0
    for column, value in items:
        residue = value % 3
        if residue == 1:
            pos |= 1 << column
        elif residue == 2:
            neg |= 1 << column
    return pos, neg


def ternary_rank(rows):
    pivots = {}
    for pos, neg in rows:
        need(not pos & neg, 'disjoint ternary masks')
        while pos | neg:
            column = (pos | neg).bit_length() - 1
            if column not in pivots:
                pivots[column] = ((pos, neg) if (pos >> column) & 1
                                  else (neg, pos))
                break
            bp, bm = pivots[column]
            pos, neg = ternary_add((pos, neg),
                                   (bm, bp) if (pos >> column) & 1 else (bp, bm))
    return len(pivots)


def tangent_rows(x, symmetric, include_diagonal=True):
    """Sparse integer rows for AX^t+XA^t or BX^t-XB^t on the mask."""
    rows = []
    for i, a in enumerate(x):
        start = i if symmetric and include_diagonal else i + 1
        for j in range(start, len(x)):
            b = x[j]
            if i != j and sum(u * v for u, v in zip(a, b)) != 0:
                continue
            row = {}
            for k, value in enumerate(b):
                row[8 * i + k] = row.get(8 * i + k, 0) + value
            for k, value in enumerate(a):
                row[8 * j + k] = (row.get(8 * j + k, 0)
                                  + (value if symmetric else -value))
            rows.append(tuple((k, v) for k, v in sorted(row.items()) if v))
    return rows


def kernel_vectors(x):
    skew = []
    sym = []
    for a in range(8):
        vector = [0] * (8 * len(x))
        for i, row in enumerate(x):
            vector[8 * i + a] = row[a]
        sym.append(vector)
    for a, b in combinations(range(8), 2):
        plus, minus = [0] * (8 * len(x)), [0] * (8 * len(x))
        for i, row in enumerate(x):
            plus[8 * i + a], plus[8 * i + b] = row[b], row[a]
            minus[8 * i + a], minus[8 * i + b] = -row[b], row[a]
        sym.append(plus)
        skew.append(minus)
    # Omit the last scaling: sum_i diag(e_i)X = XI is already symmetric gauge.
    scaling = []
    for i, row in enumerate(x[:-1]):
        vector = [0] * (8 * len(x))
        vector[8 * i:8 * i + 8] = row
        scaling.append(vector)
    return skew, sym, scaling


def annihilates(rows, vector):
    return all(sum(value * vector[column] for column, value in row) == 0
               for row in rows)


def matrix_rank_mod3(rows):
    return ternary_rank(ternary_encode(enumerate(row)) for row in rows)


def controls(x, symmetric_rows, antisymmetric_rows, skew, sym, scaling):
    count = 0
    for a, b in product(range(3), repeat=2):
        encoded = ternary_add(ternary_encode([(0, a)]), ternary_encode([(0, b)]))
        need(encoded == ternary_encode([(0, (a + b) % 3)]), 'F3 addition table')
    need(matrix_rank_mod3([[1, 2, 0], [2, 1, 0], [0, 0, 1]]) == 2,
         'dependent ternary rows control')
    count += 1
    # Removing diagonals genuinely admits uniform same-sign factor expansion.
    off_diagonal = tangent_rows(x, True, include_diagonal=False)
    uniform = [entry for row in x for entry in row]
    need(annihilates(off_diagonal, uniform)
         and not annihilates(symmetric_rows, uniform), 'diagonal omission witness')
    off_rank = ternary_rank(ternary_encode(row) for row in off_diagonal)
    need(off_rank == 756 and off_rank < 868, 'diagonal omission rank control')
    count += 1
    need(annihilates(symmetric_rows, skew[0])
         and not annihilates(antisymmetric_rows, skew[0]), 'transpose sign control')
    count += 1
    need(annihilates(antisymmetric_rows, scaling[0])
         and not annihilates(symmetric_rows, scaling[0]), 'reciprocal scaling sign control')
    count += 1
    wrong = sym[0][:]
    # A unit-coordinate mutation need not remain tangent; choose a nonzero root slot.
    first = next(k for k, value in enumerate(x[0]) if value)
    wrong[first] += 1
    need(not annihilates(antisymmetric_rows, wrong), 'kernel coefficient mutation')
    count += 1
    # D=Lambda X, T=Lambda^-1 X is exactly masked, outside the all-pairs class.
    lambdas = [2] + [1] * (len(x) - 1)
    changed = 0
    for i, a in enumerate(x):
        for j, b in enumerate(x):
            gram = sum(u * v for u, v in zip(a, b))
            discrepancy_numerator = (lambdas[i] - lambdas[j]) * gram
            if i == j or gram == 0:
                need(discrepancy_numerator == 0, 'exact masked scaling fixture')
            changed += discrepancy_numerator != 0
    need(changed == 104, 'non-all-pairs fixture changes 104 directed entries')
    need(all((lambdas[i] * value != 0) == (value != 0)
             for i, row in enumerate(x) for value in row), 'scaling preserves supports')
    # One changed nonzero column leaves the root code (F3 rank lower bound).
    column = next(j for j in range(8) if x[0][j])
    augmented = [list(row) + [lambdas[i] * row[column]] for i, row in enumerate(x)]
    need(matrix_rank_mod3(x) == 8 and matrix_rank_mod3(augmented) == 9,
         'scaled reader outside root code')
    count += 1
    return count, off_rank, changed


def main():
    roots, x = roots_and_readers()
    symmetric_rows = tangent_rows(x, True)
    antisymmetric_rows = tangent_rows(x, False)
    need((len(symmetric_rows), len(antisymmetric_rows)) == (3416, 3304),
         'mask coverage')
    skew, sym, scaling = kernel_vectors(x)
    need((len(skew), len(sym), len(scaling)) == (28, 36, 111), 'kernel counts')
    need(all(annihilates(symmetric_rows, v) for v in skew), 'integer skew kernels')
    need(all(annihilates(antisymmetric_rows, v) for v in sym + scaling),
         'integer symmetric and scaling kernels')
    need(matrix_rank_mod3(skew) == 28, 'independent skew kernels')
    need(matrix_rank_mod3(sym + scaling) == 147, 'independent antisymmetric kernels')
    ranks = [ternary_rank(ternary_encode(row) for row in rows)
             for rows in (symmetric_rows, antisymmetric_rows)]
    need(ranks == [868, 749], 'split modular ranks')
    need(ranks[0] + len(skew) == 896 and ranks[1] + len(sym + scaling) == 896,
         'matching exact characteristic-zero upper and lower bounds')
    count, off_rank, changed = controls(x, symmetric_rows, antisymmetric_rows,
                                       skew, sym, scaling)
    receipt = {
        'geometry_sha256': hashlib.sha256(json.dumps(
            {'roots': roots, 'readers': x}, separators=(',', ':')).encode()).hexdigest(),
        'variables_per_split': 896,
        'equation_counts': [3416, 3304],
        'odd_graph_connected_vertices': 112,
        'odd_graph_edges': 2912,
        'ranks_over_Q_and_C': ranks,
        'integer_kernel_dimensions': [28, 147],
        'full_tangent_rank': sum(ranks),
        'full_tangent_nullity': len(skew + sym + scaling),
        'diagonal_omission_symmetric_rank': off_rank,
        'scaling_fixture_changed_all_pairs_entries': changed,
        'controls': count,
    }
    print(json.dumps(receipt, sort_keys=True))
    print('PASS_P112_MASKED_TANGENT_INDEPENDENT rank=1617 nullity=175 controls=6')


if __name__ == '__main__':
    main()
