"""Exact finite corroboration of orthogonal Schur dilation rigidity."""

import hashlib
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from matrix import (
    add, basis, block, diag, eye, householder, inv, matrix, mul,
    orthoproject, psd, rank, require, rref, schur, tr, zero,
)

SECTORS = ((0, 0), (1, 0), (0, 1), (1, 1))


def sectors(p, q):
    ident = eye(len(p))
    pq = mul(p, q)
    return (add(add(add(ident, p, -1), q, -1), pq),
            add(p, pq, -1), add(q, pq, -1), pq)


def premises(p, q, d):
    n = len(p)
    require(1 <= d < n <= 14, "fixture dimensions")
    require(len(p[0]) == n and len(q) == len(q[0]) == n, "square shape")
    for a in (p, q):
        require(a == tr(a), "self-adjointness")
        require(mul(a, a) == a, "idempotence")
        require(rank(block(a, range(d), range(d))) == d, "invertible pivot")
    require(mul(p, q) == mul(q, p), "commutation")


def data(p, q, d):
    premises(p, q, d)
    es = sectors(p, q)
    ys = tuple(block(e, range(len(p)), range(d)) for e in es)
    ts = tuple(block(e, range(d), range(d)) for e in es)
    cs = tuple(orthoproject(y) for y in ys)
    for y, t, c in zip(ys, ts, cs, strict=True):
        require(mul(tr(y), y) == t and psd(t), "positive Gram effect")
        require(rank(c) == rank(t), "core sector dimension")
    return es, ys, ts, cs


def concatenate(parts):
    return matrix([sum((part[i] for part in parts), ())
                   for i in range(len(parts[0]))])


def lifted_schur(p, d):
    n = len(p)
    first = range(d)
    correction = mul(mul(block(p, range(n), first),
                         inv(block(p, first, first))), block(p, first, range(n)))
    return add(p, correction, -1)


def verify_decomposition(p, q, d):
    es, _, ts, cs = data(p, q, d)
    n = len(p)
    core = zero(n, n)
    for c in cs:
        core = add(core, c)
    observed = diag([int(i < d) for i in range(n)])
    require(mul(core, observed) == observed, "core contains observed space")
    require(mul(core, core) == core, "orthogonal core projection")
    require(rank(core) == sum(rank(t) for t in ts), "minimum core dimension")
    w = basis(add(core, observed, -1))
    ks = tuple(basis(add(e, c, -1)) for e, c in zip(es, cs, strict=True))
    change = block(concatenate((w,) + ks), range(d, n), range(n - d))
    change_inv = inv(change)
    core_size = len(w[0])
    iota = block(eye(n), range(n), range(d))
    core_basis = concatenate((iota, w))
    left = mul(inv(mul(tr(core_basis), core_basis)), tr(core_basis))
    for index, original in enumerate((p, q)):
        require(mul(original, core) == mul(core, original), "reducing core")
        residual = schur(original, d)
        lift = lifted_schur(original, d)
        require(lift == tr(lift) and mul(lift, lift) == lift, "Schur projection")
        expected = [list(row) for row in zero(n - d, n - d)]
        if core_size:
            small = schur(mul(mul(left, original), core_basis), d)
            for r in range(core_size):
                for c in range(core_size):
                    expected[r][c] = small[r][c]
        offset = core_size
        for label, k in zip(SECTORS, ks, strict=True):
            for r in range(len(k[0])):
                expected[offset + r][offset + r] = label[index]
            offset += len(k[0])
        require(offset == n - d, "complete residual decomposition")
        require(mul(mul(change_inv, residual), change) == matrix(expected),
                "literal ordered residual decomposition")
    comm = add(mul(schur(p, d), schur(q, d)), mul(schur(q, d), schur(p, d)), -1)
    require(rank(comm) % 2 == 0, "orthogonal commutator even rank")
    return ts, rank(comm)


def generated_pair(profile, seed):
    n = sum(profile)
    v = [i + 1 for i in range(n)]
    rotation = householder(v)
    if seed:
        w = [((3 * i + seed) % 7) - 3 for i in range(n)]
        rotation = mul(rotation, householder(w))
    labels = tuple(label for label, count in zip(SECTORS, profile, strict=True)
                   for _ in range(count))
    return tuple(mul(mul(tr(rotation), diag([label[j] for label in labels])), rotation)
                 for j in range(2))


def padded_pair(p, q, d, label):
    n = len(p)
    tail = householder([i + 1 for i in range(n + 1 - d)])
    rotation = [list(row) for row in eye(n + 1)]
    for i in range(n + 1 - d):
        for j in range(n + 1 - d):
            rotation[d + i][d + j] = tail[i][j]
    rotation = matrix(rotation)
    result = []
    for index, a in enumerate((p, q)):
        extended = matrix([list(row) + [0] for row in a] + [[0] * n + [label[index]]])
        result.append(mul(mul(tr(rotation), extended), rotation))
    return tuple(result)


