#!/usr/bin/env python3
"""Independent exact lattice/certificate oracle; @CubeJerry/AI, Apache-2.0.

The oracle reconstructs rational period bases, uses their inverse matrices to
classify cosets, and evaluates the native complex tensor directly. It does not
use the production quotient formulas to decide the certificate predicates.
"""
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

import construction as impl
from kernel import block, real_map

HERE = Path(__file__).resolve().parent
N = 16
MOD = (8, 4, 4, 4, 4)
KEYS = tuple(product(*(range(m) for m in MOD)))
ZERO = (0,) * N
W = tuple(tuple((-1) ** ((i & j).bit_count()) for j in range(N))
          for i in range(N))
CHECKS = 0
CONTROLS = []


def require(condition, message):
    global CHECKS
    CHECKS += 1
    if not condition:
        raise ValueError(message)


def reject(label, action, reason=None):
    try:
        action()
    except (ValueError, TypeError, KeyError, IndexError) as error:
        require(reason is None or reason in str(error), 'Intended failure control: ' + label)
        CONTROLS.append(label)
    else:
        raise ValueError('Failure control was accepted: ' + label)


def mv(matrix, vector):
    return tuple(sum(a * b for a, b in zip(row, vector)) for row in matrix)


def transform(vector):
    """Independent butterfly, whereas construction.walsh uses dense rows."""
    out = list(vector)
    width = 1
    while width < N:
        for start in range(0, N, 2 * width):
            for j in range(start, start + width):
                a, b = out[j], out[j + width]
                out[j], out[j + width] = a + b, a - b
        width *= 2
    return tuple(out)


def inverse_and_determinant(matrix):
    n = len(matrix)
    rows = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    determinant = Fraction(1)
    for j in range(n):
        pivot = next((k for k in range(j, n) if rows[k][j]), None)
        require(pivot is not None, 'Nonsingular period matrix')
        if pivot != j:
            rows[j], rows[pivot] = rows[pivot], rows[j]
            determinant = -determinant
        q = rows[j][j]
        determinant *= q
        rows[j] = [x / q for x in rows[j]]
        for k in range(n):
            if k != j and rows[k][j]:
                q = rows[k][j]
                rows[k] = [a - q * b for a, b in zip(rows[k], rows[j])]
    return tuple(tuple(row[n:]) for row in rows), determinant


def rank_mod2(matrix):
    pivots = {}
    for row in matrix:
        bits = sum((v % 2) << j for j, v in enumerate(row))
        while bits:
            p = bits.bit_length() - 1
            if p in pivots:
                bits ^= pivots[p]
            else:
                pivots[p] = bits
                break
    return len(pivots)


def unit(i):
    return tuple(int(i == j) for j in range(N))


def add(a, b, scale=1):
    return tuple(x + scale * y for x, y in zip(a, b))


def kernel_column(s):
    out = list(unit(s))
    out[0] = s.bit_count() - 1
    for j in range(4):
        if s >> j & 1:
            out[1 << j] = -1
    return tuple(out)


