"""Exact two-coordinate collision counts for primitive modular demands."""

from math import gcd

MAX_MODULUS = 64
MAX_DEMANDS = 256
MAX_COEFFICIENT = 2**31


def checked_demands(modulus, demands):
    """The executable is bounded; PROOF.md has no corresponding size cap."""
    if type(modulus) is not int or not 2 <= modulus <= MAX_MODULUS:
        raise ValueError("modulus must be an integer from 2 through 64")
    if not isinstance(demands, (list, tuple)) or len(demands) > MAX_DEMANDS:
        raise ValueError("at most 256 demand pairs are supported")
    result = []
    for pair in demands:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("each demand must have two integer coefficients")
        if any(type(x) is not int or abs(x) > MAX_COEFFICIENT for x in pair):
            raise ValueError("integer coefficient magnitude exceeds 2**31")
        a, b = pair
        if gcd(a, b, modulus) != 1:
            raise ValueError("every demand must be primitive modulo the modulus")
        result.append((a % modulus, b % modulus))
    return tuple(result)


def units(modulus):
    return tuple(x for x in range(modulus) if gcd(x, modulus) == 1)


def projective_key(pair, modulus):
    """Internal primitive pair, at a divisor of a checked modulus."""
    a, b = pair
    if not 2 <= modulus <= MAX_MODULUS or gcd(a, b, modulus) != 1:
        raise ValueError("projective coordinates must be primitive")
    return min(((u * a) % modulus, (u * b) % modulus) for u in units(modulus))


def signature(modulus, demands):
    """Return (divisor, phi(divisor), demand-class count) for each divisor."""
    return tuple(
        (q, len(units(q)), len({projective_key(d, q) for d in demands}))
        for q in range(2, modulus + 1)
        if modulus % q == 0
    )


def projection_count(modulus, demands):
    demands = checked_demands(modulus, demands)
    primitive_pairs = sum(
        gcd(x, y, modulus) == 1
        for x in range(modulus)
        for y in range(modulus)
    )
    if not demands:
        return {"count": modulus**2, "primitive_count": primitive_pairs,
                "signature": ()}
    rows = signature(modulus, demands)
    result = modulus**2 - 1 - sum(phi * classes for _, phi, classes in rows)
    _, phi, classes = rows[-1]
    primitive_count = primitive_pairs - phi * classes
    if not 0 <= primitive_count <= result <= modulus**2:
        raise ArithmeticError("collision-count invariant failed")
    return {"count": result, "primitive_count": primitive_count,
            "signature": rows}


def projection_witness(modulus, demands):
    """Return a primitive avoiding pair, or None when every pair is blocked."""
    demands = checked_demands(modulus, demands)
    forbidden = {projective_key(d, modulus) for d in demands}
    for a in range(modulus):
        for b in range(modulus):
            if gcd(a, b, modulus) != 1:
                continue
            if projective_key((a, b), modulus) in forbidden:
                continue
            witness = (-b % modulus, a)
            if not all((x * witness[0] + y * witness[1]) % modulus
                       for x, y in demands):
                raise ArithmeticError("constructed projection does not avoid demands")
            return witness
    return None
