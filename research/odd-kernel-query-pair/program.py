"""General odd-kernel native BIT query-pair compiler; VALUE addition is XOR.

ADDRESS scalings use exact rationals specialized to odd residue rings coprime
to the odd kernel q. The child event is one ordinary full-row ADDRESS
interchange. This reference compiler does not implement the inherited tape
primitive.

Kernel q=1 recovers PR840 (all odd moduli). Kernel q=3 recovers the pending
triadic package. This module parameterizes arbitrary odd q.
"""
from fractions import Fraction
from math import gcd


def need(condition, message):
    if not condition:
        raise ValueError(message)


def odd_kernel_power(j, sign=1, kernel=1):
    """a = sign * kernel * 2^j for nonnegative j and positive odd kernel."""
    need(type(j) is int and j >= 0, "nonnegative dyadic index")
    need(type(sign) is int and sign in (-1, 1), "integer sign")
    need(type(kernel) is int and kernel > 0 and kernel % 2 == 1, "positive odd kernel")
    return sign * kernel * (1 << j)


def odd_part(n):
    n = abs(int(n))
    while n % 2 == 0 and n:
        n //= 2
    return n


def odd_primes(n):
    """Distinct odd prime factors of |n|."""
    n = odd_part(n)
    primes = []
    p = 3
    while p * p <= n:
        if n % p == 0:
            primes.append(p)
            while n % p == 0:
                n //= p
        p += 2
    if n > 1:
        primes.append(n)
    return tuple(primes)


def address_word(k):
    """Seven events for M(k)=I+(k/4) s r^T; k nonzero integer."""
    need(type(k) is int and k != 0, "nonzero integer query power")
    a = Fraction(k, 4)
    return (
        ("affine", 2, Fraction(1), ((0, Fraction(-1)),)),
        ("affine", 3, Fraction(1), ((0, Fraction(1)),)),
        ("affine", 5, a, ((0, 1 + a), (2, -a), (3, -a))),
        ("child", 0, 5),
        ("affine", 2, Fraction(1), ((0, Fraction(1)),)),
        ("affine", 3, Fraction(1), ((0, Fraction(-1)),)),
        ("affine", 5, -1 / a, ((0, 1 / a - 1), (2, Fraction(1)),
                              (3, Fraction(1)))),
    )


def inverse_word(word):
    result = []
    for event in reversed(word):
        if event[0] == "child":
            result.append(event)
        else:
            _, target, diagonal, controls = event
            result.append(
                (
                    "affine",
                    target,
                    1 / diagonal,
                    tuple((i, -c / diagonal) for i, c in controls),
                )
            )
    return tuple(result)


def word_denominators(word):
    dens = set()
    for event in word:
        if event[0] != "affine":
            continue
        dens.add(Fraction(event[2]).denominator)
        for _, c in event[3]:
            dens.add(Fraction(c).denominator)
    return dens


def modulus_admits(k, modulus):
    """Whether every diagonal/control denominator of the lowering inverts mod modulus."""
    need(type(modulus) is int and modulus >= 2, "modulus at least two")
    if modulus % 2 == 0:
        return False
    dens = word_denominators(address_word(k))
    for d in dens:
        if gcd(d, modulus) != 1:
            return False
    return True


def modulus_admits_kernel(kernel, modulus):
    """Closed-form admission: odd modulus coprime to the odd kernel."""
    need(type(kernel) is int and kernel > 0 and kernel % 2 == 1, "odd kernel")
    need(type(modulus) is int and modulus >= 2, "modulus")
    return modulus % 2 == 1 and gcd(modulus, kernel) == 1


def run_address(address, word, modulus=None):
    need(len(address) >= 6, "six ADDRESS fields")
    if modulus is None:
        reduce = Fraction
        state = list(map(Fraction, address))
    else:
        need(type(modulus) is int and modulus >= 3 and modulus % 2 == 1,
             "odd residue modulus at least three")
        for dens in word_denominators(word):
            need(gcd(dens, modulus) == 1, "denominator not invertible on this modulus")
        need(all(type(x) is int for x in address), "integer residue coordinates")

        def reduce(value):
            value = Fraction(value)
            return value.numerator * pow(value.denominator, -1, modulus) % modulus

        state = [x % modulus for x in address]
    for event in word:
        if event[0] == "child":
            _, first, last = event
            state[first], state[last] = state[last], state[first]
        else:
            _, target, diagonal, controls = event
            state[target] = reduce(diagonal) * state[target] + sum(
                reduce(c) * state[i] for i, c in controls
            )
            if modulus is not None:
                state[target] %= modulus
    return tuple(state)


def fused_program(j=0, sign=1, kernel=1):
    a = odd_kernel_power(j, sign, kernel)
    return (
        ("query", 0, -a),
        ("xor", 0, 1),
        ("query", 0, 2 * a),
        ("xor", 0, 1),
        ("query", 0, -a),
    )


def baseline_program(j=0, sign=1, kernel=1):
    a = odd_kernel_power(j, sign, kernel)
    return (
        ("query", 0, -a),
        ("xor", 0, 1),
        ("query", 0, a),
        ("xor", 0, 1),
        ("query", 0, a),
        ("xor", 0, 1),
        ("query", 0, -a),
        ("xor", 0, 1),
    )


def invoice(program, kernel=None):
    queries = [event[2] for event in program if event[0] == "query"]
    words = [address_word(k) for k in queries]
    out = {
        "ordinary_children": len(queries),
        "ordered_affine_events": sum(sum(e[0] == "affine" for e in w) for w in words),
        "aligned_xor_scans": sum(e[0] == "xor" for e in program),
        "persistent_private_rows": 0,
        "query_powers": queries,
        "child_volume_fraction_each": "1/3",
        "child_width_fraction_each": "1/3",
    }
    if kernel is not None:
        out["kernel"] = kernel
    return out


def push_matrix(k):
    """Closed form M(k)=I+(k/4) s r^T on six ADDRESS fields."""
    s = (1, 0, 1, -1, 0, -1)
    r = (1, 0, -1, -1, 0, 1)
    c = Fraction(k, 4)
    return tuple(
        tuple((Fraction(1) if i == j else Fraction(0)) + c * s[i] * r[j] for j in range(6))
        for i in range(6)
    )


def apply_matrix(matrix, vector):
    return tuple(
        sum(matrix[i][j] * Fraction(vector[j]) for j in range(6)) for i in range(6)
    )


def fused_query_powers(j, sign, kernel):
    a = odd_kernel_power(j, sign, kernel)
    return (-a, 2 * a, -a)
