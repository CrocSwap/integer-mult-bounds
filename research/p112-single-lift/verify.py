"""Verify the finite premises of PROOF.md; standard library, Python 3.10+.

Default is read-only and compares every proof-relevant result with RESULTS.json.
All guards survive python -O. This is not a proof-assistant verification.
"""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
import sys

from geometry import (binary_basis, binary_kernel, build, check_geometry, dot,
                      evaluate, parity, rational_basis_indices, reader_space,
                      require, term_cost)

HERE = Path(__file__).resolve().parent
SEED = 40


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def check_sources():
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for name, expected in sources['local_inputs'].items():
        require(sha256((HERE / name).read_bytes()).hexdigest() == expected,
                'source hash: ' + name)


def support_certificate(data):
    records = []
    x, duals = data['X'], data['duals']
    for q in range(1, 512):
        indices = [i for i, dual in enumerate(duals) if parity(q & dual)]
        selected = rational_basis_indices([x[i] for i in indices])
        pivots = [indices[j] for j in selected]
        rank = len(selected)
        missing = [j for j in range(8) if all(x[i][j] == 0 for i in indices)]
        require(rank == 8 or (rank == 7 and len(missing) == 1),
                'unexpected functional support rank')
        records.append({'functional': q, 'rank': rank, 'basis_ports': pivots,
                        'zero_columns': missing})
    require(Counter(r['rank'] for r in records) == {8: 503, 7: 8}, 'support census')
    require(sorted(r['zero_columns'][0] for r in records if r['rank'] == 7)
            == list(range(8)), 'coordinate exceptions')
    return records


def sign_cases():
    cases = [c for c in product((-1, 0, 1), repeat=8)
             if sum(v != 0 for v in c) >= 2 and next(v for v in c if v) == 1]
    # Seed diversifies traversal, never coverage. Receipt ordering is canonical.
    random.Random(SEED).shuffle(cases)
    return cases


def constraint_rows(coefficients, data, spaces):
    active = [j for j, value in enumerate(coefficients) if value]
    rows = []
    for values, label in zip(data['X'], data['labels']):
        for sign in (-1, 1):
            row = 0
            for block, j in enumerate(active):
                if values[j] * coefficients[j] == sign:
                    row |= evaluate(spaces[j], label) << (8 * block)
            rows.append(row)
    return rows


def unpack_kernel(vector, coefficients, spaces):
    active = [j for j, value in enumerate(coefficients) if value]
    qs = [0] * 8
    for block, j in enumerate(active):
        for bit, q in enumerate(spaces[j]):
            if vector >> (8 * block + bit) & 1:
                qs[j] ^= q
    return qs


def conflicts(qs, coefficients, data):
    result = []
    for port, (values, label) in enumerate(zip(data['X'], data['labels'])):
        # Distinct signs, including zero, force incompatible values of z_i.
        demanded = {values[j] * coefficients[j] for j in range(8)
                    if coefficients[j] and parity(qs[j] & label)}
        if len(demanded) > 1:
            result.append(port)
    return result


def case_certificate(coefficients, data, spaces):
    active_count = sum(v != 0 for v in coefficients)
    rows = constraint_rows(coefficients, data, spaces)
    rank = len(binary_basis(rows))
    record = {'signs': list(coefficients), 'rank': rank, 'rows_sha256': digest(rows)}
    if active_count < 8:
        require(rank == 8 * active_count, 'proper-support injectivity')
    else:
        require(rank == 63, 'full-support rank')
        kernel = binary_kernel(rows, 64)
        require(len(kernel) == 1, 'full-support nullity')
        qs = unpack_kernel(kernel[0], coefficients, spaces)
        bad_ports = conflicts(qs, coefficients, data)
        require(len(bad_ports) == 56, 'kernel must have actual value conflicts')
        record.update(kernel=hex(kernel[0]), conflict_ports=bad_ports)
    return record


def lifted_terms(coefficients, z, data):
    x = data['X']
    terms = [([row[j] for row in x],
              [row[j] - coefficients[j] * z[i] for i, row in enumerate(x)])
             for j in range(8)]
    terms.append(([dot(row, coefficients) for row in x], z))
    return terms


def exact_identity(terms, data):
    return all(sum(d[i] * t[j] for d, t in terms)
               == dot(data['X'][i], data['X'][j])
               for i in range(112) for j in range(112))


