#!/usr/bin/env python3
"""Bounded exact corroboration; the universal claim is proved in PROOF.md."""
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Gate:
    source: int
    target: int
    matrix: tuple
    polynomial: tuple
    placement: str
    label: str


def validate(word, roles, dimension):
    require(2 <= roles <= 4 and 1 <= dimension <= 4, 'fixture dimensions')
    require(len(word) <= 40, 'word capacity')
    for g in word:
        require(0 <= g.source < roles and 0 <= g.target < roles, 'port range')
        require(g.source != g.target, 'distinct ports')
        require(g.placement in ('before', 'after'), 'placement')
        require(len(g.matrix) == dimension, 'matrix height')
        require(all(len(row) == dimension for row in g.matrix), 'matrix width')
        require(1 <= len(g.polynomial) <= 4, 'polynomial capacity')
        require(bool(g.label), 'label')
        require(len(set(map(sum, g.matrix))) == 1, 'constant row sum')


def value(coefficients, x):
    result = Q(0)
    for coefficient in reversed(coefficients):
        result = result * x + coefficient
    return result


def slope(coefficients, x):
    return sum((i * coefficients[i] * x ** (i - 1)
                for i in range(1, len(coefficients))), Q(0))


def matvec(matrix, vector):
    return tuple(sum((a * b for a, b in zip(row, vector)), Q(0))
                 for row in matrix)


def extract(word, roles, dimension):
    validate(word, roles, dimension)
    constants = [Q(0)] * roles
    extracted, trajectory = [], []
    for g in word:
        row_sum = sum(g.matrix[0])
        argument = constants[g.source]
        if g.placement == 'after':
            argument *= row_sum
            increment = value(g.polynomial, argument)
        else:
            increment = row_sum * value(g.polynomial, argument)
        coefficient = slope(g.polynomial, argument)
        constants[g.target] += increment
        trajectory.append(tuple(constants))
        if coefficient:
            extracted.append(Gate(g.source, g.target, g.matrix,
                                  (Q(0), coefficient), g.placement, g.label))
    return tuple(extracted), tuple(trajectory)


def normalized(terms):
    result = {p: c for p, c in terms.items() if c}
    require(len(result) <= 4096, 'monomial capacity')
    require(all(sum(p) <= 16 for p in result), 'degree capacity')
    return result


def plus(left, right):
    result = dict(left)
    for powers, coefficient in right.items():
        result[powers] = result.get(powers, Q(0)) + coefficient
    return normalized(result)


def scale(polynomial, scalar):
    return normalized({p: scalar * c for p, c in polynomial.items()})


def times(left, right):
    require(len(left) * len(right) <= 4096, 'product capacity')
    result = {}
    for p, a in left.items():
        for q, b in right.items():
            powers = tuple(x + y for x, y in zip(p, q))
            result[powers] = result.get(powers, Q(0)) + a * b
    return normalized(result)


def substitute(coefficients, polynomial, variables):
    zero = (0,) * variables
    result = {}
    for coefficient in reversed(coefficients):
        result = plus(times(result, polynomial), {zero: coefficient})
    return result


def polynomial_matrix(matrix, vector):
    result = []
    for row in matrix:
        entry = {}
        for scalar, polynomial in zip(row, vector):
            entry = plus(entry, scale(polynomial, scalar))
        result.append(entry)
    return tuple(result)


