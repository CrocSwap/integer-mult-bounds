"""Literal odd-kernel native BIT query-pair compiler; VALUE addition is XOR.

ADDRESS scalings use exact rationals specialized to odd residue rings that are
coprime to the odd kernel (here kernel 3). The child event is one ordinary
full-row ADDRESS interchange. This reference compiler does not implement the
inherited tape primitive.
"""
from fractions import Fraction


def need(condition, message):
    if not condition:
        raise ValueError(message)


def odd_kernel_power(j, sign=1, kernel=3):
    """a = sign * kernel * 2^j for nonnegative j."""
    need(type(j) is int and j >= 0, "nonnegative dyadic index")
    need(type(sign) is int and sign in (-1, 1), "integer sign")
    need(type(kernel) is int and kernel > 0 and kernel % 2 == 1, "positive odd kernel")
    return sign * kernel * (1 << j)


def address_word(k):
    """Seven events for M(k)=I+(k/4) s r^T; k is any nonzero integer.

    For dyadic k this recovers PR521/PR840. For odd-kernel k the same word is
    valid over every odd modulus invertible for the odd part of k (and of the
    resulting diagonal units). No all-odd-radix claim is made.
    """
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
            result.append(("affine", target, 1 / diagonal,
                           tuple((i, -c / diagonal) for i, c in controls)))
    return tuple(result)


def odd_part(n):
    n = abs(int(n))
    while n % 2 == 0:
        n //= 2
    return n


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
    """Odd residue rings on which every diagonal/control denominator of the lowering inverts."""
    need(type(modulus) is int and modulus >= 3, "modulus at least three")
    if modulus % 2 == 0:
        return False
    dens = word_denominators(address_word(k))
    for d in dens:
        if d % modulus == 0:
            return False
        try:
            pow(d % modulus, -1, modulus)
        except ValueError:
            return False
    return True


def run_address(address, word, modulus=None):
    need(len(address) >= 6, "six ADDRESS fields")
    if modulus is None:
        reduce = Fraction
        state = list(map(Fraction, address))
    else:
        need(type(modulus) is int and modulus >= 3 and modulus % 2 == 1,
             "odd residue modulus at least three")
        for dens in word_denominators(word):
            need(dens % modulus != 0, "denominator not invertible on this modulus")
            pow(dens % modulus, -1, modulus)
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
                reduce(c) * state[i] for i, c in controls)
            if modulus is not None:
                state[target] %= modulus
    return tuple(state)


def fused_program(j=0, sign=1, kernel=3):
    a = odd_kernel_power(j, sign, kernel)
    return (("query", 0, -a), ("xor", 0, 1), ("query", 0, 2 * a),
            ("xor", 0, 1), ("query", 0, -a))


def baseline_program(j=0, sign=1, kernel=3):
    a = odd_kernel_power(j, sign, kernel)
    return (("query", 0, -a), ("xor", 0, 1), ("query", 0, a),
            ("xor", 0, 1), ("query", 0, a), ("xor", 0, 1),
            ("query", 0, -a), ("xor", 0, 1))


def inverse_program(program):
    return tuple(("query", event[1], -event[2]) if event[0] == "query"
                 else event for event in reversed(program))


def invoice(program):
    queries = [event[2] for event in program if event[0] == "query"]
    words = [address_word(k) for k in queries]
    return {
        "ordinary_children": len(queries),
        "ordered_affine_events": sum(sum(e[0] == "affine" for e in w) for w in words),
        "aligned_xor_scans": sum(e[0] == "xor" for e in program),
        "persistent_private_rows": 0,
        "query_powers": queries,
        "child_volume_fraction_each": "1/3",
        "child_width_fraction_each": "1/3",
        "kernel": 3,
    }


def run_bits(rows, program, permutations):
    need(type(rows) is list and len(rows) >= 3, "three DATA rows")
    need(all(type(row) is set for row in rows), "mutable BIT position sets")
    need(len({id(row) for row in rows}) == len(rows), "distinct physical rows")
    for event in program:
        if event[0] == "query":
            _, row, k = event
            permutation = permutations[k]
            replacement = {permutation[i] for i in rows[row]}
            rows[row].clear()
            rows[row].update(replacement)
        else:
            _, target, source = event
            need(target != source, "distinct XOR source and target")
            rows[target].symmetric_difference_update(rows[source])
    return rows


def push_matrix(k):
    """Independent closed form M(k)=I+(k/4) s r^T on six ADDRESS fields."""
    s = (1, 0, 1, -1, 0, -1)
    r = (1, 0, -1, -1, 0, 1)
    c = Fraction(k, 4)
    return tuple(
        tuple((Fraction(1) if i == j else Fraction(0)) + c * s[i] * r[j]
              for j in range(6))
        for i in range(6)
    )


def apply_matrix(matrix, vector):
    return tuple(sum(matrix[i][j] * Fraction(vector[j]) for j in range(6))
                 for i in range(6))
