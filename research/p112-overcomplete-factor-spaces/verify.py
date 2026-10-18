#!/usr/bin/env python3
"""Exact finite premises and controls for the theorem in PROOF.md (stdlib only)."""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = 'research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json'
SOURCE_SHA = '327d2a868043e846381aa58a33053c24425e8cad522ff401b10ec8af1d649a3f'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def transpose(a):
    return [list(x) for x in zip(*a)]


def product(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in transpose(b)] for row in a]


def primitive(row):
    denominator = 1
    for x in row:
        if isinstance(x, Q):
            denominator = lcm(denominator, x.denominator)
    row = [int(x*denominator) for x in row]
    g = 0
    for x in row:
        g = gcd(g, x)
    if not g:
        return row
    g *= 1 if next(x for x in row if x) > 0 else -1
    return [x//g for x in row]


def echelon(rows, width):
    """Integer fraction-free elimination; retained rows span the exact Q row space."""
    basis = {}
    for original in rows:
        row = primitive(original)
        for p, b in sorted(basis.items()):
            if row[p]:
                c, d = row[p], b[p]
                row = primitive([d*x-c*y for x, y in zip(row, b)])
        p = next((j for j, x in enumerate(row) if x), None)
        if p is not None:
            basis[p] = primitive(row)
        if len(basis) == width:
            break
    return sorted(basis.items())


def rank(rows):
    return len(echelon(rows, len(rows[0]))) if rows else 0


def canonical(rows, width=9):
    b = [(p, list(map(Q, row))) for p, row in echelon(rows, width)]
    for i in range(len(b)-1, -1, -1):
        p, row = b[i]
        pivot = row[p]
        row[:] = [x/pivot for x in row]
        for _, previous in b[:i]:
            c = previous[p]
            previous[:] = [x-c*y for x, y in zip(previous, row)]
    return [row for _, row in b]


def kernel(rows, width):
    b = canonical(rows, width)
    pivots = [next(j for j, x in enumerate(row) if x) for row in b]
    result = []
    for free in sorted(set(range(width))-set(pivots)):
        v = [Q(0)]*width
        v[free] = Q(1)
        for p, row in zip(pivots, b):
            v[p] = -row[free]
        result.append(v)
    return result


def inverse(a):
    n = len(a)
    augmented = [list(map(Q, row))+[Q(i == j) for j in range(n)] for i, row in enumerate(a)]
    for p in range(n):
        k = next(i for i in range(p, n) if augmented[i][p])
        augmented[p], augmented[k] = augmented[k], augmented[p]
        c = augmented[p][p]
        augmented[p] = [x/c for x in augmented[p]]
        for i in range(n):
            if i != p:
                c = augmented[i][p]
                augmented[i] = [x-c*y for x, y in zip(augmented[i], augmented[p])]
    return [row[n:] for row in augmented]


def gf2_basis(values):
    basis = {}
    for value in values:
        while value:
            p = value.bit_length()-1
            if p in basis:
                value ^= basis[p]
            else:
                basis[p] = value
                break
    return [basis[p] for p in sorted(basis)]


def gf2_rank_low(values):
    """Independent elimination direction, also used on the unreduced support matrix."""
    rows = list(values)
    r = 0
    width = max((x.bit_length() for x in rows), default=0)
    for p in range(width):
        k = next((i for i in range(r, len(rows)) if (rows[i] >> p) & 1), None)
        if k is None:
            continue
        rows[r], rows[k] = rows[k], rows[r]
        for i in range(r+1, len(rows)):
            if (rows[i] >> p) & 1:
                rows[i] ^= rows[r]
        r += 1
    return r


def pairing_rows(left, right):
    return [sum(((a & b).bit_count() % 2) << j for j, b in enumerate(right)) for a in left]


def charge(d, t, labels):
    dl = [labels[i] for i, x in enumerate(d) if x != 0]
    tl = [labels[i] for i, x in enumerate(t) if x != 0]
    reduced = len(gf2_basis(pairing_rows(gf2_basis(dl), gf2_basis(tl))))
    direct = gf2_rank_low(pairing_rows(dl, tl))
    require(reduced == direct, 'binary rank algorithms disagree')
    return direct


def serial(value):
    if isinstance(value, Q):
        return int(value) if value.denominator == 1 else str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(x) for x in value]
    return value