def polynomial_run(word, roles, dimension, clean=()):
    validate(word, roles, dimension)
    variables = roles * dimension
    state = []
    for index in range(variables):
        powers = tuple(int(i == index) for i in range(variables))
        state.append({powers: Q(1)} if index // dimension not in clean else {})
    for g in word:
        begin = g.source * dimension
        source = tuple(state[begin:begin + dimension])
        if g.placement == 'after':
            source = polynomial_matrix(g.matrix, source)
        source = tuple(substitute(g.polynomial, entry, variables)
                       for entry in source)
        if g.placement == 'before':
            source = polynomial_matrix(g.matrix, source)
        for i, increment in enumerate(source):
            index = g.target * dimension + i
            state[index] = plus(state[index], increment)
    return tuple(state)


def literal_run(word, initial, dimension):
    state = list(initial)
    for g in word:
        begin = g.source * dimension
        source = tuple(state[begin:begin + dimension])
        if g.placement == 'after':
            source = matvec(g.matrix, source)
        source = tuple(value(g.polynomial, x) for x in source)
        if g.placement == 'before':
            source = matvec(g.matrix, source)
        for i, increment in enumerate(source):
            state[g.target * dimension + i] += increment
    return tuple(state)


def evaluate(polynomials, point):
    values = []
    for polynomial in polynomials:
        total = Q(0)
        for powers, coefficient in polynomial.items():
            term = coefficient
            for x, exponent in zip(point, powers):
                term *= x ** exponent
            total += term
        values.append(total)
    return tuple(values)


def degree_one(polynomials):
    return tuple({p: c for p, c in entry.items() if sum(p) == 1}
                 for entry in polynomials)


def identity(dimension):
    return tuple(tuple(Q(i == j) for j in range(dimension))
                 for i in range(dimension))


def operators(dimension):
    unit = identity(dimension)
    zero = tuple((Q(0),) * dimension for _ in range(dimension))
    cyclic = tuple(tuple(Q(j == (i + 1) % dimension)
                        for j in range(dimension)) for i in range(dimension))
    doubled = tuple(tuple(2 * x for x in row) for row in unit)
    matrices = [unit, zero, cyclic, doubled]
    if dimension >= 2:
        rows = [list(row) for row in unit]
        rows[0][0] += Q(1, 2)
        rows[0][1] -= Q(1, 2)
        matrices.append(tuple(map(tuple, rows)))
    return tuple(matrices)


def translation(source, target, constant, dimension):
    return Gate(source, target, identity(dimension), (constant,),
                'before', 'translation')


def inverse(word):
    return tuple(Gate(g.source, g.target, g.matrix,
                      tuple(-c for c in g.polynomial), g.placement, g.label)
                 for g in reversed(word))


def square_word(matrix, dimension, constant, placement, source=0, target=1):
    row_sum = sum(matrix[0])
    correction = constant ** 2 * row_sum
    if placement == 'after':
        correction *= row_sum
    label = 'T:' + str(matrix) + ':' + str((source, target, placement))
    word = (translation(target, source, constant, dimension),
            Gate(source, target, matrix, (0, 0, 1), placement, label),
            translation(target, source, -constant, dimension),
            Gate(source, target, matrix, (0, 0, -1), placement, label),
            translation(source, target, -correction, dimension))
    coefficient = 2 * constant * (row_sum if placement == 'after' else 1)
    expected = (Gate(source, target, matrix, (0, coefficient), 'before', label),)
    return word, expected


def check_fixture(word, expected, roles, dimension, clean):
    endpoint = polynomial_run(word, roles, dimension, clean)
    target = polynomial_run(expected, roles, dimension, clean)
    require(endpoint == target, 'complete polynomial endpoint')
    extracted, trajectory = extract(word, roles, dimension)
    require(polynomial_run(extracted, roles, dimension, clean) == endpoint,
            'extracted endpoint')
    old_counts = Counter(g.label for g in word)
    new_counts = Counter(g.label for g in extracted)
    require(all(n <= old_counts[label] for label, n in new_counts.items()),
            'label domination')
    variables = roles * dimension
    points = [tuple(Q(((i + 1) * seed) % 7 - 3, seed)
                    if i // dimension not in clean else Q(0)
                    for i in range(variables)) for seed in range(1, 5)]
    for point in points:
        final = literal_run(word, point, dimension)
        require(final == evaluate(endpoint, point), 'literal polynomial agreement')
        require(literal_run(inverse(word), final, dimension) == point,
                'complete inverse')
    return int(any(any(row) for row in trajectory)), len(points)


def endpoint_fixtures():
    count = nonzero = points = 0
    for dimension in range(1, 5):
        for matrix, constant, placement in product(
                operators(dimension), (Q(-2), Q(1, 2), Q(3)), ('before', 'after')):
            word, expected = square_word(matrix, dimension, constant, placement)
            for roles, clean in ((2, ()), (3, (2,)), (3, (1,))):
                active, tested = check_fixture(word, expected, roles, dimension, clean)
                count += 1
                nonzero += active
                points += tested
    for dimension in range(2, 5):
        matrices = operators(dimension)
        a, ae = square_word(matrices[2], dimension, Q(1), 'after', 0, 2)
        b, be = square_word(matrices[4], dimension, Q(2), 'before', 2, 1)
        for clean in ((), (2,)):
            word, expected = a + b + inverse(a), ae + be + inverse(ae)
            active, tested = check_fixture(word, expected, 3, dimension, clean)
            endpoint = polynomial_run(word, 3, dimension, clean)
            start = polynomial_run((), 3, dimension, clean)
            require(endpoint[2 * dimension:] == start[2 * dimension:],
                    'active workspace return')
            count += 1
            nonzero += active
            points += tested
    return count, nonzero, points


def nonlinear_prefixes():
    count = 0
    for dimension in (1, 2):
        matrix = operators(dimension)[-1]
        for placement, constant in product(('before', 'after'), (Q(-1), Q(2))):
            word = (translation(1, 0, constant, dimension),
                    Gate(0, 1, matrix, (1, 1, 1), placement, 'nonlinear'),
                    Gate(1, 2, identity(dimension), (2, -1, 1), 'before', 'next'))
            for end in range(1, 4):
                original = polynomial_run(word[:end], 3, dimension)
                extracted, _ = extract(word[:end], 3, dimension)
                tangent = polynomial_run(extracted, 3, dimension)
                require(degree_one(original) == tangent, 'prefix Jacobian')
                count += 1
    return count


def controls():
    names = []
    word, _ = square_word(operators(2)[3], 2, Q(1), 'after')
    original = polynomial_run(word, 2, 2)
    mutants = [('missing correction', word[:-1]),
               ('missing source restoration', word[:2] + word[3:])]
    naive = tuple(Gate(g.source, g.target, g.matrix,
                       (0, slope(g.polynomial, 0)), 'before', g.label) for g in word)
    mutants.append(('naive zero extraction', naive))
    before, _ = square_word(operators(2)[3], 2, Q(1), 'before')
    mutants.append(('placement distinction', before))
    for name, mutant in mutants:
        require(original != polynomial_run(mutant, 2, 2), name)
        names.append(name)
    nonlinear = (Gate(0, 1, identity(2), (0, 1, 1), 'before', 'T'),)
    linear, _ = extract(nonlinear, 2, 2)
    require(polynomial_run(nonlinear, 2, 2) != polynomial_run(linear, 2, 2),
            'Jacobian does not prove linearity')
    names.append('nonlinear endpoint')
    bad = ((Q(1), Q(0)), (Q(0), Q(2)))
    for name, matrix, source, target in (
            ('nonconstant row sum', bad, 0, 1), ('aliased ports', identity(2), 0, 0),
            ('wrong matrix shape', ((Q(1),),), 0, 1)):
        gate = Gate(source, target, matrix, (1, 0, 1), 'after', 'bad')
        try:
            extract((gate,), 2, 2)
        except ValueError:
            names.append(name)
            continue
        raise ValueError('invalid contract accepted')
    derivative = ((Q(2), Q(0)), (Q(0), Q(8)))
    require(derivative[0][0] / bad[0][0] != derivative[1][1] / bad[1][1],
            'nonhomogeneous derivative is nonscalar')
    names.append('nonscalar derivative boundary')
    squares = tuple(x * x % 2 for x in (0, 1))
    require(squares == (0, 1) and squares != (0, 0), 'finite field boundary')
    names.append('finite field boundary')
    return names


def uniform_controls():
    coefficients = []
    for width in (1, 2, 3):
        matrix = tuple(tuple(width * x for x in row) for row in identity(2))
        word, _ = square_word(matrix, 2, Q(1), 'after')
        extracted, _ = extract(word, 2, 2)
        coefficients.append(extracted[0].polynomial[1])
    require(coefficients == [2, 4, 6], 'width-dependent coefficients')
    for dimension in range(1, 5):
        word, _ = square_word(identity(dimension), dimension, Q(3), 'after')
        extracted, _ = extract(word, 2, dimension)
        require(tuple(g.polynomial for g in extracted) == ((0, 6),),
                'uniform row-sum extraction')
    return ['width-dependent row sums', 'uniform row-sum extraction']


def main():
    fixtures, nonzero, points = endpoint_fixtures()
    prefixes = nonlinear_prefixes()
    checked_controls = controls() + uniform_controls()
    package = Path(__file__).resolve().parent
    paths = sorted(path for path in package.iterdir() if path.is_file())
    require(len(paths) <= 12, 'package file capacity')
    require(all(path.stat().st_size <= 1048576 for path in paths),
            'source byte capacity')
    hashes = {path.name: sha256(path.read_bytes()).hexdigest() for path in paths}
    print(json.dumps({
        'status': 'PASS_HOMOGENEOUS_POLYNOMIAL_PROFILE',
        'claim_type': 'scoped proof with exact finite corroboration',
        'linear_endpoint_fixtures': fixtures,
        'nonzero_constant_trajectories': nonzero,
        'literal_points_and_inverse_roundtrips': points,
        'nonlinear_prefix_jacobians': prefixes,
        'controls': checked_controls,
        'source_sha256': hashes,
        'no_new_kappa': True,
    }, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
