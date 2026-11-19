#!/usr/bin/env python3
"""An independent exact interpolation check on an embedded Clifford alphabet.

Coordinates and row weights are Gaussian integers with explicit common powers
of 8. No primary checker, predecessor code or numerical algebra is imported.
Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""

from collections import Counter, deque


ZERO = (0, 0)
ONE = (1, 0)
UNITS = (ONE, (0, 1), (-1, 0), (0, -1))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def add(z, w):
    return z[0] + w[0], z[1] + w[1]


def mul(z, w):
    return z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0]


def conj(z):
    return z[0], -z[1]


def scale(z, k):
    return z[0] * k, z[1] * k


def power(z, n):
    value = ONE
    while n:
        if n & 1:
            value = mul(value, z)
        z = mul(z, z)
        n //= 2
    return value


def multiply(a, b):
    """Multiply literal 2-by-2 Gaussian integer matrices in row-major order."""
    return tuple(add(mul(a[2*r], b[c]), mul(a[2*r+1], b[c+2]))
                 for r in range(2) for c in range(2))


def phase(a, unit):
    return tuple(mul(unit, entry) for entry in a)


def enumerate_alphabet():
    """Close on H'=(1+i)H/sqrt(2) and the phase gate, storing 2U."""
    identity = ((2, 0), ZERO, ZERO, (2, 0))
    gates = (((1, 1), (1, 1), (1, 1), (-1, -1)),
             ((2, 0), ZERO, ZERO, (0, 2)))
    seen = {identity}
    pending = deque([identity])
    while pending:
        current = pending.popleft()
        for gate in gates:
            expanded = multiply(current, gate)
            check(all(k % 2 == 0 for z in expanded for k in z),
                  "matrix failed its common denominator")
            child = tuple((a // 2, b // 2) for a, b in expanded)
            if child not in seen:
                seen.add(child)
                pending.append(child)
    representatives = sorted({min(phase(a, u) for u in UNITS) for a in seen})
    check(len(seen) == 96 and len(representatives) == 24,
          "incomplete one-qubit Clifford alphabet")
    return representatives


def coordinate_rows(target):
    # <U_a W_j,V>/2 on the normalized V tensor I_8 column. The four
    # nonzero row weights below act on V/4 at fixed spectator index 0.
    # V/4 has numerator 2V and denominator 8. For embedded inputs this is
    # equivalent to averaging all eight equal spectator blocks.
    identity = (ONE, ZERO, ZERO, ONE)
    x = (ZERO, ONE, ONE, ZERO)
    z = (ONE, ZERO, ZERO, (-1, 0))
    return [tuple(map(conj, multiply(target, w)))
            for w in (identity, x, z, multiply(x, z))]


def inner(row, column):
    result = ZERO
    for a, b in zip(row, column):
        result = add(result, mul(a, b))
    return result


def inversion_terms():
    # Actual subspaces of F_2^2. All other F_2^8 subspaces contain a
    # probe outside this active plane and hence contribute zero. Restrict
    # the first E8 block to two coordinate functions of RM(1,3).
    bases = [(), (1,), (2,), (3,), (1, 2)]
    terms = []
    for basis in bases:
        columns = []
        for position in range(16):
            label = 0
            if position < 8:
                for bit, point in enumerate(basis):
                    if position & (1 << bit):
                        label ^= point
            columns.append(label)
        # In the F_2^2 subspace lattice the top coefficient is +2:
        # 1 (bottom) - 3 (lines) + 2 (plane) = 0.
        terms.append(((1, -1, 2)[len(basis)], tuple(columns)))
    check(Counter(terms[-1][1]) == {0: 10, 1: 2, 2: 2, 3: 2},
          "bad restriction of the doubly-even length-16 probe")
    return terms


def evaluate(points, terms):
    total = ZERO
    for weight, columns in terms:
        value = ONE
        for j in columns:
            value = mul(value, points[j])
        total = add(total, scale(value, weight))
    return mul(points[0], total)


def multiply_linear(poly, row):
    result = {}
    for word, a in poly.items():
        for i, b in enumerate(row):
            if b == ZERO:
                continue
            next_word = list(word)
            next_word[i] += 1
            key = tuple(next_word)
            result[key] = add(result.get(key, ZERO), mul(a, b))
    return {key: z for key, z in result.items() if z != ZERO}


def literal_tensor_row(rows, terms):
    """Lift each monomial to one grouped, ordered tensor coordinate."""
    result = {}
    for weight, columns in terms:
        poly = {(0, 0, 0, 0): (weight, 0)}
        for index in (0,) + columns:
            poly = multiply_linear(poly, rows[index])
        for address, value in poly.items():
            check(sum(address) == 17, "inhomogeneous tensor coordinate")
            result[address] = add(result.get(address, ZERO), value)
    return {address: z for address, z in result.items() if z != ZERO}


def literal_column_entry(column, address):
    value = ONE
    for entry, count in zip(column, address):
        value = mul(value, power(entry, count))
    return value


def main():
    representatives = enumerate_alphabet()
    # Each target may have an arbitrary independent choice of scalar lift.
    targets = [phase(a, UNITS[i % 4]) for i, a in enumerate(representatives)]
    terms = inversion_terms()
    faults = {"top-term dropped": terms[:-1],
              "sign of lines reversed": [(abs(w), p) for w, p in terms],
              "bad code column": [*terms[:-1], (2, (1,) + terms[-1][1][1:])]}
    rejected = set()
    literal_cases = 0
    literal_coefficients = 0
    checked_widths = (17, 18, 19, 20)
    expanded_shapes = set()
    for a, target in enumerate(targets):
        rows = coordinate_rows(target)
        # Include one sparse and one flat source matrix in tensor-row
        # expansion. All source matrices are checked by direct evaluation.
        literal = None
        nonzero = sum(z != ZERO for z in target)
        if nonzero not in expanded_shapes:
            expanded_shapes.add(nonzero)
            literal = literal_tensor_row(rows, terms)
            literal_coefficients += len(literal)
        for b, other in enumerate(targets):
            points = [inner(row, other) for row in rows]
            canonical = evaluate(points, terms)
            for bug, mutated in faults.items():
                if bug not in rejected and evaluate(points, mutated) != canonical:
                    rejected.add(bug)
            if literal is not None:
                entry = ZERO
                for address, value in literal.items():
                    entry = add(entry, mul(value, literal_column_entry(other, address)))
                check(entry == canonical, "literal tensor contraction mismatch")
                literal_cases += 1
            for unit in UNITS:
                actual = [mul(unit, p) for p in points]
                base = evaluate(actual, terms)
                for width in checked_widths:
                    recovered = mul(base, power(actual[0], width - 17))
                    expected = scale(power(unit, width), 8**width) if a == b else ZERO
                    check(recovered == expected, "incorrect normalized left-inverse entry")
    check(rejected == set(faults), "a faulty construction survived the calibration")
    check(expanded_shapes == {2, 4} and literal_cases == 48 and literal_coefficients > 0,
          "missing sparse or flat literal tensor coverage")
    print("PASS_INDEPENDENT_CLIFFORD_MOBIUS",
          f"cosets={len(targets)} gauge_pairs={len(targets)**2*len(UNITS)}",
          f"normalized_width_checks={len(targets)**2*len(UNITS)*len(checked_widths)}",
          f"literal_entries={literal_cases} literal_coefficients={literal_coefficients}",
          f"mutants_rejected={len(rejected)}")


if __name__ == "__main__":
    main()
