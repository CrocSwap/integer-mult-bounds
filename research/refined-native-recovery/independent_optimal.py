#!/usr/bin/env python3
"""Independent source-sized check of the two-stage optimal frame.

No imports of the construction, codec, or primary verifier. This checker uses
literal integer quotient enumeration and direct binary image enumeration.
Finite replay corroborates, and does not replace, the all-integer proof.
Prepared for @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0.
"""
import argparse
import ast
from collections import Counter
import hashlib
import itertools
import json
from math import prod
from pathlib import Path
import random

SOURCE_SHA = '2ca4d7550fcae5b757ec500f87aee1d2ef9f64b59e4abe2bda93319521304af8'
SELECT = (0, 1, 2, 4)
SPARSE = (
    ((64, 1), (65, -1), (96, -1), (97, 1)),
    ((10, 1), (11, -1), (62, 1), (63, -1)),
    ((14, 1), (15, -1), (41, 1), (42, -1)),
    ((18, 1), (19, -1), (39, 1), (40, -1)),
)
DUALS = ((4, 64), (10, 70), (14, 52), (18, 54))
CAPS = (169, 1, 13, 13)
CHARACTERS = ((0, 0), (1, 0), (0, 1), (1, 1))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def add(x, y):
    return [a + b for a, b in zip(x, y)]


def round52(n):
    # Quotient/remainder implementation, including signed half ties.
    quotient, remainder = divmod(abs(n), 52)
    result = quotient + (2 * remainder >= 52)
    return result if n >= 0 else -result


