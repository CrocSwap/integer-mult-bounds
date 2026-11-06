"""Exact bounded constructor for the Cayley-Hamilton lattice over Z_(2)."""

from fractions import Fraction


def matrix(rows):
    """Validate the public square-matrix boundary; never coerce floats."""
    if not isinstance(rows, (list, tuple)) or not 1 <= len(rows) <= 4:
        raise ValueError("supported dimensions are 1 through 4")
    n = len(rows)
    if any(not isinstance(row, (list, tuple)) or len(row) != n for row in rows):
        raise ValueError("matrix must be square")
    for row in rows:
        for x in row:
            if type(x) not in (int, Fraction):
                raise ValueError("entries must be exact integers or Fractions")
            q = Fraction(x)
            if max(abs(q.numerator).bit_length(), q.denominator.bit_length()) > 64:
                raise ValueError("input entry exceeds 64 bits")
    return tuple(tuple(Fraction(x) for x in row) for row in rows)


def identity(n):
    return tuple(tuple(Fraction(i == j) for j in range(n)) for i in range(n))


def product(a, b):
    n = len(a)
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(n))
                       for j in range(n)) for i in range(n))


def integral(q):
    return Fraction(q).denominator % 2 == 1


def valuation(q):
    """Only nonzero rational inputs have a finite valuation."""
    if not q:
        raise ValueError("zero has no finite valuation")
    numerator, denominator = abs(q.numerator), q.denominator
    return ((numerator & -numerator).bit_length()
            - (denominator & -denominator).bit_length())


def characteristic(t):
    """Faddeev-LeVerrier, returning descending coefficients including 1."""
    n = len(t)
    b = identity(n)
    coefficients = [Fraction(1)]
    for k in range(1, n + 1):
        a = product(t, b)
        c = -sum(a[i][i] for i in range(n)) / k
        coefficients.append(c)
        b = tuple(tuple(a[i][j] + (c if i == j else 0)
                        for j in range(n)) for i in range(n))
    if any(x for row in b for x in row):
        raise ArithmeticError("Cayley-Hamilton residual is nonzero")
    return tuple(coefficients)


def generated_basis(t):
    """Column elimination over the DVR, on [I|T|...|T^(n-1)]."""
    n = len(t)
    powers = [identity(n)]
    for _ in range(1, n):
        powers.append(product(t, powers[-1]))
    a = [[power[i][j] for power in powers for j in range(n)] for i in range(n)]
    order = list(range(n))
    width = n * n
    for k in range(n):
        candidates = [(valuation(a[i][j]), i, j)
                      for i in range(k, n) for j in range(k, width) if a[i][j]]
        if not candidates:
            raise ArithmeticError("generators lost full rational rank")
        _, i, j = min(candidates)
        a[k], a[i] = a[i], a[k]
        order[k], order[i] = order[i], order[k]
        for row in a:
            row[k], row[j] = row[j], row[k]
        for j in range(k + 1, width):
            ratio = a[k][j] / a[k][k]
            if not integral(ratio):
                raise ArithmeticError("column operation is not in Z_(2)")
            for i in range(n):
                a[i][j] -= ratio * a[i][k]
    if any(a[i][j] for i in range(n) for j in range(n, width)):
        raise ArithmeticError("generator remainder is nonzero")
    return tuple(tuple(a[order.index(i)][j] for j in range(n)) for i in range(n))


def solve(rows):
    """Return a stable basis, or the first nonintegral characteristic coefficient."""
    t = matrix(rows)
    coefficients = characteristic(t)
    for index, coefficient in enumerate(coefficients):
        if not integral(coefficient):
            return {"kind": "obstruction", "index": index,
                    "coefficient": coefficient}
    return {"kind": "basis", "basis": generated_basis(t)}
