"""Exact integer operations for the contracts in PROOF.md.

Prepared for Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. See NOTICE.md for source credit.
"""


def nearest(numerator, denominator):
    """Round a rational number to nearest, with ties toward positive infinity."""
    if denominator <= 0:
        raise ValueError("positive denominator required")
    return (2 * numerator + denominator) // (2 * denominator)


def residue_response(p, q, residue, shift):
    """Use a saved numerator residue to recover the exact output difference."""
    if not 0 <= residue < q:
        raise ValueError("canonical residue required")
    return nearest(residue + p * shift, q) - nearest(residue, q)


def offset_sum(p, q, value):
    """Use all q residue offsets and subtract their prepared constants."""
    return sum(nearest(p * (value + r), q) - nearest(p * r, q)
               for r in range(q))


def replay(word, state, leaf):
    """Execute signed shears on a copied scalar state."""
    result = list(state)
    for source, target, factor, sign in word:
        result[target] += sign * leaf(factor, result[source])
    return result


def inverse(word):
    return [(s, t, i, -sign) for s, t, i, sign in reversed(word)]


def prefix_degree(word, rows):
    """Keep every initial-row symbol and every ordered factor word."""
    state = [{((), i): 1} for i in range(rows)]
    degree = 0
    for source, target, factor, sign in word:
        for (factors, origin), coefficient in state[source].items():
            monomial = ((factor,) + factors, origin)
            value = state[target].get(monomial, 0) + sign * coefficient
            if value:
                state[target][monomial] = value
                degree = max(degree, len(monomial[0]))
            else:
                state[target].pop(monomial, None)
    return degree


def exact_lift(word, initial, p, q, degree):
    """Execute the word on integer numerators with denominator q**degree.

    The returned counts exclude the verifier's copied state. A backend must
    also pay for routing, coefficients, control, scalar work, and preparation.
    """
    if q < 1 or degree < 0:
        raise ValueError("positive denominator and nonnegative degree required")
    denominator = q ** degree
    state = [[value * denominator for value in row] for row in initial]
    peak = max(abs(value) for row in state for value in row)
    entries = sum(map(len, initial))
    count = {
        "initial_reads": entries,
        "initial_products": entries,
        "initial_writes": entries,
        "source_reads": 0,
        "target_reads": 0,
        "writes": 0,
        "products": 0,
        "exact_divisions": 0,
        "additions": 0,
    }
    for source, target, factor, sign in word:
        for j in range(len(state[source])):
            product = p * state[source][j]
            quotient, remainder = divmod(product, q)
            if remainder:
                raise ValueError("exact lift needs more denominator precision")
            state[target][j] += sign * quotient
            peak = max(peak, abs(product), abs(state[target][j]))
            for key in ("source_reads", "target_reads", "writes", "products",
                        "exact_divisions", "additions"):
                count[key] += 1
    count["peak_signed_bits"] = peak.bit_length() + 1
    count["denominator_bits"] = denominator.bit_length()
    return state, denominator, count
