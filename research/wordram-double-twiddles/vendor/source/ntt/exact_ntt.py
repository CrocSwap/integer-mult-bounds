"""Exact zero-padded NTT multiplication; Python 3 standard library only.

Original reference implementation. CatCrypt supplies the cited mathematical
transform identities; this module is not claimed to be compiled from Lean.
No timing here is a Word RAM or integer-mult-bounds kappa certificate.
"""
from dataclasses import dataclass
from math import isqrt


@dataclass
class Counts:
    butterflies: int = 0
    twiddle_products: int = 0
    butterfly_products: int = 0
    pointwise_products: int = 0
    inverse_scales: int = 0
    # pow(), indexing, permutations and all other overhead are NOT counted.


def is_prime(p):
    return p >= 2 and all(p % d for d in range(2, isqrt(p) + 1))


def validate_root(p, n, omega):
    if not is_prime(p):
        raise ValueError("modulus must be prime")
    if n < 1 or n & (n - 1) or n >= p:
        raise ValueError("length must be a positive power of two less than p")
    if pow(omega, n, p) != 1 or (n > 1 and pow(omega, n // 2, p) == 1):
        raise ValueError("omega must have exact order n")


def ntt(values, p, omega, inverse=False, counts=None):
    """Positive-exponent forward DFT; normalized inverse for inverse=True."""
    n = len(values)
    validate_root(p, n, omega)
    a = [x % p for x in values]
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    root = pow(omega, p - 2, p) if inverse else omega
    width = 2
    while width <= n:
        wlen = pow(root, n // width, p)
        for lo in range(0, n, width):
            w = 1
            for j in range(lo, lo + width // 2):
                u = a[j]
                v = a[j + width // 2] * w % p
                a[j] = (u + v) % p
                a[j + width // 2] = (u - v) % p
                w = w * wlen % p
                if counts is not None:
                    counts.butterflies += 1
                    counts.butterfly_products += 1
                    counts.twiddle_products += 1
        width *= 2
    if inverse:
        invn = pow(n, p - 2, p)
        a = [v * invn % p for v in a]
        if counts is not None:
            counts.inverse_scales += n
    return a


def direct_dft(values, p, omega, inverse=False):
    """Independent quadratic transform oracle."""
    n = len(values)
    validate_root(p, n, omega)
    root = pow(omega, p - 2, p) if inverse else omega
    scale = pow(n, p - 2, p) if inverse else 1
    return [scale * sum(v * pow(root, j * k, p)
                        for j, v in enumerate(values)) % p
            for k in range(n)]


def schoolbook(a, b):
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] += x * y
    return c


def exact_convolution(a, b, base=16, p=65537, generator=3, counts=None):
    """Recover all nonnegative coefficients, under an explicit sufficient bound."""
    if not a or not b or base < 2:
        raise ValueError("nonempty digit vectors and base >= 2 required")
    if any(type(x) is not int or not 0 <= x < base for x in list(a) + list(b)):
        raise ValueError("digits must be integers in [0,base)")
    if min(len(a), len(b)) * (base - 1) ** 2 >= p:
        raise ValueError("coefficient bound must be strictly below modulus")
    length = len(a) + len(b) - 1
    n = 1 << (length - 1).bit_length()
    if not is_prime(p) or (p - 1) % n:
        raise ValueError("prime modulus must admit the required power-of-two root")
    omega = pow(generator, (p - 1) // n, p)
    aa = ntt(list(a) + [0] * (n - len(a)), p, omega, counts=counts)
    bb = ntt(list(b) + [0] * (n - len(b)), p, omega, counts=counts)
    cc = [(x * y) % p for x, y in zip(aa, bb)]
    if counts is not None:
        counts.pointwise_products += n
    c = ntt(cc, p, omega, inverse=True, counts=counts)
    if any(c[length:]):
        raise ArithmeticError("zero-padding invariant failed")
    return c[:length]


def carry_normalize(coefficients, base):
    """Euclidean carrying, including a possibly multi-digit terminal carry."""
    if base < 2 or any(type(c) is not int or c < 0 for c in coefficients):
        raise ValueError("base >= 2 and nonnegative integer coefficients required")
    out, carry = [], 0
    for c in coefficients:
        carry, digit = divmod(c + carry, base)
        out.append(digit)
    while carry:
        carry, digit = divmod(carry, base)
        out.append(digit)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [0]


def evaluate(digits, base):
    result = 0
    for digit in reversed(digits):
        result = result * base + digit
    return result


def multiply_digits(a, b, base=16, p=65537, generator=3, counts=None):
    return carry_normalize(exact_convolution(a, b, base, p, generator, counts), base)


def multiply_integers(x, y, base=16, p=65537, generator=3, counts=None):
    """Signed integer endpoint, under the same explicit digit-length contract."""
    if type(x) is not int or type(y) is not int or base < 2:
        raise ValueError("integer operands and base >= 2 required")
    def digits(v):
        out = []
        while v:
            v, d = divmod(v, base)
            out.append(d)
        return out or [0]
    z = evaluate(multiply_digits(digits(abs(x)), digits(abs(y)), base,
                                 p, generator, counts), base)
    return -z if (x < 0) != (y < 0) else z
