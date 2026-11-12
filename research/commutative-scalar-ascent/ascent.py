"""Convert a prime-field recovery certificate to a K-linear one.

Produced by Nick Petalas. Apache-2.0.
"""

from algebra import (Field, check_algebra, check_matrix, check_tensor, evaluate,
                     identity, inverse, isotope, matvec, pack, require,
                     restrict_tensor)


def validate_certificate(tensor, certificate, field):
    """Check supplied evidence, without running a tensor recognizer."""
    n = check_tensor(tensor, field)
    require(isinstance(certificate, dict) and
            set(certificate) >= {'table', 'U', 'V', 'W'}, 'certificate keys')
    table = certificate['table']
    require(check_tensor(table, field) == n, 'certificate dimension')
    unit = check_algebra(table, field)
    for key in ('U', 'V', 'W'):
        check_matrix(certificate[key], n, field)
        inverse(certificate[key], field)
    actual = isotope(tensor, certificate['U'], certificate['V'], identity(n), field)
    wanted = isotope(table, identity(n), identity(n), certificate['W'], field)
    require(actual == wanted, 'certificate isotopy')
    return unit


def ascend(tensor, certificate, field):
    """Return a K-table and K-linear maps t(Ua,Vb)=W*table(a,b)."""
    n = check_tensor(tensor, field)
    prime = Field(field.p, (0, 1))
    restricted = restrict_tensor(tensor, field)
    unit = validate_certificate(restricted, certificate, prime)
    u = pack(matvec(certificate['U'], unit, prime), field)
    v = pack(matvec(certificate['V'], unit, prime), field)
    basis = identity(n)
    left_slice = [list(row) for row in zip(*(evaluate(tensor, u, x, field) for x in basis))]
    right_slice = [list(row) for row in zip(*(evaluate(tensor, x, v, field) for x in basis))]
    left, right = inverse(right_slice, field), inverse(left_slice, field)
    table = isotope(tensor, left, right, identity(n), field)
    result = dict(table=table, U=left, V=right, W=identity(n))
    output_unit = validate_certificate(tensor, result, field)
    require(output_unit == evaluate(tensor, u, v, field), 'normalized unit')
    result['unit'] = output_unit
    return result
