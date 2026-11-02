"""Minimal intermediate fields for finite-field norm witnesses. Apache-2.0."""

from math import gcd, isqrt


def require(condition, message):
    if not condition:
        raise ValueError(message)


def positive(value, name, maximum):
    require(type(value) is int and 1 <= value <= maximum, name + " out of range")


def minimal_degree(q, d):
    """q is a supplied prime-power order; the arithmetic formula needs q >= 2."""
    positive(q, "q", 2**32)
    require(q >= 2, "q must be at least two")
    positive(d, "d", 2**32)
    remaining = d
    for _ in range(d.bit_length()):
        common = gcd(remaining, q - 1)
        if common == 1:
            answer = d // remaining
            require(d % answer == 0 and gcd(d // answer, q - 1) == 1,
                    "minimal degree invariant")
            return answer
        remaining //= common
    raise ValueError("gcd stripping exhausted its proven bound")


class Field:
    """Bounded polynomial quotient; certify the field with a full generator cycle."""

    def __init__(self, p, modulus):
        positive(p, "prime", 31)
        require(p >= 2 and all(p % i for i in range(2, isqrt(p) + 1)),
                "coefficient characteristic must be prime")
        require(isinstance(modulus, (tuple, list)) and 2 <= len(modulus) <= 9,
                "modulus degree must be in 1..8")
        require(all(type(c) is int and 0 <= c < p for c in modulus)
                and modulus[-1] == 1, "modulus must be monic and canonical")
        self.p, self.modulus = p, tuple(modulus)
        self.n, self.order = len(modulus) - 1, p ** (len(modulus) - 1)
        require(self.order <= 4096, "quotient capacity exceeded")

    def element(self, value):
        require(type(value) is int and 0 <= value < self.order,
                "noncanonical quotient element")

    def digits(self, value):
        self.element(value)
        return [(value // self.p**i) % self.p for i in range(self.n)]

    def multiply(self, left, right):
        a, b = self.digits(left), self.digits(right)
        coefficients = [0] * (2 * self.n - 1)
        for i in range(self.n):
            for j in range(self.n):
                coefficients[i + j] += a[i] * b[j]
        for k in range(2 * self.n - 2, self.n - 1, -1):
            for j in range(self.n):
                coefficients[k - self.n + j] -= coefficients[k] * self.modulus[j]
        return sum((coefficients[i] % self.p) * self.p**i for i in range(self.n))

    def power(self, value, exponent):
        self.element(value)
        require(type(exponent) is int and 0 <= exponent < 2**64,
                "power exponent out of range")
        result = 1
        for bit in range(exponent.bit_length()):
            if (exponent >> bit) & 1:
                result = self.multiply(result, value)
            value = self.multiply(value, value)
        return result

    def certify_generator(self, generator):
        self.element(generator)
        require(generator != 0, "zero generator")
        seen, value = set(), 1
        for _ in range(self.order - 1):
            require(value != 0 and value not in seen, "nonprimitive generator")
            seen.add(value)
            value = self.multiply(value, generator)
        require(value == 1 and len(seen) == self.order - 1, "incomplete unit cycle")


def norm_witness(field, base_degree, generator, desired):
    """Return an exact witness and its minimal uniform subfield degree.

    Caller supplies a certified primitive generator. No generator discovery or
    field-table construction is hidden in this operation.
    """
    positive(base_degree, "base degree", field.n)
    require(field.n % base_degree == 0, "base degree must divide ambient degree")
    field.element(generator)
    field.element(desired)
    q, d = field.p**base_degree, field.n // base_degree
    require(desired != 0 and field.power(desired, q) == desired,
            "desired norm must be a nonzero base-field element")
    e = minimal_degree(q, d)
    h = field.power(generator, (field.order - 1) // (q**e - 1))
    norm_h = field.power(h, (field.order - 1) // (q - 1))
    value, candidate = 1, 1
    for exponent in range(q - 1):
        if value == desired:
            require(field.power(candidate, q**e) == candidate,
                    "witness escaped intermediate field")
            require(field.power(candidate, (field.order - 1) // (q - 1)) == desired,
                    "wrong witness norm")
            return {"element": candidate, "degree": e, "exponent": exponent}
        value = field.multiply(value, norm_h)
        candidate = field.multiply(candidate, h)
    raise ValueError("generator does not supply every requested norm")
