#!/usr/bin/env python3
"""Exact finite corroboration of the block-solve downset envelope."""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from math import lcm
import json
from pathlib import Path

MAX_N = 5
MAX_REAL = 10
MAX_TREES = 16
MAX_STATES = 256
FILES = ('README.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def zeros(rows, cols):
    require(0 <= rows <= MAX_REAL and 0 <= cols <= MAX_REAL, 'matrix capacity')
    return [[F(0) for _ in range(cols)] for _ in range(rows)]


def eye(n):
    out = zeros(n, n)
    for i in range(n):
        out[i][i] = F(1)
    return out


def transpose(a):
    return [list(row) for row in zip(*a)]


def mul(a, b):
    require(bool(a) and bool(b) and len(a[0]) == len(b), 'product shape')
    out = zeros(len(a), len(b[0]))
    columns = list(zip(*b))
    row_scale = [lcm(*(x.denominator for x in row)) for row in a]
    col_scale = [lcm(*(x.denominator for x in col)) for col in columns]
    left = [[x.numerator * (scale // x.denominator) for x in row]
            for row, scale in zip(a, row_scale)]
    right = [[x.numerator * (scale // x.denominator) for x in col]
             for col, scale in zip(columns, col_scale)]
    for i, row in enumerate(left):
        for j, col in enumerate(right):
            out[i][j] = F(sum(x*y for x, y in zip(row, col)), row_scale[i]*col_scale[j])
    return out


def sub(a, b):
    require(len(a) == len(b) and len(a[0]) == len(b[0]), 'difference shape')
    return [[x - y for x, y in zip(r, s)] for r, s in zip(a, b)]


def block(a, r0, r1, c0, c1):
    return [row[c0:c1] for row in a[r0:r1]]


def put(a, r0, c0, b):
    for i, row in enumerate(b):
        for j, value in enumerate(row):
            a[r0 + i][c0 + j] = value


def inv(a):
    n = len(a)
    require(1 <= n <= MAX_REAL and all(len(r) == n for r in a), 'inverse shape')
    out = eye(n)
    work = [r[:] for r in a]
    for k in range(n):
        pivot = next((i for i in range(k, n) if work[i][k]), None)
        require(pivot is not None, 'singular matrix')
        work[k], work[pivot] = work[pivot], work[k]
        out[k], out[pivot] = out[pivot], out[k]
        scale = work[k][k]
        work[k] = [x / scale for x in work[k]]
        out[k] = [x / scale for x in out[k]]
        for i in range(n):
            if i != k:
                scale = work[i][k]
                work[i] = [x - scale * y for x, y in zip(work[i], work[k])]
                out[i] = [x - scale * y for x, y in zip(out[i], out[k])]
    require(mul(a, out) == eye(n) and mul(out, a) == eye(n), 'inverse residual')
    return out


def psd(a):
    n = len(a)
    require(a == transpose(a), 'PSD symmetry')
    work = [r[:] for r in a]
    for k in range(n):
        pivot = work[k][k]
        if pivot < 0:
            return False
        if pivot == 0:
            if any(work[i][k] for i in range(k + 1, n)):
                return False
        else:
            for i in range(k + 1, n):
                for j in range(k + 1, n):
                    work[i][j] -= work[i][k] * work[k][j] / pivot
    return True


def norm_squared_at_most(a, bound):
    require(bound >= 0 and bool(a) and bool(a[0]), 'norm contract')
    # Use the smaller Gram matrix without changing its nonzero spectrum.
    gram = mul(a, transpose(a)) if len(a) <= len(a[0]) else mul(transpose(a), a)
    return psd(sub([[bound * x for x in r] for r in eye(len(gram))], gram))


def envelope(a):
    return max(F(1), max(sum(map(abs, r)) for r in a),
               max(sum(map(abs, r)) for r in transpose(a)))


def fixture(n, width):
    size = n * width
    lower, upper, diagonal = eye(size), eye(size), zeros(size, size)
    for i in range(n):
        pivot = [[F(i + 2, i + 1)]] if width == 1 else [
            [F(i + 2, i + 1), F(-1, i + 2)],
            [F(1, i + 2), F(i + 2, i + 1)]]
        put(diagonal, width * i, width * i, pivot)
        for j in range(i):
            real, imag = F((-1) ** (i + j), 3 + i + j), F(1, 4 + i + j)
            lo = [[real]] if width == 1 else [[real, -imag], [imag, real]]
            up = [[-2 * real]] if width == 1 else [
                [-2 * real, imag], [-imag, -2 * real]]
            put(lower, width * i, width * j, lo)
            put(upper, width * j, width * i, up)
    return mul(mul(lower, diagonal), upper)


def schur(t, a, b):
    out = block(t, a, b, a, b)
    if a:
        out = sub(out, mul(mul(block(t, a, b, 0, a),
                               inv(block(t, 0, a, 0, a))), block(t, 0, a, a, b)))
    return out


def unit_upper(t, width):
    size = len(t)
    out = eye(size)
    for end in range(width, size, width):
        solve = mul(inv(block(t, 0, end, 0, end)), block(t, 0, end, end, size))
        put(out, end - width, end, block(solve, end - width, end, 0, size - end))
    return out


def interval_trees(n):
    # Each record is (start, end, split); split=0 denotes a leaf.
    require(1 <= n <= MAX_N, 'logical dimension capacity')
    levels = {1: [((0, 1, 0),)]}
    for size in range(2, n + 1):
        shapes = []
        for cut in range(1, size):
            for left, right in product(levels[cut], levels[size - cut]):
                shifted = tuple((a + cut, b + cut, s + cut if s else 0)
                                for a, b, s in right)
                shapes.append(left + shifted + ((0, size, cut),))
        require(len(shapes) <= MAX_TREES, 'tree capacity')
        levels[size] = shapes
    return levels[n]


def program(t, tree, width):
    size = len(t)
    info, atoms = {}, []
    for a, b, split in tree:
        x, y = width * a, width * b
        matrix = schur(t, x, y)
        if not split:
            atom = eye(size)
            put(atom, x, x, matrix)
            number = len(atoms)
            atoms.append(atom)
            info[a, b] = {'mask': 1 << number, 'states': [0, 1 << number],
                          'order': [number], 'split': 0}
            continue
        mid = width * split
        pivot = inv(block(matrix, 0, mid - x, 0, mid - x))
        upper, lower = eye(size), eye(size)
        put(upper, x, mid, mul(pivot, block(matrix, 0, mid - x, mid - x, y - x)))
        put(lower, mid, x, mul(block(matrix, mid - x, y - x, 0, mid - x), pivot))
        up, low = len(atoms), len(atoms) + 1
        atoms.extend((upper, lower))
        left, right = info[a, split], info[split, b]
        full = (1 << up) | (1 << low) | left['mask'] | right['mask']
        states = [0] + [(1 << up) | l | r for l, r in
                        product(left['states'], right['states'])] + [full]
        require(len(states) <= MAX_STATES and len(set(states)) == len(states),
                'state capacity or uniqueness')
        info[a, b] = {'mask': full, 'states': states, 'split': split,
                      'order': [up] + left['order'] + right['order'] + [low]}
    return info, atoms


def partition(info, n, state):
    pending, out = [(0, n)], []
    for _ in range(2 * n - 1):
        if not pending:
            break
        a, b = pending.pop()
        node = info[a, b]
        selected = state & node['mask']
        if selected in (0, node['mask']):
            out.append((a, b, selected != 0))
        else:
            split = node['split']
            require(a < split < b, 'partial leaf')
            pending.extend(((split, b), (a, split)))
    require(not pending, 'partition capacity')
    validate_partition(out, n)
    return out


def validate_partition(parts, n):
    require(1 <= len(parts) <= n, 'partition count')
    end = 0
    for a, b, finished in parts:
        require(a == end and a < b <= n and type(finished) is bool, 'partition interval')
        end = b
    require(end == n, 'partition coverage')


def literal(atoms, order, state, size):
    out = eye(size)
    for number in order:
        if state & (1 << number):
            out = mul(atoms[number], out)
    return out


def block_forward(t, parts, width):
    size = len(t)
    out = zeros(size, size)
    for a0, b0, finished in parts:
        a, b = width * a0, width * b0
        if finished:
            row = block(t, a, b, a, size)
            if a:
                row = sub(row, mul(mul(block(t, a, b, 0, a),
                                       inv(block(t, 0, a, 0, a))), block(t, 0, a, a, size)))
            put(out, a, a, row)
        else:
            put(out, a, a, eye(b - a))
            if b < size:
                solve = mul(inv(block(t, 0, b, 0, b)), block(t, 0, b, b, size))
                put(out, a, b, block(solve, a, b, 0, size - b))
    return out


def block_inverse(t, parts, width):
    size = len(t)
    out = zeros(size, size)
    for a0, b0, finished in parts:
        a, b = width * a0, width * b0
        if finished:
            put(out, 0, a, block(inv(block(t, 0, b, 0, b)), 0, b, a, b))
        else:
            put(out, a, a, eye(b - a))
            if a:
                solve = mul(inv(block(t, 0, a, 0, a)), block(t, 0, a, a, b))
                put(out, 0, a, [[-v for v in row] for row in solve])
    return out


def factorized(t, upper, parts, width):
    size = len(t)
    ub, eb = zeros(size, size), zeros(size, size)
    for a0, b0, finished in parts:
        a, b = width * a0, width * b0
        put(ub, a, a, block(upper, a, b, a, b))
        put(eb, a, a, schur(t, a, b) if finished else eye(b - a))
    return mul(mul(eb, inv(ub)), upper), ub, eb


def check_state(t, upper, parts, width, p, pinv, lam, q, counts):
    size, chi = len(t), lam * q
    s = lam + lam * lam * q
    predicted, ub, eb = factorized(t, upper, parts, width)
    require(p == predicted, 'ordered frontier formula')
    require(p == block_forward(t, parts, width), 'block row formula')
    require(pinv == block_inverse(t, parts, width), 'inverse block column formula')
    require(pinv == mul(mul(inv(upper), ub), inv(eb)), 'inverse factor order')
    counts['matrix_identities'] += 4
    c = sum(finished for _, _, finished in parts)
    u = len(parts) - c
    require(norm_squared_at_most(p, c * s * s + u * (1 + chi * chi)), 'forward bound')
    require(norm_squared_at_most(pinv, c * q * q + u * (1 + chi * chi)), 'inverse bound')
    counts['spectral_certificates'] += 2
    for a0, b0, finished in parts:
        a, b = width * a0, width * b0
        row, col = block(p, a, b, 0, size), block(pinv, 0, size, a, b)
        rb = s * s if finished else 1 + chi * chi
        cb = q * q if finished else 1 + chi * chi
        require(norm_squared_at_most(row, rb), 'individual row bound')
        require(norm_squared_at_most(col, cb), 'individual column bound')
        counts['spectral_certificates'] += 2
        counts['partition_blocks'] += 1
    wrong_order = mul(mul(upper, inv(ub)), eb) != p
    missing_endpoint = mul(inv(ub), upper) != p
    wrong_sign = False
    for a0, b0, finished in parts:
        if a0 and not finished:
            a, b = width * a0, width * b0
            mutant = [row[:] for row in pinv]
            put(mutant, 0, a, [[-v for v in row] for row in block(pinv, 0, a, a, b)])
            wrong_sign |= mutant != pinv
    return wrong_order, missing_endpoint, wrong_sign


def rejected(call):
    try:
        call()
    except ValueError:
        return
    raise ValueError('control did not reject')


def controls():
    rejected(lambda: inv([[F(0)]]))
    rejected(lambda: validate_partition([(0, 1, False), (2, 3, True)], 3))
    rejected(lambda: validate_partition([(0, 2, False), (1, 3, True)], 3))
    require(not psd([[F(0), F(1)], [F(1), F(0)]]), 'zero pivot PSD control')
    require(not psd([[F(-1)]]), 'negative PSD control')
    require(not norm_squared_at_most([[F(2)]], F(3)), 'spectral control')
    # Well-conditioned endpoint, but a badly conditioned first leading section.
    t = [[F(1, 128), F(1)], [F(1), F(0)]]
    require(norm_squared_at_most(t, F(4)), 'whole endpoint norm control')
    require(norm_squared_at_most(inv(t), F(4)), 'whole inverse norm control')
    prefix = [[F(1), F(128)], [F(0), F(1)]]
    require(not norm_squared_at_most(prefix, F(4 * 2 * 4 ** 4)), 'leading premise control')
    require(inv(block(t, 0, 1, 0, 1))[0][0] == 128, 'leading inverse witness')
    # A punctured triangular restriction is not a contiguous interval.
    u = [[F(1), F(1), F(0)], [F(0), F(1), F(1)], [F(0), F(0), F(1)]]
    require(inv(u)[0][2] != inv([[u[0][0], u[0][2]], [u[2][0], u[2][2]]])[0][1],
            'noncontiguous restriction control')
    return 8


def run():
    counts = {'fixtures': 0, 'trees': 0, 'states': 0, 'partition_blocks': 0,
              'matrix_identities': 0, 'spectral_certificates': 0,
              'wrong_order_witnesses': 0, 'missing_endpoint_witnesses': 0,
              'wrong_sign_witnesses': 0}
    for n, width in product(range(1, MAX_N + 1), (1, 2)):
        t = fixture(n, width)
        size = len(t)
        lam = envelope(t)
        q = max(envelope(inv(block(t, 0, k, 0, k)))
                for k in range(width, size + 1, width))
        require(norm_squared_at_most(t, lam * lam), 'root admission')
        for k in range(width, size + 1, width):
            require(norm_squared_at_most(inv(block(t, 0, k, 0, k)), q * q), 'leading admission')
        upper = unit_upper(t, width)
        counts['fixtures'] += 1
        for tree in interval_trees(n):
            info, atoms = program(t, tree, width)
            root = info[0, n]
            require(literal(atoms, root['order'], root['mask'], size) == t, 'atomic endpoint')
            for state in root['states']:
                parts = partition(info, n, state)
                p = literal(atoms, root['order'], state, size)
                pinv = inv(p)
                wrong, missing, sign = check_state(t, upper, parts, width, p, pinv, lam, q, counts)
                counts['wrong_order_witnesses'] += int(wrong)
                counts['missing_endpoint_witnesses'] += int(missing)
                counts['wrong_sign_witnesses'] += int(sign)
                counts['states'] += 1
            counts['trees'] += 1
    require(counts['wrong_order_witnesses'] > 0, 'wrong-order control exercised')
    require(counts['missing_endpoint_witnesses'] > 0, 'finished-endpoint control exercised')
    require(counts['wrong_sign_witnesses'] > 0, 'inverse-sign control exercised')
    counts['controls'] = controls() + 3
    return counts


def product_controls():
    checked = 0
    shapes = list(product((1, 2, 3), repeat=3)) + [(1, 10, 2), (10, 1, 10), (5, 10, 3)]
    for rows, inner, cols in shapes:
        for variant in range(3):
            a = [[F(((i+1)*(k+2)+variant) % 7-3, 2+i+2*k)
                  for k in range(inner)] for i in range(rows)]
            b = [[F(((k+2)*(j+1)+variant) % 5-2, 3+2*k+j)
                  for j in range(cols)] for k in range(inner)]
            if variant == 0:
                a[0] = [F(0)] * inner
            before_a, before_b = [r[:] for r in a], [r[:] for r in b]
            expected = [[sum((a[i][k]*b[k][j] for k in range(inner)), F(0))
                         for j in range(cols)] for i in range(rows)]
            actual = mul(a, b)
            require(actual == expected, 'integer product differs from Fraction oracle')
            require(a == before_a and b == before_b, 'product changed an input')
            require(all(type(x) is F for row in actual for x in row), 'product result type')
            actual[0][0] += 1
            require(mul(a, b) == expected, 'product result is not independent')
            checked += 1
    rejected(lambda: mul([], [[F(1)]]))
    rejected(lambda: mul([[F(1), F(2)]], [[F(1)]]))
    require(mul([[F(0), F(0)]], [[F(2)], [F(3)]]) == [[F(0)]], 'zero product')
    return checked + 3


def main():
    product_cases = product_controls()
    counts = run()
    root = Path(__file__).resolve().parent
    hashes = {name: sha256((root / name).read_bytes()).hexdigest() for name in FILES}
    print(json.dumps({'status': 'PASS_DOWNSET_BLOCK_SOLVE', 'claim_type': 'scoped proof',
                      'finite_evidence': counts, 'product_controls': product_cases, 'source_sha256': hashes,
                      'no_new_kappa': True}, sort_keys=True))


if __name__ == '__main__':
    main()
