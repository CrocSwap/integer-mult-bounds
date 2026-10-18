#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite premises for the P112 nonzero-coefficient COPY theorem.
Prepared for commdata2338 with substantial OpenAI Codex assistance.
Support classification/duality method: Hanhong Zhao, PR2321 (credited).
No predecessor executable is imported.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json'
SOURCE_SHA = '327d2a868043e846381aa58a33053c24425e8cad522ff401b10ec8af1d649a3f'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def transpose(a):
    return list(map(list, zip(*a)))


def product(a, b):
    return [[dot(row, col) for col in transpose(b)] for row in a]


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def rref(a, width=9):
    a = [list(map(Q, row)) for row in a]
    pivots = []
    for c in range(width):
        r = len(pivots)
        p = next((i for i in range(r, len(a)) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        v = a[r][c]
        a[r] = [x/v for x in a[r]]
        for i in range(len(a)):
            if i != r and a[i][c]:
                v = a[i][c]
                a[i] = [x-v*y for x, y in zip(a[i], a[r])]
        pivots.append(c)
        if len(pivots) == len(a):
            break
    return a[:len(pivots)], pivots


def inverse(a):
    n = len(a)
    rows, pivots = rref([r+e for r, e in zip(a, identity(n))], n)
    require(pivots == list(range(n)), 'singular coefficient basis')
    return [r[n:] for r in rows]


def det_integer(a):
    """Bareiss with explicit exact-division checks."""
    a = [r[:] for r in a]
    if not a:
        return 1
    sign, previous = 1, 1
    for k in range(len(a)-1):
        p = next((i for i in range(k, len(a)) if a[i][k]), None)
        if p is None:
            return 0
        if p != k:
            a[p], a[k] = a[k], a[p]
            sign = -sign
        pivot = a[k][k]
        for i in range(k+1, len(a)):
            for j in range(k+1, len(a)):
                numerator = pivot*a[i][j]-a[i][k]*a[k][j]
                require(numerator % previous == 0, 'Bareiss nonexact division')
                a[i][j] = numerator//previous
            a[i][k] = 0
        previous = pivot
    return sign*a[-1][-1]


def minor_witness(a):
    """A finite field only proposes a minor; an INTEGER determinant certifies it."""
    p = 65521
    b = [[x % p for x in row] for row in a]
    ids = list(range(len(a)))
    rows, cols = [], []
    for c in range(len(a[0])):
        k = len(cols)
        selected = next((i for i in range(k, len(a)) if b[i][c]), None)
        if selected is None:
            continue
        b[k], b[selected] = b[selected], b[k]
        ids[k], ids[selected] = ids[selected], ids[k]
        rows.append(ids[k]); cols.append(c)
        scale = pow(b[k][c], -1, p)
        b[k] = [x*scale % p for x in b[k]]
        for i in range(k+1, len(a)):
            scale = b[i][c]
            if scale:
                b[i] = [(x-scale*y) % p for x, y in zip(b[i], b[k])]
    determinant = det_integer([[a[i][j] for j in cols] for i in rows])
    require(determinant != 0, 'zero lower-rank minor')
    return {'rows': rows, 'columns': cols, 'determinant': determinant}


def binary_rank(rows):
    basis = {}
    for value in rows:
        while value:
            p = value.bit_length()-1
            if p not in basis:
                basis[p] = value
                break
            value ^= basis[p]
    return len(basis)


def kernel_check(matrix, basis):
    require(all(dot(row, v) == 0 for row in matrix for v in basis),
            'kernel vector does not annihilate character rows')
    require(len(rref(basis)[0]) == len(basis), 'dependent kernel basis')
    minor = minor_witness(matrix)
    require(len(minor['columns'])+len(basis) == 9, 'kernel dimension gap')
    return minor


def canonical_space(vectors):
    return tuple(tuple(row) for row in rref(vectors)[0])


def support(matrix, vector):
    return [i for i, row in enumerate(matrix) if dot(row, vector)]


def copy_rank(pairing, left, right):
    return binary_rank([sum(pairing[i][j] << k for k, j in enumerate(right)) for i in left])


def serial(matrix):
    return [[str(x) for x in row] for row in matrix]


def factor_data(x, value):
    require(value != 0, 'coefficient must be nonzero')
    left = [r+[int(i == 0)] for i, r in enumerate(x)]
    right = [([0]*8 if i == 0 else r[:])+[4*int(i == 0)+value*int(i == 1)]
             for i, r in enumerate(x)]
    return left, right


def endpoint(x, value):
    return [[dot(a, b)-(dot(a, x[0])-4*int(i == 0))*int(j == 0)
             +value*int(i == 0 and j == 1) for j, b in enumerate(x)] for i, a in enumerate(x)]


def witness(x, pairing, n, value):
    left, right = factor_data(x, value)
    m = transpose(inverse(n))
    require(product(m, transpose(n)) == identity(9), 'coefficient duality')
    d, t = product(left, m), product(right, n)
    require(product(d, transpose(t)) == endpoint(x, value), 'complete endpoint identity')
    ranks = [copy_rank(pairing, [i for i in range(112) if d[i][k]],
                       [i for i in range(112) if t[i][k]]) for k in range(9)]
    return m, d, t, ranks


def coefficient_transport(x, right_constant=4):
    """Coefficients of lambda R_lambda = diag(1,lambda,...)*R_1*D_lambda."""
    _, base = factor_data(x, 1)
    for i in range(112):
        for k in range(9):
            lhs = [0, 0, 0]
            lhs[1] = (0 if i == 0 else x[i][k]) if k < 8 else right_constant*int(i == 0)
            if k == 8:
                lhs[2] = int(i == 1)
            rhs = [0, 0, 0]
            rhs[int(i != 0)+int(k == 8)] = base[i][k]
            require(lhs == rhs, 'symbolic coefficient transport')


def rejection(fn, reason):
    try:
        fn()
    except ValueError as exc:
        require(str(exc) == reason, 'wrong rejection reason: '+str(exc))
    else:
        raise ValueError('negative control accepted: '+reason)


def compute(data):
    roots, ports = data['root_lines'], data['binary_ports']
    require(len(roots) == len(ports) == 120, 'root/label count')
    require(all(type(v) is int for row in roots for v in row)
            and all(type(v) is int for v in ports), 'integer root/label schema')
    x, labels, frame = roots[8:], ports[8:], ports[:8]
    require(all(len(r) == 8 for r in roots), 'root width')
    require(product(transpose(x), x) == [[56*a for a in r] for r in identity(8)],
            'root tight-frame identity')
    gram = [[dot(a, b) for b in x] for a in x]
    require(all(gram[i][i] == 4 for i in range(112)), 'root norm')
    pairing = [[(g//2+1) % 2 for g in row] for row in gram]
    require(all(g % 2 == 0 for row in gram for g in row), 'integral pairing')
    require(all(pairing[i][j] == ((labels[i] & labels[j]).bit_count() % 2)
                for i in range(112) for j in range(112)), 'binary label binding')
    s, t = x[:2]
    require(dot(s, t) == 2 and [bool(v) for v in s] == [bool(v) for v in t],
            'fixed port-pair geometry')
    require(all(gram[i][j] in (0, -2, 2) for i in range(112) for j in range(112) if i != j),
            'off-diagonal mask geometry')
    k0 = endpoint(x, 0)
    require(all(k0[i][j] == gram[i][j] and not (i == 0 and j == 1)
                for i in range(112) for j in range(112) if pairing[i][j]),
            'coefficient-family mask')
    require(sum(k0[i][0] != gram[i][0] for i in range(112)) == 52,
            'first correction column support')
    left, right = factor_data(x, 1)
    require(len(minor_witness(left)['columns']) == 9
            and len(minor_witness(right)['columns']) == 9, 'rank-nine factor spaces')
    z = [0]*8+[1]
    lv, rv, ru = s+[-4], s+[0], t+[-4]
    records, histograms = {}, {}
    for name, matrix in (('L', left), ('R1', right)):
        records[name] = []
        groups = set()
        for h in range(1, 512):
            basis = []
            if h in frame:
                p = frame.index(h)
                basis = [identity(9)[p]]
                if s[p]:
                    basis.append(z)
            elif h == labels[0]:
                basis = [lv if name == 'L' else rv]
            elif name == 'R1' and h == labels[1]:
                basis = [ru]
            elif not ((h & labels[0]).bit_count() % 2) and (
                    name == 'L' or not ((h & labels[1]).bit_count() % 2)):
                basis = [z]
            ids = [i for i, label in enumerate(labels) if (h & label).bit_count() % 2]
            minor = kernel_check([matrix[i] for i in ids], basis)
            minor['rows'] = [ids[i] for i in minor['rows']]
            records[name].append({'character': h, 'kernel': basis, 'minor': minor})
            if basis:
                groups.add(canonical_space(basis))
        for a, b in combinations(sorted(groups), 2):
            intersection = len(a)+len(b)-len(rref(list(a)+list(b))[0])
            if intersection:
                require(intersection == 1 and canonical_space(list(a)+[z]) == a
                        and canonical_space(list(b)+[z]) == b, 'non-pure kernel intersection')
        histograms[name] = dict(sorted(Counter(len(r['kernel']) for r in records[name]).items()))
    require(histograms == {'L': {0: 251, 1: 256, 2: 4}, 'R1': {0: 378, 1: 129, 2: 4}},
            'kernel histogram')
    coefficient_transport(x)
    lclasses = {'Z': z, **{'E'+str(k): identity(9)[k] for k in range(8)},
                'V': lv, 'F': [2**k for k in range(9)]}
    rclasses = {'W': z, **{'E'+str(k): identity(9)[k] for k in range(8)},
                'V': rv, 'U': ru, 'F': [2**k for k in range(9)]}
    ls = {k: support(left, v) for k, v in lclasses.items()}
    rs = {k: support(right, v) for k, v in rclasses.items()}
    ld = {k: binary_rank([labels[i] for i in ids]) for k, ids in ls.items()}
    rd = {k: binary_rank([labels[i] for i in ids]) for k, ids in rs.items()}
    require(ld == {k: 1 if k == 'Z' else 9 if k == 'F' else 8 for k in ls}, 'left support dimensions')
    require(rd == {k: 2 if k == 'W' else 9 if k == 'F' else 8 for k in rs}, 'right support dimensions')
    table = {a: {b: copy_rank(pairing, ls[a], rs[b]) for b in rs} for a in ls}
    require([(a, b) for a in ls for b in rs if table[a][b] == 0] == [('Z', 'V')],
            'unique zero-cost pair')
    for a in ls:
        for b in rs:
            if a != 'Z' and b != 'W':
                require(table[a][b] >= 7, 'mixed rank floor')
                require(table[a][b] != 7 or a == 'V' or b in ('V', 'U'), 'rank-seven classes')
    require(table['V']['V'] == 8, 'V/V costs eight')
    require(all(table['Z'][b] == 1 for b in rs if b != 'V'), 'left pure cost')
    require(all(table[a]['W'] == (1 if a in ('Z', 'V') else 2) for a in ls), 'right pure cost')

    # N is independent of lambda. Only its pure last physical factor changes.
    p = next(i for i, v in enumerate(s) if v)
    n = identity(9)
    for i in range(9):
        n[i][p] = rv[i]
    m, d, tout, ranks = witness(x, pairing, n, Q(1))
    require(sorted(ranks) == [1, 7]+[8]*7, 'uniform attainer profile')
    r0 = [([0]*8 if i == 0 else row[:])+[4*int(i == 0)] for i, row in enumerate(x)]
    r1 = [[0]*8+[int(i == 1)] for i in range(112)]
    t0, t1 = product(r0, n), product(r1, n)
    require(product(d, transpose(t0)) == endpoint(x, 0), 'constant endpoint coefficient')
    require(product(d, transpose(t1)) == [[int(i == 0 and j == 1) for j in range(112)]
                                         for i in range(112)], 'linear endpoint coefficient')
    require(all(t1[i][k] == 0 for i in range(112) for k in range(8)), 'fixed mixed attainer supports')
    require([t0[i][8] for i in range(112)] == [4]+[0]*111
            and [t1[i][8] for i in range(112)] == [0, 1]+[0]*110, 'uniform pure attainer support')

    # A valid exceptional dual basis refutes the stale generic exclusion.
    ep = next(i for i, v in enumerate(t) if v)
    en = [[Q(v) for v in row] for row in identity(9)]
    for i in range(8):
        en[i][ep] = Q(t[i])
    for k in range(8):
        en[8][k] = dot(s, [en[i][k] for i in range(8)])/4
    en[8][8] = Q(-1, 4)
    em, ed, et, eranks = witness(x, pairing, en, Q(-8))
    require([em[i][8] for i in range(9)] == lv, 'exceptional left V compensation')
    require([en[i][ep] for i in range(9)] == t+[Q(1, 2)], 'exceptional right U mixed column')
    require(dot(lv, t+[Q(1, 2)]) == 0, 'exceptional orthogonality')
    require(sorted(eranks) == [1, 7]+[8]*7, 'exceptional attainer profile')
    require(dot(s, t) == 2 and lv[8]*(-4) == 16 and dot(lv, rv) == 4
            and dot(z, rv) == 0, 'symbolic duality coefficients')
    profiles = {'nine_mixed': [8]*7+[7, 7], 'left_pure': [8]*7+[7, 1],
                'right_pure_left_V_generic': [8]*8+[1],
                'right_pure_left_V_exceptional': [8]*7+[7, 1],
                'right_pure_other': [8]*6+[7, 7, 2]}
    sharp = [8]*7+[7, 1]
    for name, profile in profiles.items():
        if name == 'right_pure_other':
            require(sum(profile) == sum(sharp) == 64, 'majorization equal mass')
            require(all(sum(sorted(profile, reverse=True)[:k]) <= sum(sharp[:k])
                        for k in range(1, 10)), 'concave-power majorization')
        else:
            require(all(a >= b for a, b in zip(sorted(profile), sorted(sharp))), 'case profile dominance')

    controls = []
    rejection(lambda: factor_data(x, 0), 'coefficient must be nonzero')
    controls.append('zero_coefficient_outside_support_transport')
    rejection(lambda: coefficient_transport(x, 5), 'symbolic coefficient transport')
    controls.append('wrong_anchor_in_symbolic_transport')
    ids = [i for i, v in enumerate(labels) if (labels[0] & v).bit_count() % 2]
    rejection(lambda: kernel_check([right[i] for i in ids], [lv]),
              'kernel vector does not annihilate character rows')
    controls.append('left_kernel_in_right_space')
    bad = [row[:] for row in n]; bad[8][8] = 0
    rejection(lambda: inverse(bad), 'singular coefficient basis')
    controls.append('missing_compensation_basis')
    require(dot(d[0][:8], tout[0][:8]) != endpoint(x, 1)[0][0], 'omission control')
    controls.append('omitted_pure_factor_breaks_endpoint')
    # Multiplying a D column by i and its T column by -i preserves ordinary
    # products. Hermitian transpose instead negates that nonzero rank-one term.
    column = next(k for k in range(9) if any(row[k] for row in d) and any(row[k] for row in tout))
    oi = next(i for i in range(112) if d[i][column])
    oj = next(i for i in range(112) if tout[i][column])
    require(-2*d[oi][column]*tout[oj][column] != 0, 'ordinary/Hermitian distinction')
    controls.append('exact_nonreal_phase_rejects_Hermitian_transpose')
    require(dot(lv, t+[-4]) != 0 and dot(lv, t+[Q(1, 2)]) == 0, 'stale generic exclusion control')
    controls.append('exceptional_valid_basis_refutes_generic_U_exclusion')
    require(dot(z, rv) == 0, 'zero-cost pair cannot be dual')
    controls.append('zero_cost_pair_fails_diagonal_duality')
    return {'schema_version': 1, 'source_sha256': SOURCE_SHA,
            'scope': 'fixed P112 (0,1), lambda in C*, nine ordinary-transpose terms, separate COPY',
            'sharp_power': '7*8^q+7^q+1 for every 0<q<=1', 'exceptional_lambda': -8,
            'kernel_histograms': histograms, 'kernels': records, 'pairing_table': table,
            'uniform_attainer': {'N': serial(n), 'M': serial(m), 'ranks': ranks},
            'exceptional_attainer': {'N': serial(en), 'M': serial(em), 'ranks': eranks,
                                     'mixed_U_index': ep, 'pure_W_index': 8},
            'case_lower_profiles': profiles, 'controls': controls, 'polynomial_endpoint_entries': 25088}


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'), allow_nan=False)


def strict_json(path):
    def pairs(items):
        out = {}
        for k, v in items:
            require(k not in out, 'duplicate JSON key')
            out[k] = v
        return out
    def invalid(value):
        raise ValueError('nonfinite JSON number')
    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_constant=invalid)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='create a new receipt exclusively')
    args = parser.parse_args()
    if args.write:
        require(not args.write.exists(), 'output exists')
    raw = (ROOT/SOURCE).read_bytes()
    require(sha256(raw).hexdigest() == SOURCE_SHA, 'source digest mismatch')
    receipt = compute(json.loads(raw))
    encoded = canonical(receipt)
    if args.write:
        with args.write.open('x') as stream:
            stream.write(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    else:
        require(canonical(strict_json(HERE/'CERTIFICATE.json')) == encoded, 'certificate mismatch')
    print('PASS_P112_COEFFICIENT_COPY_FLOOR kernels=1022 lambda=nonzero_complex '
          'exception=-8 copy_sum=64 controls=8 no_new_kappa')
    print('receipt_sha256='+sha256(encoded.encode()).hexdigest())


if __name__ == '__main__':
    main()
