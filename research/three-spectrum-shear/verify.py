"""Exact corroboration of the new three-value shear obstruction, not a census."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from fractions import Fraction

from exact import I, ONE, ZERO, Q, encode_matrix, factor, identity, kernel, multiply, rref

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(predicate, message):
    if not predicate:
        raise ValueError(message)


def column_matrix(vectors):
    return [list(row) for row in zip(*vectors)]


def canonical_h(z, first_sign):
    directions = [(ONE, ZERO, ZERO, ZERO), (ZERO, ONE, ZERO, ZERO),
                  (ZERO, ZERO, ONE, ZERO), (ONE, -ONE, ONE, ZERO)]
    columns = []
    for beta_slot in range(4):
        word = identity(4)
        for j in range(4):
            beta = ONE if j == beta_slot else ZERO
            covector = (ONE, ONE, ONE, beta)
            word = multiply(factor(z, first_sign * (-1) ** j,
                                   directions[j], covector), word)
        require([row[:3] for row in word[:3]] == identity(3), 'loop on Y')
        require(word[3] == identity(4)[3], 'outside input restoration')
        columns.append([word[r][3] / (z - ONE) for r in range(3)])
    return column_matrix(columns)


def loop_certificate():
    records = []
    for first_sign, expected_rank in ((1, 1), (-1, 2)):
        at_i, at_minus = canonical_h(I, first_sign), canonical_h(-ONE, first_sign)
        difference = [[at_i[r][c] - at_minus[r][c] for c in range(4)]
                      for r in range(3)]
        basis = kernel(difference)
        projected = multiply(at_i, column_matrix(basis))
        require(len(rref(projected)[1]) == expected_rank, 'constant image rank')
        expected_basis = ([[ONE, ONE, ZERO, ZERO], [ZERO, ZERO, ONE, ONE]]
                          if first_sign == 1 else
                          [[ONE, ZERO, ZERO, ZERO], [ZERO, ONE, ONE, ZERO],
                           [ZERO, ZERO, ZERO, ONE]])
        require(len(basis) == len(expected_basis), 'constraint nullity')
        require(multiply(difference, column_matrix(expected_basis)) ==
                [[ZERO] * len(expected_basis) for _ in range(3)], 'beta constraints')
        records.append({'signs': '+-+-' if first_sign == 1 else '-+-+',
                        'H_i': encode_matrix(at_i), 'H_minus_one': encode_matrix(at_minus),
                        'kernel_basis': encode_matrix(basis),
                        'constant_image_rank': expected_rank})
    return records


def paired_collapse():
    cases = 0
    for d_int, u_int, v_int in itertools.product((-1, 1, 2), repeat=3):
        d, u, v = Q(Fraction(d_int)), Q(Fraction(u_int)), Q(Fraction(v_int))
        b1 = [ONE, ONE / d, u, v]
        b2 = [d * x for x in b1]
        a1, a2 = identity(4)[:2]
        shear_direction = [a1[j] - d * a2[j] for j in range(4)]
        require(sum((b1[j] * shear_direction[j] for j in range(4)), ZERO) == ZERO,
                'square-zero collapse')
        for z in (I, -ONE, Q(Fraction(2))):
            word = multiply(factor(z, -1, a2, b2), factor(z, 1, a1, b1))
            expected = identity(4)
            for r in range(4):
                for c in range(4):
                    expected[r][c] += (z - ONE) * shear_direction[r] * b1[c]
            require(word == expected, 'literal paired collapse')
            cases += 1
    return cases


def upper_word(z, omitted=None):
    word = identity(8)
    for source in range(3):
        a1 = identity(8)[source]
        a2 = a1[:]
        a2[source + 3] = -ONE
        for offset, (sign, direction) in enumerate(((1, a1), (-1, a2))):
            if source * 2 + offset != omitted:
                word = multiply(factor(z, sign, direction, a1), word)
    return word


def expected_upper(z):
    word = identity(8)
    for source in range(3):
        word[source + 3][source] = z - ONE
    return word


def two_value_constraints():
    active = (I, -ONE)
    negative_ratio = [-(ONE / z) for z in active]
    inverse_values = [ONE / z for z in active]
    g = [z - ONE for z in active]
    require(negative_ratio[0] != negative_ratio[1], 'negative first-call exclusion')
    require(inverse_values[0] != inverse_values[1], 'alternating row constraint')
    require(g[0] != g[1], 'positive pair row constraint')
    signs = [list(pattern) for pattern in itertools.product((-1, 1), repeat=4)
             if sum(pattern) % 4 == 0]
    require(len(signs) == 8, 'four-call determinant patterns')
    surviving = [s for s in signs if s[0] == 1 and s[-1] == -1]
    require(surviving == [[1, -1, 1, -1], [1, 1, -1, -1]], 'endpoint sign screen')
    for count in (3, 5):
        require(not any(sum(s) % 4 == 0 for s in
                        itertools.product((-1, 1), repeat=count)), 'odd determinant')
    return {'negative_first_ratios': [x.encode() for x in negative_ratio],
            'inverse_values': [x.encode() for x in inverse_values],
            'positive_parameters': [x.encode() for x in g],
            'determinant_patterns': signs, 'endpoint_patterns': surviving}


def controls():
    rejected = []
    for omitted in range(6):
        require(upper_word(I, omitted) != expected_upper(I), 'omitted-call control')
        rejected.append(f'omitted_call_{omitted + 1}')
    # At one active value the first-row two-value argument has no exclusion.
    require(len(rref([[ONE, -(ONE / I)]])[1]) == 1, 'binary interpolation control')
    require(len(rref([[ONE, -(ONE / I)], [ONE, ONE]])[1]) == 2,
            'two active values restore exclusion')
    rejected.append('single_active_value_is_insufficient')
    try:
        factor(I, 1, [ONE, ZERO], [ZERO, ONE])
    except ValueError:
        rejected.append('nonidempotent_paid_factor')
    else:
        raise ValueError('nonidempotent factor was accepted')
    try:
        _ = ONE / ZERO
    except ZeroDivisionError:
        rejected.append('zero_character')
    else:
        raise ValueError('zero character was accepted')
    return rejected


def source_hashes():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    hashes = {}
    for row in manifest['files']:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            require(digest == row['sha256'], 'predecessor input bytes changed')
            hashes[row['path']] = digest
    for name in ('README.md', 'PROOF.md', 'TASK.json', 'SOURCES.json',
                 'VERIFY.json', 'exact.py', 'verify.py'):
        path = PACKAGE / name
        hashes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def certificate():
    samples = (ONE, I, -ONE, -I, Q(Fraction(2)), Q(Fraction(1, 2), Fraction(1, 2)))
    for z in samples:
        require(upper_word(z) == expected_upper(z), 'complete eight-role upper endpoint')
    return {'schema': 'three-spectrum-shear/v1', 'claim_type': 'scoped proof',
            'minimum_calls': 6, 'spectrum': ['1', 'i', '-1'],
            'two_value_constraints': two_value_constraints(),
            'canonical_loops': loop_certificate(), 'pair_collapse_cases': paired_collapse(),
            'upper_endpoint_samples': len(samples), 'upper_roles': 8,
            'controls': controls(), 'source_sha256': source_hashes()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='write a new generated receipt exclusively')
    parser.add_argument('--certificate', type=Path, default=PACKAGE / 'RESULT.json')
    args = parser.parse_args()
    result = certificate()
    canonical = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.write:
        with args.write.open('x') as stream:
            stream.write(canonical)
    else:
        loaded = json.loads(args.certificate.read_text())
        require(json.dumps(loaded, sort_keys=True, indent=2) + '\n' == canonical,
                'receipt differs, including value types or source hashes')
    print('PASS_THREE_SPECTRUM_SHEAR minimum=6 loops=2 collapse_cases=81 '
          'upper_samples=6 controls=9 no_new_kappa')


if __name__ == '__main__':
    main()
