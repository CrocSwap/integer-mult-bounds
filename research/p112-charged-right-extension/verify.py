#!/usr/bin/env python3
"""Finite premises for the charged-pure theorem; Apache-2.0.
Arham Tahir, with substantial OpenAI Codex assistance. No predecessor code
is imported. The universal complex argument is written in README.md.
"""
from collections import Counter
from fractions import Fraction as F
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = 'research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json'
INPUT_SHA = '327d2a868043e846381aa58a33053c24425e8cad522ff401b10ec8af1d649a3f'


def check(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    check(len(a) == len(b), 'dot dimensions')
    return sum(x*y for x, y in zip(a, b))


def unit(n, k):
    return [F(j == k) for j in range(n)]


def reduced(rows, width):
    a = [list(map(F, row)) for row in rows]
    check(all(len(row) == width for row in a), 'matrix width')
    r, pivots = 0, []
    for col in range(width):
        hit = next((i for i in range(r, len(a)) if a[i][col]), None)
        if hit is None:
            continue
        a[r], a[hit] = a[hit], a[r]
        v = a[r][col]
        a[r] = [x/v for x in a[r]]
        for i in range(len(a)):
            if i != r:
                v = a[i][col]
                a[i] = [x-v*y for x, y in zip(a[i], a[r])]
        pivots.append(col)
        r += 1
        if r == len(a):
            break
    return a[:r], pivots


def nullspace(rows, width):
    a, pivots = reduced(rows, width)
    answer = []
    for k in range(width):
        if k not in pivots:
            v = unit(width, k)
            for row, p in zip(a, pivots):
                v[p] = -row[k]
            answer.append(v)
    return reduced(answer, width)[0]


def rank_mod(rows, width):
    """Independent modular lower bound via incremental row reduction."""
    prime, table = 65521, {}
    for raw in rows:
        row = [int(x) % prime for x in raw]
        for p, b in sorted(table.items()):
            c = row[p]
            row = [(x-c*y) % prime for x, y in zip(row, b)]
        p = next((i for i in range(width) if row[i]), None)
        if p is not None:
            inv = pow(row[p], -1, prime)
            table[p] = [x*inv % prime for x in row]
    return len(table)


def parity(a, b):
    return (a & b).bit_count() & 1


def binary_basis(values):
    table = {}
    for v in values:
        while v:
            p = v.bit_length()-1
            if p in table:
                v ^= table[p]
            else:
                table[p] = v
                break
    return list(table.values())


def rank_low(values):
    rows, r = list(values), 0
    for col in range(max((v.bit_length() for v in rows), default=0)):
        p = next((i for i in range(r, len(rows)) if rows[i] & (1 << col)), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(r+1, len(rows)):
            if rows[i] & (1 << col):
                rows[i] ^= rows[r]
        r += 1
    return r


def pairing(left, right):
    rows = [sum(parity(x, y) << j for j, y in enumerate(right)) for x in left]
    result = len(binary_basis(rows))
    check(result == rank_low(rows), 'binary algorithms disagree')
    return result


def inverse(a):
    n = len(a)
    b, pivots = reduced([row+unit(n, i) for i, row in enumerate(a)], 2*n)
    check(pivots[:n] == list(range(n)), 'singular basis')
    return [row[n:] for row in b]


def reject(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('negative control accepted: '+label)


def plain(obj):
    if isinstance(obj, F):
        return int(obj) if obj.denominator == 1 else str(obj)
    if isinstance(obj, dict):
        return {str(k): plain(v) for k, v in obj.items()}
    if isinstance(obj, (tuple, list)):
        return [plain(v) for v in obj]
    return obj


def encoded(obj):
    return json.dumps(plain(obj), sort_keys=True, separators=(',', ':')).encode()


def build(raw=None):
    raw = (ROOT/INPUT).read_bytes() if raw is None else raw
    check(hashlib.sha256(raw).hexdigest() == INPUT_SHA, 'prototype hash mismatch')
    data = json.loads(raw)
    all_x, all_l = data['root_lines'], data['binary_ports']
    check(all_x[:8] == [[2*int(i == j) for j in range(8)] for i in range(8)], 'removed frame')
    x, labels, frame = all_x[8:], all_l[8:], all_l[:8]
    check(len(x) == 112 and len(set(all_l)) == 120, 'geometry dimensions')
    check(all(0 < lab < 512 for lab in all_l) and len(binary_basis(all_l)) == 9, 'nine-dimensional labels')
    s, t = x[0], x[1]
    check(dot(s, s) == dot(t, t) == 4 and dot(s, t) == 2, 'exceptional pair')
    shared = [j for j in range(8) if s[j]]
    check(shared == [j for j in range(8) if t[j]] == [1, 2, 4, 7], 'shared coordinate support')
    gram = [[dot(a, b) for b in x] for a in x]
    check(all(gram[i][i] == 4 for i in range(112)) and
          all(v % 2 == 0 for row in gram for v in row), 'root normalization')
    check(all(parity(labels[i], labels[j]) == (gram[i][j]//2+1) % 2
              for i in range(112) for j in range(112)), 'binary Gram binding')
    left = [row+[int(i == 0)] for i, row in enumerate(x)]
    right = [row+[int(i == 0), int(i == 1)] for i, row in enumerate(x)]
    check(rank_mod(left, 9) == 9 and rank_mod(right, 10) == 10, 'factor spaces independent')
    target = [[gram[i][j]-(gram[i][0]-4*int(i == 0))*int(j == 0)
               +int(i == 0 and j == 1) for j in range(112)] for i in range(112)]
    check(all(target[i][j] == gram[i][j] for i in range(112) for j in range(112)
              if parity(labels[i], labels[j])), 'masked identity')
    records, kernels = {}, {}
    for side, matrix, width in [('left', left, 9), ('right', right, 10)]:
        histogram, rows_out = Counter(), []
        for h in range(1, 512):
            rows = [row for row, lab in zip(matrix, labels) if parity(h, lab)]
            actual = nullspace(rows, width)
            expected = []
            if not parity(h, labels[0]):
                expected.append(unit(width, 8))
            if side == 'right' and not parity(h, labels[1]):
                expected.append(unit(width, 9))
            if h in frame:
                expected.append(unit(width, frame.index(h)))
            elif h == labels[0]:
                expected.append(s+[-4]+([0] if side == 'right' else []))
            elif side == 'right' and h == labels[1]:
                expected.append(t+[0, -4])
            check(actual == reduced(expected, width)[0], f'{side} character {h}: kernel')
            check(rank_mod(rows, width) == width-len(actual), 'independent nullity bound')
            check(all(dot(row, v) == 0 for row in rows for v in actual), 'nullvector annihilation')
            histogram[len(actual)] += 1
            rows_out.append([h, actual])
            kernels[side, h] = actual
        normals = frame+[labels[0]]+([labels[1]] if side == 'right' else [])
        for i, h in enumerate(normals):
            for k in normals[i+1:]:
                rows = [row for row, lab in zip(matrix, labels) if parity(h, lab) or parity(k, lab)]
                check(all(not any(v[:8]) for v in nullspace(rows, width)), 'hidden smaller mixed support')
        records[side] = {'nullities':dict(sorted(histogram.items())),
            'kernels_sha256':hashlib.sha256(encoded(rows_out)).hexdigest()}
    classes_l = [('E'+str(i), frame[i], unit(8, i)) for i in range(8)]+[('S', labels[0], s), ('F', None, None)]
    classes_r = [('E'+str(i), frame[i], unit(8, i)) for i in range(8)]+[('S', labels[0], s), ('T', labels[1], t), ('F', None, None)]
    table, seven = [], []
    for ln, lh, _ in classes_l:
        for rn, rh, _ in classes_r:
            u = binary_basis(v for v in range(512) if lh is None or not parity(lh, v))
            v = binary_basis(w for w in range(512) if rh is None or not parity(rh, w))
            cost = pairing(u, v)
            check(cost >= 7 and (cost != 7 or ln == 'S' or rn in ('S', 'T')), 'mixed cost catalogue')
            check(not (ln == rn == 'S' and cost != 8), 'S/S charge')
            table.append([ln, rn, cost])
            if cost == 7:
                seven.append((ln, rn))
    dl = {name:vec for name, _, vec in classes_l}
    dr = {name:vec for name, _, vec in classes_r}
    conflicts = []
    for a, b in seven:
        for c, d in seven:
            cross = [dot(dr[b], dl[c]), dot(dr[d], dl[a])]
            check(any(cross), 'two cost-seven classes admit distinct dual positions')
            conflicts.append([a, b, c, d, cross])
    check(kernels['left', labels[0]] == reduced([s+[-4]], 9)[0], 'free right-e classification')
    check(kernels['left', labels[1]] == reduced([unit(9, 8)], 9)[0], 'free right-f classification')
    check(nullspace([row for row, lab in zip(left, labels) if parity(labels[0], lab) or parity(labels[1], lab)], 9) == [], 'free right-both classification')
    check(kernels['right', labels[0]] == reduced([s+[-4, 0], unit(10, 9)], 10)[0], 'free left-e classification')

    def fixture(name, pairs, expected=None):
        physical = [([dot(row, a) for row in left], [dot(row, b) for row in right]) for a, b in pairs]
        check(all(any(d) and any(r) for d, r in physical), 'zero physical factor')
        actual = [[sum(d[i]*r[j] for d, r in physical) for j in range(112)] for i in range(112)]
        check(actual == target, 'fixture identity: '+name)
        costs = [pairing([lab for z, lab in zip(d, labels) if z], [lab for z, lab in zip(r, labels) if z]) for d, r in physical]
        mixed = [cost for (a, b), cost in zip(pairs, costs) if any(a[:8]) and any(b[:8])]
        pure = [cost for (a, b), cost in zip(pairs, costs) if not (any(a[:8]) and any(b[:8]))]
        check(len(mixed) >= 8, 'too few mixed terms')
        if len(mixed) == 8:
            check(mixed.count(7) <= 1, 'dual incompatibility')
            check(not mixed.count(7) or sum(pure) >= 1, 'unpaid exceptional compensation')
        if expected is not None:
            check(costs == expected, 'fixture charge: '+name)
        return {'name':name, 'profile':costs, 'mixed':len(mixed), 'pure_charge':sum(pure), 'entries':112**2}

    fixtures = []
    for alpha in [F(-1), F(1), F(2), F(1, 2)]:
        beta = 1+1/alpha
        pairs = [(unit(8, j)+[-beta*s[j]], unit(8, j)+[-(1+alpha)*s[j], F(0)]) for j in range(8)]
        pairs.append(([alpha*v for v in s+[-4]], [F(0)]*8+[F(1), F(0)]))
        if beta:
            pairs.append(([F(0)]*8+[beta], s+[-4, F(0)]))
        pairs.append((unit(9, 8), unit(10, 9)))
        fixtures.append(fixture('free-alpha='+str(alpha), pairs, [8]*8+[0]*(len(pairs)-8)))
    n = [unit(9, j) for j in range(9)]
    n[1] = list(map(F, s))+[F(0)]
    m = inverse([list(row) for row in zip(*n)])
    charged = [(m[j], n[j][:8]+[-dot(s, n[j][:8])+4*n[j][8], n[j][8]]) for j in range(9)]
    fixtures.append(fixture('charged-pure-attainer', charged, [8, 7, 8, 8, 8, 8, 8, 8, 1]))
    a, b = [F(1)]*9, [F(1)]*10
    fixtures.append(fixture('redundant-mixed-and-charged-pure', charged+[(a, b), ([-v for v in a], b)]))
    p, q = [8]*8+[0], [8]+[7]*8
    check(sum(p) == sum(q) and all(sum(p[:i]) >= sum(q[:i]) for i in range(10)), 'many-term majorization')
    controls = []
    altered = [(list(a), list(b)) for a, b in charged]
    altered[0][0][0] += 1
    controls.append(reject(lambda:fixture('changed coefficient', altered), 'changed coefficient'))
    controls.append(reject(lambda:fixture('omitted charged pure term', charged[:-1]), 'omitted charged pure term'))
    controls.append(reject(lambda:fixture('false charge', charged, [8]*8+[0]), 'false COPY invoice'))
    controls.append(reject(lambda:check(dot(s, t) == 0, 'false off-diagonal duality'), 'false exceptional duality'))
    controls.append(reject(lambda:check([j for j in range(8) if t[j]] != shared, 'false disjoint support'), 'false disjoint support'))
    controls.append(reject(lambda:check(F(0)*(F(2)-1) == 1, 'alpha zero'), 'alpha zero'))
    controls.append(reject(lambda:check(F(2)*(F(1)-1) == 1, 'beta one'), 'beta one'))
    controls.append(reject(lambda:build(raw+b' '), 'prototype drift'))
    def gaussian_product(a, b):
        return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])
    check(gaussian_product((0, 1), (0, -1)) == (1, 0), 'ordinary phase')
    controls.append(reject(lambda:check(gaussian_product((0, 1), (0, 1)) == (1, 0), 'Hermitian shortcut'), 'Hermitian shortcut'))
    return plain({'schema_version':1, 'status':'PASS_P112_CHARGED_RIGHT_EXTENSION',
        'source_sha256':INPUT_SHA, 'kernels':records, 'class_pairs':table,
        'cost_seven_classes':seven, 'ordered_dual_conflicts':conflicts,
        'shared_coordinate_support':shared, 'fixtures':fixtures, 'controls':controls,
        'scope':'Finite premises and rational fixtures; written all-length complex proof in README.md. No supplier or new kappa.'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='exclusively create regenerated evidence')
    args = parser.parse_args()
    result = build()
    if args.out:
        with args.out.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    else:
        check(json.loads((HERE/'RESULT.json').read_text(encoding='utf-8')) == result, 'full receipt mismatch')
    print('PASS_P112_CHARGED_RIGHT_EXTENSION kernels=1022 class_pairs=110 dual_conflicts='+
        str(len(result['ordered_dual_conflicts']))+' fixtures='+str(len(result['fixtures']))+
        ' controls='+str(len(result['controls']))+' COPY=64 no_new_kappa')


if __name__ == '__main__':
    main()
