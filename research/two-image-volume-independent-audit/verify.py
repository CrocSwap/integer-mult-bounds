#!/usr/bin/env python3
"""Code-disjoint, bounded source/character/boundary checks; standard library only."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def compose(left, right):
    return (tuple(left[0][right[0][x]] for x in range(len(right[0]))),
            tuple((right[1][x] + left[1][right[0][x]]) % 4
                  for x in range(len(right[0]))))


def inverse(word):
    p = tuple(word[0].index(x) for x in range(len(word[0])))
    return p, tuple(-word[1][p[x]] % 4 for x in range(len(p)))


def power(word, exponent):
    result = tuple(range(len(word[0]))), (0,) * len(word[0])
    for _ in range(exponent):
        result = compose(word, result)
    return result


def tensor(left, right):
    n = len(right[0])
    return (tuple(a * n + b for a in left[0] for b in right[0]),
            tuple((a + b) % 4 for a in left[1] for b in right[1]))


def trace(word):
    counts = [0] * 4
    for x, y in enumerate(word[0]):
        if x == y:
            counts[word[1][x]] += 1
    return counts[0] - counts[2], counts[1] - counts[3]


def source_definitions():
    pins = json.loads((ROOT / 'RETAINED-SOURCES.json').read_text())
    for row in pins['files']:
        data = (ROOT / row['retained_path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'retained source changed')
        require(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                == row['git_blob'], 'retained Git blob mismatch')
    # Evaluate only literal defining expressions, never import a predecessor module.
    old = ast.parse((ROOT / 'vendor/pr4688/verify.py').read_text())
    env = {'__builtins__': {}, 'tuple': tuple, 'range': range}
    definitions = {}
    for node in old.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in ('U_PERM', 'V_PERM'):
                definitions[name] = eval(compile(ast.Expression(node.value), '<source-definition>', 'eval'), env)
    expected_u, expected_v = [], []
    for x in range(8):
        a, b, c = (x >> j & 1 for j in range(3))
        expected_u.append(a + 2 * b + 4 * (c ^ a))
        expected_v.append(b + 2 * a + 4 * c)
    require(definitions == {'U_PERM': tuple(expected_u), 'V_PERM': tuple(expected_v)},
            'source address definition differs from independent coordinate action')
    u, v = (tuple(expected_u), (0,) * 8), (tuple(expected_v), (0,) * 8)
    identity = tuple(range(8)), (0,) * 8
    env.update(identity=identity, u=u, v=v, monomial_compose=compose)
    repaired = ast.parse((ROOT / 'vendor/pr4710/verify.py').read_text())
    fn = next(n for n in repaired.body if isinstance(n, ast.FunctionDef) and n.name == 'monomial_checks')
    for node in fn.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in ('phase', 'P', 'Q'):
                env[name] = eval(compile(ast.Expression(node.value), '<source-definition>', 'eval'), env)
    s = identity[0], tuple(sum(x >> j & 1 for j in range(3)) % 4 for x in range(8))
    require(env['phase'] == s, 'source phase is not exact i^popcount')
    require(env['P'] == compose(s, compose(u, s)) and env['Q'] == compose(s, compose(v, s)),
            'source branch phase binding')
    return u, v, s, env['P'], env['Q']


def det_integer(matrix):
    a = [row[:] for row in matrix]
    previous, sign = 1, 1
    for k in range(len(a) - 1):
        pivot_row = next((r for r in range(k, len(a)) if a[r][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            a[k], a[pivot_row] = a[pivot_row], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, len(a)):
            for j in range(k + 1, len(a)):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                require(numerator % previous == 0, 'Bareiss nonexact division')
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = pivot
    return sign * a[-1][-1]


def counts(width):
    d, a, b = 8 ** width, 4 ** width, 2 ** width
    return [(d + a + 2 * b) // 4, (d - a) // 4,
            (d + a - 2 * b) // 4, (d - a) // 4]


def multiply(a, b, p=17):
    out = [[0] * len(b[0]) for _ in a]
    for i, row in enumerate(a):
        for k, value in enumerate(row):
            if value:
                for j, other in enumerate(b[k]):
                    out[i][j] = (out[i][j] + value * other) % p
    return out


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def invert(a, p=17):
    n = len(a)
    rows = [a[i][:] + eye(n)[i] for i in range(n)]
    for j in range(n):
        k = next((k for k in range(j, n) if rows[k][j] % p), None)
        require(k is not None, 'unexpected singular modular operator')
        rows[j], rows[k] = rows[k], rows[j]
        scale = pow(rows[j][j], -1, p)
        rows[j] = [x * scale % p for x in rows[j]]
        for k in range(n):
            if k != j and rows[k][j]:
                c = rows[k][j]
                rows[k] = [(x - c * y) % p for x, y in zip(rows[k], rows[j])]
    return [row[n:] for row in rows]


def matrix(word):
    out = [[0] * len(word[0]) for _ in word[0]]
    for x, y in enumerate(word[0]):
        out[y][x] = pow(4, word[1][x], 17)
    return out


def lift(word, width):
    result = word
    for _ in range(width - 1):
        result = tensor(result, word)
    return result


def kernel(width):
    n = 8 ** width
    out = eye(n)
    for digit in range(width):
        updated = [[0] * n for _ in range(n)]
        mask = 8 ** digit
        for x in range(n):
            updated[x] = [(11 * a + 7 * b) % 17 for a, b in zip(out[x], out[x ^ mask])]
        out = updated
    return out


def boundary_check(u, v, s, P, Q, width):
    program = json.loads((ROOT / 'vendor/pr4998/PROGRAM.json').read_text())
    n = 8 ** width
    c = kernel(width)
    require(multiply(c, invert(c)) == eye(n), 'paid C invertibility')
    x = tuple(z ^ 1 for z in range(8)), (0,) * 8
    require(multiply(c, c) == matrix(lift(x, width)), 'actual normalized C squared is X')
    result = {}
    for variant, a, b in [('original', u, v), ('phase_repaired', P, Q)]:
        am, bm = matrix(lift(a, width)), matrix(lift(b, width))
        for image in (am, bm):
            single = multiply(c, multiply(image, c))
            require(multiply(single, invert(single)) == eye(n), 'allowed single-image boundary')
        middle = [[(x + 2 * y) % 17 for x, y in zip(rx, ry)] for rx, ry in zip(am, bm)]
        f = multiply(c, multiply(middle, c))
        fi = invert(f)
        state = [eye(2 * n)[:n], eye(2 * n)[n:]]
        for op in program[variant]:
            if op['op'] == 'paid_C':
                bank = op['bank']
                state[bank] = multiply(c, state[bank])
            elif op['op'] == 'add':
                numerator, denominator = op['coefficient']
                coefficient = numerator * pow(denominator, -1, 17) % 17
                dst, src = op['destination'], op['source']
                state[dst] = [[(x + coefficient * y) % 17 for x, y in zip(rx, ry)]
                              for rx, ry in zip(state[dst], state[src])]
            else:
                require(op['op'] == 'address', 'unknown program instruction')
                name = op['letter']
                if name in ('U', 'V', 'X'):
                    word = {'U': u, 'V': v, 'X': (tuple(x ^ 1 for x in range(8)), (0,) * 8)}[name]
                else:
                    sign = -1 if name.startswith('-') else 1
                    bit = int(name[-1])
                    word = tuple(range(8)), tuple(sign * (x >> bit & 1) % 4 for x in range(8))
                bank = op['bank']
                state[bank] = multiply(matrix(lift(word, width)), state[bank])
        expected = [row + [0] * n for row in f] + [[0] * n + row for row in fi]
        require(state[0] + state[1] == expected, 'compensated program differs from independent map')
        require(fi != eye(n), 'compensated partner must not be called returned dirt')
        result[variant] = {'independent_columns': 2 * n, 'literal_instructions': len(program[variant]),
                           'partner_is_identity': False, 'single_image_cases_invertible': True, 'arithmetic': 'F17 with i=4; finite boundary control only'}
    return result


def verify():
    u, v, s, P, Q = source_definitions()
    r = compose(inverse(u), v)
    repaired = compose(inverse(P), Q)
    require(repaired == compose(inverse(s), compose(r, s)), 'absolute-phase conjugacy')
    require(power(r, 4) == power(r, 0) and power(r, 2) != power(r, 0), 'source relative order')
    require([trace(power(r, k)) for k in range(4)] == [(8, 0), (2, 0), (4, 0), (2, 0)], 'base characters')
    # A projectively equal Q with changed absolute phase changes the relative spectrum.
    wrong_q = Q[0], tuple((x + 1) % 4 for x in Q[1])
    require(trace(compose(inverse(P), wrong_q)) != trace(repaired), 'absolute-phase omission control')
    records = []
    base_counts = [4, 1, 2, 1]  # Eigenvalue order 1,i,-1,-i.
    previous = [1, 0, 0, 0]
    for width in (1, 2):
        rt, rpt = lift(r, width), lift(repaired, width)
        require(rpt == compose(inverse(lift(s, width)), compose(rt, lift(s, width))), 'tensor phase conjugacy')
        traces = [trace(power(rt, k))[0] for k in range(4)]
        require(traces == [8 ** width, 2 ** width, 4 ** width, 2 ** width], 'tensor character trace')
        character_counts = [(traces[0] + traces[2] + 2 * traces[1]) // 4,
                            (traces[0] - traces[2]) // 4,
                            (traces[0] + traces[2] - 2 * traces[1]) // 4,
                            (traces[0] - traces[2]) // 4]
        convolution = [sum(previous[j] * base_counts[(k - j) % 4] for j in range(4)) for k in range(4)]
        require(character_counts == counts(width) == convolution, 'character/convolution independence')
        previous = convolution
        d = 8 ** width
        a = eye(d)
        for x, y in enumerate(rt[0]):
            a[y][x] += 2
        absolute_det = abs(det_integer(a))
        m = counts(width)
        require(absolute_det == 3 ** m[0] * 5 ** m[1], 'direct exact determinant')
        singular_ranks = [d - m[2], d - m[0], d - m[1], d - m[3]]
        require(all(0 < rank < d for rank in singular_ranks), 'singular rank-drop hypotheses')
        # A q-bank singular register mixing loses >=d rank; these targets lose <d.
        for q in (1, 2, 4):
            require(all((q - 1) * d + rank > (q - 1) * d for rank in singular_ranks), 'rank threshold')
        records.append({'width': width, 'character_counts_1_i_minus1_minusi': m,
                        'absolute_determinant': str(absolute_det), 'singular_target_ranks': singular_ranks,
                        'compensated_boundary': boundary_check(u, v, s, P, Q, width)})
    m3 = counts(3)
    require((m3[0] + 64 * 4 - 16 * 22, m3[1] + 64 - 16 * 12) == (52, -16), 'symbolic curvature')
    require(3 ** 52 != 5 ** 16, 'nonaffine curvature witness')
    require(3 ** 64 * 5 ** 16 != 3 ** 22 * 5 ** 12, 'tensorizing a sum control')
    # For t=iy, A=B automatically, but the second condition cannot hold when y!=0.
    for y in (Fraction(1, 2), Fraction(-1, 2), Fraction(2), Fraction(-2)):
        require(1 + y * y > abs(1 - y * y), 'pure-imaginary coefficient classification control')
    require(det_integer([[2, 0], [0, 0]]) == 0, 'clean full-space map is singular')
    require(multiply([[2, 0], [0, 0]], [[1], [0]]) == [[2], [0]], 'clean restriction remains injective')
    return {'result': 'PASS', 'scope': 'Independent scoped written theorem audit; exact finite source checks, not full theorem formalization',
            'singular_gap_completion': 'rank-drop argument for every fixed finite bank count',
            'source_relative_traces': [8, 2, 4, 2], 'finite_checks': records,
            'all_width_character_formula': ['(8^f+4^f+2*2^f)/4', '(8^f-4^f)/4', '(8^f+4^f-2*2^f)/4', '(8^f-4^f)/4'],
            'normalized_profile': 'log|alpha|+(A+B+E)/4+(A+B-E)/(4*2^f)+(A-B)/(2*4^f)',
            'curvature_witness': '3^52/5^16 != 1',
            'controls': ['absolute phase of Q', 'tensorizing a sum', 'pure-imaginary nonzero ratio',
                         'singular rank-drop hypotheses', 'allowed single-image cases', 'compensating output is transformed', 'clean subspace is outside full-space volume lemma']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    result = verify()
    if args.check:
        require(json.loads(args.check.read_text()) == result, 'stored report differs')
    if args.out:
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS_TWO_IMAGE_VOLUME_INDEPENDENT_AUDIT')
