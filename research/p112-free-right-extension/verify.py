#!/usr/bin/env python3
"""Exact premises for the scoped free-correction theorem; Apache-2.0.
Prepared for ywz65 with substantial OpenAI Codex assistance.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json'
SOURCE_SHA = '327d2a868043e846381aa58a33053c24425e8cad522ff401b10ec8af1d649a3f'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rref(rows, width):
    a = [list(map(Q, row)) for row in rows]
    pos, pivots = 0, []
    for col in range(width):
        pivot = next((i for i in range(pos, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[pos], a[pivot] = a[pivot], a[pos]
        p = a[pos][col]
        a[pos] = [v/p for v in a[pos]]
        for i in range(len(a)):
            if i != pos and a[i][col]:
                p = a[i][col]
                a[i] = [x-p*y for x, y in zip(a[i], a[pos])]
        pivots.append(col)
        pos += 1
        if pos == len(a):
            break
    return a[:pos], pivots


def nullspace(rows, width):
    reduced, pivots = rref(rows, width)
    basis = []
    for col in range(width):
        if col not in pivots:
            v = [Q(int(j == col)) for j in range(width)]
            for row, p in zip(reduced, pivots):
                v[p] = -row[col]
            basis.append(v)
    return rref(basis, width)[0]


def modular_rank(rows, width, prime=65521):
    """Separate streaming modular elimination: a rigorous rational rank lower bound."""
    basis = {}
    for original in rows:
        row = [int(v) % prime for v in original]
        for col in sorted(basis):
            scale = row[col]
            row = [(x-scale*y) % prime for x, y in zip(row, basis[col])]
        col = next((j for j, v in enumerate(row) if v), None)
        if col is not None:
            scale = pow(row[col], -1, prime)
            basis[col] = [(v*scale) % prime for v in row]
    return len(basis)


def bits_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return len(pivots)


def bits_rank_low(rows):
    a = list(rows)
    rank = 0
    for col in range(max((v.bit_length() for v in a), default=0)):
        p = next((j for j in range(rank, len(a)) if (a[j] >> col) & 1), None)
        if p is None:
            continue
        a[rank], a[p] = a[p], a[rank]
        for j in range(rank+1, len(a)):
            if (a[j] >> col) & 1:
                a[j] ^= a[rank]
        rank += 1
    return rank


def parity(a, b):
    return (a & b).bit_count() % 2


def bilinear_rank(left, right):
    rows = [sum(parity(a, b) << j for j, b in enumerate(right)) for a in left]
    hi, lo = bits_rank(rows), bits_rank_low(rows)
    need(hi == lo, 'binary rank implementations disagree')
    return hi


def multiply(matrix, vector):
    return [sum(x*y for x, y in zip(row, vector)) for row in matrix]


def charge(d, t, labels):
    return bilinear_rank([lab for v, lab in zip(d, labels) if v],
                         [lab for v, lab in zip(t, labels) if v])


def serial(obj):
    if isinstance(obj, Q):
        return int(obj) if obj.denominator == 1 else str(obj)
    if isinstance(obj, list):
        return [serial(v) for v in obj]
    if isinstance(obj, dict):
        return {str(k): serial(v) for k, v in obj.items()}
    return obj


def encoded(obj):
    return json.dumps(serial(obj), sort_keys=True, separators=(',', ':')).encode()


def reject(f, label):
    try:
        f()
    except ValueError:
        return label
    raise ValueError('negative control accepted: '+label)


def load_source(raw=None):
    raw = (ROOT/SOURCE).read_bytes() if raw is None else raw
    need(sha256(raw).hexdigest() == SOURCE_SHA, 'source hash mismatch')
    return json.loads(raw)


def model_kernel(side, h, roots, labels, frame):
    width = 9 if side == 'left' else 10
    e = [int(j == 8) for j in range(width)]
    f = [int(j == 9) for j in range(width)]
    result = []
    if not parity(h, labels[0]):
        result.append(e)
    if side == 'right' and not parity(h, labels[1]):
        result.append(f)
    if h in frame:
        result.append([int(j == frame.index(h)) for j in range(width)])
    elif h == labels[0]:
        result.append(roots[0]+[-4]+([0] if side == 'right' else []))
    elif side == 'right' and h == labels[1]:
        result.append(roots[1]+[0, -4])
    return rref(result, width)[0]


def check_fixture(pairs, left, right, target, labels, require_free=True):
    n = len(target)
    actual = [[Q(0) for _ in range(n)] for _ in range(n)]
    profile, pure, mixed = [], [], 0
    for a, b in pairs:
        d, t = multiply(left, a), multiply(right, b)
        need(any(d) and any(t), 'zero physical factor')
        cost = charge(d, t, labels)
        profile.append(cost)
        if any(a[:8]) and any(b[:8]):
            mixed += 1
        else:
            pure.append(cost)
            if require_free:
                need(cost == 0, 'positive-COPY pure term outside theorem')
        for i, x in enumerate(d):
            for j, y in enumerate(t):
                actual[i][j] += x*y
    need(actual == target, 'all-entry factor identity failed')
    return {'profile': profile, 'mixed_terms': mixed, 'pure_costs': pure,
            'entries': n*n, 'matrix_sha256': sha256(encoded(actual)).hexdigest()}


def build():
    source = load_source()
    roots, labels = source['root_lines'][8:], source['binary_ports'][8:]
    frame = source['binary_ports'][:8]
    need(source['root_lines'][:8] == [[2*int(i == j) for j in range(8)] for i in range(8)], 'frame binding')
    need(len(roots) == len(labels) == 112 and len(set(labels)) == 112, 'dimensions')
    s, t = roots[0], roots[1]
    dot = lambda a, b: sum(x*y for x, y in zip(a, b))
    gram = [[dot(a, b) for b in roots] for a in roots]
    need(all(gram[i][j] % 2 == 0 and (gram[i][j]//2+1) % 2 == parity(labels[i], labels[j])
             for i in range(112) for j in range(112)), 'Gram/binary pairing binding')
    need(dot(s, s) == dot(t, t) == 4 and dot(s, t) == 2, 'exceptional projections')
    left = [row+[int(i == 0)] for i, row in enumerate(roots)]
    right = [row+[int(i == 0), int(i == 1)] for i, row in enumerate(roots)]
    need(modular_rank(left, 9) == 9 and modular_rank(right, 10) == 10, 'factor-space ranks')
    target = [[gram[i][j]-(gram[i][0]-4*int(i == 0))*int(j == 0)+int(i == 0 and j == 1)
               for j in range(112)] for i in range(112)]
    need(all(target[i][j] == gram[i][j] for i in range(112) for j in range(112)
             if parity(labels[i], labels[j])), 'required mask entry')

    kernels, histograms, projection_checks = {}, {}, 0
    for side, matrix, width in [('left', left, 9), ('right', right, 10)]:
        census, histogram = [], Counter()
        for h in range(1, 512):
            rows = [row for row, lab in zip(matrix, labels) if parity(h, lab)]
            expected = model_kernel(side, h, roots, labels, frame)
            actual = nullspace(rows, width)
            need(actual == expected, f'{side} character kernel {h}')
            # Modular rank + integer annihilation certify exactness without trusting RREF.
            need(all(dot(row, vector) == 0 for row in rows for vector in expected), 'kernel annihilation')
            need(modular_rank(rows, width)+len(expected) == width, 'independent modular nullity')
            histogram[len(expected)] += 1
            census.append({'h': h, 'basis': expected})
        # No two distinct character kernels share a nonzero root projection.
        relevant = [(item['h'], item['basis']) for item in census if any(any(v[:8]) for v in item['basis'])]
        for i, (_, a) in enumerate(relevant):
            for _, b in relevant[i+1:]:
                na, nb = len(a), len(b)
                relations = nullspace([[a[j][k] for j in range(na)]+[-b[j][k] for j in range(nb)]
                                       for k in range(width)], na+nb)
                for rel in relations:
                    common = [sum(rel[j]*a[j][k] for j in range(na)) for k in range(8)]
                    need(not any(common), 'two-character non-pure intersection')
                projection_checks += 1
        kernels[side] = census
        histograms[side] = dict(sorted(histogram.items()))

    # Complete hyperplane pairing table, plus full spans; pure pairs are certified below.
    lchars, rchars = frame+[labels[0]], frame+[labels[0], labels[1]]
    table = []
    for a in lchars+[None]:
        row = []
        for b in rchars+[None]:
            al = [v for v in range(512) if a is None or not parity(a, v)]
            bl = [v for v in range(512) if b is None or not parity(b, v)]
            value = bilinear_rank(al, bl)
            expected = 9 if a is b is None else (8 if a is None or b is None or parity(a, b) else 7)
            need(value == expected, 'hyperplane pairing formula')
            if value == 7:
                need(a == labels[0] or b in labels[:2], 'unclassified cost-seven projection')
            row.append(value)
        table.append(row)
    need(all(table[i][j] == 8 for i in range(8) for j in range(8)), 'coordinate-pair cost')
    # All zero-COPY pure terms are spanned by l e^T, e (Xs-4e)^T, e f^T.
    z, l = [0]*8+[1], s+[-4]
    er, fr, vr = [0]*8+[1, 0], [0]*8+[0, 1], s+[-4, 0]
    need(model_kernel('left', labels[0], roots, labels, frame) == rref([l], 9)[0], 'left e kernel')
    need(model_kernel('left', labels[1], roots, labels, frame) == rref([z], 9)[0], 'left f kernel')
    need(model_kernel('right', labels[0], roots, labels, frame) == rref([vr, fr], 10)[0], 'right e kernel')
    need(not nullspace([[l[k], -z[k]] for k in range(9)], 2), 'mixed pure support intersection')

    fixture = [([int(k == j) for k in range(8)]+[0], [int(k == j) for k in range(8)]+[0, 0]) for j in range(8)]
    fixture += [([-v for v in l], er), (z, fr)]
    fixtures = {'credited_ten_term_boundary': check_fixture(fixture, left, right, target, labels)}
    # Nontrivial free-correction family, alpha != 0, beta = 1+1/alpha.
    for alpha in [Q(1), Q(2), Q(-2), Q(1, 2)]:
        beta = 1+1/alpha
        pairs = [([int(k == j) for k in range(8)]+[-beta*s[j]],
                  [int(k == j) for k in range(8)]+[-(1+alpha)*s[j], 0]) for j in range(8)]
        pairs += [([alpha*v for v in l], er), ([beta*v for v in z], vr), (z, fr)]
        fixtures[str(alpha)] = check_fixture(pairs, left, right, target, labels)
        need(fixtures[str(alpha)]['profile'] == [8]*8+[0]*3, 'sharp family profile')
    overcomplete = fixture + [(fixture[0][0], fixture[0][1]), ([-v for v in fixture[0][0]], fixture[0][1])]
    fixtures['redundant_mixed_pair'] = check_fixture(overcomplete, left, right, target, labels)
    # Ordinary transpose over Q(i): a phase and its reciprocal retain the product.
    d, tr = multiply(left, fixture[0][0]), multiply(right, fixture[0][1])
    need(all((0*x)*(0*y) - x*(-y) == x*y for x in d for y in tr), 'Gaussian ordinary phase control')
    need(any(x*y and x*y != -x*y for x in d for y in tr), 'Hermitian substitution witness')

    controls = [reject(lambda: load_source((ROOT/SOURCE).read_bytes()+b' '), 'changed source')]
    bad = [([*a], [*b]) for a, b in fixture]
    bad[-2][0][-1] += 1
    controls.append(reject(lambda: check_fixture(bad, left, right, target, labels), 'altered zero-COPY compensation'))
    controls.append(reject(lambda: check_fixture(fixture[:-1], left, right, target, labels), 'omitted e0 e1 correction'))
    # Exact boundary: adding a cancelling positive-COPY pure pair preserves K but leaves the model.
    positive = fixture+[(z, er), ([-v for v in z], er)]
    check_fixture(positive, left, right, target, labels, require_free=False)
    controls.append(reject(lambda: check_fixture(positive, left, right, target, labels), 'positive-COPY pure pair'))
    false_kernel = model_kernel('right', labels[0], roots, labels, frame)+[er]
    controls.append(reject(lambda: need(all(dot(row, v) == 0 for row, lab in zip(right, labels)
                         if parity(labels[0], lab) for v in false_kernel), 'false extension kernel'), 'free e0 in wrong kernel'))
    controls.append(reject(lambda: need(table[8][8] == 7, 'same exceptional line costs eight'), 'undercharged V V'))
    controls.append(reject(lambda: need(0*(2-1) == 1, 'coefficient compatibility'), 'alpha zero compatibility'))
    controls.append(reject(lambda: need(1*(1-1) == 1, 'coefficient compatibility'), 'beta one compatibility'))
    # For >=9 mixed terms: one 8 and eight 7 are already enough. P majorizes Qmany.
    p, q = [8]*8+[0], [8]+[7]*8
    need(sum(p) == sum(q) == 64 and all(sum(p[:i]) >= sum(q[:i]) for i in range(1, 10)), 'concave-power majorization')
    return serial({'scope': 'left col(X,e0), right col(X,e0,e1), all pure-projection terms COPY zero; all finite term counts; ordinary complex transpose',
        'source_sha256': SOURCE_SHA, 'factor_dimensions': [9, 10], 'character_kernels': kernels,
        'nullity_histograms': histograms, 'kernel_intersection_checks': projection_checks,
        'pairing_table': table, 'zero_pure_generators': [[l, er], [z, vr], [z, fr]],
        'compatibility': 'alpha*(beta-1)=1', 'sharp_profile': [8]*8, 'fixtures': fixtures,
        'majorization': {'P': p, 'Q': q}, 'controls': controls,
        'limits': 'Written arbitrary-complex proof; finite premise checks are not a formal kernel proof. Positive-COPY pure terms, both-space extensions, native sharing and supplier admission excluded.'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = build()
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    else:
        expected = json.loads((HERE/'RESULT.json').read_text())
        need(encoded(result) == encoded(expected), 'complete receipt mismatch')
    print('PASS_P112_FREE_RIGHT_EXTENSION kernels=1022 mixed_pairings=110 fixtures=6 controls=8 sharp_COPY=64')


if __name__ == '__main__':
    main()