def quotient_set(s):
    # The closed residual interval supplies candidates only; every accepted
    # candidate is tested with the original rounded identity.
    lo = -((26 + s) // 4)
    hi = (26 - s) // 4
    return [q for q in range(lo, hi + 1) if round52(s + 56 * q) == q]


def joint_table(s):
    table = [[0, 0], [0, 0]]
    totals = set()
    for last in quotient_set(s):
        for first in quotient_set(s + 56 * last):
            total = first + last
            need(total not in totals, 'two quotient pairs share a total')
            totals.add(total)
            step = total - round52(s + 56 * total)
            need(step == last and step - round52(s + 56 * step) == 0,
                 'literal total dynamics disagree with quotient enumeration')
            table[total & 1][last & 1] += 1
    need(totals and max(totals) - min(totals) + 1 == len(totals),
         'two-stage total set is not an interval')
    return table


def walsh(table):
    return tuple(sum((-1) ** (a * p + b * q) * table[p][q]
                     for p, q in itertools.product(range(2), repeat=2))
                 for a, b in CHARACTERS)


def apply_frame(x, inverse=False, columns=SPARSE, selectors=SELECT):
    result = list(x)
    factor = -1 if inverse else 1
    for source, col in zip(selectors, columns):
        for target, coefficient in col:
            result[target] += factor * coefficient * x[source]
    return result


def bitvector(vector):
    return sum((value & 1) << i for i, value in enumerate(vector))


def load_source(path):
    blob = Path(path).read_bytes()
    need(hashlib.sha256(blob).hexdigest() == SOURCE_SHA, 'source SHA mismatch')
    raw = json.loads(blob)['mode_columns']
    need(len(raw) == 8 and all(len(col) == 112 for col in raw), 'source dimensions')
    need(all(type(v) is int for col in raw for v in col), 'noninteger source')
    return list(zip(*raw)), raw


def check_declared_constants(path):
    tree = ast.parse(Path(path).read_text())
    actual = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in ('SELECTORS', 'COLUMNS', 'DUAL_ROWS'):
                actual[target.id] = ast.literal_eval(node.value)
    need(actual == {'SELECTORS': SELECT, 'COLUMNS': SPARSE, 'DUAL_ROWS': DUALS},
         'primary frame constants differ from independently checked witness')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parent.parent / 'precision-state-frontier' / 'FIXTURE.json')
    parser.add_argument('--construction', type=Path, default=Path(__file__).resolve().with_name('construction.py'))
    args = parser.parse_args()
    matrix, columns = load_source(args.source)
    check_declared_constants(args.construction)
    projection = lambda x: [dot(col, x) for col in columns]
    lift = lambda q: [dot(row, q) for row in matrix]
    kernel = lambda x: add(x, [-v for v in lift([round52(a) for a in projection(x)])])
    forward = lambda x: kernel(apply_frame(kernel([2 * a for a in x])))

    for j, col in enumerate(columns):
        need(projection(col) == [56 * (i == j) for i in range(8)], 'source Gram')
    vcols = []
    for sparse in SPARSE:
        dense = [0] * 112
        for i, coefficient in sparse:
            dense[i] = coefficient
        vcols.append(dense)
        need(projection(dense) == [0] * 8, 'exact mode preservation')
        need(all(dense[i] == 0 for i in SELECT), 'E V is not zero')
    for i, pair in enumerate(DUALS):
        need(all(sum(matrix[k][j] for k in pair) % 2 == 0 for j in range(8)), 'dual does not annihilate M')
        need([sum(v[k] for k in pair) for v in vcols] == [int(i == j) for j in range(4)], 'dual V is not identity')
    for i in range(112):
        e = [int(i == j) for j in range(112)]
        need(apply_frame(apply_frame(e), True) == e and apply_frame(apply_frame(e, True)) == e,
             'integer inverse failure')
        need(projection(apply_frame(e)) == projection(e), 'basis mode failure')

    binary = [[(mask >> j) & 1 for j in range(8)] for mask in range(256)]
    images = [bitvector(lift(q)) for q in binary]
    moved = [bitvector(apply_frame(lift(q), True)) for q in binary]
    need(len(set(images)) == len(set(moved)) == 16, 'binary source rank')
    need(set(images) & set(moved) == {0}, 'binary image separation')
    code = [i for i, image in enumerate(images) if image == 0]
    need(len(code) == 16, 'code size')
    need(Counter(c.bit_count() for c in code) == {0: 1, 4: 14, 8: 1}, 'source weight enumerator')
    need(all((a & b).bit_count() % 2 == 0 for a in code for b in code), 'code self-orthogonality')
    em_kernel = [q for q in range(256) if all(dot(matrix[k], binary[q]) % 2 == 0 for k in SELECT)]
    need(em_kernel == code, 'selector code kernel')

    # Full quotient census, not a sampled floating-point model.
    exceptional = {}
    for s in range(-10000, 10001):
        q = quotient_set(s)
        expected_length = 12 if s % 4 == 2 and abs(s) <= 26 else 13
        need(len(q) == expected_length and q == list(range(q[0], q[-1] + 1)), 'scalar Q classification')
        table = joint_table(s)
        transform = walsh(table)
        need(all(abs(a) <= b for a, b in zip(transform, CAPS)), 'Walsh cap failed')
        if s in range(2, 31, 4):
            exceptional[str(s)] = {'table': table, 'walsh': transform}
    zero = joint_table(0)
    need(zero == [[49, 36], [42, 42]] and walsh(zero) == CAPS, 'zero scalar count')

    # Enumerate all binary q1,q2, group by literal 112-bit inverse syndrome.
    # This counts all 256 zero-mode affine parity cosets without Fourier code.
    weights = [prod(7 if bit == 0 else 6 for bit in q) for q in binary]
    syndrome_counts = Counter()
    for first in range(256):
        for last in range(256):
            syndrome_counts[images[first] ^ moved[last]] += weights[first] * weights[last]
    one_stage = sum(weights[c] for c in code)
    maximum = syndrome_counts[0]
    need(len(syndrome_counts) == 256, 'combined binary rank')
    need(maximum == max(syndrome_counts.values()) == one_stage ** 2 == 2601832488601921,
         'optimal source count')
    need((maximum - 1).bit_length() == 52, 'packed tag width')

    # Reconstruct every zero-fiber parity block at three different corners.
    # The full Cartesian count is exact; these are finite trajectory controls.
    roundtrips = 0
    for first in code:
        for last in code:
            for choice in range(3):
                q2 = []
                q1 = []
                for j in range(8):
                    choices2 = [q for q in range(-6, 7) if q % 2 == binary[last][j]]
                    b = choices2[(0, len(choices2) // 2, -1)[choice]]
                    choices1 = [q for q in range(-6, 7) if q % 2 == binary[first][j]]
                    a = choices1[(0, len(choices1) // 2, -1)[choice]] - 14 * b
                    q2.append(b)
                    q1.append(a)
                numerator = add(apply_frame(lift(q2), True), lift(q1))
                need(all(a % 2 == 0 for a in numerator), 'zero block parity failure')
                x = [a // 2 for a in numerator]
                need(forward(x) == [0] * 112, 'zero block forward replay')
                need(projection([2 * a for a in x]) == [56 * (a + b) for a, b in zip(q1, q2)], 'zero total pin')
                roundtrips += 1

    # Arbitrary outputs from literal source-sized inputs; no codec imported.
    rng = random.Random(908173)
    inputs = [[(1 if i == j else 0) * magnitude for i in range(112)]
              for j in range(112) for magnitude in (-26, 1, 52)]
    inputs.extend([[rng.randrange(-200, 201) for _ in range(112)] for _ in range(48)])
    omitted_frame_detected = False
    outputs = set()
    for x in inputs:
        y = forward(x)
        outputs.add(tuple(y))
        s = projection(y)
        raw_total = [2 * a - b for a, b in zip(projection(x), s)]
        need(all(a % 56 == 0 for a in raw_total), 'total quotient not integral')
        total = [a // 56 for a in raw_total]
        q2 = [t - round52(a + 56 * t) for a, t in zip(s, total)]
        q1 = [t - q for t, q in zip(total, q2)]
        need(all(q in quotient_set(a) and first in quotient_set(a + 56 * q)
                 for a, q, first in zip(s, q2, q1)), 'reverse quotient membership')
        numerator = add(apply_frame(add(y, lift(q2)), True), lift(q1))
        need(numerator == [2 * a for a in x], 'actual inverse chronology')
        omitted_frame_detected |= add(add(y, lift(q2)), lift(q1)) != numerator
        roundtrips += 1

    # Necessary separation is tested by deliberately restoring one overlap.
    # All parity pairs have positive scalar weights, so every new nonzero
    # image intersection contributes strictly more than the C x C baseline.
    missing = SPARSE[:-1] + ((),)
    badimages = [bitvector(apply_frame(lift(q), True, columns=missing)) for q in binary]
    intersection = set(images) & set(badimages)
    need(len(intersection) > 1, 'negative separation control has no overlap')
    badzero = sum(weights[a] * weights[b] for a in range(256) for b in range(256)
                  if images[a] == badimages[b])
    need(badzero > maximum, 'positive extra overlap inputs not detected')
    badcolumn = list(SPARSE)
    badcolumn[0] = ((64, 2),) + SPARSE[0][1:]
    badv = [0] * 112
    for i, v in badcolumn[0]:
        badv[i] = v
    need(projection(badv) != [0] * 8, 'negative mode control survived')
    badselectors = (64, 1, 2, 4)
    e = [int(i == 64) for i in range(112)]
    need(apply_frame(apply_frame(e, selectors=badselectors), True, selectors=badselectors) != e,
         'negative inverse control survived')
    need(round52(26) == 1 and round52(-26) == -1, 'half-away tie control')
    need(min(sum(joint_table(2), [])) > min(sum(zero, [])), 'entrywise-domination false control')
    need(omitted_frame_detected, 'omitted inverse frame was not detected')
    identityzero = sum(weights[a] * weights[b] for a in range(256) for b in range(256)
                       if images[a] == images[b])
    need(identityzero > maximum, 'identity frame should not be optimal')

    print(json.dumps({
        'status': 'PASS_INDEPENDENT_OPTIMAL_FRAME', 'source_sha256': SOURCE_SHA,
        'scalar_cases': 20001, 'scalar_domain': [-10000, 10000],
        'exceptional_tables': exceptional, 'binary_quotient_pairs': 65536,
        'affine_binary_cosets': len(syndrome_counts), 'source_image_intersection_size': 1,
        'one_stage_states': one_stage, 'optimal_two_stage_states': maximum, 'tag_bits': 52,
        'basis_inverse_checks': 224, 'zero_parity_blocks': 256,
        'actual_forward_reverse_checks': roundtrips, 'distinct_sample_outputs': len(outputs),
        'removed_column_intersection_size': len(intersection),
        'removed_column_zero_states': badzero, 'identity_zero_states': identityzero,
        'negative_controls': ['mode coefficient', 'inverse selector', 'image overlap',
                              'half-away ties', 'entrywise domination', 'omitted inverse frame',
                              'identity frame optimality'],
        'scope': 'Exact finite checks plus source identities; universal Walsh proof is in PROOF.md; no physical cost or new kappa claim.'
    }, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
