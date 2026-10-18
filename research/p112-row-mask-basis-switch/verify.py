#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact balanced certificates for arbitrary row-masked two-coordinate switches.

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
No predecessor Python, floating-point arithmetic, solver, or network is used.
The universal step is the written argument in README.md; fixtures are controls.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GEOMETRY = 'research/p112-single-lift/reference-geometry.json'
RAYS = ((1, 0), (0, 1), (1, 1), (1, -1), (1, 2))
STRATA = tuple(combinations(range(5), 2)) + ((4, 4),)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def read_json(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            require(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    return json.loads(path.read_text(), object_pairs_hook=unique)


def source_pins():
    manifest = read_json(HERE / 'SOURCES.json')
    entries = [row for row in manifest['files'] if row['usage'] == 'input']
    require({x['path'] for x in entries} == {
        GEOMETRY, 'research/p112-complex-single-lift/PROOF.md',
        'research/p112-two-total-rank-one-seed21/PROOF.md'}, 'input inventory')
    for row in entries:
        require(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                'source SHA256: ' + row['path'])


def basis(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return [pivots[k] for k in sorted(pivots, reverse=True)]


def projected(space, label):
    return sum(((row & label).bit_count() & 1) << j for j, row in enumerate(space))


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def geometry():
    data = read_json(ROOT / GEOMETRY)
    x, labels, duals = data['X'], data['labels'], data['duals']
    require(len(x) == len(labels) == len(duals) == len(data['roots']) == 112,
            'geometry cardinality')
    require(len(set(labels)) == len(set(duals)) == 112, 'distinct labels')
    require(all(type(v) is int and 0 < v < 512 for v in labels + duals), 'label domain')
    require(len(basis(labels)) == len(basis(duals)) == 9, 'full label rank')
    require(all(len(row) == 8 and all(type(v) is int and v in (-1, 0, 1)
                for v in row) and dot(row, row) == 4 for row in x), 'X alphabet')
    for i, root in enumerate(data['roots']):
        require(dot(root, root) == 8, 'doubled root norm')
        require(x[i] == [dot(root, f) // 4 for f in data['frame']], 'frame coordinates')
        for j, other in enumerate(data['roots']):
            require(dot(root, other) % 4 == 0, 'integral root Gram')
            g = dot(root, other) // 4
            require(dot(x[i], x[j]) == 2 * g, 'XX transpose')
            require(((duals[i] & labels[j]).bit_count() & 1) == (1 + g) % 2,
                    'binary pairing')
    for j, k in product(range(8), repeat=2):
        require(sum(row[j] * row[k] for row in x) == 56 * (j == k), 'X column Gram')
    for j in range(8):
        col = [row[j] for row in x]
        require(cost(col, col, data) == 8, 'coordinate COPY8')
    return data


def cost(reader, source, data):
    space = basis(v for value, v in zip(reader, data['duals']) if value)
    return len(basis(projected(space, l) for value, l in zip(source, data['labels']) if value))


def model(data, pair, strata):
    p, q = pair
    u, v = strata
    a = RAYS[u]
    b = RAYS[v] if u != v else (1, 3)
    require(a[0] * b[1] != a[1] * b[0], 'singular representative')
    rows = [(row[p], row[q]) for row in data['X']]
    readers = [[dot(row, ray) for row in rows] for ray in ((1, 0), (0, 1), a, b)]
    # A^{-T} columns, with their common nonzero determinant omitted.
    sources = [[dot(row, ray) for row in rows] for ray in ((b[1], -b[0]), (-a[1], a[0]))]
    spaces = [basis(v for value, v in zip(col, data['duals']) if value) for col in readers]
    return readers, sources, spaces


def check_case(row, data):
    require(set(row) == {'pair', 'strata', 'units'}, 'case fields')
    pair, strata, units = row['pair'], row['strata'], row['units']
    require(isinstance(pair, list) and len(pair) == 2 and
            all(type(x) is int for x in pair) and tuple(pair) in combinations(range(8), 2), 'pair')
    require(isinstance(strata, list) and len(strata) == 2 and
            all(type(x) is int for x in strata) and tuple(strata) in STRATA, 'strata')
    require(isinstance(units, list) and len(units) == 16, 'sixteen units')
    require(all(isinstance(t, list) and len(t) == 3 and all(type(v) is int for v in t)
                and 0 <= t[0] < 112 and t[1] in (0, 1) and t[2] in (0, 1) for t in units),
            'unit domain')
    require(len({tuple(t) for t in units}) == 16, 'duplicate unit')
    readers, sources, spaces = model(data, pair, strata)
    old, new = [[], []], [[], []]
    for i, j, k in units:
        require(readers[j][i] != 0 and sources[k][i] != 0, 'unit support incidence')
        old[j].append(projected(spaces[j], data['labels'][i]))
        new[k].append(projected(spaces[k + 2], data['labels'][i]))
    for group in old + new:
        require(len(group) == 8, 'balanced eight-unit groups')
        require(len(basis(group)) == 8, 'independent unit group')
    return len({i for i, _, _ in units})


def certificate(data, path=HERE / 'CERTIFICATE.json'):
    cert = read_json(path)
    require(set(cert) == {'schema_version', 'cases'} and type(cert['schema_version']) is int
            and cert['schema_version'] == 1, 'certificate schema')
    require(isinstance(cert['cases'], list) and len(cert['cases']) == 308, 'complete case count')
    expected = {(p, q, u, v) for p, q in combinations(range(8), 2) for u, v in STRATA}
    seen = set()
    sizes = Counter()
    for row in cert['cases']:
        sizes[check_case(row, data)] += 1
        key = tuple(row['pair'] + row['strata'])
        require(key not in seen, 'duplicate case')
        seen.add(key)
    require(seen == expected, 'complete support-stratum coverage')
    return cert, sizes


# Exact Gaussian integers, only for literal coefficient/transpose controls.
def ga(x):
    return (x, 0) if type(x) is int else x


def add(x, y):
    x, y = ga(x), ga(y)
    return x[0] + y[0], x[1] + y[1]


def mul(x, y):
    x, y = ga(x), ga(y)
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def neg(x):
    x = ga(x)
    return -x[0], -x[1]


def nonzero(x):
    return ga(x) != (0, 0)


def fixture(data, pair, a, b, mask, conjugate=False, omit=False):
    require(isinstance(mask, set) and all(type(i) is int and 0 <= i < 112 for i in mask), 'mask')
    p, q = pair
    det = add(mul(a[0], b[1]), neg(mul(a[1], b[0])))
    require(nonzero(det), 'singular switch')
    readers, sources = [[], [], [], []], [[], [], [], []]
    for i, row in enumerate(data['X']):
        x, y = row[p], row[q]
        rd = (ga(x), ga(y), add(mul(x, a[0]), mul(y, a[1])), add(mul(x, b[0]), mul(y, b[1])))
        sc = (mul(x, det) if i not in mask else (0, 0),
              mul(y, det) if i not in mask else (0, 0),
              add(mul(x, b[1]), neg(mul(y, b[0]))) if i in mask else (0, 0),
              add(neg(mul(x, a[1])), mul(y, a[0])) if i in mask else (0, 0))
        for k in range(4):
            readers[k].append(rd[k]); sources[k].append(sc[k])
    entries = 0
    for i, j in product(range(112), repeat=2):
        got = (0, 0)
        for k in range(2 if omit else 4):
            z = sources[k][j]
            if conjugate:
                z = (z[0], -z[1])
            got = add(got, mul(readers[k][i], z))
        target = mul(det, data['X'][i][p] * data['X'][j][p] + data['X'][i][q] * data['X'][j][q])
        require(got == target, 'literal ordinary-transpose endpoint')
        entries += 1
    ranks = [cost([nonzero(x) for x in r], [nonzero(x) for x in s], data)
             for r, s in zip(readers, sources)]
    require(sum(ranks) >= 16, 'fixture COPY floor')
    return {'pair': list(pair), 'mask_size': len(mask), 'ranks': ranks, 'entries': entries}


def must_fail(call, text):
    try:
        call()
    except ValueError as exc:
        require(text in str(exc), 'wrong rejection: ' + str(exc))
    else:
        raise ValueError('control accepted: ' + text)


def modular_rank(rows, prime=101):
    """A nonzero minor mod a prime is an exact rational-rank lower bound."""
    work = [[x % prime for x in row] for row in rows]
    pivot = 0
    for col in range(len(work[0])):
        found = next((i for i in range(pivot, len(work)) if work[i][col]), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        inv = pow(work[pivot][col], -1, prime)
        work[pivot] = [x * inv % prime for x in work[pivot]]
        for i in range(pivot + 1, len(work)):
            c = work[i][col]
            work[i] = [(x - c*y) % prime for x, y in zip(work[i], work[pivot])]
        pivot += 1
    return pivot


def fixtures_and_controls(data, cert):
    masks = [set(), set(range(112)), {i for i in range(112) if (i * i + 3 * i + 1) % 11 < 5}]
    fixtures = []
    for u, v in STRATA:
        a = RAYS[u]; b = RAYS[v] if u != v else (1, 3)
        fixtures.append(fixture(data, (0, 1), a, b, masks[2]))
    for mask in masks[:2]:
        fixtures.append(fixture(data, (4, 6), (1, 1), (1, -1), mask))
    complex_a, complex_b = ((1, 0), (0, 1)), ((0, 1), (1, 0))
    fixtures.append(fixture(data, (2, 7), complex_a, complex_b, masks[2]))
    for pair in combinations(range(8), 2):
        fixtures.append(fixture(data, pair, (1, 1), (1, -1), {i for i in range(112) if i % 3 == 0}))
    row = cert['cases'][0]
    bad = json.loads(json.dumps(row)); bad['units'][0] = bad['units'][1]
    must_fail(lambda: check_case(bad, data), 'duplicate unit')
    bad = json.loads(json.dumps(row)); bad['units'][0][0] = True
    must_fail(lambda: check_case(bad, data), 'unit domain')
    bad = json.loads(json.dumps(row)); bad['units'] = bad['units'][:-1]
    must_fail(lambda: check_case(bad, data), 'sixteen units')
    must_fail(lambda: fixture(data, (0, 1), (1, 1), (2, 2), set()), 'singular switch')
    must_fail(lambda: fixture(data, (0, 1), (1, 1), (1, -1), {112}), 'mask')
    must_fail(lambda: fixture(data, (0, 1), (1, 1), (1, -1), masks[1], omit=True), 'endpoint')
    must_fail(lambda: fixture(data, (2, 7), complex_a, complex_b, masks[2], conjugate=True), 'endpoint')
    require(9 + 7 == 16 and 9 * 7 < 64, 'unbalanced power control')
    count_vectors = [c for c in product(range(9), repeat=4) if sum(c) == 16]
    require(all(8 * c >= c * c for counts in count_vectors for c in counts), 'chord control')
    # Both added sources can leave col(X). Full column rank modulo 101 gives
    # rank >=10 over Q; there are only ten columns, so the rank is exactly ten.
    outside = [row + ([row[0]+row[1], row[0]-row[1]] if i % 3 == 0 else [0, 0])
               for i, row in enumerate(data['X'])]
    require(modular_rank(outside) == 10, 'two independent outside-code sources')
    return fixtures, len(count_vectors), 10


def run():
    source_pins()
    data = geometry()
    cert, sizes = certificate(data)
    fixtures, count_vectors, controls = fixtures_and_controls(data, cert)
    return {'schema_version': 1, 'coordinate_pairs': 28, 'unordered_support_strata': 11,
            'certificates': 308, 'units': 4928, 'balanced_groups': 1232,
            'distinct_ports_histogram': dict(sorted(sizes.items())),
            'certificate_sha256': sha256((HERE / 'CERTIFICATE.json').read_bytes()).hexdigest(),
            'geometry_pairing_entries': 12544, 'literal_endpoint_entries': sum(x['entries'] for x in fixtures),
            'fixtures': fixtures, 'balanced_count_vectors': count_vectors, 'controls': controls,
            'outside_code_fixture_rank': 10, 'outside_code_fixture_columns': 10,
            'copy_floor': 64, 'power_floor': '8 * 8**theta for every 0 < theta <= 1',
            'all_masks': 'Every subset of 112 rows; not enumerated', 'no_new_kappa': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='write a new receipt; never overwrite')
    args = parser.parse_args()
    if args.write:
        require(not args.write.exists(), 'refuse to overwrite receipt')
    result = run()
    if args.write:
        with args.write.open('x') as out:
            json.dump(result, out, indent=2); out.write('\n')
    else:
        require(canonical(result) == canonical(read_json(HERE / 'RESULT.json')), 'complete result receipt')
    print('PASS_P112_ROW_MASK_BASIS_SWITCH cases=308 units=4928 copy_floor=64 power_floor=8*8^theta no_new_kappa')


if __name__ == '__main__':
    main()
