"""Independent, finite exact audit of complex-to-real support preservation.

No primary checker imports; Gaussian rationals are pairs of Fraction values,
and binary ranks use sets. This finite regression is not the quantified proof
in PROOF.md. The predecessor's geometry/minor audit must also be run separately.
Apache-2.0; substantial OpenAI Codex assistance, no human-only review claimed.
"""

import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from math import lcm
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
GEOMETRY = HERE.parent / 'p112-single-lift' / 'reference-geometry.json'
GEOMETRY_SHA256 = '4f44af368e046002553d632ee90c6470990827cea3fae41f0f54018522d7a080'
ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def g(real=0, imag=0):
    return Fraction(real), Fraction(imag)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def scale(k, a):
    return k * a[0], k * a[1]


def inverse(a):
    norm = a[0] * a[0] + a[1] * a[1]
    check(norm != 0, 'zero Gaussian denominator')
    return a[0] / norm, -a[1] / norm


def project(a, parameter):
    return a[0] + parameter * a[1]


def reader(x, a):
    return [g(sum(row[j] * a[j][0] for j in range(8)),
              sum(row[j] * a[j][1] for j in range(8))) for row in x]


def sources(x, a, z):
    return [[sub(g(row[j]), mul(a[j], z[i])) for i, row in enumerate(x)]
            for j in range(8)]


def forbidden(x, a, z, include_reader=True, include_inverse=True,
              include_residual=True):
    values = set(a)
    if include_reader:
        values.update(reader(x, a))
    for i, value in enumerate(z):
        if value == ZERO:
            continue
        inv = inverse(value)
        if include_inverse:
            values.add(inv)
        if include_residual:
            values.update(sub(a[j], scale(x[i][j], inv)) for j in range(8))
    values.discard(ZERO)
    return values


def reduce_to_real(x, a, z):
    avoid = forbidden(x, a, z)
    check(len(avoid) <= 1128, 'finite forbidden-set bound')
    parameter = next((t for t in range(len(avoid) + 1)
                      if all(project(w, t) != 0 for w in avoid)), None)
    check(parameter is not None, 'N+1 parameter search')
    real_a = [g(project(w, parameter)) for w in a]
    real_z = [ZERO if w == ZERO else g(1 / project(inverse(w), parameter))
              for w in z]
    return real_a, real_z, parameter, len(avoid)


def bits(value):
    return {j for j in range(9) if (value >> j) & 1}


def basis(rows):
    pivots = {}
    for original in rows:
        row = set(original)
        while row:
            pivot = min(row)
            if pivot in pivots:
                row.symmetric_difference_update(pivots[pivot])
            else:
                pivots[pivot] = row
                break
    return list(pivots.values())


def support(vector):
    return {i for i, value in enumerate(vector) if value != ZERO}


def beta(d, s, labels, duals):
    normals = basis(duals[i] for i in support(d))
    evaluations = [{j for j, q in enumerate(normals) if len(q & labels[i]) % 2}
                   for i in support(s)]
    return len(basis(evaluations))


def costs(x, a, z, labels, duals):
    source_columns = sources(x, a, z)
    return [beta([g(row[j]) for row in x], source_columns[j], labels, duals)
            for j in range(8)] + [beta(reader(x, a), z, labels, duals)]


def identity(x, a, z):
    """All 112^2 entries, evaluated as nine terms with scaled integers."""
    d, columns = reader(x, a), sources(x, a, z)
    check(all(v[0].denominator == v[1].denominator == 1 for v in d),
          'integer reader required by this identity regression')
    denominator = lcm(*(c.denominator for v in z for c in v),
                      *(c.denominator for column in columns for v in column for c in v))
    scaled_z = [(int(v[0] * denominator), int(v[1] * denominator)) for v in z]
    scaled_columns = [[(int(v[0] * denominator), int(v[1] * denominator))
                       for v in column] for column in columns]
    for i, row in enumerate(x):
        dr, di = map(int, d[i])
        for k, other in enumerate(x):
            zr, zi = scaled_z[k]
            real = sum(row[j] * scaled_columns[j][k][0] for j in range(8)) + dr * zr - di * zi
            imag = sum(row[j] * scaled_columns[j][k][1] for j in range(8)) + dr * zi + di * zr
            check(real == denominator * sum(u * v for u, v in zip(row, other))
                  and imag == 0, 'entrywise bilinear nine-term identity')


def family(x):
    """448 pair cases, 8 singletons, 2 zero cases, and 2 full-support cases."""
    coefficient_values = [g(1), g(0, 1), g(1, 1), g(2, -1)]
    for pair_index, (left, right) in enumerate(combinations(range(8), 2)):
        for coefficient_index, (u, v) in enumerate(product(coefficient_values, repeat=2)):
            a = [ZERO] * 8
            a[left], a[right] = u, v
            choices = [ZERO, inverse(u), scale(-1, inverse(u)),
                       inverse(v), scale(-1, inverse(v)), g(1, 1)]
            z = [choices[(i + pair_index + coefficient_index) % 6] for i in range(112)]
            yield a, z, pair_index == 40 % 28
    for j in range(8):
        a = [ZERO] * 8
        a[j] = g(0, 1)
        z = [[ZERO, g(0, 1), g(0, -1), g(1, 1)][i % 4] for i in range(112)]
        yield a, z, True
    yield [ZERO] * 8, [ZERO] * 112, True
    yield [ZERO] * 8, [g(1, 1)] * 112, True
    for offset in range(2):
        a = [coefficient_values[(j + offset) % 4] for j in range(8)]
        z = [ZERO if i % 9 == 0 else scale((-1) ** i, inverse(a[i % 8]))
             for i in range(112)]
        yield a, z, True


