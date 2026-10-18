#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate full-column/set-elimination replay; no primary/predecessor imports.

Uses Euclidean doubled roots to reconstruct the entire binary pairing matrix,
not the primary checker's nine-bit dual-label projections. Shares the stored
geometry ordering and certificate witnesses, not the elimination algorithm.
Ross Richardson, with substantial OpenAI Codex assistance.
"""
from itertools import combinations, product
from hashlib import sha256
import json
from pathlib import Path

P = Path(__file__).resolve().parent
R = P.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def rank(columns):
    pivots = {}
    for original in columns:
        col = set(original)
        while col:
            pivot = min(col)
            if pivot in pivots:
                col.symmetric_difference_update(pivots[pivot])
            else:
                pivots[pivot] = col
                break
    return len(pivots)


def canonical_root(row):
    first = next(x for x in row if x)
    return tuple(row if first > 0 else [-x for x in row])


def reconstruct(data):
    roots = set()
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            v = [0] * 8; v[i] = a; v[j] = b
            roots.add(canonical_root(v))
    for v in product((-1, 1), repeat=8):
        if sum(x < 0 for x in v) % 2 == 0:
            roots.add(canonical_root(v))
    frame = []
    for j in range(4):
        for s in (1, -1):
            row = [0] * 8; row[2*j] = 2; row[2*j+1] = 2*s
            frame.append(row)
    live = roots - {canonical_root(row) for row in frame}
    need(len(roots) == 120 and len(live) == 112, 'root enumeration')
    ordered = data['roots']
    need(len(ordered) == 112 and {canonical_root(row) for row in ordered} == live,
         'complete live root set')
    coords = []
    for root in ordered:
        products = [sum(x*y for x, y in zip(root, f)) for f in frame]
        need(all(x % 4 == 0 for x in products), 'coordinate integrality')
        coords.append([x // 4 for x in products])
    need(coords == data['X'] and frame == data['frame'], 'ordered coordinates')
    pairing = []
    for root in ordered:
        row = []
        for other in ordered:
            prod = sum(x*y for x, y in zip(root, other))
            need(prod % 4 == 0, 'Gram integrality')
            row.append((1 + prod // 4) % 2)
        pairing.append(row)
    need(rank([{i for i in range(112) if pairing[i][j]} for j in range(112)]) == 9,
         'literal pairing rank')
    return coords, pairing


def nonzero_combo(x, a, y, b):
    return (x*a[0]+y*b[0], x*a[1]+y*b[1]) != (0, 0)


def support_strata(coords):
    # Regression test for the written all-complex cancellation classification.
    scalars = list(product(range(-2, 3), repeat=2))
    reps = ((1, 0), (0, 1), (1, 1), (1, -1), (1, 2))
    checked = 0
    for p, q in combinations(range(8), 2):
        expected = [{i for i, row in enumerate(coords) if a*row[p]+b*row[q]}
                    for a, b in reps]
        for a, b in product(scalars, repeat=2):
            if a == b == (0, 0):
                continue
            if b == (0, 0): kind = 0
            elif a == (0, 0): kind = 1
            elif a == b: kind = 2
            elif a == (-b[0], -b[1]): kind = 3
            else: kind = 4
            actual = {i for i, row in enumerate(coords) if nonzero_combo(row[p], a, row[q], b)}
            need(actual == expected[kind], 'complex support stratum')
            checked += 1
    return checked


def replay(cert, coords, pairing):
    pairs = list(combinations(range(8), 2))
    types = list(combinations(range(5), 2)) + [(4, 4)]
    rays = ((1, 0), (0, 1), (1, 1), (1, -1), (1, 2))
    need(type(cert.get('schema_version')) is int and cert['schema_version'] == 1, 'schema')
    need(len(cert['cases']) == 308, 'case count')
    seen = set()
    for case in cert['cases']:
        need(all(type(v) is int for v in case['pair'] + case['strata']), 'integer case key')
        pq, uv = tuple(case['pair']), tuple(case['strata'])
        need(pq in pairs and uv in types and (pq, uv) not in seen, 'case coverage')
        seen.add((pq, uv))
        p, q = pq; u, v = uv
        a, b = rays[u], (rays[v] if u != v else (1, 3))
        normals = ((1, 0), (0, 1), a, b)
        reader_sets = [{i for i, r in enumerate(coords) if aa*r[p]+bb*r[q]} for aa, bb in normals]
        source_normals = ((b[1], -b[0]), (-a[1], a[0]))
        source_sets = [{i for i, r in enumerate(coords) if aa*r[p]+bb*r[q]} for aa, bb in source_normals]
        units = case['units']
        need(len(units) == 16 and len({tuple(t) for t in units}) == 16, 'units')
        columns = [[], [], [], []]
        for unit in units:
            need(len(unit) == 3 and all(type(x) is int for x in unit), 'integer unit')
            i, old, new = unit
            need(0 <= i < 112 and old in (0, 1) and new in (0, 1), 'unit range')
            need(i in reader_sets[old] and i in source_sets[new], 'support incidence')
            columns[old].append({j for j in reader_sets[old] if pairing[j][i]})
            columns[new+2].append({j for j in reader_sets[new+2] if pairing[j][i]})
        need(all(len(group) == 8 and rank(group) == 8 for group in columns), 'balanced full-column rank')
    need(seen == {(p, t) for p in pairs for t in types}, 'all pairs and strata')
    return len(seen)


def main():
    pins = json.loads((P / 'SOURCES.json').read_text())
    data_path = 'research/p112-single-lift/reference-geometry.json'
    pin = [r for r in pins['files'] if r['path'] == data_path]
    need(len(pin) == 1, 'unique geometry pin')
    raw = (R / data_path).read_bytes()
    need(sha256(raw).hexdigest() == pin[0]['sha256'], 'geometry source hash')
    coords, pairing = reconstruct(json.loads(raw))
    cert = json.loads((P / 'CERTIFICATE.json').read_text())
    cases = replay(cert, coords, pairing)
    support_cases = support_strata(coords)
    # The final generic/generic stratum is essential, not a singular repeated ray.
    reduced = json.loads(json.dumps(cert)); reduced['cases'] = reduced['cases'][:-1]
    try: replay(reduced, coords, pairing)
    except ValueError as exc: need('case count' in str(exc), 'control rejection')
    else: raise ValueError('missing generic/generic control accepted')
    bad = json.loads(json.dumps(cert)); bad['cases'][0]['units'][0] = bad['cases'][0]['units'][1]
    try: replay(bad, coords, pairing)
    except ValueError as exc: need('units' in str(exc), 'control rejection')
    else: raise ValueError('dependent unit control accepted')
    # A dependent four-column control defeats cardinality-as-rank.
    need(rank([{1, 3}, {2, 3}, {1, 2}, {1, 3}]) == 2, 'set elimination control')
    print(f'PASS_P112_MASK_INDEPENDENT cases={cases} groups=1232 gaussian_supports={support_cases} controls=3')


if __name__ == '__main__':
    main()
