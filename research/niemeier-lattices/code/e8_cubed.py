"""Exact E8^3 norm-four shell, binary fit, and dyadic scalar factorization.

Coordinates are doubled: roots have squared norm 8 and the norm-four shell
has squared norm 16. All rank calculations are over finite fields; no
floating-point rank or sampled all-pairs assertion is used.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
import hashlib
import json
import numpy as np


def require(condition, message):
    if not condition:
        raise ValueError(message)


def insert_binary(basis, value):
    value = int(value)
    while value:
        pivot = value.bit_length() - 1
        if pivot in basis:
            value ^= basis[pivot]
        else:
            basis[pivot] = value
            return True
    return False


def inverse_binary(matrix):
    size = len(matrix)
    work = np.concatenate((matrix.copy(), np.eye(size, dtype=np.uint8)), axis=1)
    for col in range(size):
        choices = np.flatnonzero(work[col:, col])
        require(len(choices) > 0, 'Invertible binary Gram matrix')
        pivot = col + int(choices[0])
        work[[col, pivot]] = work[[pivot, col]]
        for row in range(size):
            if row != col and work[row, col]:
                work[row] ^= work[col]
    return work[:, size:]


def symplectic_transform(matrix):
    size = len(matrix)
    require(size % 2 == 0 and np.array_equal(matrix, matrix.T)
            and not np.diag(matrix).any(), 'Alternating binary form')
    transform = np.eye(size, dtype=np.uint8)
    work = matrix.copy()
    for first in range(0, size, 2):
        choices = np.argwhere(work[first:, first:])
        require(len(choices) > 0, 'Nondegenerate alternating form')
        a, b = (int(value) + first for value in choices[0])
        for current, target in ((a, first), (b if b != first else a, first + 1)):
            work[[current, target]] = work[[target, current]]
            work[:, [current, target]] = work[:, [target, current]]
            transform[[current, target]] = transform[[target, current]]
        for row in range(first + 2, size):
            left, right = int(work[row, first + 1]), int(work[row, first])
            if left:
                transform[row] ^= transform[first]
            if right:
                transform[row] ^= transform[first + 1]
        work = (transform @ matrix @ transform.T) & 1
    target = np.zeros_like(matrix)
    for first in range(0, size, 2):
        target[first, first + 1] = target[first + 1, first] = 1
    require(np.array_equal(work, target), 'Symplectic basis identity')
    return transform


def canonical_lines(vectors):
    array = np.asarray(vectors, dtype=np.int16)
    first = np.argmax(array != 0, axis=1)
    signs = np.where(array[np.arange(len(array)), first] > 0, 1, -1)
    return np.unique(array * signs[:, None], axis=0).astype(np.int16)


def e8_shells():
    roots, fourth = [], []
    for positions in combinations(range(8), 2):
        for signs in product((-2, 2), repeat=2):
            row = np.zeros(8, dtype=np.int16)
            row[list(positions)] = signs
            roots.append(row)
    for signs in product((-1, 1), repeat=8):
        if sum(signs) % 4 == 0:
            roots.append(np.array(signs, dtype=np.int16))
    for coordinate in range(8):
        for sign in (-4, 4):
            row = np.zeros(8, dtype=np.int16)
            row[coordinate] = sign
            fourth.append(row)
    for positions in combinations(range(8), 4):
        for signs in product((-2, 2), repeat=4):
            row = np.zeros(8, dtype=np.int16)
            row[list(positions)] = signs
            fourth.append(row)
    for coordinate in range(8):
        for signs in product((-1, 1), repeat=8):
            row = np.array(signs, dtype=np.int16)
            row[coordinate] *= 3
            if int(row.sum()) % 4 == 0:
                fourth.append(row)
    require(len(roots) == 240 and len(fourth) == 2160, 'E8 shell vector counts')
    roots, fourth = canonical_lines(roots), canonical_lines(fourth)
    require(roots.shape == (120, 8) and fourth.shape == (1080, 8), 'E8 line counts')
    for rows, norm in ((roots, 8), (fourth, 16)):
        require(np.all((rows * rows).sum(axis=1) == norm), 'Exact E8 shell norms')
        require(np.all(rows.sum(axis=1) % 4 == 0), 'Doubled E8 parity condition')
        require(np.all((rows % 2) == (rows[:, :1] % 2)), 'Doubled E8 coordinate parity')
    return roots, fourth


def construct_shell():
    roots, fourth = e8_shells()
    pieces, profiles = [], []
    for block in range(3):
        rows = np.zeros((1080, 24), dtype=np.int16)
        rows[:, 8 * block:8 * (block + 1)] = fourth
        pieces.append(rows)
        profiles.extend([1 << block] * len(rows))
    for first, second in combinations(range(3), 2):
        rows = np.zeros((28800, 24), dtype=np.int16)
        rows[:, 8 * first:8 * (first + 1)] = np.repeat(roots, 240, axis=0)
        rows[:, 8 * second:8 * (second + 1)] = (
            np.tile(np.repeat(roots, 2, axis=0), (120, 1))
            * np.tile([1, -1], 14400)[:, None])
        pieces.append(rows)
        profiles.extend([(1 << first) | (1 << second)] * len(rows))
    rows = np.concatenate(pieces)
    require(rows.shape == (89640, 24), 'E8 cubed norm-four line count')
    require(np.all((rows * rows).sum(axis=1) == 16), 'E8 cubed shell norms')
    require(len({row.tobytes() for row in rows}) == len(rows), 'Distinct canonical lines')
    first = np.argmax(rows != 0, axis=1)
    require(np.all(rows[np.arange(len(rows)), first] > 0), 'Canonical antipodal orientation')
    return roots, fourth, rows, np.array(profiles, dtype=np.uint8)


def binary_labels(roots, ports):
    blocks = ports.shape[1] // 8
    dimension = 8 * blocks + 1
    integer_gram = roots @ roots.T
    require(not (integer_gram % 4).any(), 'Integral E8 lattice pairings')
    gram = ((integer_gram // 4) & 1).astype(np.uint8)
    work, available, selected = gram.copy(), list(range(120)), []
    while work[np.ix_(available, available)].any():
        a, b = np.argwhere(work[np.ix_(available, available)])[0]
        a, b = available[int(a)], available[int(b)]
        selected.extend((a, b))
        left, right = work[a].copy(), work[b].copy()
        work ^= np.outer(left, right) ^ np.outer(right, left)
        available.remove(a)
        available.remove(b)
    require(len(selected) == 8, 'E8 mod-two rank eight')
    basis = roots[selected]
    inverse = inverse_binary(gram[np.ix_(selected, selected)])
    coordinates = np.zeros((len(ports), dimension - 1), dtype=np.uint8)
    form = np.zeros((dimension - 1, dimension - 1), dtype=np.uint8)
    for block in range(blocks):
        pairings = ports[:, 8 * block:8 * (block + 1)] @ basis.T
        require(not (pairings % 4).any(), 'Integral shell-basis pairings')
        coordinates[:, 8 * block:8 * (block + 1)] = (pairings // 4) & 1
        form[8 * block:8 * (block + 1), 8 * block:8 * (block + 1)] = inverse
    even_gram = np.ones((dimension - 1, dimension - 1), dtype=np.uint8) ^ np.eye(dimension - 1, dtype=np.uint8)
    change = (inverse_binary(symplectic_transform(form))
              @ symplectic_transform(even_gram)) & 1
    require(np.array_equal((change @ even_gram @ change.T) & 1, form),
            'Standard-dot even-space isometry')
    even_basis = np.concatenate((np.eye(dimension - 1, dtype=np.uint8),
                                 np.ones((dimension - 1, 1), dtype=np.uint8)), axis=1)
    labels = ((coordinates @ change @ even_basis) & 1) ^ 1
    require(np.all(labels.sum(axis=1) % 2 == 1), 'Odd standard-dot labels')
    packed = labels.astype(np.uint32) @ (1 << np.arange(dimension, dtype=np.uint32))
    spanning, witnesses = {}, []
    for index, value in enumerate(packed):
        if insert_binary(spanning, value):
            witnesses.append(index)
    require(len(spanning) == dimension, 'Full binary label span')
    samples = np.unique(np.concatenate((witnesses, np.linspace(0, len(ports) - 1, 32, dtype=int))))
    for index in samples:
        dots = ports @ ports[index]
        require(not (dots % 4).any(), 'Integral shell pairings')
        require(np.array_equal((labels @ labels[index]) & 1, 1 ^ ((dots // 4) & 1)),
                'Exact label identity on additional diagnostic rows')
    return labels, packed, dict(dimension=dimension, root_basis_indices=selected,
        root_basis_vectors=basis.tolist(), alternating_gram=form.tolist(),
        standard_dot_coordinate_map=((change @ even_basis) & 1).tolist(),
        span_witnesses=witnesses, diagnostic_rows=samples.tolist(),
        identity='p(u) dot p(v) = 1 + (u dot v / 4) mod 2',
        universal_proof=f'The eight E8 basis roots have an odd integral Gram determinant. In lattice pairing coordinates its rational inverse reduces to the displayed binary inverse. {"Three" if blocks == 3 else "Two"} orthogonal blocks give the alternating rank-{dimension - 1} form; the verified even-space isometry and the orthogonal all-ones vector realize it by the standard dot product in dimension {dimension}.')


def modular_rank_witnesses(rows, prime=101):
    basis, selected = {}, []
    for index, raw in enumerate(rows):
        row = np.asarray(raw, dtype=np.int64).copy() % prime
        for pivot in sorted(basis):
            row = (row - row[pivot] * basis[pivot]) % prime
        nonzero = np.flatnonzero(row)
        if not len(nonzero):
            continue
        pivot = int(nonzero[0])
        basis[pivot] = row * pow(int(row[pivot]), -1, prime) % prime
        selected.append(index)
        if len(basis) == rows.shape[1]:
            break
    return selected


def real_rank(roots, fourth):
    witnesses = {}
    for name, rows, degree, expected in (
            ('pure_cubics', fourth, 3, 120),
            ('root_quadratics', roots, 2, 36), ('root_linears', roots, 1, 8)):
        monomials = list(combinations_with_replacement(range(8), degree))
        features = np.stack([np.prod(rows[:, monomial].astype(np.int64), axis=1)
                             for monomial in monomials], axis=1)
        selected = modular_rank_witnesses(features)
        require(len(selected) == expected, f'Exact rational feature rank: {name}')
        witnesses[name] = dict(prime=101, rank=expected, independent_rows=selected)
    trace_norm = (Fraction(1) + Fraction(23, 3)) / 256
    correction_eigenvalue = 1 - 64 * trace_norm
    require(trace_norm == Fraction(13, 384) and correction_eigenvalue == Fraction(-7, 6),
            'Nonzero trace-correction eigenvalue')
    return dict(real_kernel_rank=2088, pure_cubic_features=360, mixed_cubic_features=1728,
        omitted_three_block_features=512, finite_rank_witnesses=witnesses,
        trace_correction_eigenvalue=str(correction_eigenvalue), signature=[2064, 24],
        proof='The pure norm-four sectors make all 3 times 120 pure cubics independent. On each root-pair sector, changing one block sign separates the two mixed parities; ranks 36 and 8 give 288 independent features per ordered block pair. Thus the 2088 retained cubic columns are independent. Let D contain cubic multinomial coefficients and represent u_i as (sum_j u_i*u_j^2)/16. The coefficient matrix is (D-64 L L^T)/3072, with L^T D^-1 L=(13/384)I_24. Its rank-24 correction has nonzero eigenvalue -7/6, proving rank 2088 and the displayed signature.')


def support_orbit(ports, packed, name, coordinates=None):
    if coordinates is not None:
        values = np.prod(ports[:, coordinates].astype(np.int32), axis=1)
    else:
        value = ports[:, 0].astype(np.int32)
        quotient = (value ** 3 - value) // 3
        values = 5 * value - quotient if name == 'unary_f' else quotient - value
    support = np.flatnonzero(values)
    basis, witnesses = {}, []
    for index in support:
        if insert_binary(basis, packed[index]):
            witnesses.append(int(index))
    return dict(name=name, representative_coordinates=list(coordinates) if coordinates else [0],
                support_size=len(support), binary_span=len(basis), independent_ports=witnesses)


def factorization(ports, packed):
    orbits = [support_orbit(ports, packed, name, coordinates) for name, coordinates in (
        ('pure_cube', (0, 0, 0)), ('pure_repeated', (0, 0, 1)),
        ('pure_distinct', (0, 1, 2)), ('mixed_repeated', (0, 0, 8)),
        ('mixed_distinct', (0, 1, 8)), ('unary_f', None), ('unary_g', None))]
    require([orbit['binary_span'] for orbit in orbits] == [25, 25, 25, 17, 17, 25, 25],
            'Complete binary support spans for each center orbit')
    for left, right in product(range(-4, 5), repeat=2):
        q_left, q_right = (left ** 3 - left) // 3, (right ** 3 - right) // 3
        require(left ** 3 * right ** 3 - 64 * left * right ==
                3 * (-(5 * left - q_left) * (5 * right - q_right)
                     + 4 * (q_left - left) * (q_right - right)),
                'Dyadic unary factorization identity')
    monomials = [indices for indices in combinations_with_replacement(range(24), 3)
                 if len({index // 8 for index in indices}) <= 2]
    counts = Counter()
    for indices in monomials:
        blocks = len({index // 8 for index in indices})
        distinct = len(set(indices))
        counts[(blocks, distinct)] += 1
    require(dict(counts) == {(1, 1): 24, (1, 2): 168, (1, 3): 168,
                             (2, 2): 384, (2, 3): 1344}, 'Cubic feature orbit counts')
    return dict(center_count=2112, center_width_histogram={'25': 384, '17': 1728},
        center_bill=38976, literal_cubic_only_bill=38376,
        literal_cubic_only_bill_scope='Omits the linear correction; not a certified factorization bill.',
        support_orbits=orbits,
        dyadic_unary_identity='q(u)=(u^3-u)/3; (u^3*v^3-64*u*v)/3072 = (-(5*u-q(u))*(5*v-q(v))+4*(q(u)-u)*(q(v)-v))/1024',
        diagonal_coefficients={'unary_f': '-1/1024', 'unary_g': '1/256',
                               'repeated_cubic': '1/1024', 'distinct_cubic': '1/512'},
        proof='Expand (u dot v)^3. All three-block monomials vanish on this shell. Keep the 168 pure repeated, 168 pure distinct, 384 mixed repeated, and 1344 mixed distinct monomials; replace each of the 24 pure-cube plus linear terms by the two displayed unary centers. All coefficients are dyadic. The same feature supports occur on encoder and decoder sides because the factorization is symmetric and diagonal. Block and coordinate permutations preserve E8^3 and induce invertible binary label changes, so the seven full-support orbit checks establish all 2112 center widths.',
        scope='Exact scalar fitting kernel and symmetric dyadic factorization with binary support bill. A finite recursive word, helper exits, scheduling, and a new kappa are not supplied by this certificate.')


def certify_e8_cubed():
    roots, fourth, ports, profiles = construct_shell()
    _, packed, fitting = binary_labels(roots, ports)
    values = {str(t): str(Fraction(t ** 3 - 4 * t, 48)) for t in range(-4, 5)}
    require(values['4'] == '1' and all(values[str(t)] == '0' for t in (-2, 0, 2)),
            'Scalar kernel diagonal and even off-diagonal zeros')
    return dict(status='PASS_EXACT_E8_CUBED_SCALAR_FACTORIZATION',
        lattice='E8 cubed', doubled_coordinate_scale=2, norm_four_lines=89640,
        norm_four_vectors=179280, e8_root_lines=120, e8_norm_four_lines=1080,
        profile_counts={str(key): value for key, value in sorted(Counter(map(int, profiles)).items())},
        ports_sha256=hashlib.sha256(ports.astype('<i2').tobytes()).hexdigest(),
        enumeration_proof='Every nonzero E8 vector has even norm at least two. Norm four in E8 cubed is therefore either one norm-four block, giving 3*1080 lines, or two root blocks, giving 3*120*120*2 lines. Relative signs are counted as separate scalar ports.',
        kernel=dict(formula='K(u,v)=(t^3-4*t)/48, t=(u dot v)/4', values=values,
            fitting_proof='Distinct canonical norm-four lines have integral inner product t between -3 and 3. Even t gives zero kernel; odd t gives zero binary pairing under the proved label identity. At t=4 the real and binary diagonal entries are both one.'),
        fitting=fitting, real_rank=real_rank(roots, fourth),
        factorization=factorization(ports, packed))


if __name__ == '__main__':
    print(json.dumps(certify_e8_cubed(), indent=2, sort_keys=True))
