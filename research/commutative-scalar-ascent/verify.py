"""Standalone checks of scalar ascent on newly constructed certificates.

Produced by Nick Petalas. Apache-2.0.
"""

import copy
import hashlib
import json
from pathlib import Path

from algebra import (Field, check_algebra, evaluate, identity, inverse, isotope,
                     matmul, matvec, require, restrict_matrix, restrict_tensor)
from ascent import ascend


def truncated(variables):
    """K[x_i]/(x_i^2), using bit-mask monomials."""
    require(type(variables) is int and 0 <= variables <= 2, 'fixture variable count')
    n = 2**variables
    table = [[[0]*n for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if not i & j:
                table[i][j][i | j] = 1
    return table


def square_zero():
    """The non-Gorenstein algebra K[x,y]/(x,y)^2."""
    table = [[[0]*3 for _ in range(3)] for _ in range(3)]
    for i in range(3):
        table[0][i][i] = table[i][0][i] = 1
    return table


def quadratic(field):
    """A nonsplit quadratic field over each tested K."""
    if field.q == 4:
        c, b = 2, 1
    elif field.q == 9:
        c, b = 4, 0
    else:
        raise ValueError('quadratic fixture field')
    table = [[[0]*2 for _ in range(2)] for _ in range(2)]
    table[0][0][0] = table[0][1][1] = table[1][0][1] = 1
    table[1][1] = [c, b]
    roots = [x for x in range(field.q) if
             field.add(field.mul(x, x), field.neg(field.add(c, field.mul(b, x)))) == 0]
    require(not roots, 'nonsplit fixture polynomial')
    return table


def direct_product(first, second):
    a, b = len(first), len(second)
    result = [[[0]*(a+b) for _ in range(a+b)] for _ in range(a+b)]
    for offset, table in ((0, first), (a, second)):
        for i in range(len(table)):
            for j in range(len(table)):
                result[offset+i][offset+j][offset:offset+len(table)] = table[i][j]
    return result


def dualize(table):
    n = len(table)
    result = [[[0]*(2*n) for _ in range(2*n)] for _ in range(2*n)]
    for i in range(n):
        for j in range(n):
            for a, b in ((0, 0), (0, 1), (1, 0)):
                for k in range(n):
                    result[2*i+a][2*j+b][2*k+a+b] = table[i][j][k]
    return result


def field_checks():
    triples = 0
    fields = (Field(2, (1, 1, 1)), Field(2, (1, 1, 0, 1)),
              Field(3, (1, 0, 1)), Field(5, (2, 0, 1)))
    for f in fields:
        for a in range(f.q):
            require(f.add(a, 0) == a and f.mul(a, 1) == a and
                    f.add(a, f.neg(a)) == 0, 'field identities')
            for b in range(f.q):
                require(f.mul(a, b) == f.mul(b, a) and f.add(a, b) == f.add(b, a),
                        'commutative field operations')
                for c in range(f.q):
                    require(f.mul(f.mul(a, b), c) == f.mul(a, f.mul(b, c)), 'field associativity')
                    require(f.add(f.add(a, b), c) == f.add(a, f.add(b, c)), 'additive associativity')
                    require(f.mul(a, f.add(b, c)) == f.add(f.mul(a, b), f.mul(a, c)),
                            'field distributivity')
                    triples += 1
    return triples


def presentation(n, field, seed):
    matrix = identity(n)
    for i in range(n):
        j = (i+1) % n
        if i != j:
            matrix[i] = [field.add(a, field.mul(1+seed % (field.q-1), b))
                         for a, b in zip(matrix[i], matrix[j])]
    if seed % 2 and n > 1:
        matrix[0], matrix[-1] = matrix[-1], matrix[0]
    inverse(matrix, field)
    return matrix


def make_fixture(table, field, seed):
    """Build an arbitrary F-basis certificate, without a predecessor routine."""
    n, prime = len(table), Field(field.p, (0, 1))
    maps = [presentation(n, field, seed+i) for i in range(3)]
    tensor = isotope(table, inverse(maps[0], field), inverse(maps[1], field), maps[2], field)
    restricted_table = restrict_tensor(table, field)
    size = n*field.degree
    h = presentation(size, prime, seed+3)
    changed = isotope(restricted_table, h, h, inverse(h, prime), prime)
    certificate = dict(table=changed)
    for key, matrix in zip(('U', 'V', 'W'), maps):
        certificate[key] = matmul(restrict_matrix(matrix, field), h, prime)
    return tensor, certificate, maps, h


def fixture_checks():
    fields = [Field(2, (1, 1, 1)), Field(2, (1, 1, 0, 1)),
              Field(3, (1, 0, 1)), Field(5, (2, 0, 1))]
    cases, products, non_linear = 0, 0, 0
    witnesses = []
    for field in fields:
        prime = Field(field.p, (0, 1))
        tables = [truncated(0), truncated(1), truncated(2), square_zero(),
                  direct_product(truncated(0), truncated(1))]
        if field.q in (4, 9):
            residue = quadratic(field)
            tables += [residue, direct_product(residue, truncated(1)), dualize(residue)]
        for number, table in enumerate(tables):
            unit = check_algebra(table, field)
            for seed in range(3):
                tensor, certificate, maps, h = make_fixture(table, field, seed)
                result = ascend(tensor, certificate, field)
                require(result['unit'] == matvec(maps[2], unit, field), 'independent unit')
                expected = isotope(table, inverse(maps[2], field),
                                   inverse(maps[2], field), maps[2], field)
                require(result['table'] == expected, 'independent normalized table')
                scalar = [[field.p if i == j else 0 for j in range(len(table))]
                          for i in range(len(table))]
                scalar_f = restrict_matrix(scalar, field)
                non_linear += matmul(h, scalar_f, prime) != matmul(scalar_f, h, prime)
                witnesses.append([field.q, number, seed, result['unit'], result['table']])
                cases += 1
                products += len(table)**2
    return dict(fixtures=cases, transported_K_basis_products=products,
                non_K_linear_recovery_bases=non_linear), witnesses


def expect_failure(action, message):
    try:
        action()
    except ValueError as exc:
        require(message in str(exc), 'wrong rejection: '+str(exc))
        return 1
    raise ValueError('control incorrectly accepted: '+message)


def controls():
    field, failures = Field(2, (1, 1, 1)), 0
    tensor, cert, _, _ = make_fixture(square_zero(), field, 0)
    bad = copy.deepcopy(cert)
    bad['U'][0] = [0]*len(bad['U'])
    failures += expect_failure(lambda: ascend(tensor, bad, field), 'linear system not unique')
    bad = copy.deepcopy(cert)
    bad['W'][0] = [a ^ b for a, b in zip(bad['W'][0], bad['W'][1])]
    failures += expect_failure(lambda: ascend(tensor, bad, field), 'certificate isotopy')
    bad = copy.deepcopy(cert)
    bad['table'][0][0][0] = field.p
    failures += expect_failure(lambda: ascend(tensor, bad, field), 'canonical matrix entries')
    failures += expect_failure(lambda: ascend(tensor, {}, field), 'certificate keys')
    failures += expect_failure(lambda: Field(2, (0, 0, 1)), 'unsupported field modulus')
    failures += expect_failure(lambda: Field(True, (0, 1)), 'unsupported characteristic')
    failures += expect_failure(lambda: ascend([[[0]]], cert, field), 'certificate dimension')
    failures += expect_failure(lambda: restrict_tensor(
        [[[0]*5 for _ in range(5)] for _ in range(5)], Field(2, (1, 1, 0, 1))),
        'restricted dimension')
    bad_table = square_zero()
    bad_table[1][1][2], bad_table[2][2][1] = 1, 1
    failures += expect_failure(lambda: check_algebra(bad_table, field), 'associative algebra')
    bad_table = square_zero()
    bad_table[1][2][1] = 1
    failures += expect_failure(lambda: check_algebra(bad_table, field), 'commutative algebra')
    frobenius = lambda x, y: field.mul(field.mul(x, x), y)
    require(frobenius(2, 1) != field.mul(2, frobenius(1, 1)), 'semilinear escape')
    for x in range(field.q):
        for y in range(field.q):
            require(frobenius(field.mul(x, x), y) == field.mul(x, y), 'F-isotopy escape')
    prime = Field(2, (0, 1))
    restricted = restrict_tensor(truncated(0), field)
    require(all(evaluate(restricted, list(v), list(v), prime) != [0, 0]
                for v in ((1, 0), (0, 1), (1, 1))), 'restriction is reduced')
    require(evaluate(truncated(1), [0, 1], [0, 1], prime) == [0, 0], 'class boundary')
    return dict(rejecting_controls=failures, boundary_witnesses=2)


def main():
    counts, witnesses = fixture_checks()
    counts['field_law_triples'] = field_checks()
    counts.update(controls())
    require(counts['non_K_linear_recovery_bases'] > 0, 'nonlinear basis coverage')
    here = Path(__file__).resolve().parent
    names = ('README.md', 'PROOF.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json',
             'algebra.py', 'ascent.py', 'verify.py')
    hashes = {name: hashlib.sha256((here/name).read_bytes()).hexdigest() for name in names}
    digest = hashlib.sha256(json.dumps(witnesses, separators=(',', ':')).encode()).hexdigest()
    print(json.dumps(dict(status='PASS_COMMUTATIVE_SCALAR_ASCENT', **counts,
                         witness_sha256=digest, source_sha256=hashes), sort_keys=True))


if __name__ == '__main__':
    main()
