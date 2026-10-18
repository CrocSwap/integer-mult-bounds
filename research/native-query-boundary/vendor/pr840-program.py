"""Literal native BIT query-pair compiler; all VALUE additions are XOR.

ADDRESS scalings use exact rationals, specialized only to odd residue rings.
The child event denotes one full-row ordinary ADDRESS interchange. This
reference compiler does not implement or time the inherited tape primitive.
"""
from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def power(j, sign=1):
    require(type(j) is int and j >= 0, "nonnegative integer dyadic index")
    require(type(sign) is int and sign in (-1, 1), "integer sign")
    return sign * (1 << j)


def address_word(k):
    """Seven events for M(k)=I+(k/4)s r^T; k is a signed power of two."""
    require(type(k) is int and k != 0 and abs(k) & (abs(k) - 1) == 0,
            "nonzero signed dyadic power")
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


def run_address(address, word, modulus=None):
    """Execute the literal events, with optional full spectator coordinates."""
    require(len(address) >= 6, "six ADDRESS fields")
    if modulus is None:
        reduce = Fraction
        state = list(map(Fraction, address))
    else:
        require(type(modulus) is int and modulus >= 3 and modulus % 2 == 1,
                "odd residue modulus at least three")
        require(all(type(x) is int for x in address), "integer residue coordinates")

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


def fused_program(j, sign=1):
    a = power(j, sign)
    return (("query", 0, -a), ("xor", 0, 1), ("query", 0, 2 * a),
            ("xor", 0, 1), ("query", 0, -a))


def baseline_program(j, sign=1):
    a = power(j, sign)
    return (("query", 0, -a), ("xor", 0, 1), ("query", 0, a),
            ("xor", 0, 1), ("query", 0, a), ("xor", 0, 1),
            ("query", 0, -a), ("xor", 0, 1))


def inverse_program(program):
    return tuple(("query", event[1], -event[2]) if event[0] == "query"
                 else event for event in reversed(program))


def invoice(program):
    queries = [event[2] for event in program if event[0] == "query"]
    words = [address_word(k) for k in queries]
    return {"ordinary_children": len(queries),
            "ordered_affine_events": sum(sum(e[0] == "affine" for e in w)
                                         for w in words),
            "aligned_xor_scans": sum(e[0] == "xor" for e in program),
            "persistent_private_rows": 0,
            "query_powers": queries,
            "child_volume_fraction_each": "1/3",
            "child_width_fraction_each": "1/3"}


def run_bits(rows, program, permutations):
    """Sparse exact finite-array evaluator, mutating distinct dirty row sets.

    permutations[k][i] is the literal ADDRESS push map for the entire finite
    domain. No copying, erasure, or clean-row initialization is a program event.
    Python's simulator storage is not a physical tape/workspace measurement.
    """
    require(type(rows) is list and len(rows) >= 3, "three DATA rows")
    require(all(type(row) is set for row in rows), "mutable BIT position sets")
    require(len({id(row) for row in rows}) == len(rows), "distinct physical rows")
    for event in program:
        if event[0] == "query":
            _, row, k = event
            permutation = permutations[k]
            replacement = {permutation[i] for i in rows[row]}
            rows[row].clear()
            rows[row].update(replacement)
        else:
            _, target, source = event
            require(target != source, "distinct XOR source and target")
            rows[target].symmetric_difference_update(rows[source])
    return rows
