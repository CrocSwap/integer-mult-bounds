#!/usr/bin/env python3
"""Exact P112 two-column masked-completion certificate. Apache-2.0.
Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import gcd
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json'
PRIME = 65521
BASE = '1ff9c501b624ec354e1330b1b9be571a6adba9cb'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def rank_certificate(matrix):
    """A modular lower bound and a specific nonzero square minor.

    This NEVER supplies a characteristic-zero upper bound. Those are proved
    separately by ambient dimension, orthogonality, or exact factorizations.
    """
    if not matrix:
        return 0, [], []
    width = len(matrix[0])
    need(all(len(row) == width for row in matrix), 'rectangular matrix')
    a = [[v % PRIME for v in row] for row in matrix]
    ids = list(range(len(a)))
    chosen_columns = []
    r = 0
    for col in range(width):
        pivot = next((k for k in range(r, len(a)) if a[k][col]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        ids[r], ids[pivot] = ids[pivot], ids[r]
        scale = pow(a[r][col], -1, PRIME)
        a[r] = [(v * scale) % PRIME for v in a[r]]
        for k in range(r + 1, len(a)):
            scale = a[k][col]
            if scale:
                a[k] = [(x - scale * y) % PRIME for x, y in zip(a[k], a[r])]
        chosen_columns.append(col)
        r += 1
        if r == min(len(a), width):
            break
    return r, ids[:r], chosen_columns


def rank(matrix):
    return rank_certificate(matrix)[0]


def bind_sources():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    need(manifest['base_commit'] == BASE, 'source base changed')
    expected_inputs = {SOURCE, 'research/p112-sparse-completion-rank/README.md'}
    inputs = [entry for entry in manifest['files'] if entry['usage'] == 'input']
    need({entry['path'] for entry in inputs} == expected_inputs and len(inputs) == 2,
         'complete live input inventory')
    for entry in inputs:
        need(sha256((ROOT / entry['path']).read_bytes()).hexdigest() == entry['sha256'],
             'source bytes changed: ' + entry['path'])
    return json.loads((ROOT / SOURCE).read_text())


def geometry(source):
    all_roots = source['root_lines']
    roots = all_roots[8:]
    need(len(all_roots) == 120 and len(roots) == 112, 'P112 inventory')
    need(all(type(x) is int for r in roots for x in r), 'integer root coordinates')
    need(len({tuple(r) for r in roots}) == 112 and all(len(r) == 8 for r in roots),
         'distinct eight-coordinate roots')
    need(all_roots[:8] == [[2 * int(i == j) for j in range(8)] for i in range(8)],
         'removed coordinate frame')
    gram = [[dot(r, s) for s in roots] for r in roots]
    need(all(gram[i][i] == 4 for i in range(112)), 'root normalization')
    need(all(gram[i][j] in (-2, 0, 2) for i, j in combinations(range(112), 2)),
         'off-diagonal Gram alphabet')
    labels = source['binary_ports'][8:]
    need(len(labels) == 112 and len(set(labels)) == 112, 'label inventory')
    need(all(((labels[i] & labels[j]).bit_count() % 2) ==
             ((gram[i][j] // 2 + 1) % 2) for i in range(112) for j in range(112)),
         'all binary pairing / odd-mask bindings')
    frame_gram = [[sum(r[i] * r[j] for r in roots) for j in range(8)] for i in range(8)]
    need(frame_gram == [[56 * int(i == j) for j in range(8)] for i in range(8)],
         'X transpose X = 56 I')
    need(all(sum(abs(v) == 2 for v in row) == 52 for row in gram), 'odd degree 52')
    return roots, gram


def minor_on_rows(roots, indices, expected):
    value, row_ids, cols = rank_certificate([roots[i] for i in indices])
    need(value == expected, 'wrong finite root-span lower bound')
    return [[indices[i] for i in row_ids], cols]


def pencil_profile(gram, j, k):
    """All projective zero patterns in span(G[:,j], G[:,k]), over C."""
    directions = set()
    active = 0
    for row in gram:
        x, y = row[j], row[k]
        if x or y:
            active += 1
            divisor = gcd(x, y)
            a, b = y // divisor, -x // divisor
            if a < 0 or (a == 0 and b < 0):
                a, b = -a, -b
            directions.add((a, b))
    strata = [[a, b, sum(a * row[j] + b * row[k] != 0 for row in gram)]
              for a, b in sorted(directions)]
    need((1, 3) not in directions and
         sum(row[j] + 3 * row[k] != 0 for row in gram) == active,
         'generic pencil direction')
    need(min(row[2] for row in strata) == 53, 'two-root pencil minimum support')
    return [j, k, active, strata]


def census(roots, gram):
    singles, pairs, pencils = [], [], []
    counts = Counter()
    for j in range(112):
        constrained = [i for i in range(112) if abs(gram[i][j]) != 2]
        minor = minor_on_rows(roots, constrained, 8)
        singles.append([j, len(constrained), *minor])
    for j, k in combinations(range(112), 2):
        odd = abs(gram[j][k]) == 2
        constrained = [i for i in range(112) if abs(gram[i][j]) != 2 and abs(gram[i][k]) != 2]
        expected = 6 if odd else 8
        # For odd pairs, every constrained row is perpendicular to both roots.
        # The two independent roots supply the matching characteristic-zero upper bound.
        if odd:
            pencils.append(pencil_profile(gram, j, k))
            need(all(gram[i][j] == gram[i][k] == 0 for i in constrained),
                 'rank-six orthogonality upper bound')
            need(gram[j][j] * gram[k][k] - gram[j][k] ** 2 != 0,
                 'two independent root normals')
        common_minor = minor_on_rows(roots, constrained, expected)
        kept = [i for i in range(112) if i not in (j, k)]
        deletion_minor = minor_on_rows(roots, kept, 8)
        pairs.append([j, k, gram[j][k], len(constrained), *common_minor, *deletion_minor])
        counts[(('odd' if odd else 'orthogonal'), len(constrained), expected)] += 1
    return {'schema_version': 1, 'singletons': singles, 'pairs': pairs, 'odd_pencils': pencils}, {
        '|'.join(map(str, key)): count for key, count in sorted(counts.items())}


def zeros():
    return [[0] * 112 for _ in range(112)]


def validate_mask(q, gram, maximum_columns=None):
    need(len(q) == 112 and all(len(row) == 112 for row in q), 'correction dimensions')
    active = sorted({j for row in q for j, value in enumerate(row) if value})
    need(maximum_columns is None or len(active) <= maximum_columns, 'column support outside scope')
    need(all(not q[i][j] or abs(gram[i][j]) == 2 for i in range(112) for j in active),
         'correction is not odd-only')
    return active


def low_witness(gram, j, k):
    need(j != k and abs(gram[j][k]) == 2, 'low witness needs odd columns')
    q = zeros()
    for i in range(112):
        if i != j:
            q[i][j] = -gram[i][j]
    q[j][k] = 1
    return q


def project_columns(roots, y):
    # P=56I-XX^T; no floating point, and no Hermitian substitution.
    width = len(y[0])
    xty = [[sum(roots[i][a] * y[i][b] for i in range(112))
            for b in range(width)] for a in range(8)]
    return [[56 * y[i][b] - sum(roots[i][a] * xty[a][b] for a in range(8))
             for b in range(width)] for i in range(112)]


def inspect_witness(name, q, roots, gram, q_rank, completion_rank, projection_rank):
    columns = validate_mask(q, gram)
    y = [[row[j] for j in columns] for row in q]
    m = [[gram[i][j] + q[i][j] for j in range(112)] for i in range(112)]
    need(rank(y) == q_rank, 'correction rank claim fails')
    need(rank(m) == completion_rank, 'completion rank lower-bound claim fails')
    need(rank(project_columns(roots, y)) == projection_rank, 'quotient rank claim fails')
    # All entries are stored, sparsely, for an independent rational rank check.
    entries = [[i, j, q[i][j]] for i in range(112) for j in columns if q[i][j]]
    return {'name': name, 'columns': columns, 'row_support': len({i for i, j, v in entries}),
            'nonzero_entries': entries, 'correction_rank': q_rank,
            'completion_rank': completion_rank, 'projection_rank': projection_rank}


def binary_copy_rank(gram, left, right):
    pivots = {}
    for i in left:
        row = sum((((gram[i][j] // 2 + 1) % 2) << bit) for bit, j in enumerate(right))
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def witnesses_and_controls(roots, gram):
    odd = next((j, k) for j, k in combinations(range(112), 2) if abs(gram[j][k]) == 2)
    even = next((j, k) for j, k in combinations(range(112), 2) if gram[j][k] == 0)
    j, k = odd
    low = low_witness(gram, j, k)
    witnesses = [inspect_witness('odd_pair_rank9', low, roots, gram, 2, 9, 1)]
    need(witnesses[0]['row_support'] == 53, 'sharp 53-row boundary')
    copy_ranks = [binary_copy_rank(gram, [i for i in range(112) if roots[i][a]],
                                  [i for i in range(112) if roots[i][a] and i != j])
                  for a in range(8)] + [binary_copy_rank(gram, [j], [j, k])]
    need(copy_ranks == [8] * 8 + [1], 'explicit factorization COPY invoice')
    witnesses[0]['displayed_factorization_copy_ranks'] = copy_ranks
    witnesses[0]['displayed_factorization_copy_total'] = sum(copy_ranks)
    # Check the exact rank-nine factorization X A + e_j b on every entry.
    for row in range(112):
        for col in range(112):
            factored = (0 if col == j else gram[row][col])
            if row == j:
                factored += 4 * int(col == j) + int(col == k)
            need(gram[row][col] + low[row][col] == factored, 'rank-nine factorization')
    for label, pair in [('odd_pair_rank10', odd), ('orthogonal_pair_rank10', even)]:
        u, v = pair
        a = next(i for i in range(112) if abs(gram[i][u]) == 2)
        b = next(i for i in range(112) if i != a and abs(gram[i][v]) == 2)
        q = zeros(); q[a][u] = q[b][v] = 1
        witnesses.append(inspect_witness(label, q, roots, gram, 2, 10, 2))
    q = zeros()
    for i in range(112):
        if abs(gram[i][j]) == 2:
            q[i][j] = 1
    witnesses.append(inspect_witness('maximal_one_column_rank9', q, roots, gram, 1, 9, 1))
    a, b = 0, 1
    cols = [c for c in range(112) if abs(gram[a][c]) == abs(gram[b][c]) == 2]
    q = zeros()
    for i in (a, b):
        for c in cols:
            q[i][c] = 1
    need(len(cols) > 2, 'rank-one example has more than two columns')
    witnesses.append(inspect_witness('wide_rank1_rectangle', q, roots, gram, 1, 9, 1))

    controls = []
    def rejects(name, fn):
        try:
            fn()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('control did not reject: ' + name)
    bad = [row[:] for row in low]; bad[j][j] = 1
    rejects('nonmasked_diagonal', lambda: validate_mask(bad, gram, 2))
    rejects('rank1_correction_mislabel', lambda: inspect_witness('bad', low, roots, gram, 1, 9, 1))
    rejects('false_additivity_rank10', lambda: inspect_witness('bad', low, roots, gram, 2, 10, 1))
    rejects('false_rank8_completion', lambda: inspect_witness('bad', low, roots, gram, 2, 8, 1))
    omitted = [row[:] for row in low]; omitted[j][k] = 0
    rejects('omitted_second_column', lambda: inspect_witness('bad', omitted, roots, gram, 2, 9, 1))
    rejects('orthogonal_pair_low_witness', lambda: low_witness(gram, *even))
    rejects('wide_rectangle_as_two_columns', lambda: validate_mask(q, gram, 2))
    wrong = [[55 * roots[i][a] - sum(gram[i][t] * roots[t][a] for t in range(112))
              for a in range(8)] for i in range(112)]
    rejects('wrong_projection_normalization', lambda: need(all(not x for row in wrong for x in row),
                                                          'projection must kill the root code'))
    return witnesses, controls


def compute():
    need(all(PRIME % d for d in range(2, 256)), 'prime modulus')
    source = bind_sources()
    roots, gram = geometry(source)
    cert, histogram = census(roots, gram)
    witnesses, controls = witnesses_and_controls(roots, gram)
    result = {
        'schema_version': 1,
        'result_kind': 'scoped-proof-with-finite-certificate',
        'base_commit': BASE,
        'source_sha256': sha256((ROOT / SOURCE).read_bytes()).hexdigest(),
        'normalization': 'X has squared row norm 4; R=X/sqrt(2); G=XX^T=2RR^T',
        'gram_rank': 8, 'frame_constant': 56, 'odd_degree': 52,
        'singletons_checked': len(cert['singletons']),
        'unordered_pairs_checked': len(cert['pairs']),
        'odd_pairs': sum(abs(row[2]) == 2 for row in cert['pairs']),
        'orthogonal_pairs': sum(row[2] == 0 for row in cert['pairs']),
        'odd_pencils_checked': len(cert['odd_pencils']),
        'two_column_failure_row_floor': 53,
        'pair_class_histogram': histogram,
        'census_sha256': sha256(canonical(cert).encode()).hexdigest(),
        'witnesses': witnesses, 'controls': controls,
        'theorem': 'For <=2 changed columns: rank(G+Q)=8+rank((56I-G)Q). Nonzero rank-one Q gives 9. Rank-two Q gives 9 or 10; orthogonal changed columns force 10. Every odd pair attains both 9 and 10. Every nonzero odd-only rank-one correction, of any column support, gives 9.',
        'boundary': 'Rank-two odd-only corrections on 53 rows and two columns attain completion rank 9; rank-one odd rectangles have at most 52 rows and 52 columns.',
        'scope': 'Ordinary complex matrix rank, not binary COPY cost, recursive child rank, a new supplier or kappa.'
    }
    return cert, result


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--write', action='store_true', help='write initial certificates; refuse existing paths')
    group.add_argument('--write-to', type=Path, help='write certificates in a new output directory')
    args = parser.parse_args()
    output = args.write_to if args.write_to is not None else HERE
    writing = args.write or args.write_to is not None
    if writing:
        need(all(not (output / name).exists() for name in ('CENSUS.json', 'RESULT.json')),
             'refuse existing certificate output')
        output.mkdir(parents=True, exist_ok=True)
    cert, result = compute()
    for name, value in [('CENSUS.json', cert), ('RESULT.json', result)]:
        path = output / name
        if writing:
            with path.open('x') as out:
                if name == 'CENSUS.json':
                    blocks = ['"schema_version": 1']
                    for key in ('singletons', 'pairs', 'odd_pencils'):
                        blocks.append('"' + key + '": [\n' +
                                      ',\n'.join('  ' + canonical(row) for row in value[key]) + '\n]')
                    out.write('{\n' + ',\n'.join(blocks) + '\n}\n')
                else:
                    out.write(json.dumps(value, indent=2, sort_keys=True) + '\n')
        else:
            need(canonical(json.loads(path.read_text())) == canonical(value), name + ' differs from exact replay')
    print('PASS_P112_TWO_COLUMN_COMPLETION pairs=6216 odd=2912 orthogonal=3304 boundary_rows=53 correction_rank=2 completion_rank=9 controls=' + str(len(result['controls'])))


if __name__ == '__main__':
    main()
