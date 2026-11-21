"""Lower a rank-one covered leaf to later-target shears and reversed children."""

from math import gcd
from retained import fallback


def good_column(projector, weights, modulus):
    m = len(weights)
    d = weights[0] * projector[0][0] % modulus
    di = pow(d, -1, modulus)
    pi = pow(projector[0][0], -1, modulus)
    lower = [
        ["lower", i, 0, -weights[i] * projector[i][0] * di % modulus]
        for i in range(1, m)
    ]
    lower.extend(
        ["lower", 2 * m - 1, m + i, projector[0][m - 1 - i] * pi % modulus]
        for i in range(m - 1)
    )

    def undo(ops):
        return [["lower", i, j, -c % modulus] for _, i, j, c in reversed(ops)]

    unit = fallback.identity(2 * m)
    t = fallback.execute_rows(lower, unit, modulus)
    tinv = fallback.execute_rows(undo(lower), unit, modulus)
    source = fallback.conjugate_diagonal(
        fallback.residual(projector, modulus), [*weights, *[1] * m], modulus
    )
    reduced = fallback.multiply(fallback.multiply(t, source, modulus), tinv, modulus)
    a = [(reduced[0][j] - int(j == 0)) % modulus for j in range(m)]
    for i in range(m):
        b = (reduced[m + i][-1] - int(i == m - 1)) * di
        lower.append(["lower", m + i, 0, (-b - int(i == m - 1) * di) % modulus])
    lower.extend(["lower", 2 * m - 1, j, di * a[j] % modulus] for j in range(1, m))
    return lower + [["weighted_swap", 0, 2 * m - 1, d]] + undo(lower)


def column_program(projector, weights, prime, width):
    modulus = prime**width
    if gcd(projector[0][0], prime) == 1:
        return good_column(projector, weights, modulus), True
    pm = fallback.residual(projector, modulus)
    pm = fallback.conjugate_diagonal(pm, [*weights, *[1] * len(weights)], modulus)
    plan = fallback.compile_fallback(pm, prime, width)
    return plan["lowered_operations"], False


def reversed_call(left, right, weights, modulus):
    """One reversed child. Weight j refers to the head position j."""
    return (
        [a * y % modulus for a, y in zip(weights, reversed(right), strict=True)],
        list(
            reversed(
                [
                    pow(a, -1, modulus) * x % modulus
                    for a, x in zip(weights, left, strict=True)
                ]
            )
        ),
    )


def reverse_by_halves(field, modulus):
    half = len(field) // 2
    if not half:
        return list(field)
    first, last = reversed_call(field[:half], field[-half:], [1] * half, modulus)
    return first + field[half : len(field) - half] + last


def run_columns(projector, weight_columns, head, tail, prime, width):
    """Execute the fixed low-class topology on actual atom order."""
    m = len(projector)
    f = len(weight_columns)
    modulus = prime**width
    fields = [list(row) for row in head + tail]
    plans = [column_program(projector, a, prime, width) for a in weight_columns]
    good = plans[0][1]
    calls = []
    for ops in zip(*(p for p, _ in plans), strict=True):
        op, i, j = ops[0][:3]
        if op == "sign":
            if not all(ins == ops[0] for ins in ops):
                raise ValueError("variable low-class sign")
            fields[i] = [j * x % modulus for x in fields[i]]
            continue
        if not all(ins[:3] == ops[0][:3] for ins in ops):
            raise ValueError("variable low-class topology")
        units = [ins[3] for ins in ops]
        if op == "lower":
            for k, c in enumerate(units):
                dest = k if i < m else f - 1 - k
                src = k if j < m else f - 1 - k
                fields[i][dest] = (fields[i][dest] + c * fields[j][src]) % modulus
        else:
            if op != "weighted_swap":
                raise ValueError("unlowered instruction")
            if i >= m:
                units.reverse()
            # Opposite banks have opposite column order. Equal orientations
            # need two real half reversals around the middle reversed child.
            same = (i < m) == (j < m)
            data = reverse_by_halves(fields[j], modulus) if same else fields[j]
            fields[i], result = reversed_call(fields[i], data, units, modulus)
            fields[j] = reverse_by_halves(result, modulus) if same else result
            calls.append(f)
            if same and f // 2:
                calls.extend((f // 2, f // 2))
    return fields, good, calls
