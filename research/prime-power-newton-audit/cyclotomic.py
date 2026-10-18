"""Recover tail valuations from exact cyclotomic-ring coefficients.

For r = p**a and gcd(t, r) = 1, entry j is

    a_j = product(1 - u**(t*s) for s in range(j + 1, r)),

where u is a primitive r-th root.  This module does not use a formula for
the valuation of an individual factor or sum factor valuations.  It builds
the products in Z[u]/(u**r - 1), reduces modulo Phi_r, and changes basis to
pi = 1 - u.  All coefficient calculations use Python integers.

The mathematical input is that Phi_{p**a}(1 - X) is Eisenstein at p (up to
its leading sign).  Thus pi is a uniformizer in the p-adic cyclotomic field,
and v(p) = e = phi(r) for the normalization v(pi) = 1.  For a reduced
coefficient expansion sum(c_i*pi**i), the nonzero summands have valuations
e*v_p(c_i) + i with distinct residues modulo e.  The minimum is unique, so
the ultrametric inequality is an equality there.  This theorem, rather than
finite enumeration, justifies the valuation extraction.
"""

from math import comb, isqrt


def _prime_power(p: int, a: int) -> tuple[int, int, int]:
    """Validate the parameters and return (r, r/p, phi(r))."""
    if isinstance(p, bool) or not isinstance(p, int):
        raise TypeError("p must be an integer prime")
    if p < 2 or any(p % d == 0 for d in range(2, isqrt(p) + 1)):
        raise ValueError("p must be prime")
    if isinstance(a, bool) or not isinstance(a, int):
        raise TypeError("a must be a positive integer")
    if a < 1:
        raise ValueError("a must be positive")
    q = p ** (a - 1)
    return p * q, q, (p - 1) * q


def _primitive_exponent(t: int, p: int, r: int) -> int:
    if isinstance(t, bool) or not isinstance(t, int):
        raise TypeError("t must be an integer primitive exponent")
    if t % p == 0:
        raise ValueError("t must be coprime to p**a")
    return t % r


def _one_minus_variable(coefficients: tuple[int, ...]) -> tuple[int, ...]:
    """Return exact coefficients of f(1-X), in ascending degree order."""
    return tuple(
        (-1) ** i
        * sum(comb(k, i) * coefficients[k] for k in range(i, len(coefficients)))
        for i in range(len(coefficients))
    )


def cyclotomic_pi_polynomial(p: int, a: int) -> tuple[int, ...]:
    """Return coefficients of Phi_{p**a}(1-X), including its leading term.

    Coefficients are in ascending degree order.  The polynomial is kept
    with its actual leading sign, which is -1 when p**a = 2.
    """
    _, q, e = _prime_power(p, a)
    coefficients = tuple(int(i % q == 0) for i in range(e + 1))
    return _one_minus_variable(coefficients)


def tail_coefficients(p: int, a: int, t: int, *, basis: str = "pi") -> list[tuple[int, ...]]:
    """Return a_j for j=0,...,r-1 in the u or pi=1-u power basis.

    Each tuple has e=phi(r) entries in ascending degree order, including
    trailing zeros.  The empty tail a_{r-1} is 1.  Any integer t coprime to
    p is accepted; exponents are normalized modulo r.  The algorithm works
    for prime powers beyond the audit range, but no performance bound is
    promised for large inputs.
    """
    r, q, e = _prime_power(p, a)
    t = _primitive_exponent(t, p, r)
    if basis not in ("u", "pi"):
        raise ValueError("basis must be 'u' or 'pi'")

    # A cyclic vector represents a polynomial modulo u**r - 1.  Since
    # Phi_r divides u**r - 1, this intermediate quotient preserves the
    # subsequent reduction modulo Phi_r.
    cyclic = [1] + [0] * (r - 1)
    tails: list[tuple[int, ...]] = [()] * r
    for j in range(r - 1, -1, -1):
        if j < r - 1:
            shift = (t * (j + 1)) % r
            cyclic = [cyclic[k] - cyclic[(k - shift) % r] for k in range(r)]

        # Phi_r(u) = sum(u**(k*q) for k=0,...,p-1).  Eliminating
        # u**(e+h), 0<=h<q, subtracts its coefficient at each k*q+h,
        # 0<=k<p-1.  All resulting degrees are already below e.
        reduced = tuple(cyclic[k] - cyclic[e + k % q] for k in range(e))
        tails[j] = reduced if basis == "u" else _one_minus_variable(reduced)
    return tails


def _integer_p_valuation(value: int, p: int) -> int:
    """Return v_p(value) for a nonzero integer."""
    if value == 0:
        raise ValueError("zero has no finite integer p-adic valuation")
    value = abs(value)
    valuation = 0
    while value % p == 0:
        value //= p
        valuation += 1
    return valuation


def tail_valuations(p: int, a: int, t: int) -> list[int]:
    """Return v(a_j), j=0,...,p**a-1, normalized by v(1-u)=1.

    Recover each valuation directly from its exact reduced pi-basis
    coefficients.  A primitive exponent makes every tail nonzero.
    """
    _, _, e = _prime_power(p, a)
    result = []
    for coefficients in tail_coefficients(p, a, t):
        weights = [e * _integer_p_valuation(c, p) + i
                   for i, c in enumerate(coefficients) if c != 0]
        if not weights:
            raise ArithmeticError("a primitive tail unexpectedly reduced to zero")
        result.append(min(weights))
    return result
