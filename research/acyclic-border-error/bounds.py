"""Exact certificates for the bounded acyclic-selector error threshold."""

from fractions import Fraction

MAX_DIMENSION = 32
MAX_BITS = 4096


def validate(n: int, limit: Fraction, error: Fraction) -> None:
    """Bound the public arithmetic domain before constructing certificates."""
    if type(n) is not int or not 1 <= n <= MAX_DIMENSION:
        raise ValueError("dimension must be an integer in 1..32")
    for value in (limit, error):
        if not isinstance(value, Fraction):
            raise ValueError("parameters must be exact Fractions")
        height = max(abs(value.numerator).bit_length(), value.denominator.bit_length())
        if height > MAX_BITS:
            raise ValueError("parameter height exceeds 4096 bits")
    if limit < 1 or not 0 <= error <= 1:
        raise ValueError("require limit >= 1 and error in [0,1]")


def comparison(n: int, limit: Fraction, error: Fraction) -> list[list[Fraction]]:
    """Return I-B, where B has limit above and error on/below the diagonal."""
    validate(n, limit, error)
    return [[Fraction(i == j) - (limit if i < j else error)
             for j in range(n)] for i in range(n)]


def certificate(n: int, limit: Fraction, error: Fraction) -> tuple[tuple[Fraction, ...], Fraction]:
    """Return positive weights and their common comparison residual."""
    validate(n, limit, error)
    ratio = 1 + limit - error
    weights = tuple(ratio ** (n - 1 - i) for i in range(n))
    residual = 1 - error * sum(weights)
    return weights, residual


def cutoff(n: int, limit: Fraction, bits: int = 80) -> tuple[Fraction, Fraction]:
    """Enclose the first root in an exact rational interval of width <= 2^-bits."""
    validate(n, limit, Fraction(0))
    if type(bits) is not int or not 1 <= bits <= 128:
        raise ValueError("precision must be an integer in 1..128")
    if n == 1:
        return Fraction(1), Fraction(1)
    low, high = Fraction(0), Fraction(1, n)
    for _ in range(bits):
        middle = (low + high) / 2
        _, margin = certificate(n, limit, middle)
        if margin > 0:
            low = middle
        else:
            high = middle
    assert high - low <= Fraction(1, 2 ** bits)
    assert certificate(n, limit, low)[1] > 0
    assert certificate(n, limit, high)[1] <= 0
    return low, high


def rational_boundary(n: int, ratio: Fraction) -> tuple[Fraction, Fraction, tuple[Fraction, ...]]:
    """A rational rank-(n-1) boundary family, parameterized by ratio >= 2."""
    validate(n, ratio, Fraction(0))
    if ratio < 2:
        raise ValueError("boundary ratio must be >= 2")
    error = 1 / sum(ratio ** k for k in range(n))
    limit = ratio - 1 + error
    validate(n, limit, error)
    weights, margin = certificate(n, limit, error)
    assert margin == 0
    return limit, error, weights