def verify_core_isometry(p, q, p2, q2, d):
    _, ys, ts, cs = data(p, q, d)
    _, zs, us, ds = data(p2, q2, d)
    require(ts == us, "same prescribed effects")
    mapping = zero(len(p2), len(p))
    core, core2 = zero(len(p), len(p)), zero(len(p2), len(p2))
    for y, z, c, e in zip(ys, zs, cs, ds, strict=True):
        pivots = rref(y)[1]
        if pivots:
            b = matrix([[row[j] for j in pivots] for row in y])
            b2 = matrix([[row[j] for j in pivots] for row in z])
            local = mul(mul(b2, inv(mul(tr(b), b))), tr(b))
            require(mul(local, y) == z, "Gram isometry maps all observed columns")
            mapping = add(mapping, local)
        core, core2 = add(core, c), add(core2, e)
    require(mul(tr(mapping), mapping) == core, "initial core isometry")
    require(mul(mapping, tr(mapping)) == core2, "final core isometry")
    iota = block(eye(len(p)), range(len(p)), range(d))
    iota2 = block(eye(len(p2)), range(len(p2)), range(d))
    require(mul(mapping, iota) == iota2, "isometry fixes retained coordinates")
    for a, b in ((p, p2), (q, q2)):
        require(mul(mapping, a) == mul(b, mapping), "original pair intertwining")
        require(mul(mapping, lifted_schur(a, d)) == mul(lifted_schur(b, d), mapping),
                "Schur pair intertwining")


def scalar_check(p, q, ts):
    a = ts[1][0][0] + ts[3][0][0]
    b = ts[2][0][0] + ts[3][0][0]
    h = ts[3][0][0]
    c = (a - h) * (b - h) / (a * b)
    s, z = schur(p, 1), schur(q, 1)
    k = add(mul(s, z), mul(z, s), -1)
    norm_squared = -sum(mul(k, k)[i][i] for i in range(len(k))) / 2
    require(norm_squared == c * (1 - c), "scalar norm formula")
    require(rank(k) == (2 if 0 < h < min(a, b) else 0), "scalar rank formula")
    return norm_squared


def fixtures():
    for n in range(2, 5):
        for profile in itertools.product(range(n + 1), repeat=4):
            if sum(profile) == n:
                for seed in range(2):
                    for d in range(1, min(2, n - 1) + 1):
                        yield profile, seed, d
    for n in (5, 6, 7):
        for profile in ((0, 2, 2, n - 4), (1, 1, 2, n - 4), (n - 3, 1, 1, 1)):
            for d in (1, 2, 3):
                yield profile, 2, d


def rejection_controls(p, q):
    rejected = 0
    for mode in range(6):
        a, b, d = p, q, 1
        if mode == 0:
            a = add(a, eye(len(a)))
        elif mode == 1:
            rows = [list(row) for row in a]
            rows[0][1] += 1
            a = matrix(rows)
        elif mode == 2:
            b = diag([1] + [0] * (len(a) - 1))
        elif mode == 3:
            a = zero(len(a), len(a))
        elif mode == 4:
            d = 0
        else:
            d = len(a)
        try:
            premises(a, b, d)
        except ValueError:
            rejected += 1
    require(rejected == 6, "hypothesis controls")
    require(not psd(matrix([[0, 1], [1, 0]])), "indefinite zero-diagonal control")
    require(not psd(matrix([[-1, 0], [0, 1]])), "negative-effect control")
    return rejected + 2


def run():
    counts = dict(candidates=0, admitted=0, singular_pivots=0, scalar=0, padded=0)
    histogram = {}
    padding_seeds = []
    by_size = {1: 0, 2: 0, 3: 0}
    for profile, seed, d in fixtures():
        counts['candidates'] += 1
        p, q = generated_pair(profile, seed)
        if any(rank(block(a, range(d), range(d))) < d for a in (p, q)):
            counts['singular_pivots'] += 1
            continue
        ts, r = verify_decomposition(p, q, d)
        counts['admitted'] += 1
        histogram[str(r)] = histogram.get(str(r), 0) + 1
        if d == 1:
            scalar_check(p, q, ts)
            counts['scalar'] += 1
        if by_size[d] < 3 and r:
            padding_seeds.append((p, q, d))
            by_size[d] += 1
    for p, q, d in padding_seeds:
        for label in SECTORS:
            p2, q2 = padded_pair(p, q, d, label)
            verify_decomposition(p2, q2, d)
            verify_core_isometry(p, q, p2, q2, d)
            counts['padded'] += 1
    v = [F(1, 3)] * 3 + [F(1, 2)] * 2 + [F(1, 3), F(1, 6), F(1, 6)]
    rotation = householder([int(i == 0) - x for i, x in enumerate(v)])
    labels = [(1, 0)] * 3 + [(0, 1)] * 2 + [(1, 1)] * 3
    p, q = tuple(mul(mul(tr(rotation), diag([x[j] for x in labels])), rotation)
                 for j in range(2))
    ts, r = verify_decomposition(p, q, 1)
    require(tuple(t[0][0] for t in ts) == (0, F(1, 3), F(1, 2), F(1, 6)),
            "half-norm fixture effects")
    require(r == 2 and scalar_check(p, q, ts) == F(1, 4), "attained half norm")
    counts['controls'] = rejection_controls(p, q)
    counts['rank_histogram'] = histogram
    counts['padding_seed_pivot_sizes'] = by_size
    counts['half_norm_fixture_core_dimension'] = sum(rank(t) for t in ts)
    require(tuple(counts[k] for k in ('candidates', 'admitted', 'singular_pivots',
                                      'scalar', 'padded')) == (267, 137, 130, 93, 32),
            "fixture coverage")
    require(histogram == {'0': 110, '2': 25, '4': 2}, "rank coverage")
    return counts


if __name__ == '__main__':
    result = run()
    root = Path(__file__).resolve().parent
    names = ('README.md', 'PROOF.md', 'matrix.py', 'verify.py',
             'TASK.json', 'SOURCES.json', 'VERIFY.json')
    result['source_sha256'] = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names
    }
    result['status'] = 'PASS_ORTHOGONAL_SCHUR_RIGIDITY'
    print(json.dumps(result, sort_keys=True))
