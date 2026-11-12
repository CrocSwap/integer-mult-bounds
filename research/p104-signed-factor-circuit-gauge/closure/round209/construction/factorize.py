"""Exact deterministic shortest rational transvection factorization.

Matrices are tuples of columns and a factor (u, f) acts as x -> x + u f(x).
The returned factors multiply from left to right in their listed order.
"""
from fractions import Fraction as F


def dot(left, right):
    return sum((a * b for a, b in zip(left, right) if a and b), F(0))


def add(left, right, scale=1):
    return tuple(a + scale * b for a, b in zip(left, right))


def column_matrix_vector(columns, vector):
    return tuple(dot(row, vector) for row in zip(*columns))


def identity(size):
    return tuple(tuple(F(row == column) for row in range(size))
                 for column in range(size))


def displacement(columns):
    return tuple(tuple(entry - (row == j) for row, entry in enumerate(column))
                 for j, column in enumerate(columns))


def determinant_and_rank(columns):
    """Return determinant and rank, using exact column elimination."""
    width = len(columns)
    pending = list(columns)
    pivot_count = 0
    determinant = F(1)
    for row in range(width):
        pivot_at = next((j for j in range(pivot_count, width)
                         if pending[j][row]), None)
        if pivot_at is None:
            determinant = F(0)
            continue
        if pivot_at != pivot_count:
            pending[pivot_count], pending[pivot_at] = pending[pivot_at], pending[pivot_count]
            determinant = -determinant
        pivot = pending[pivot_count]
        determinant *= pivot[row]
        for j in range(pivot_count + 1, width):
            if pending[j][row]:
                pending[j] = add(pending[j], pivot, -pending[j][row] / pivot[row])
        pivot_count += 1
    return determinant, pivot_count


def proportionality(first, second):
    """Return the ratio second / first if proportional, else None."""
    i = next(j for j, value in enumerate(first) if value)
    ratio = second[i] / first[i]
    return ratio if all(b == ratio * a for a, b in zip(first, second)) else None


def select_displacement(columns):
    """Return Dx and D²x independent, or Dx with Dbar = scalar I."""
    representative = None
    ratio = None
    for column in columns:
        if not any(column):
            continue
        squared = column_matrix_vector(columns, column)
        current = proportionality(column, squared)
        if current is None:
            return column, squared, None
        if representative is None:
            representative = column
            ratio = current
        elif current != ratio:
            combined = tuple(ratio * a + current * b for a, b in zip(representative, column))
            return add(representative, column), combined, None
    return representative, None, ratio


def inverse_left(columns, image, covector):
    assert any(image) and any(covector) and dot(covector, image) == 0
    return tuple(add(column, image, -dot(covector, column)) for column in columns)


def obstructed(delta):
    """A nonidentity rational SL involution requires one extra factor."""
    nonzero = False
    for column in delta:
        if not any(column):
            continue
        nonzero = True
        if column_matrix_vector(delta, column) != tuple(-2 * x for x in column):
            return False
    return nonzero


def solve_two(image, squared, i, j, target, other):
    determinant = image[i] * squared[j] - image[j] * squared[i]
    return ((target * squared[j] - other * image[j]) / determinant,
            (image[i] * other - squared[i] * target) / determinant)


def peel(columns, delta, image, squared, ratio):
    """Choose a transvection whose removal drops displacement rank."""
    rows = tuple(zip(*delta))
    i = next(j for j, value in enumerate(image) if value)
    if ratio == 0:
        covector = tuple(x / image[i] for x in rows[i])
        return (image, covector), inverse_left(columns, image, covector)
    j = next(j for j in range(len(columns))
             if image[i] * squared[j] != image[j] * squared[i])
    first, second = solve_two(image, squared, i, j, F(1), F(0))
    covector = tuple(first * x + second * y for x, y in zip(rows[i], rows[j]))
    remainder = inverse_left(columns, image, covector)
    if obstructed(displacement(remainder)):
        for h, row in enumerate(rows):
            first, second = solve_two(image, squared, i, j, image[h], squared[h])
            adjustment = tuple(z - first * x - second * y
                               for x, y, z in zip(rows[i], rows[j], row))
            if any(adjustment):
                covector = add(covector, adjustment)
                remainder = inverse_left(columns, image, covector)
                break
        else:
            raise ArithmeticError("no independent adjustment for exceptional quotient")
        assert not obstructed(displacement(remainder))
    return (image, covector), remainder


def factor_product(factors, size):
    """Rebuild the listed product by exact independent column application."""
    columns = identity(size)
    for image, covector in reversed(factors):
        if not any(image) or not any(covector) or dot(covector, image):
            raise ValueError("a supplied factor is not a nontrivial transvection")
        columns = tuple(add(column, image, dot(covector, column)) for column in columns)
    return columns


def factorize(columns):
    """Return minimum length, displacement rank, obstruction and factors."""
    original = tuple(tuple(map(F, column)) for column in columns)
    size = len(original)
    if any(len(column) != size for column in original):
        raise ValueError("matrix must be square and supplied in columns")
    if determinant_and_rank(original)[0] != 1:
        raise ValueError("matrix must have determinant one")
    delta = displacement(original)
    rank = determinant_and_rank(delta)[1]
    exceptional = obstructed(delta)
    current = original
    factors = []
    if exceptional:
        rows = tuple(zip(*delta))
        image = next(column for column in delta if any(column))
        i = next(j for j, value in enumerate(image) if value)
        for j, row in enumerate(rows):
            covector = add(row, rows[i], -image[j] / image[i])
            if any(covector):
                break
        else:
            raise ArithmeticError("nonidentity rational SL involution has rank below two")
        factors.append((image, covector))
        current = inverse_left(current, image, covector)
    for _ in range(rank):
        delta = displacement(current)
        image, squared, ratio = select_displacement(delta)
        if image is None or (ratio is not None and ratio != 0):
            raise ArithmeticError("rank-dropping induction reached unexpected quotient")
        factor, current = peel(current, delta, image, squared, ratio)
        factors.append(factor)
    if current != identity(size) or factor_product(factors, size) != original:
        raise ArithmeticError("exact factorization verification failed")
    return {"length": len(factors), "rank": rank, "involution": exceptional,
            "factors": tuple(factors)}
