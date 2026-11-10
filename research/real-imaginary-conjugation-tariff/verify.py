#!/usr/bin/env python3
"""Exact rational conjugation compiler and finite corroboration. Apache-2.0."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path

MAX_DIM = 8
MAX_BITS = 256


def need(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def trans(a):
    return tuple(zip(*a))


def mul(a, b):
    out = tuple(tuple(sum((x * y for x, y in zip(row, col)), F(0))
                      for col in trans(b)) for row in a)
    need(all(max(abs(x.numerator).bit_length(), x.denominator.bit_length())
             <= 4096 for row in out for x in row), 'working bit bound')
    return out


def sub(a, b):
    return tuple(tuple(x - y for x, y in zip(r, s)) for r, s in zip(a, b))


def rank(a):
    """Rational row elimination for the compiler's progress checks."""
    work = [list(row) for row in a]
    count = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(count, len(work)) if work[i][j]), None)
        if pivot is None:
            continue
        work[count], work[pivot] = work[pivot], work[count]
        d = work[count][j]
        work[count] = [x / d for x in work[count]]
        for i in range(count + 1, len(work)):
            c = work[i][j]
            work[i] = [x - c * y for x, y in zip(work[i], work[count])]
        count += 1
        if count == len(work):
            break
    return count


def matrix(a):
    """Validate the rational, square, bounded executable interface."""
    need(isinstance(a, (tuple, list)) and 1 <= len(a) <= MAX_DIM, 'dimension')
    n = len(a)
    need(all(isinstance(row, (tuple, list)) and len(row) == n for row in a),
         'square matrix')
    need(all(type(x) in (int, F) for row in a for x in row), 'rational entries')
    out = tuple(tuple(F(x) for x in row) for row in a)
    need(all(max(abs(x.numerator).bit_length(), x.denominator.bit_length())
             <= MAX_BITS for row in out for x in row), 'entry bit bound')
    return out


def reflection(v):
    n = len(v)
    norm = sum(x * x for x in v)
    need(norm > 0, 'nonzero real reflection normal')
    return tuple(tuple(F(i == j) - 2 * v[i] * v[j] / norm
                       for j in range(n)) for i in range(n))


def reflection_basis(v):
    """Rational S,S^-1 with first column v and other columns in v-perp."""
    n = len(v)
    k = next((i for i in range(n) if v[i]), None)
    need(k is not None, 'nonzero basis normal')
    norm = sum(x * x for x in v)
    other = [j for j in range(n) if j != k]
    columns = [tuple(v)] + [tuple(F(i == j) - F(i == k) * v[j] / v[k]
                                 for i in range(n)) for j in other]
    inverse = [tuple(x / norm for x in v)]
    inverse += [tuple(F(i == j) - v[j] * v[i] / norm for i in range(n))
                for j in other]
    s, si = trans(columns), tuple(inverse)
    need(mul(s, si) == eye(n) == mul(si, s), 'rational basis inverse')
    return s, si


def normals(q):
    """Return v_1,...,v_r with q=H(v_1)...H(v_r), r=rank(I-q)."""
    n = len(q)
    current = q
    result = []
    initial = rank(sub(eye(n), q))
    for _ in range(n):
        if current == eye(n):
            break
        j = next(j for j in range(n)
                 if any(current[i][j] != F(i == j) for i in range(n)))
        v = tuple(current[i][j] - F(i == j) for i in range(n))
        before = rank(sub(eye(n), current))
        current = mul(reflection(v), current)
        need(rank(sub(eye(n), current)) == before - 1, 'rank drops once')
        result.append(v)
    need(current == eye(n) and len(result) == initial, 'reflection termination')
    return tuple(result)


def compile_frames(p, q):
    """Chronological ('L', real matrix) / ('C', coordinate) instructions."""
    p, q = matrix(p), matrix(q)
    n = len(p)
    need(len(q) == n, 'matching dimensions')
    need(mul(trans(p), p) == eye(n), 'orthogonal P')
    need(mul(trans(q), q) == eye(n), 'orthogonal Q')
    result = []
    for v in reversed(normals(mul(trans(p), q))):
        s, si = reflection_basis(v)
        result.extend((('L', si), ('C', 0), ('L', s)))
    result.append(('L', p))
    need(sum(op == 'C' for op, _ in result) == rank(sub(p, q)), 'tariff')
    return tuple(result)


