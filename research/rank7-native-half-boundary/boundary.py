# SPDX-License-Identifier: Apache-2.0
"""Exact Gaussian rows for one native rank-seven half-ADD boundary."""

from fractions import Fraction as Q

DIM = 512


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add_rows(left, right, factor=Q(1)):
    out = left.copy()
    for key, (real, imag) in right.items():
        a, b = out.get(key, (Q(0), Q(0)))
        value = a + factor * real, b + factor * imag
        if value != (0, 0):
            out[key] = value
        else:
            out.pop(key, None)
    require(len(out) <= 16, "bounded Gaussian row support")
    return out


def multiply(row, real, imag):
    return {
        key: (real * a - imag * b, real * b + imag * a) for key, (a, b) in row.items()
    }


def matrix(circuit, initial=None, observations=None):
    """Apply literal gates to sparse complex rows, with no packed arithmetic."""
    require(len(circuit) <= 20, "bounded local circuit")
    rows = [{x: (Q(1), Q(0))} for x in range(DIM)] if initial is None else initial
    require(len(rows) == DIM, "complete local field")
    require(all(len(row) <= 16 for row in rows), "bounded initial row support")
    for index, gate in enumerate(circuit):
        tag = gate[0]
        if tag == "P":
            require(len(gate[1]) == 9, "nine-axis permutation")
            perm = [
                sum(((r & x).bit_count() % 2) << i for i, r in enumerate(gate[1]))
                for x in range(DIM)
            ]
            require(set(perm) == set(range(DIM)), "invertible permutation")
            moved = [None] * DIM
            for x, y in enumerate(perm):
                moved[y] = rows[x]
            rows = moved
        elif tag == "D":
            quad, linear = gate[1:]
            require(len(quad) == len(linear) == 9, "nine-axis phase")
            moved = []
            for x in range(DIM):
                phase = sum(linear[i] for i in range(9) if x >> i & 1)
                phase += 2 * sum(
                    ((quad[i] >> (i + 1)) & (x >> (i + 1))).bit_count() % 2
                    for i in range(9)
                    if x >> i & 1
                )
                moved.append(
                    multiply(rows[x], *[(1, 0), (0, 1), (-1, 0), (0, -1)][phase % 4])
                )
            rows = moved
        elif tag == "C":
            axis, sign = gate[1:]
            require(0 < axis < DIM and sign in (-1, 1), "valid square-root gate")
            numerator = [
                add_rows(multiply(rows[x], 1, sign), multiply(rows[x ^ axis], 1, -sign))
                for x in range(DIM)
            ]
            if observations is not None:
                observations.append((index, "numerator", numerator))
            rows = [multiply(row, Q(1, 2), 0) for row in numerator]
        else:
            raise ValueError("unsupported local gate: " + str(tag))
        if observations is not None:
            observations.append((index, "endpoint", rows))
    return rows


def component(row, imaginary=False):
    """Real input component 2*x, imaginary input component 2*x+1."""
    out = {}
    for x, (a, b) in row.items():
        if a:
            out[2 * x + int(imaginary)] = a
        if b:
            out[2 * x + int(not imaginary)] = b if imaginary else -b
    return out


def output_rows(frame, source):
    """Five independent complex fields: 126,127,164,165,83."""
    rows = []
    for x in range(DIM):
        for imaginary in (False, True):
            row = {}
            for field, sign in enumerate((1, -1, 1, -1)):
                for atom, value in component(frame[x], imaginary).items():
                    row[field * 2 * DIM + atom] = sign * value / 2
            for atom, value in component(source[x], imaginary).items():
                row[4 * 2 * DIM + atom] = -value / 2
            rows.append(row)
    return rows


def interval(row, precision):
    require(type(precision) is int and 3 <= precision <= 128, "input precision 3..128")
    limit = 1 << (precision - 1)
    positive = sum((q for q in row.values() if q > 0), Q(0))
    negative = sum((-q for q in row.values() if q < 0), Q(0))
    return -limit * positive - (limit - 1) * negative, (
        limit - 1
    ) * positive + limit * negative


def summary(rows, precision):
    require(0 < len(rows) <= 2048, "bounded real row inventory")
    require(all(len(r) <= 32 for r in rows), "bounded real row support")
    values = [q for row in rows for q in row.values()]
    require(all(q.denominator.bit_count() == 1 for q in values), "dyadic coefficients")
    depth = max(q.denominator.bit_length() - 1 for q in values)
    bounds = [interval(row, precision) for row in rows]
    low, high = min(a for a, _ in bounds), max(b for _, b in bounds)
    extent = max(-low * 2**depth, high * 2**depth + 1)
    require(extent.denominator == 1, "integral encoded bound")
    width = 1 + (int(extent) - 1).bit_length()
    return {
        "fractional_bits": depth,
        "max_norm": str(max(sum(map(abs, r.values())) for r in rows)),
        "low": str(low),
        "high": str(high),
        "signed_width": width,
    }


def evaluate(row, assignment):
    return sum((q * assignment.get(atom, 0) for atom, q in row.items()), Q(0))


def witnesses(rows, precision, expected):
    depth, width = expected["fractional_bits"], expected["signed_width"]
    limit = 1 << (precision - 1)
    index, atom, q = next(
        (i, a, q)
        for i, r in enumerate(rows)
        for a, q in r.items()
        if q.denominator == 2**depth
    )
    require((q * 2 ** (depth - 1)).denominator == 2, "smaller grid fails")
    out = {"grid": {"row": index, "atom": atom, "value": str(q)}}
    for side in ("low", "high"):
        index = next(
            i
            for i, r in enumerate(rows)
            if str(interval(r, precision)[side == "high"]) == expected[side]
        )
        row = rows[index]
        assignment = {
            a: (limit - 1 if (q > 0) == (side == "high") else -limit)
            for a, q in row.items()
        }
        value = evaluate(row, assignment)
        require(str(value) == expected[side], "attaining box endpoint")
        encoded = value * 2**depth
        require(
            not -(1 << (width - 2)) <= encoded < (1 << (width - 2)),
            "smaller signed width fails",
        )
        out[side] = {
            "row": index,
            "value": str(value),
            "encoded": str(encoded),
            "assignment": [[a, value] for a, value in sorted(assignment.items())],
        }
    return out