def negative_controls(x):
    # Excluding inverses is independently necessary: all other projected
    # forbidden values here survive t=0, yet the selected denominator vanishes.
    a, z = [ONE] * 8, [ZERO] * 112
    z[0] = g(0, 1)
    check(all(project(w, 0) for w in forbidden(x, a, z, include_inverse=False))
          and project(inverse(z[0]), 0) == 0, 'inverse-omission control')
    # The extra reader can lose support if its nonzero coordinates are omitted.
    a, z = [g(1, 1), g(1, -1)] + [ZERO] * 6, [ZERO] * 112
    check(all(project(w, 0) for w in forbidden(x, a, z, include_reader=False))
          and support(reader(x, a)) != support(reader(x, [g(w[0]) for w in a])),
          'reader-omission control')
    # Avoiding only a, Xa and 1/z permits extra source cancellations.
    a, z = [g(1, 1)] + [ZERO] * 7, [ZERO] * 112
    z[0] = inverse(g(1, 2))
    check(all(project(w, 0) for w in forbidden(x, a, z, include_residual=False)),
          'smaller forbidden set permits t=0')
    check(sources(x, a, z)[0][0] != ZERO
          and sources(x, [ONE] + [ZERO] * 7, [ONE] + [ZERO] * 111)[0][0] == ZERO,
          'residual-omission control')
    check(project(g(0, 1), 0) == 0 and project(g(0, 1), 1) != 0,
          'fixed t=0 control')
    # Transposing is bilinear; conjugating the source is a different identity.
    a, z = g(0, 1), ONE
    s = sub(ONE, mul(a, z))
    check(add(s, mul(a, z)) == ONE
          and add((s[0], -s[1]), mul(a, z)) != ONE, 'conjugation control')
    check(len(basis([{0, 1}, {1, 2}, {0, 2}])) == 2, 'GF2 dependence control')
    return 6


def run():
    raw = GEOMETRY.read_bytes()
    check(sha256(raw).hexdigest() == GEOMETRY_SHA256, 'pinned geometry hash')
    data = json.loads(raw)
    x = data['X']
    check(len(x) == 112 and all(len(row) == 8 and set(row) <= {-1, 0, 1} for row in x),
          'P112 dimensions and coordinate alphabet')
    labels, duals = [list(map(bits, data[key])) for key in ('labels', 'duals')]
    check(len(labels) == len(duals) == 112, 'label dimensions')
    count = identities = 0
    parameters, sizes, cost_sums = [], [], []
    for a, z, entrywise in family(x):
        real_a, real_z, parameter, size = reduce_to_real(x, a, z)
        check(all(v[1] == 0 for v in real_a + real_z), 'real output')
        check(support(a) == support(real_a) and support(z) == support(real_z),
              'coefficient and added-source support')
        check(support(reader(x, a)) == support(reader(x, real_a)), 'extra reader support')
        old, new = sources(x, a, z), sources(x, real_a, real_z)
        check(all(support(old[j]) == support(new[j]) for j in range(8)),
              'all eight source supports exactly preserved')
        old_costs, new_costs = costs(x, a, z, labels, duals), costs(x, real_a, real_z, labels, duals)
        check(old_costs == new_costs and sum(old_costs) >= 64,
              'nine individual costs and inherited bound on tested cases')
        if entrywise:
            identity(x, a, z)
            identity(x, real_a, real_z)
            identities += 2
        count += 1
        parameters.append(parameter)
        sizes.append(size)
        cost_sums.append(sum(old_costs))
    check(count == 460 and identities == 56, 'finite-domain coverage')
    return {'schema': 1, 'geometry_sha256': GEOMETRY_SHA256,
            'pair_cases': 448, 'singleton_cases': 8, 'zero_cases': 2, 'full_support_cases': 2,
            'total_cases': count, 'support_pair_comparisons': 9 * count,
            'cost_vector_comparisons': count, 'entrywise_identity_matrices': identities,
            'entrywise_identity_entries': identities * 112 * 112,
            'parameter_min': min(parameters), 'parameter_max': max(parameters),
            'distinct_forbidden_values_min': min(sizes), 'distinct_forbidden_values_max': max(sizes),
            'observed_cost_sum_min': min(cost_sums), 'observed_cost_sum_max': max(cost_sums),
            'negative_controls': negative_controls(x),
            'scope': 'finite Gaussian-rational regression; universal theorem is written mathematics'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', type=Path, help='write deterministic JSON receipt at this path')
    mode.add_argument('--check', type=Path, help='compare deterministic receipt at this path')
    args = parser.parse_args()
    receipt = run()
    if args.write:
        args.write.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    if args.check:
        check(receipt == json.loads(args.check.read_text(encoding='utf-8')), 'receipt equality')
    print('PASS_P112_COMPLEX_SINGLE_LIFT_INDEPENDENT: 460 exact cases; '
          '4140 support pairs; 460 cost vectors; 56 entrywise identities; 6 controls')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, ZeroDivisionError) as error:
        print('FAIL_P112_COMPLEX_SINGLE_LIFT_INDEPENDENT: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