def dense_rank(a):
    """Independent full Gauss-Jordan oracle, without compiler rank calls."""
    rows = [list(map(F, row)) for row in a]
    pivot_row = 0
    for col in range(len(rows[0])):
        choices = [i for i in range(pivot_row, len(rows)) if rows[i][col]]
        if not choices:
            continue
        i = choices[-1]
        rows[i], rows[pivot_row] = rows[pivot_row], rows[i]
        divisor = rows[pivot_row][col]
        for j in range(col, len(rows[0])):
            rows[pivot_row][j] /= divisor
        for k in range(len(rows)):
            if k != pivot_row:
                c = rows[k][col]
                for j in range(col, len(rows[0])):
                    rows[k][j] -= c * rows[pivot_row][j]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def dense_product(a, b):
    """Literal full real matrix product, without compiler arithmetic calls."""
    n = len(a)
    out = [[F(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if a[i][k]:
                for j in range(n):
                    out[i][j] += a[i][k] * b[k][j]
    return tuple(tuple(row) for row in out)


def real_linear(a, b=None):
    """Realification of complex-linear a+i*b; b defaults to zero."""
    n = len(a)
    if b is None:
        b = tuple((F(0),) * n for _ in range(n))
    return tuple(tuple(a[i % n][j % n] if i // n == j // n
                       else (-1 if i < n else 1) * b[i % n][j % n]
                       for j in range(2 * n)) for i in range(2 * n))


def anti_rank(a):
    """Half the real rank of M+J M J, the full antilinear component."""
    n = len(a) // 2
    b = [[F(0)] * (2 * n) for _ in range(2 * n)]
    for i in range(2 * n):
        for j in range(2 * n):
            sign = -1 if (i < n) == (j < n) else 1
            b[i][j] = a[i][j] + sign * a[(i + n) % (2 * n)][(j + n) % (2 * n)]
    r = dense_rank(b)
    need(r % 2 == 0, 'even real antilinear rank')
    return r // 2


def full_step(instruction, n, spectators):
    op, payload = instruction
    d = n + spectators
    if op == 'C':
        need(type(payload) is int and 0 <= payload < n, 'conjugation coordinate')
        return tuple(tuple(F(i == j) * (-1 if i == d + payload else 1)
                           for j in range(2 * d)) for i in range(2 * d))
    need(op == 'L', 'instruction opcode')
    need(len(payload) == n and all(len(row) == n for row in payload),
         'instruction matrix shape')
    need(dense_rank(payload) == n, 'invertible linear step')
    padded = tuple(tuple(payload[i][j] if i < n and j < n else F(i == j)
                         for j in range(d)) for i in range(d))
    return real_linear(padded)


def target(p, q, spectators):
    n, d = len(p), len(p) + spectators
    out = [[F(0)] * (2 * d) for _ in range(2 * d)]
    for i in range(d):
        for j in range(d):
            out[i][j] = p[i][j] if i < n and j < n else F(i == j)
            out[i + d][j + d] = q[i][j] if i < n and j < n else F(i == j)
    return tuple(tuple(row) for row in out)


def replay(p, q, spectators=0):
    program = compile_frames(p, q)
    d = len(p) + spectators
    state = eye(2 * d)
    calls = 0
    for instruction in program:
        state = dense_product(full_step(instruction, len(p), spectators), state)
        calls += instruction[0] == 'C'
        need(anti_rank(state) <= calls, 'every prefix obeys call lower bound')
    need(state == target(p, q, spectators), 'complete real endpoint')
    need(calls == dense_rank(sub(p, q)), 'independent exact tariff')
    need(anti_rank(state) == calls, 'endpoint lower bound attained')
    return calls, len(program), (2 * d) ** 2


def signed_permutations(n):
    for permutation in permutations(range(n)):
        for signs in product((-1, 1), repeat=n):
            yield tuple(tuple(F(signs[i] if j == permutation[i] else 0)
                              for j in range(n)) for i in range(n))


def rational_fixtures(n):
    """Fixed rational orthogonal products, including oblique frames."""
    fixtures = [eye(n)]
    for seed in range(1, 9):
        a = eye(n)
        for k in range(1, n + 1):
            v = tuple(F(((i + 2) * (seed + k) + i * i) % 7 - 3)
                      for i in range(n))
            if not any(v):
                v = (F(1),) + (F(0),) * (n - 1)
            a = mul(reflection(v), a)
        fixtures.append(a)
    return tuple(fixtures)


def census():
    counts, histogram = Counter(), Counter()
    for n in range(1, 4):
        choices = tuple(signed_permutations(n))
        for p, q in product(choices, repeat=2):
            calls, instructions, entries = replay(p, q)
            counts['ordered_signed_permutation_pairs'] += 1
            counts['instructions'] += instructions
            counts['full_endpoint_entries'] += entries
            histogram[calls] += 1
    for q in signed_permutations(4):
        calls, instructions, entries = replay(eye(4), q)
        counts['four_coordinate_targets'] += 1
        counts['instructions'] += instructions
        counts['full_endpoint_entries'] += entries
        histogram[calls] += 1
    for n in range(1, 7):
        choices = rational_fixtures(n)
        for p, q in zip(choices, reversed(choices)):
            for spectators in (0, 1, 2):
                calls, instructions, entries = replay(p, q, spectators)
                counts['rational_dirty_fixtures'] += 1
                counts['instructions'] += instructions
                counts['full_endpoint_entries'] += entries
                histogram[calls] += 1
    large = reflection((F(1 << 126), F(1)))
    boundary = ((eye(8), eye(8)),
                (eye(8), tuple(tuple(-x for x in row) for row in eye(8))),
                (eye(2), large))
    for p, q in boundary:
        calls, instructions, entries = replay(p, q)
        counts['dimension_and_coefficient_boundary_fixtures'] += 1
        counts['instructions'] += instructions
        counts['full_endpoint_entries'] += entries
        histogram[calls] += 1
    return counts, histogram


def mixed_dirty_fixture():
    """Nonreal free mixing of dirty coordinates inside a paid-call block."""
    p = eye(2)
    q = ((F(3, 5), F(-4, 5)), (F(4, 5), F(3, 5)))
    program = compile_frames(p, q)
    state = eye(8)
    calls = 0
    for op, payload in program:
        if op == 'C':
            # z_1 += i*z_2 mixes active/dirty data and commutes with C_0.
            a = eye(4)
            b = tuple(tuple(F(i == 1 and j == 2) for j in range(4))
                      for i in range(4))
            w = real_linear(a, b)
            wi = real_linear(a, tuple(tuple(-x for x in row) for row in b))
            state = dense_product(w, state)
            need(state[1][6] != 0, 'dirty data enters an active coordinate')
            state = dense_product(full_step((op, payload), 2, 2), state)
            state = dense_product(wi, state)
            calls += 1
        else:
            state = dense_product(full_step((op, payload), 2, 2), state)
    need(state == target(p, q, 2) and anti_rank(state) == calls == 2,
         'mixed dirty endpoint')
    return 64


def small_complex_rank(a):
    """Independent 2-by-2 Gaussian determinant from four real blocks."""
    b = [[((a[i][j] - a[i + 2][j + 2]) / 2,
           (a[i + 2][j] + a[i][j + 2]) / 2)
          for j in range(2)] for i in range(2)]
    if all(x == (0, 0) for row in b for x in row):
        return 0
    x, y, z, w = b[0][0], b[0][1], b[1][0], b[1][1]
    det = (x[0] * w[0] - x[1] * w[1] - y[0] * z[0] + y[1] * z[1],
           x[0] * w[1] + x[1] * w[0] - y[0] * z[1] - y[1] * z[0])
    return 1 if det == (0, 0) else 2


def complex_word_checks():
    """Complete short words with nonreal complex-linear frames."""
    zero = ((F(0), F(0)), (F(0), F(0)))
    phase = real_linear(zero, eye(2))
    shear = real_linear(eye(2), ((F(0), F(1)), (F(0), F(0))))
    swap = real_linear(((F(0), F(1)), (F(1), F(0))))
    generators = ((full_step(('C', 0), 2, 0), 1),
                  (full_step(('C', 1), 2, 0), 1),
                  (phase, 0), (shear, 0), (swap, 0))
    count = 0
    for length in range(5):
        for indices in product(range(5), repeat=length):
            state, calls = eye(4), 0
            for index in indices:
                g, c = generators[index]
                state = dense_product(g, state)
                calls += c
            need(anti_rank(state) == small_complex_rank(state) <= calls,
                 'independent Gaussian rank and word bound')
            count += 1
    return count


def controls():
    rejected = 0
    bad_inputs = [([], []), ([[1, 0]], [[1]]), ([[True]], [[1]]),
                  ([[F(1, 3)]], [[1]]), ([[1]], [[1, 0], [0, 1]]),
                  ([[1 << 257]], [[1]]), ([[1]], [[0]]),
                  (eye(9), eye(9)), ([[1.0]], [[1]])]
    for p, q in bad_inputs:
        try:
            compile_frames(p, q)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('invalid compiler input accepted')
    p, q = eye(2), ((F(3, 5), F(-4, 5)), (F(4, 5), F(3, 5)))
    program = compile_frames(p, q)
    for defect in ('omit_conjugation', 'flip_real', 'reverse_word'):
        state = eye(4)
        removed = False
        for op, payload in reversed(program) if defect == 'reverse_word' else program:
            if defect == 'omit_conjugation' and op == 'C' and not removed:
                removed = True
                continue
            step = full_step((op, payload), 2, 0)
            if defect == 'flip_real' and op == 'C':
                step = tuple(tuple(F(i == j) * (-1 if i == payload else 1)
                                   for j in range(4)) for i in range(4))
            state = dense_product(step, state)
        need(state != target(p, q, 0), 'endpoint corruption must be detected')
        rejected += 1
    zero, one = ((F(0),),), ((F(1),),)
    need(anti_rank(real_linear(zero, one)) == 0, 'displacement is not tariff')
    need(anti_rank(target(p, q, 0)) == 2, 'orientation alone is insufficient')
    return rejected


def main():
    counts, histogram = census()
    counts['mixed_dirty_endpoint_entries'] = mixed_dirty_fixture()
    counts['nonreal_complex_frame_words'] = complex_word_checks()
    counts['rejected_invalid_or_corrupt_cases'] = controls()
    here = Path(__file__).resolve().parent
    hashes = {p.name: sha256(p.read_bytes()).hexdigest()
              for p in sorted(here.iterdir()) if p.is_file()}
    print(json.dumps({'status': 'PASS_REAL_IMAGINARY_CONJUGATION_TARIFF',
                      'counts': dict(sorted(counts.items())),
                      'tariff_histogram': dict(sorted(histogram.items())),
                      'source_sha256': hashes}, sort_keys=True))


if __name__ == '__main__':
    main()
