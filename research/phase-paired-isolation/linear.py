"""Exact common input/output bases for two invertible maps.

Produced by Nick Petalas. Apache-2.0.
The public boundary accepts rational matrices or the listed prime fields.
"""

from fractions import Fraction

MAX_DIMENSION = 12
FIELDS = (0, 2, 3, 5, 7)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def matrix(rows, prime):
    need(type(prime) is int and prime in FIELDS, "Unsupported field")
    need(isinstance(rows, (tuple, list)), "Matrix rows required")
    n = len(rows)
    need(1 <= n <= MAX_DIMENSION, "Matrix dimension outside capacity")
    result = []
    for row in rows:
        need(isinstance(row, (tuple, list)) and len(row) == n, "Square matrix required")
        need(all(type(x) in (int, Fraction) for x in row), "Exact scalar required")
        need(all(max(x.numerator.bit_length(), x.denominator.bit_length()) <= 128
                 for x in row), "Input scalar outside capacity")
        if prime:
            need(all(x.denominator % prime for x in row), "Noninvertible denominator")
            result.append(tuple(x.numerator * pow(x.denominator, -1, prime) % prime
                                for x in row))
        else:
            result.append(tuple(Fraction(x) for x in row))
    return tuple(result)


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def reduce_scalar(value, prime):
    return value % prime if prime else value


def multiply(left, right, prime):
    return tuple(tuple(reduce_scalar(sum(a * b for a, b in zip(row, col)), prime)
                       for col in zip(*right)) for row in left)


def rref(rows, prime):
    work = [list(row) for row in rows]
    pivots = []
    width = len(work[0]) if work else 0
    need(len(work) <= 2 * MAX_DIMENSION and width <= 2 * MAX_DIMENSION,
         "Elimination outside capacity")
    for column in range(width):
        candidates = [i for i in range(len(pivots), len(work)) if work[i][column]]
        if not candidates:
            continue
        target, source = len(pivots), candidates[0]
        work[target], work[source] = work[source], work[target]
        value = work[target][column]
        scale = pow(value, -1, prime) if prime else Fraction(1, 1) / value
        work[target] = [reduce_scalar(x * scale, prime) for x in work[target]]
        for i in range(len(work)):
            if i != target:
                scale = work[i][column]
                work[i] = [reduce_scalar(x - scale * y, prime)
                           for x, y in zip(work[i], work[target])]
        pivots.append(column)
        if len(pivots) == len(work):
            break
    return tuple(tuple(row) for row in work), tuple(pivots)


def rank(rows, prime):
    return len(rref(rows, prime)[1])


def inverse(rows, prime):
    n = len(rows)
    augmented = [tuple(row) + unit for row, unit in zip(rows, identity(n))]
    reduced, pivots = rref(augmented, prime)
    need(pivots == tuple(range(n)), "Invertible map required")
    return tuple(row[n:] for row in reduced)


def kernel(rows, prime):
    reduced, pivots = rref(rows, prime)
    n = len(rows)
    vectors = []
    for free in range(n):
        if free in pivots:
            continue
        vector = [int(j == free) for j in range(n)]
        for i, pivot in enumerate(pivots):
            vector[pivot] = reduce_scalar(-reduced[i][free], prime)
        vectors.append(tuple(vector))
    return vectors


def extend_basis(selected, candidates, prime):
    basis = list(selected)
    for vector in candidates:
        if rank(basis + [vector], prime) > len(basis):
            basis.append(tuple(vector))
    return basis


def check_block(rows, size, prime):
    n = len(rows)
    need(0 <= size <= n, "Block size outside dimension")
    for i in range(n):
        for j in range(n):
            if i < size or j < size:
                need(reduce_scalar(rows[i][j] - int(i == j), prime) == 0,
                     "Identity and both zero cross blocks required")


def isolate(left, right, prime=0):
    left, right = matrix(left, prime), matrix(right, prime)
    need(len(left) == len(right), "Equal dimensions required")
    left_inverse = inverse(left, prime)
    inverse(right, prime)  # Check the second public invertibility contract.
    relative = multiply(left_inverse, right, prime)
    n = len(left)
    defect = tuple(tuple(reduce_scalar(relative[i][j] - int(i == j), prime)
                         for j in range(n)) for i in range(n))
    square = multiply(defect, defect, prime)
    readable = n - rank(defect, prime)
    capacity = n - 2 * rank(defect, prime) + rank(square, prime)
    image = extend_basis([], list(zip(*defect)), prime)
    expanded = extend_basis(image, kernel(defect, prime), prime)
    isolated = expanded[len(image):]
    need(len(isolated) == capacity, "Kernel quotient dimension")
    columns = extend_basis(isolated + image, identity(n), prime)
    need(len(columns) == n, "Complete invariant complement")
    input_basis = tuple(zip(*columns))
    output_basis = multiply(inverse(input_basis, prime), left_inverse, prime)
    first = multiply(multiply(output_basis, left, prime), input_basis, prime)
    second = multiply(multiply(output_basis, right, prime), input_basis, prime)
    need(first == identity(n), "First map normalized exactly")
    check_block(second, capacity, prime)
    return {"capacity": capacity, "readable": readable, "input": input_basis,
            "output": output_basis, "relative": relative, "second": second}
