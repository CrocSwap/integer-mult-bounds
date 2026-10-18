#!/usr/bin/env python3
"""Independent exact-integer check of the five-cube affine-copy obstruction.

Uses only the Python standard library and literal pinned data. Imports no
primary verifier or discovery code. This is a separate implementation by an
AI collaborator, not independent human peer review or formal verification.
Copyright 2026 martinxxx9. Apache-2.0. Substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter
from functools import reduce
from itertools import combinations, product
from math import gcd
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = '2921874911956718fcaaaf9396fe8267b3cfa9f0'
FORMS = tuple(range(1, 64))
DECODER_ROWS = [32] * 5 + [63]
PARITY_SPACE = frozenset((0, 31, 32, 63))
WITNESS_SOURCE = (30, 33, 62, 1)
WITNESS_READER = (1, 30, 33, 62)
SOURCE_PATHS = frozenset(('sources/PR958-PROOF.md', 'sources/PR958-NOTICE.md',
                          'sources/PR231-README.md', 'sources/PR446-PROOF.md',
                          'sources/FORMAT-AXIOMS.md', 'sources/SELECTED-RESULT.json'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def form_value(form, point):
    require(type(form) is int and 0 <= form < 64, 'six-bit affine form')
    return ((form & point & 31).bit_count() + (form >> 5)) % 2


def integer_rank(matrix):
    """Exact rank over Q by integer row operations and content reduction.

    At each nonzero pivot, a row is replaced by pivot*row-entry*pivot_row.
    Dividing a row by its nonzero integer content preserves rational rank.
    No prime, floating point, or probabilistic rank estimate occurs here.
    """
    require(matrix and matrix[0], 'nonempty matrix')
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), 'rectangular matrix')
    require(all(type(v) is int for row in matrix for v in row), 'integer entries')
    rows = [list(row) for row in matrix]
    rank = 0
    for column in range(width):
        pivot_index = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot_index is None:
            continue
        rows[rank], rows[pivot_index] = rows[pivot_index], rows[rank]
        pivot = rows[rank][column]
        for i in range(rank + 1, len(rows)):
            entry = rows[i][column]
            if not entry:
                continue
            for j in range(column + 1, width):
                rows[i][j] = pivot * rows[i][j] - entry * rows[rank][j]
            rows[i][column] = 0
            content = reduce(gcd, rows[i][column + 1:], 0)
            if content:
                for j in range(column + 1, width):
                    require(rows[i][j] % content == 0, 'exact content division')
                    rows[i][j] //= content
        rank += 1
        if rank == len(rows):
            break
    return rank


def binary_rank(matrix):
    require(matrix and matrix[0], 'nonempty binary matrix')
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), 'rectangular binary matrix')
    require(all(v in (0, 1) for row in matrix for v in row), 'binary entries')
    rows = [sum(value << j for j, value in enumerate(row)) for row in matrix]
    rank = 0
    for column in range(width):
        pivot = next((i for i in range(rank, len(rows)) if rows[i] >> column & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(rank + 1, len(rows)):
            if rows[i] >> column & 1:
                rows[i] ^= rows[rank]
        rank += 1
        if rank == len(rows):
            break
    return rank


def check_source_record(record):
    require(type(record.get('path')) is str, 'source path')
    require(record.get('commit') == BASE, 'pinned source commit')
    path = (HERE / record['path']).resolve()
    require(path.is_relative_to(HERE.resolve()), 'source confined to package')
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == record.get('sha256'), 'pinned source SHA256')
    if 'git_blob_sha1' in record:
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == record['git_blob_sha1'], 'pinned source Git blob')
    return digest


def check_inputs():
    claim = json.loads((HERE / 'CLAIM.json').read_text(encoding='utf-8'))
    require(claim.get('assignment_seed') == 42, 'assignment seed pin')
    require(claim.get('base_commit') == BASE, 'claim base pin')
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    require(manifest.get('base_commit') == BASE, 'source manifest base pin')
    records = manifest.get('files')
    require(isinstance(records, list) and records, 'nonempty source manifest')
    require(len({r.get('path') for r in records}) == len(records), 'distinct pinned source paths')
    require({r.get('path') for r in records} == SOURCE_PATHS, 'six-source inventory pin')
    hashes = {r['path']: check_source_record(r) for r in records}
    return hashes, records


def support_census():
    ports = [frozenset(2 * i + (point >> i & 1) for i in range(5))
             for point in range(32)]
    # The overlap-feature expression independently evaluates the supplied Gram.
    gram = []
    for left in ports:
        row = []
        for right in ports:
            overlap = len(left.intersection(right))
            row.append(6 - 6 * overlap + 2 * overlap * (overlap - 1))
        gram.append(row)
    supports = {f: frozenset(x for x in range(32) if form_value(f, x)) for f in FORMS}
    require(len(set(supports.values())) == 63 and all(supports.values()),
            'all nonzero affine functions have distinct nonempty supports')
    table, histogram, frontier = [], Counter(), {}
    for source in FORMS:
        row = []
        for reader in FORMS:
            rank = integer_rank([[gram[x][y] for y in sorted(supports[reader])]
                                 for x in sorted(supports[source])])
            row.append(rank)
            histogram[rank] += 1
            coverage = len(supports[source].intersection(supports[reader]))
            frontier[rank] = max(frontier.get(rank, 0), coverage)
        table.append(row)
    require(dict(histogram) == {6: 30, 8: 480, 10: 1230, 11: 1530, 13: 690, 16: 9},
            'exact rational rank histogram')
    require(frontier == {6: 0, 8: 8, 10: 8, 11: 16, 13: 16, 16: 32},
            'cost/diagonal coverage frontier')
    require(all(table[a - 1][b - 1] == table[b - 1][a - 1] for a in FORMS for b in FORMS),
            'source/reader transpose symmetry')
    return ports, gram, supports, table, histogram, frontier


def check_primary_receipt(table, histogram):
    path = HERE / 'CERTIFICATE.json'
    if path.exists():
        receipt = json.loads(path.read_text(encoding='utf-8'))
        require(receipt.get('cross_rank_table') == table, 'independent versus primary rank table')
        if 'cross_rank_histogram' in receipt:
            require(receipt['cross_rank_histogram'] == {str(k): v for k, v in sorted(histogram.items())},
                    'independent versus primary rank histogram')


def check_independent_receipt(result, exhaustive):
    path = HERE / 'INDEPENDENT.json'
    if path.exists():
        receipt = json.loads(path.read_text(encoding='utf-8'))
        if not exhaustive:
            receipt.pop('exhaustive_factorizations', None)
        require(receipt == result, 'independent committed receipt equality')


def check_factorization(sources, readers, ports, table):
    require(len(sources) == len(readers) and sources, 'paired nonempty factors')
    require(all(type(f) is int and f in FORMS for f in tuple(sources) + tuple(readers)),
            'nonzero affine source and reader factors')
    coefficients = [0] * 6
    for source, reader in zip(sources, readers):
        for k in range(6):
            if source >> k & 1:
                coefficients[k] ^= reader
    require(coefficients == DECODER_ROWS, 'literal decoder coefficient matrix')
    for x, left in enumerate(ports):
        for y, right in enumerate(ports):
            actual = sum(form_value(a, x) * form_value(b, y)
                         for a, b in zip(sources, readers)) % 2
            require(actual == len(left.intersection(right)) % 2, 'all 1024 decoder coefficients')
    costs = [table[a - 1][b - 1] for a, b in zip(sources, readers)]
    return dict(source_forms=list(sources), reader_forms=list(readers),
                factor_costs=costs, total_cost=sum(costs), peak_cost=max(costs),
                decoded_coefficients=1024)


def coverage_bound(frontier, length):
    candidates = [sum(frontier[c] for c in costs)
                  for costs in product(frontier, repeat=length) if sum(costs) < 32]
    require(candidates, 'nonempty sub-32 cost candidates')
    return max(candidates)


def price_check(copy_charge):
    require(copy_charge >= 32, 'certified copy lower bound')
    # D <= (s-1)*32-s*c = -32-s*(c-32) <= -32 for every s>=1.
    return dict(ports=32, copy_charge_lower=copy_charge,
                all_stage_deficit_upper=-32, required_stage_range='all integers s >= 3')


def check_proof(ports, supports, table, frontier):
    observation = [[int(coordinate in port) for coordinate in range(10)] for port in ports]
    decoder = [[len(left.intersection(right)) % 2 for right in ports] for left in ports]
    affine_basis = [[1] + [x >> i & 1 for i in range(5)] for x in range(32)]
    require(binary_rank(observation) == 6, 'coordinate-star observation rank six')
    require(binary_rank(affine_basis) == 6, 'injective affine coefficient evaluation')
    require(binary_rank(decoder) == 2, 'star decoder rank two')
    require(binary_rank([[row >> i & 1 for i in range(6)] for row in DECODER_ROWS]) == 2,
            'decoder coefficient matrix rank two')
    require(all(decoder[x][y] == (1 + x.bit_count() + y.bit_count()) % 2
                for x in range(32) for y in range(32)), 'decoder parity identity')
    u = sorted(PARITY_SPACE - {0})
    require(all(table[a - 1][b - 1] == 16 for a in u for b in u),
            'all minimal rank-two factor pairs cost sixteen')
    require(min(table[a - 1][b - 1] for a in u for b in FORMS) == 11,
            'rank-three Sylvester reduction costs at least eleven per factor')
    four, five = coverage_bound(frontier, 4), coverage_bound(frontier, 5)
    require(four == 24 < 32 and five == 0 < 32, 'four/five-factor diagonal coverage exclusion')
    require(min(frontier) == 6 and 6 * 6 > 32, 'six-plus factor exclusion')
    require(all(not supports[a].intersection(supports[b])
                for a in FORMS for b in FORMS if table[a - 1][b - 1] < 8),
            'peak below eight cannot cover any decoder diagonal')
    witness = check_factorization(WITNESS_SOURCE, WITNESS_READER, ports, table)
    require(witness['factor_costs'] == [8] * 4 and witness['total_cost'] == 32
            and witness['peak_cost'] == 8, 'four-total optimum total and peak witness')
    parity = check_factorization((31, 63), (31, 63), ports, table)
    require(parity['factor_costs'] == [16, 16], 'two-total parity optimum witness')
    return dict(observation_rank_f2=6, decoder_rank_f2=2, affine_evaluation_rank_f2=6,
                rank_two_charge_lower=32, rank_three_charge_lower=33,
                sub32_four_factor_diagonal_coverage_upper=four,
                sub32_five_factor_diagonal_coverage_upper=five,
                six_or_more_charge_lower=36, global_charge_minimum=32,
                global_peak_minimum=8, optimal_four_total_witness=witness,
                optimal_two_total_witness=parity, pricing=price_check(32))


def expect_rejection(fn, label):
    try:
        fn()
    except (ValueError, TypeError, KeyError):
        return label
    raise ValueError('negative control accepted: ' + label)


def negative_controls(ports, table, frontier, records):
    wrong_source = (31,) + WITNESS_SOURCE[1:]
    wrong_frontier = dict(frontier)
    wrong_frontier[6] = 16
    wrong_record = dict(records[0])
    wrong_record['sha256'] = '0' * 64
    checks = [expect_rejection(lambda: check_factorization((0,) + WITNESS_SOURCE[1:],
                                                         WITNESS_READER, ports, table),
                               'zero affine source factor'),
              expect_rejection(lambda: check_factorization(wrong_source, WITNESS_READER, ports, table),
                               'altered source fails decoder replay'),
              expect_rejection(lambda: require(coverage_bound(wrong_frontier, 4) < 32,
                                              'false frontier'), 'false diagonal-coverage frontier'),
              expect_rejection(lambda: price_check(31), 'uncertified copy charge thirty-one'),
              expect_rejection(lambda: check_source_record(wrong_record), 'altered pinned source hash'),
              expect_rejection(lambda: require(integer_rank([[2, 4], [3, 6]]) == 2,
                                              'singular rank'), 'singular matrix claimed full rank'),
              expect_rejection(lambda: form_value(64, 0), 'form outside six-bit affine domain')]
    require(integer_rank([[0, 2], [3, 6]]) == 2, 'integer elimination row-swap control')
    require(integer_rank([[0, 0, 1], [0, 0, 2]]) == 1, 'skipped-column integer rank control')
    checks.extend(('integer row-swap control', 'integer skipped-column control'))
    return checks


def enumerate_factorizations(ports, table):
    """Optional exhaustive corroboration after a separate subspace reduction.

    If cost<32 there are at most five terms. Sylvester gives one factor span
    dimension <=3; it contains U=<31,32>. Transpose if necessary. Merge equal
    reader factors without increasing cost: XOR source support lies inside
    the union, and rank on union rows is at most the sum of the two ranks.
    Thus enumerate distinct readers in U or its 15 dimension-three extensions.
    """
    extensions, seen = [], set()
    for a in FORMS:
        if a in PARITY_SPACE:
            continue
        span = frozenset(PARITY_SPACE | {q ^ a for q in PARITY_SPACE})
        if span not in seen:
            extensions.append(sorted(span - {0}))
            seen.add(span)
    require(len(extensions) == 15, 'all dimension-three parity-space extensions')
    best, counts, valid, reader_subsets = {}, Counter(), Counter(), set()
    for readers in [sorted(PARITY_SPACE - {0})] + extensions:
        for n in range(1, 6):
            for subset in combinations(readers, n):
                if subset in reader_subsets:
                    continue
                reader_subsets.add(subset)
                solutions = {32: [], 63: []}
                for mask in range(1 << n):
                    value = 0
                    for i, reader in enumerate(subset):
                        if mask >> i & 1:
                            value ^= reader
                    if value in solutions:
                        solutions[value].append(mask)
                if not all(solutions.values()):
                    continue
                for rows in product(*([solutions[32]] * 5 + [solutions[63]])):
                    counts[n] += 1
                    sources = tuple(sum((rows[k] >> i & 1) << k for k in range(6))
                                    for i in range(n))
                    if 0 in sources:
                        continue
                    valid[n] += 1
                    charge = sum(table[source - 1][reader - 1]
                                 for source, reader in zip(sources, subset))
                    if n not in best or charge < best[n]['total_cost']:
                        best[n] = dict(total_cost=charge, source_forms=list(sources),
                                       reader_forms=list(subset))
    require(dict(counts) == {2: 3, 3: 484, 4: 33600, 5: 1290240},
            'exhaustive assignment counts')
    require(dict(valid) == {2: 3, 3: 301, 4: 28530, 5: 1197270},
            'exhaustive nonzero assignment counts')
    require({n: w['total_cost'] for n, w in best.items()} == {2: 32, 3: 35, 4: 32, 5: 43},
            'exhaustive reduced-factorization minima')
    for witness in best.values():
        check_factorization(witness['source_forms'], witness['reader_forms'], ports, table)
    return dict(dimension_three_extensions=extensions, reader_subset_count=len(reader_subsets),
                assignments={str(k): v for k, v in sorted(counts.items())},
                nonzero_assignments={str(k): v for k, v in sorted(valid.items())},
                reduced_span_minima={str(k): v for k, v in sorted(best.items())},
                caveat='These are minima in the reduced reader-span search; only exclusion below 32 is global.')


def verify(exhaustive=False):
    hashes, records = check_inputs()
    ports, gram, supports, table, histogram, frontier = support_census()
    check_primary_receipt(table, histogram)
    proof = check_proof(ports, supports, table, frontier)
    controls = negative_controls(ports, table, frontier, records)
    result = dict(schema='five-cube-coded-copy-independent-v1', base_commit=BASE,
                  source_sha256=hashes, cross_rank_table=table,
                  cross_rank_histogram={str(k): v for k, v in sorted(histogram.items())},
                  coverage_frontier={str(k): v for k, v in sorted(frontier.items())},
                  proof=proof, negative_controls=controls,
                  independence='Separate exact-integer implementation by an AI collaborator; not independent human review.')
    if exhaustive:
        result['exhaustive_factorizations'] = enumerate_factorizations(ports, table)
    check_independent_receipt(result, exhaustive)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exhaustive-factorizations', action='store_true',
                        help='also enumerate about 1.3 million reduced-span assignments')
    parser.add_argument('--write-certificate', type=Path,
                        help='write a new independent receipt with exclusive creation')
    args = parser.parse_args()
    result = verify(args.exhaustive_factorizations)
    if args.write_certificate:
        with args.write_certificate.open('x', encoding='utf-8', newline='\n') as handle:
            json.dump(result, handle, indent=2)
            handle.write('\n')
    print('PASS_FIVE_CUBE_CODED_COPY_INDEPENDENT ranks=3969 '
          'observation_rank=6 decoder_rank=2 copy_min=32 peak_min=8 '
          'all_stage_deficit<=-32 controls=' + str(len(result['negative_controls']))
          + ' exhaustive=' + str(args.exhaustive_factorizations).lower())


if __name__ == '__main__':
    main()