def digest(value):
    return sha256(json.dumps(serial(value), sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def exact_factor_check(d, t, target, labels):
    require(product(d, transpose(t)) == target, 'all-entry factor identity failed')
    return [charge(a, b, labels) for a, b in zip(transpose(d), transpose(t))]


def majorizes(p, r):
    p, r = sorted(p, reverse=True), sorted(r, reverse=True)
    return sum(p) == sum(r) and all(sum(p[:i]) >= sum(r[:i]) for i in range(1, len(p)+1))


def reject(action, reason):
    try:
        action()
    except ValueError:
        return reason
    raise ValueError('negative control accepted: '+reason)


def build():
    raw = (ROOT/SOURCE).read_bytes()
    require(sha256(raw).hexdigest() == SOURCE_SHA, 'live prototype hash mismatch')
    src = json.loads(raw)
    roots, all_labels = src['root_lines'], src['binary_ports']
    require(roots[:8] == [[2*int(i == j) for j in range(8)] for i in range(8)], 'frame binding')
    x, labels, frame = roots[8:], all_labels[8:], all_labels[:8]
    require(len(x) == 112 and len(set(labels)) == 112, 'source dimensions')
    s, t = x[0], x[1]
    z = [0]*8+[1]
    l, v, u = s+[-4], s+[0], t+[-4]
    require(sum(a*a for a in s) == 4 and sum(a*b for a, b in zip(s, t)) == 2, 'projection pairings')
    require([j for j in range(8) if s[j]] == [j for j in range(8) if t[j]] == [1, 2, 4, 7], 'coordinate support')
    g = product(x, transpose(x))
    require(all(g[i][i] == 4 for i in range(112)), 'root norm')
    require(all(g[i][j] % 2 == 0 and ((g[i][j]//2+1) % 2) == ((labels[i]&labels[j]).bit_count()%2)
                for i in range(112) for j in range(112)), 'Gram/binary convention binding')
    left = [row+[int(i == 0)] for i, row in enumerate(x)]
    right = [([0]*8 if i == 0 else row)+[4*int(i == 0)+int(i == 1)] for i, row in enumerate(x)]
    target = [[g[i][j]-(g[i][0]-4*int(i == 0))*int(j == 0)+int(i == 0 and j == 1)
               for j in range(112)] for i in range(112)]
    require(rank(left) == rank(right) == 9 and product(left, transpose(right)) == target, 'rank-nine binding')
    require(all(target[i][j] == g[i][j] for i in range(112) for j in range(112)
                if ((labels[i]&labels[j]).bit_count()%2)), 'masked completion changed a required entry')

    # Complete support theorem: every nonzero binary annihilator is inspected.
    kernel_evidence = {}
    for side, matrix in [('left', left), ('right', right)]:
        found, unique, histogram = [], {}, Counter()
        for h in range(1, 512):
            rows = [row for row, lab in zip(matrix, labels) if (h & lab).bit_count()%2]
            got = canonical(kernel(rows, 9))
            if h in frame:
                r = frame.index(h)
                expected = [identity(9)[r]]+([z] if s[r] else [])
            elif h == labels[0]:
                expected = [l if side == 'left' else v]
            elif side == 'right' and h == labels[1]:
                expected = [u]
            elif (h&labels[0]).bit_count()%2 == 0 and (side == 'left' or (h&labels[1]).bit_count()%2 == 0):
                expected = [z]
            else:
                expected = []
            require(got == canonical(expected), f'{side} character {h}: kernel mismatch')
            require(all(sum(a*b for a, b in zip(row, vec)) == 0 for row in rows for vec in got), 'kernel residual')
            histogram[len(got)] += 1
            found.append([h, got])
            if got:
                unique[digest(got)] = got
        spaces = list(unique.values())
        require(len(spaces) == (10 if side == 'left' else 11), 'distinct character-kernel count')
        for i, a in enumerate(spaces):
            for b in spaces[i+1:]:
                intersection_dimension = len(a)+len(b)-rank(a+b)
                common_z = rank(a+[z]) == len(a) and rank(b+[z]) == len(b)
                require(intersection_dimension == int(common_z), 'unexpected character-kernel intersection')
        expected_hist = {0:251, 1:256, 2:4} if side == 'left' else {0:378, 1:129, 2:4}
        require(dict(histogram) == expected_hist, 'nullity histogram')
        kernel_evidence[side] = {'characters':511, 'nullity_histogram': dict(histogram),
                                'distinct_nonzero_kernels': len(spaces), 'kernels': sorted(serial(spaces), key=str),
                                'ordered_character_kernel_sha256': digest(found)}

    eclasses = {'E'+str(r): identity(9)[r] for r in range(8)}
    lc = {'Z':z, **eclasses, 'V':l, 'F':[2**j for j in range(9)]}
    rc = {'W':z, **eclasses, 'V':v, 'U':u, 'F':[2**j for j in range(9)]}
    physical_left = {name:[sum(a*b for a, b in zip(row, coeff)) for row in left] for name, coeff in lc.items()}
    physical_right = {name:[sum(a*b for a, b in zip(row, coeff)) for row in right] for name, coeff in rc.items()}
    span_dims = {}
    for side, columns, pure in [('left', physical_left, 'Z'), ('right', physical_right, 'W')]:
        span_dims[side] = {name:len(gf2_basis([labels[i] for i, value in enumerate(col) if value])) for name, col in columns.items()}
        for name, dim in span_dims[side].items():
            expected_dim = (1 if side == 'left' else 2) if name == pure else (9 if name == 'F' else 8)
            require(dim == expected_dim, 'class support dimension')
    table = {a:{b:charge(da, tb, labels) for b, tb in physical_right.items()} for a, da in physical_left.items()}
    for a in lc:
        for b in rc:
            r = table[a][b]
            require((r == 0) == (a == 'Z' and b == 'V'), 'zero-cost catalogue')
            if a != 'Z' and b != 'W':
                require(r >= 7 and (r != 7 or a == 'V' or b in ('V', 'U')), 'mixed cost catalogue')
            if a == 'Z' and b != 'V':
                require(r == 1, 'left-pure catalogue')
            if b == 'W':
                require(r == (1 if a in ('Z', 'V') else 2), 'right-pure catalogue')
    require(table['V']['V'] == 8, 'V/V charge')

    n = identity(9)
    for i in range(9):
        n[i][1] = v[i]
    m = transpose(inverse(n))
    require(product(m, transpose(n)) == identity(9), 'attainer coefficients')
    d, tt = product(left, m), product(right, n)
    attained = exact_factor_check(d, tt, target, labels)
    require(attained == [8, 7, 8, 8, 8, 8, 8, 8, 1], 'attaining profile')

    # Genuine overcomplete in-space fixture: two nonzero cancelling zero-COPY terms.
    mc, nc = transpose(m)+[z, [-a for a in z]], transpose(n)+[v, v]
    require(product(transpose(mc), nc) == identity(9), 'overcomplete coefficients')
    over_d, over_t = product(left, transpose(mc)), product(right, transpose(nc))
    over = exact_factor_check(over_d, over_t, target, labels)
    require(over == attained+[0, 0], 'zero-cost overcomplete fixture')
    require(sum(a*b for a, b in zip(mc[-1], nc[-1])) == 0, 'termwise duality control')

    # Boundary control: removing the right-space restriction admits a ten-term bill64.
    e, f = [int(i == 0) for i in range(112)], [int(i == 1) for i in range(112)]
    correction = [-g[i][0]+4*e[i] for i in range(112)]
    bd = transpose(transpose(x)+[correction, e])
    bt = transpose(transpose(x)+[e, f])
    boundary = exact_factor_check(bd, bt, target, labels)
    require(boundary == [8]*8+[0, 0], 'outside-space boundary profile')
    require(rank([a+[b] for a, b in zip(left, correction)]) == 9, 'boundary left-space membership')
    re, rf = rank([a+[b] for a, b in zip(right, e)]), rank([a+[b] for a, b in zip(right, f)])
    require(re == rf == 10, 'boundary factors must be outside right space')
    require(rank([a+b for a, b in zip(right, bt)]) == 10, 'one-dimensional right-space extension')

    p, two_sevens, many = [8]*7+[7, 1], [8]*6+[7, 7, 2], [8]+[7]*8
    require(majorizes(p, two_sevens) and majorizes(p, many), 'concavity integer partial sums')
    partials = lambda a: [sum(sorted(a, reverse=True)[:j]) for j in range(1, len(a)+1)]

    controls = []
    bad = [row[:] for row in d]
    bad[0][0] += 1
    controls.append(reject(lambda: exact_factor_check(bad, tt, target, labels), 'altered physical factor rejected'))
    missing = [row[:-1] for row in d]
    controls.append(reject(lambda: exact_factor_check(missing, [row[:-1] for row in tt], target, labels), 'omitted compensation rejected'))
    controls.append(reject(lambda: require(table['V']['V'] == 7, 'bad tariff'), 'V/V undercharge rejected'))
    controls.append(reject(lambda: require(sha256(raw+b' ').hexdigest() == SOURCE_SHA, 'bad hash'), 'source-byte mutation rejected'))
    bad_kernel = [row[:] for row in left]
    bad_kernel[0][8] += 1
    h = labels[0]
    controls.append(reject(lambda: require(canonical(kernel([row for row, lab in zip(bad_kernel, labels) if (h&lab).bit_count()%2], 9)) == canonical([l]), 'bad kernel'), 'changed character premise rejected'))
    # Exact Gaussian integer phases, with no floating-point tolerance.
    require(all(Q(value).denominator == 1 for row in d+tt for value in row), 'phase fixture uses integer coefficients')
    cd = [[complex(value) for value in row] for row in d]
    ct = [[complex(value) for value in row] for row in tt]
    for row in cd:
        row[0] *= 1j
    for row in ct:
        row[0] *= -1j
    require(exact_factor_check(cd, ct, target, labels) == attained, 'ordinary transpose phase fixture')
    controls.append(reject(lambda: exact_factor_check(cd, [[x.conjugate() for x in row] for row in ct], target, labels), 'Hermitian-transpose substitution rejected'))
    # Every Gaussian-integer value and sum here is below 2**53; complex arithmetic is exact.
    require(max(abs(x.real)+abs(x.imag) for row in cd+ct for x in row) < 100, 'phase exactness range')

    return serial({'schema_version':1, 'source_sha256':SOURCE_SHA, 'matrix':{'ports':112, 'rank_L':9, 'rank_R':9,
        's':s, 't':t, 's_dot_s':4, 's_dot_t':2, 'K_sha256':digest(target)},
        'character_kernels':kernel_evidence, 'support_span_dimensions':span_dims, 'pairing_ranks':table,
        'attainer':{'M':m, 'N':n, 'ranks':attained, 'COPY':sum(attained)},
        'overcomplete_in_space':{'terms':11, 'ranks':over, 'added_coefficient_pairs':[[z, v], [[-a for a in z], v]]},
        'outside_right_space':{'terms':10, 'ranks':boundary, 'rank_R_e':re, 'rank_R_f':rf, 'extended_right_space_rank':10},
        'majorization':{'P':p, 'two_cost7':two_sevens, 'many_mixed_surrogate':many,
                        'P_partials':partials(p), 'two_cost7_partials':partials(two_sevens), 'many_partials':partials(many)},
        'negative_controls':controls, 'positive_controls':['11-term zero-COPY cancellation', 'ordinary transpose nonreal phase', 'outside-right-space boundary']})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='create a new certificate exclusively; never overwrite')
    args = parser.parse_args()
    actual = build()
    if args.write:
        with args.write.open('x') as stream:
            json.dump(actual, stream, indent=2, sort_keys=True)
            stream.write('\n')
        print('WROTE_P112_OVERCOMPLETE_CERTIFICATE')
    else:
        expected = json.loads((HERE/'CERTIFICATE.json').read_text())
        require(actual == expected, 'certificate differs from exact recomputation')
        altered = json.loads(json.dumps(expected))
        altered['attainer']['ranks'][0] -= 1
        reject(lambda: require(actual == altered, 'altered certificate'), 'certificate undercharge rejected')
        print('PASS_P112_OVERCOMPLETE_FACTOR_SPACES kernels=1022 class_pairs=132 entries=12544 COPY=64 controls=7')


if __name__ == '__main__':
    main()