def period_bases():
    pairs = tuple(s for s in range(N) if s.bit_count() == 2)
    high = tuple(s for s in range(N) if s.bit_count() >= 3)
    u = [(4,) + (0,) * 15]
    u += [tuple(2 * x for x in add(unit(1 << j), unit(0), -1))
          for j in range(4)]
    v = []
    for s in high:
        out = kernel_column(s)
        for t in pairs:
            if t & s == t:
                out = add(out, kernel_column(t), -1)
        v.append(out)
    lcols = u + [kernel_column(s) for s in pairs + high]
    mcols = [add(a, b) for a, b in zip(u, v)]
    mcols += [kernel_column(s) for s in pairs]
    mcols += [tuple(2 * x for x in a) for a in v]
    gcols = []
    for column in mcols:
        numerator = transform(column)
        require(all(x % 4 == 0 for x in numerator), 'Integral image periods')
        gcols.append(tuple(x // 4 for x in numerator))
    return tuple(zip(*lcols)), tuple(zip(*mcols)), tuple(zip(*gcols))


def period_checker(matrix, image, expected=2048):
    inverse, determinant = inverse_and_determinant(matrix)
    require(abs(determinant) == expected, 'Declared period index')
    require(all((8 * x).denominator == 1 for row in inverse for x in row),
            'Eightfold inverse period matrix is integral')
    scaled = tuple(tuple(int(8 * x) for x in row) for row in inverse)
    for j, column in enumerate(zip(*matrix)):
        require(mv(scaled, column) == tuple(8 * int(i == j) for i in range(N)),
                'Independent inverse period matrix')
        if image is not None:
            require(transform(column) == tuple(4 * row[j] for row in image),
                    'Period carries exact ideal image')
    return scaled


def normal_key(inverse8, vector):
    return tuple(x % 8 for x in mv(inverse8, vector))


def negate(key):
    return tuple(-x % m for x, m in zip(key, MOD))


def weighted_zero(offset):
    real = imag = 0
    phase = ((1, 0), (0, -1), (-1, 0), (0, 1))
    for j, value in enumerate(offset):
        a, b = phase[j.bit_count() % 4]
        real += a * value
        imag += b * value
    return real == imag == 0


def validate_forward(forward, reps, target_labels, inverse8):
    require(set(forward) == set(KEYS), 'Complete source classes')
    for key, offset in forward.items():
        require(len(offset) == N and all(type(x) is int for x in offset),
                'Integer correction dimensions')
        require(sum(x * x for x in offset) <= 64, 'Real error radius')
        require(weighted_zero(offset), 'Native weighted sum cancellation')
        require(forward[negate(key)] == tuple(-x for x in offset),
                'Negation orbit consistency')
    backward = {}
    destinations = {}
    for key in KEYS:
        offset = forward[key]
        numerator = add(transform(reps[key]), offset)
        require(all(x % 4 == 0 for x in numerator), 'Source integrality')
        output = tuple(x // 4 for x in numerator)
        destination = target_labels[normal_key(inverse8, output)]
        require(destination not in backward, 'Target class collision')
        inverse_numerator = tuple(-x for x in transform(offset))
        require(all(x % 4 == 0 for x in inverse_numerator), 'Inverse integrality')
        inverse = tuple(x // 4 for x in inverse_numerator)
        require(sum(x * x for x in inverse) == sum(x * x for x in offset),
                'Orthogonal inverse error')
        require(weighted_zero(inverse), 'Inverse weighted sum cancellation')
        backward[destination] = inverse
        destinations[key] = destination
    require(set(backward) == set(KEYS), 'Complete target classes')
    return backward, destinations


def phase(value, exponent):
    a, b = value
    c, d = ((1, 0), (0, 1), (-1, 0), (0, -1))[exponent % 4]
    return a * c - b * d, a * d + b * c


def ideal_scaled4(values, inverse=False):
    """4U from its native tensor entries, without Walsh or D factorization."""
    result = []
    for r in range(N):
        total_re = total_im = 0
        for s, value in enumerate(values):
            exponent = 4 - (r ^ s).bit_count()
            a, b = phase(value, -exponent if inverse else exponent)
            total_re -= a
            total_im -= b
        result.append((total_re, total_im))
    return tuple(result)


def scaled_error(values, output, inverse=False):
    return sum((4 * a - c) ** 2 + (4 * b - d) ** 2
               for (a, b), (c, d) in zip(output, ideal_scaled4(values, inverse)))


def native_check(values, tables, inverse=False):
    before = tuple(tuple(z) for z in values)
    output = block(values, tables, inverse)
    require(tuple(tuple(z) for z in values) == before, 'Input nonmutation')
    require(scaled_error(values, output, inverse) <= 128, 'Sharp native error')
    require(tuple(map(sum, zip(*values))) == tuple(map(sum, zip(*output))),
            'Exact native complex sum')
    rotated = tuple(phase(z, 1) for z in values)
    require(block(rotated, tables, inverse) == tuple(phase(z, 1) for z in output),
            'Global Gaussian phase covariance')
    require(block(output, tables, not inverse) == before, 'Literal native inverse')
    return scaled_error(values, output, inverse)


def main():
    lmat, mmat, gmat = period_bases()
    _, determinant_l = inverse_and_determinant(lmat)
    require(abs(determinant_l) == 64, 'Coarse integrality index64')
    for column in zip(*lmat):
        require(all(x % 4 == 0 for x in transform(column)), 'Coarse integrality periods')
    imat = period_checker(mmat, gmat)
    igmat = period_checker(gmat, mmat)
    require([rank_mod2(x) for x in (mmat, gmat, mmat + gmat)] == [11, 11, 11],
            'Both parity kernels agree on the minimizing period')
    image_l = tuple(zip(*(tuple(v // 4 for v in transform(c)) for c in zip(*lmat))))
    require([rank_mod2(x) for x in (lmat, image_l, lmat + image_l)] == [11, 11, 16],
            'Disjoint five-dimensional parity kernels in L')
    for j in range(N):
        require(transform(unit(j)) == tuple(row[j] for row in W), 'Walsh convention')
        require(transform(transform(unit(j))) == tuple(16 * x for x in unit(j)),
                'Exact Walsh square')
    source_reps = {key: impl.source_representative(key) for key in KEYS}
    target_reps = {key: impl.target_representative(key) for key in KEYS}
    source_labels = {normal_key(imat, z): key for key, z in source_reps.items()}
    target_labels = {normal_key(igmat, z): key for key, z in target_reps.items()}
    require(len(source_labels) == len(target_labels) == 2048,
            'Independent source and target normal forms')
    for key in KEYS:
        require(impl.source_key(source_reps[key]) == key, 'Source section')
        require(impl.target_key(target_reps[key]) == key, 'Target section')
    for column in zip(*mmat):
        require(impl.source_key(column) == (0,) * 5, 'Source classifier periods')
    for column in zip(*gmat):
        require(impl.target_key(column) == (0,) * 5, 'Target classifier periods')
    certificate = json.loads((HERE / 'CERTIFICATE.json').read_text())
    require(certificate['schema_version'] == 1 and certificate['moduli'] == list(MOD),
            'Certificate format')
    require(len(certificate['rows']) == 1008, '1008 free sign orbits')
    forward = {}
    for key, offset in certificate['rows']:
        require(type(key) is list and all(type(x) is int for x in key), 'Integer key')
        key, offset = tuple(key), tuple(offset)
        require(key in KEYS and key < negate(key), 'Canonical nonfixed source orbit')
        require(key not in forward and negate(key) not in forward, 'Unique orbit witness')
        forward[key] = offset
        forward[negate(key)] = tuple(-x for x in offset)
    fixed = [key for key in KEYS if key == negate(key)]
    require(len(fixed) == 32, 'Exactly32 fixed classes')
    for key in fixed:
        require(key not in forward, 'Fixed/free disjointness')
        forward[key] = ZERO
    backward, destinations = validate_forward(forward, source_reps, target_labels, igmat)
    tables = impl.build_tables()
    require(tables == (forward, backward), 'Production tables match independent certificate')
    max_forward = max(abs(x) for e in forward.values() for x in e)
    max_inverse = max(abs(x) for e in backward.values() for x in e)
    require((max_forward, max_inverse) == (3, 5), 'Coordinate correction maxima3/5')
    require(max(sum(x * x for x in e) for e in forward.values()) == 64,
            'Attained real correction energy64')
    for inverse, representatives, table in ((False, source_reps, forward),
                                            (True, target_reps, backward)):
        for key, vector in representatives.items():
            output = real_map(vector, table, inverse)
            require(real_map(output, forward if inverse else backward, not inverse) == vector,
                    'Both real composition orders on every class')
            difference = add(tuple(4 * x for x in output), transform(vector), -1)
            require(difference == table[key], 'Literal real correction')
    max_native_energy = 0
    for inverse, representatives in ((False, source_reps), (True, target_reps)):
        for index, key in enumerate(KEYS):
            a, b = representatives[key], representatives[KEYS[(73 * index + 19) % 2048]]
            if inverse:
                values = tuple(phase((-x, -y), -j.bit_count())
                               for j, (x, y) in enumerate(zip(a, b)))
            else:
                values = tuple(phase((x, y), j.bit_count())
                               for j, (x, y) in enumerate(zip(a, b)))
            max_native_energy = max(max_native_energy, native_check(values, tables, inverse))
    witness = ((2, 2),) + ((0, 0),) * 15
    for inverse in (False, True):
        energy = native_check(witness, tables, inverse)
        require(energy == 128, 'Sharp half-grid witness')
        max_native_energy = max(max_native_energy, energy)
    zero = ((0, 0),) * 16
    require(block(zero, tables) == block(zero, tables, True) == zero, 'Zero fixed')
    large_cases = 0
    for bits in (1, 128, 1024, 4090):
        size = (1 << bits) - 1
        values = tuple((((-1) ** j) * (size - j), ((-1) ** (j // 2)) * (size + 3 * j))
                       for j in range(16))
        for inverse in (False, True):
            native_check(values, tables, inverse)
            large_cases += 1
    for index in (0, 1, 31, 511, 2047):
        vector = source_reps[KEYS[index]]
        shift = mv(mmat, tuple(((-1) ** j) * (j + 1) for j in range(N)))
        image = mv(gmat, tuple(((-1) ** j) * (j + 1) for j in range(N)))
        require(real_map(add(vector, shift), forward) == add(real_map(vector, forward), image),
                'Affine period translation')
    first = ((1, 0),) + ((0, 0),) * 15
    fourth = first
    for _ in range(4):
        fourth = block(fourth, tables)
    expected_fourth = ((1, 0), (0, -1), (0, 0), (0, 0), (0, -1), (0, 0),
                       (0, 0), (0, -1), (0, 0), (0, 0), (-1, 0), (0, 0),
                       (1, 0), (0, 2), (0, 1), (0, 0))
    require(fourth == expected_fourth and fourth != first, 'Retained fourth-power counterexample')

    # Preserve local edge predicates while deliberately breaking orbit matching.
    alternatives = {}
    for offset in forward.values():
        alternatives.setdefault(tuple(x % 4 for x in offset), set()).add(offset)
    mutation = None
    for key in KEYS:
        if key == negate(key):
            continue
        old = forward[key]
        for candidate in sorted(alternatives[tuple(x % 4 for x in old)]):
            numerator = add(transform(source_reps[key]), candidate)
            target = target_labels[normal_key(igmat, tuple(x // 4 for x in numerator))]
            if target not in (destinations[key], destinations[negate(key)]):
                mutation = key, candidate
                break
        if mutation is not None:
            break
    require(mutation is not None, 'Nontrivial locally admissible mutation exists')
    key, alternative = mutation
    bad = dict(forward)
    bad[key] = alternative
    reject('locally admissible broken negation',
           lambda: validate_forward(bad, source_reps, target_labels, igmat),
           'Negation orbit consistency')
    bad[negate(key)] = tuple(-x for x in alternative)
    reject('locally admissible sign-paired target collision',
           lambda: validate_forward(bad, source_reps, target_labels, igmat),
           'Target class collision')
    corrupted = [list(row) for row in mmat]
    corrupted[0][0] += 1
    reject('corrupted affine period', lambda: period_checker(tuple(map(tuple, corrupted)), gmat))
    reject('false 127/16 native squared-radius claim',
           lambda: require(scaled_error(witness, block(witness, tables)) <= 127, 'Too-small radius'))
    clean = ((4, 0),) + ((0, 0),) * 15
    wrong_phase = tuple((-a, -b) for a, b in block(clean, tables))
    reject('wrong native phase with reversible endpoint',
           lambda: require(scaled_error(clean, wrong_phase) <= 128, 'Wrong native operator'))
    reject('forward substituted for literal inverse',
           lambda: require(block(block(first, tables), tables) == first, 'Wrong inverse'))
    for label, value, inverse in (
            ('fifteen coordinates', zero[:-1], False),
            ('noninteger component', ((0.5, 0),) + zero[1:], False),
            ('boolean component', ((True, 0),) + zero[1:], False),
            ('4097-bit component', ((1 << 4096, 0),) + zero[1:], False),
            ('nonboolean inverse selector', zero, 1)):
        reject(label, lambda value=value, inverse=inverse: block(value, tables, inverse))
    hashes = {path.relative_to(HERE).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(HERE.rglob('*'))
              if path.is_file() and '__pycache__' not in path.parts}
    print(json.dumps({
        'status': 'PASS_PHASE_COVARIANT_GRID', 'python': sys.version.split()[0],
        'assertions_enabled': __debug__, 'predicate_checks': CHECKS,
        'real_source_classes': 2048, 'real_target_classes': 2048,
        'fixed_classes': 32, 'free_negation_orbits': 1008,
        'native_fixture_pairs': 4096, 'large_integer_fixtures': large_cases,
        'all_native_class_pairs_enumerated': False,
        'coordinate_correction_maxima': [max_forward, max_inverse],
        'max_native_squared_error_times16': max_native_energy,
        'minimal_real_affine_period_index': 2048,
        'minimal_native_affine_period_index': 4194304,
        'fourth_power_counterexample': {'input': first, 'fourth_iterate': fourth},
        'failure_controls': CONTROLS, 'sha256': hashes,
        'scope': 'Finite certificate plus scoped all-integer proof; no multiplication theorem or tariff admission'
    }, sort_keys=True))


if __name__ == '__main__':
    main()
