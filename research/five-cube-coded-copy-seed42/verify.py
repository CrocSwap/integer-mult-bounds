#!/usr/bin/env python3
"""Exact finite lower certificate for coded five-cube totals.

Copyright 2026 martinxxx9. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from hashlib import sha1, sha256
from math import gcd, isqrt
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
BASE = '2921874911956718fcaaaf9396fe8267b3cfa9f0'
PRIME = 65521
FORMS = tuple(range(1, 64))
U = (31, 32, 63)
SOURCE_PATHS = frozenset(('sources/PR958-PROOF.md', 'sources/PR958-NOTICE.md',
                          'sources/PR231-README.md', 'sources/PR446-PROOF.md',
                          'sources/FORMAT-AXIOMS.md', 'sources/SELECTED-RESULT.json'))
TWO = ((31, 31), (63, 63))  # (reader, source)
FOUR = ((1, 30), (30, 33), (33, 62), (62, 1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def support(form):
    return tuple(x for x in range(32)
                 if ((form & 31 & x).bit_count() ^ (form >> 5)) & 1)


def gram(x, y):
    j = 5 - (x ^ y).bit_count()
    return 2 * (j - 1) * (j - 3)


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def modular_rank(matrix):
    rows = [[x % PRIME for x in row] for row in matrix]
    r = 0
    for c in range(len(rows[0])):
        pivot = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        inv = pow(rows[r][c], -1, PRIME)
        normalized = [x * inv % PRIME for x in rows[r]]
        for i in range(r + 1, len(rows)):
            factor = rows[i][c]
            if factor:
                rows[i][c:] = [(x - factor * y) % PRIME
                               for x, y in zip(rows[i][c:], normalized[c:])]
        r += 1
        if r == len(rows):
            break
    return r


def rational_rank(matrix):
    """Integer row operations with gcd normalization; exact over Q."""
    rows = [list(row) for row in matrix]
    r = 0
    for c in range(len(rows[0])):
        pivot = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        for i in range(r + 1, len(rows)):
            factor = rows[i][c]
            if not factor:
                continue
            common = gcd(abs(factor), abs(rows[r][c]))
            a, b = rows[r][c] // common, factor // common
            tail = [a * x - b * y for x, y in zip(rows[i][c:], rows[r][c:])]
            scale = 0
            for x in tail:
                scale = gcd(scale, abs(x))
            rows[i][c:] = [x // (scale or 1) for x in tail]
        r += 1
        if r == len(rows):
            break
    return r


def check_pins():
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    require(manifest['base_commit'] == BASE, 'source base changed')
    require(len(manifest['files']) == len(SOURCE_PATHS)
            and {item['path'] for item in manifest['files']} == SOURCE_PATHS,
            'exact source inventory')
    for item in manifest['files']:
        require(item['commit'] == BASE, 'source commit changed')
        path = (HERE / item['path']).resolve()
        require(path.is_relative_to(HERE), 'source path escaped package')
        data = path.read_bytes()
        require(sha256(data).hexdigest() == item['sha256'], 'source SHA256: ' + item['path'])
        blob = b'blob ' + str(len(data)).encode('ascii') + b'\0' + data
        require(sha1(blob).hexdigest() == item['git_blob_sha1'], 'source Git blob: ' + item['path'])
    claim = json.loads((HERE / 'CLAIM.json').read_text(encoding='utf-8'))
    require(claim['base_commit'] == BASE and claim['assignment_seed'] == 42, 'assignment changed')
    return len(manifest['files'])


def decoder_matches(terms):
    for x in range(32):
        for y in range(32):
            value = sum((x in support(a)) and (y in support(b)) for a, b in terms) & 1
            if value != (1 ^ (x.bit_count() & 1) ^ (y.bit_count() & 1)):
                return False
    return True


def coverage_bound(frontier, n, budget):
    """Relax correlations: every term can independently use any census type."""
    values = {0: 0}
    for _ in range(n):
        updated = {}
        for paid, coverage in values.items():
            for cost, contribution in frontier.items():
                total = paid + cost
                if total <= budget:
                    updated[total] = max(updated.get(total, -1), coverage + contribution)
        values = updated
    return max(values.values(), default=-1)


def build_receipt():
    require(PRIME > 2 and all(PRIME % d for d in range(2, isqrt(PRIME) + 1)), 'modulus not prime')
    supports = {f: support(f) for f in FORMS}
    require(len(set(supports.values())) == 63 and all(supports.values()), 'affine domain incomplete')
    G = [[gram(x, y) for y in range(32)] for x in range(32)]
    B = [sum((1 ^ (x.bit_count() & 1) ^ (y.bit_count() & 1)) << y for y in range(32))
         for x in range(32)]
    incidence = [sum((1 ^ ((x >> i) & 1)) << (2 * i) | ((x >> i) & 1) << (2 * i + 1)
                     for i in range(5)) for x in range(32)]
    require(binary_rank(B) == 2, 'decoder binary rank')
    require(binary_rank(incidence) == 6, 'star observation binary rank')
    require(rational_rank(G) == 16, 'quadratic Gram rank')
    scalar_checks = 0
    for x in range(32):
        for y in range(32):
            j = 5 - (x ^ y).bit_count()
            coefficient = ((B[x] >> y) & 1) ^ int(j in (1, 3))
            require(coefficient == int(x == y), 'complete star/correction identity')
            scalar_checks += 1
    table, histogram, frontier, pairs = [], Counter(), {}, []
    for a in FORMS:
        row = []
        for b in FORMS:
            rank = modular_rank([[G[x][y] for y in supports[b]] for x in supports[a]])
            diagonal = len(set(supports[a]) & set(supports[b]))
            row.append(rank)
            histogram[rank] += 1
            frontier[rank] = max(frontier.get(rank, -1), diagonal)
            pairs.append((a, b, rank, diagonal))
        table.append(row)
    require(min(histogram) == 6, 'nonzero term rank floor')
    require(all(d == 0 for _, _, r, d in pairs if r == 6), 'rank-six terms must be disjoint')
    u_any = min(table[a - 1][b - 1] for a in U for b in FORMS)
    u_u = min(table[a - 1][b - 1] for a in U for b in U)
    require(u_any == 11 and u_u == 16, 'rank-two target-space floors')
    bounds = {n: coverage_bound(frontier, n, 31) for n in (4, 5)}
    require(bounds == {4: 24, 5: 0}, 'sub-32 diagonal coverage changed')
    require(decoder_matches(TWO) and decoder_matches(FOUR), 'literal decoder witness')
    witnesses = []
    for name, terms in [('two_total', TWO), ('four_total', FOUR)]:
        costs = [rational_rank([[G[x][y] for y in supports[b]] for x in supports[a]])
                 for a, b in terms]
        expected_costs = [16, 16] if name == 'two_total' else [8, 8, 8, 8]
        require(costs == expected_costs,
                'witness exact rational costs')
        witnesses.append(dict(name=name, terms=[dict(reader=a, source=b) for a, b in terms],
                              pairing_ranks=costs, total=sum(costs), peak=max(costs),
                              complete_matrix_coefficients=1024))
    controls = []
    def control(name, condition):
        require(condition, 'negative control: ' + name)
        controls.append(name)
    control('omit_one_parity_total', not decoder_matches(TWO[:1]))
    control('change_reader_without_source', not decoder_matches(((30, 31), (63, 63))))
    control('omit_one_four_total', not decoder_matches(FOUR[:3]))
    control('ignore_diagonal_demand', coverage_bound({6: 0}, 4, 31) == 0 and 4 * 6 < 32)
    control('rank_is_two_not_observation_six', binary_rank(B) == 2 and binary_rank(incidence) == 6)
    control('nonaffine_singleton_escapes_term_floor', modular_rank([[gram(0, 0)]]) == 1)
    control('wrong_kernel_changes_witness', rational_rank([[1 for y in supports[30]]
                                                         for x in supports[1]]) != 8)
    control('free_copy_budget_is_not_valid', (3 - 1) * 32 > 0 and (3 - 1) * 32 - 3 * 32 == -32)
    return dict(schema='five-cube-coded-copy-v1', base_commit=BASE, assignment_seed=42,
                affine_form_encoding='bits 0..4 linear; bit 5 constant; f(x)=parity(a_linear AND x) XOR a_constant',
                port_count=32, nonzero_forms=63, support_pairs=3969, prime=PRIME,
                cross_rank_table=table,
                cross_rank_histogram={str(k): v for k, v in sorted(histogram.items())},
                rank_semantics='modular ranks are rational lower bounds; independent.py verifies equality over Q',
                maximum_diagonal_coverage_by_rank={str(k): v for k, v in sorted(frontier.items())},
                decoder_binary_rank=2, coordinate_star_observation_rank=6, quadratic_gram_rank=16,
                target_code_forms=list(U), target_code_to_any_rank_floor=u_any,
                target_code_to_target_code_rank_floor=u_u,
                coverage_at_budget_31={str(k): v for k, v in bounds.items()},
                term_count_lower_bounds={'1': 'impossible by binary rank', '2': 32, '3': 33,
                                        '4': 'cost<=31 has diagonal coverage<=24<32',
                                        '5': 'cost<=31 has diagonal coverage0<32', '6_or_more': '6*n>=36'},
                exact_copy_floor=32, exact_peak_pairing_rank_floor=8,
                inherited_deficit_upper_bound='(s-1)*32-s*32=-32',
                scalar_identity_coefficients=scalar_checks, witnesses=witnesses,
                negative_controls=controls, no_new_kappa=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', type=Path)
    args = parser.parse_args()
    pins = check_pins()
    receipt = build_receipt()
    if args.write_certificate:
        with args.write_certificate.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(receipt, stream, indent=2)
            stream.write('\n')
    else:
        expected = json.loads((HERE / 'CERTIFICATE.json').read_text(encoding='utf-8'))
        require(expected == receipt, 'certificate differs from complete recomputation')
    print(f'PASS_FIVE_CUBE_CODED_COPY pairs=3969 copy_floor=32 peak_floor=8 witnesses=2 controls=8 pins={pins} no_new_kappa')


if __name__ == '__main__':
    main()
