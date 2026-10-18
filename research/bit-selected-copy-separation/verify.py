#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for ywz65 with substantial OpenAI Codex assistance.
"""Independent fixed-COPY separation; no predecessor executable imports."""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/r439-bsection-stars-seed01/candidate.json.gz'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pins():
    for e in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if e['usage'] == 'input':
            need(hashlib.sha256((ROOT / e['path']).read_bytes()).hexdigest() == e['sha256'], 'source pin: '+e['path'])
    for e in json.loads((HERE / 'PREDECESSOR.json').read_text()):
        raw = (HERE / e['local_path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == e['sha256'], 'predecessor pin: '+e['local_path'])
        git_blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        need(git_blob == e['git_blob'], 'predecessor Git blob: '+e['local_path'])


def dot(x, y):
    return sum(a*b for a, b in zip(x, y))


def mm(a, b):
    return [[dot(row, col) for col in zip(*b)] for row in a]


def ident(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def project(rows):
    # First route: RREF null vector of the actual seven-dimensional root span.
    a = [list(map(Q, r)) for r in rows]
    pivots = []
    for col in range(8):
        pos = len(pivots)
        pivot = next((i for i in range(pos, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[pos], a[pivot] = a[pivot], a[pos]
        scale = a[pos][col]
        a[pos] = [x/scale for x in a[pos]]
        for i in range(len(a)):
            if i != pos and a[i][col]:
                scale = a[i][col]
                a[i] = [x-scale*y for x, y in zip(a[i], a[pos])]
        pivots.append(col)
    need(len(pivots) == 7, 'not a rank-seven frame')
    free, = set(range(8)) - set(pivots)
    q = [Q(i == free) for i in range(8)]
    for row, pivot in zip(a, pivots):
        q[pivot] = -row[free]
    need(all(dot(r, q) == 0 for r in rows), 'normal mismatch')
    norm = dot(q, q)
    need(unit(norm), 'normal norm must be a unit in every odd characteristic')
    p = [[Q(i == j)-q[i]*q[j]/norm for j in range(8)] for i in range(8)]
    # Separately compute the projection onto the row span by Gram-Schmidt.
    orth = []
    for raw in rows:
        v = list(map(Q, raw))
        for u in orth:
            scale = dot(v, u)/dot(u, u)
            v = [x-scale*y for x, y in zip(v, u)]
        if any(v):
            orth.append(v)
    need(len(orth) == 7, 'independent rank mismatch')
    gs = [[sum(u[i]*u[j]/dot(u, u) for u in orth) for j in range(8)] for i in range(8)]
    need(p == gs and mm(p, p) == p, 'independent projector disagreement')
    return q, p


def power_two(n):
    return n > 0 and n & (n-1) == 0


def unit(x):
    return x != 0 and power_two(abs(x.numerator)) and power_two(x.denominator)


def encoded(vector):
    return [[x.numerator, x.denominator] for x in vector]


def witness(a, b):
    for col in range(16):
        for row in range(16):
            d = a[row][col]-b[row][col]
            if unit(d):
                return {'address_basis_column': col, 'output_coordinate': row, 'nonzero_difference': encoded([d])[0]}
    raise ValueError('no uniform dyadic-unit separation')


def reduce3(x):
    return x.numerator*pow(x.denominator, -1, 3) % 3


def finite_pairs(a, b, column):
    # Literal Boolean functions on F3^16, rather than matrix-entry covariance.
    ax, bx = [tuple(reduce3(row[column]) for row in m) for m in (a, b)]
    functions = (lambda z: 0, lambda z: 1, lambda z: int(z == ax), lambda z: int(z == bx))
    gl = [(x, y) for x in (1, 2, 3) for y in (1, 2, 3) if x != y]
    accepted = []
    for u, v in itertools.product(gl, repeat=2):
        passed = True
        for f in itertools.product(functions, repeat=2):
            for i, point in enumerate((ax, bx)):
                left = sum(f[j](point) for j in range(2) if u[i] >> j & 1) % 2
                right = sum(f[j]((ax, bx)[j]) for j in range(2) if v[i] >> j & 1) % 2
                if left != right:
                    passed = False
            # Deliberately exhaust all sixteen inputs, including failures.
        if passed:
            accepted.append([list(u), list(v)])
    return accepted


def reject(fn, label):
    try:
        fn()
    except ValueError:
        return label
    raise ValueError('negative control accepted: '+label)


def check_record(a, record):
    src = record['address_map']
    need(a == [[Q(x, src['denominator']) for x in r] for r in src['rows']], 'PR2088 COPY map mismatch')


def calculate():
    pins()
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    frames = list(word['start'])
    for section in ('D', 'A'):
        for f, d, sources in word[section]:
            for r in (d, *sources):
                frames[r] = f
    need(word['ret'] == list(range(472, 481)), 'retained centers changed')
    records = json.loads((HERE / 'PR2088-RESULT.json').read_text())['copy_address_maps']
    need(len(records) == 9, 'predecessor COPY count')
    maps, centers = [], []
    for center, rec in zip(word['ret'], records):
        frame = frames[center]
        q, p = project([word['lines'][j] for j in word['frames'][frame]])
        need(all(power_two(x.denominator) for row in p for x in row), 'non-dyadic entry')
        a = [[Q(i % 8 == j % 8)-p[i % 8][j % 8] if i//8 == j//8 else p[i % 8][j % 8]
              for j in range(16)] for i in range(16)]
        need(mm(a, a) == ident(16), 'partial swap not involutive')
        need((rec['center'], rec['frame'], rec['rank']) == (center, frame, 7), 'role/frame/rank mismatch')
        check_record(a, rec)
        maps.append(a)
        centers.append({'center': center, 'frame': frame, 'copy_rank': 7, 'normal': encoded(q), 'normal_squared_norm': encoded([dot(q, q)])[0]})
    pairs = []
    for i, j in itertools.combinations(range(9), 2):
        w = witness(maps[i], maps[j])
        need(finite_pairs(maps[i], maps[j], w['address_basis_column']) == [[[1, 2], [1, 2]]], 'rebasing census')
        pairs.append({'centers': [word['ret'][i], word['ret'][j]], **w})
    controls = [reject(lambda: witness(maps[0], maps[0]), 'equal maps cannot be declared separated')]
    # This pair differs over Q but becomes equal over F3: reject rational-only evidence.
    changed = [r[:] for r in maps[0]]
    changed[0][0] += 3
    controls.append(reject(lambda: witness(changed, maps[0]), 'difference 3 is not an all-odd-characteristic witness'))
    need([[reduce3(x) for x in r] for r in changed] == [[reduce3(x) for x in r] for r in maps[0]], 'collapse control')
    same = finite_pairs(maps[0], maps[0], 0)
    need(len(same) == 6 and all(u == v for u, v in same), 'equal-map positive countercontrol')
    controls.append('equal-map class admits all six synchronized GL2 changes')
    controls.append(reject(lambda: check_record(changed, records[0]), 'changed COPY coefficient rejected by independent reconstruction'))
    return {'status': 'PASS_SELECTED_COPY_SEPARATION', 'centers': centers, 'pairs': pairs,
            'uniform_address_characteristics': 'zero and all odd primes, including every field extension',
            'admitted_synchronized_scalar_pairs_for_any_subset': 'U=V=identity',
            'finite_F3_pair_checks': 36, 'GL2_pairs_per_check': 36, 'Boolean_input_pairs_per_GL2_pair': 16,
            'controls': controls, 'paid_COPY_rank_sum': 63, 'native_or_supplier_admission': False, 'new_kappa': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', type=Path)
    args = parser.parse_args()
    result = calculate()
    if args.emit:
        with args.emit.open('x', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
            f.write('\n')
    else:
        need(result == json.loads((HERE / 'CERTIFICATE.json').read_text()), 'certificate mismatch')
    print('PASS_SELECTED_COPY_SEPARATION maps=9 pairs=36 characteristic=all_odd controls=4 no_new_kappa')


if __name__ == '__main__':
    main()