def controls(data, spaces):
    rejected = []

    def must_reject(name, action):
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('negative control accepted: ' + name)

    def changed(field, row, value):
        copy = json.loads(json.dumps(data))
        copy[field][row] = value
        return copy

    bad_root = list(data['roots'][0])
    bad_root[0] += 1
    must_reject('root coordinate corruption',
                lambda: check_geometry(changed('roots', 0, bad_root)))
    must_reject('label bit corruption',
                lambda: check_geometry(changed('labels', 0, data['labels'][0] ^ 1)))
    must_reject('dual form corruption',
                lambda: check_geometry(changed('duals', 0, data['duals'][0] ^ 1)))
    short = {key: value[:-1] if key != 'frame' else value for key, value in data.items()}
    must_reject('missing live port', lambda: check_geometry(short))

    a = [1, 1, 0, 0, 0, 0, 0, 0]
    z = [int(i == SEED) for i in range(112)]
    terms = lifted_terms(a, z, data)
    require(exact_identity(terms, data), 'single-port lift identity')
    costs = [term_cost(d, t, data) for d, t in terms]
    require(costs == [8] * 8 + [1], 'mixed-rank positive control')
    must_reject('omitted additional total',
                lambda: require(exact_identity(terms[:-1], data), 'omitted lift'))
    wrong = [(list(d), list(t)) for d, t in terms]
    wrong[0][1][SEED] += 2
    must_reject('wrong compensation sign',
                lambda: require(exact_identity(wrong, data), 'wrong lift'))

    all_signs = (1,) * 8
    rows = constraint_rows(all_signs, data, spaces)
    kernel = binary_kernel(rows, 64)[0]
    must_reject('false full-rank claim at eight active coordinates',
                lambda: require(len(binary_basis(rows)) == 64, 'actual rank is 63'))
    qs = unpack_kernel(kernel, all_signs, spaces)
    require(all(parity(row & kernel) == 0 for row in rows), 'kernel is real')
    must_reject('linear-relaxation kernel treated as a feasible correction',
                lambda: require(not conflicts(qs, all_signs, data), 'incompatible z'))
    empty_rows = [0] * len(rows)
    must_reject('deleted proof constraints',
                lambda: require(len(binary_basis(empty_rows)) == 63, 'lost rank'))

    # Exact diagnostic instances, not the universal proof: unequal magnitudes,
    # each boundary support size, and a nonintegral correction outside col(X).
    diagnostics = []
    for k in range(9):
        a = [((-1) ** j) * (j + 1) if j < k else 0 for j in range(8)]
        z = [Fraction(((i * SEED + 7) % 11) - 5, 3) for i in range(112)]
        terms = lifted_terms(a, z, data)
        require(exact_identity(terms, data), 'rational lift identity')
        total = sum(term_cost(d, t, data) for d, t in terms)
        require(total >= 64, 'rational lift floor')
        diagnostics.append({'active': k, 'cost': total})
    zero_terms = lifted_terms([1] * 8, [0] * 112, data)
    require(sum(term_cost(d, t, data) for d, t in zero_terms) == 64, 'sharp z=0 control')
    return {'rejected': rejected, 'mixed_rank_costs': costs,
            'rational_instances': diagnostics, 'sharp_cost': 64}


def run():
    check_sources()
    data = build()
    check_geometry(data)
    reference = json.loads((HERE / 'reference-geometry.json').read_text(encoding='utf-8'))
    require(data == reference, 'PR717 reference geometry mismatch')
    spaces = [reader_space([row[j] for row in data['X']], data['duals']) for j in range(8)]
    require([len(space) for space in spaces] == [8] * 8, 'coordinate reader ranks')
    require([term_cost([r[j] for r in data['X']], [r[j] for r in data['X']], data)
             for j in range(8)] == [8] * 8, 'coordinate pairing costs')
    support = support_certificate(data)
    cases = sorted((case_certificate(c, data, spaces) for c in sign_cases()), key=lambda c: c['signs'])
    require(len(cases) == 3272 and len({tuple(c['signs']) for c in cases}) == 3272,
            'complete sign coverage')
    histogram = Counter((sum(v != 0 for v in c['signs']), c['rank']) for c in cases)
    require(histogram == {(2, 16): 56, (3, 24): 224, (4, 32): 560,
                          (5, 40): 896, (6, 48): 896, (7, 56): 512, (8, 63): 128},
            'sign census')
    return {'schema': 1, 'assignment_seed': SEED, 'geometry_sha256': digest(data),
            'reader_spaces': spaces, 'support_certificates': support, 'cases': cases,
            'controls': controls(data, spaces),
            'conclusion': 'copy-rank cost >= 64 for every real single lift retaining coordinate readers'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='write the recomputed certificate to this path')
    parser.add_argument('--check', type=Path, default=HERE / 'RESULTS.json')
    args = parser.parse_args()
    result = run()
    if args.write:
        args.write.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n',
                              encoding='utf-8', newline='\n')
    else:
        require(result == json.loads(args.check.read_text(encoding='utf-8')), 'certificate mismatch')
    print('PASS_P112_SINGLE_LIFT: 511 support certificates; 3272 sign cases; '
          '128 conflicting kernels; 9 negative controls; copy cost >= 64')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print('FAIL_P112_SINGLE_LIFT: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
