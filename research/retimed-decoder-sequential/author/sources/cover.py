"""Lower a rational right action on a whole GL cover to fixed stream operations."""

from collections import deque
from fractions import Fraction
from itertools import islice, product
from math import gcd


def require(condition, message):
    if not condition:
        raise ValueError(message)


def residue(value, modulus):
    value = Fraction(value)
    return value.numerator * pow(value.denominator, -1, modulus) % modulus


def row_program(matcher, prime):
    """Act on one row X by X S. Use pivots that are units at the actual prime."""
    rows = [[Fraction(x) for x in row] for row in zip(*matcher, strict=True)]
    n = len(rows)
    require(n > 0 and all(len(row) == n for row in rows), "square matcher")
    require(
        all(v.denominator % prime for row in rows for v in row), "matcher denominator"
    )
    undo = []
    for j in range(n):
        pivot = next((k for k in range(j, n) if residue(rows[k][j], prime)), None)
        require(pivot is not None, "singular low matcher")
        if pivot != j:
            rows[j], rows[pivot] = rows[pivot], rows[j]
            undo.append(("swap", j, pivot))
        unit = rows[j][j]
        if unit != 1:
            rows[j] = [a / unit for a in rows[j]]
            undo.append(("scale", j, unit))
        for k in range(n):
            if k != j and rows[k][j]:
                factor = rows[k][j]
                rows[k] = [
                    a - factor * b for a, b in zip(rows[k], rows[j], strict=True)
                ]
                undo.append(("add", k, j, factor))
    return tuple(reversed(undo))


def low_action(low, matcher, prime):
    """Return the fixed new low type and the exact rational high carry."""
    columns = list(zip(*matcher, strict=True))
    moved = [
        [sum(x * y for x, y in zip(row, col, strict=True)) for col in columns]
        for row in low
    ]
    representative = [[residue(x, prime) for x in row] for row in moved]
    carry = [
        [(Fraction(x) - y) / prime for x, y in zip(row, rep, strict=True)]
        for row, rep in zip(moved, representative, strict=True)
    ]
    require(
        all(c.denominator % prime for row in carry for c in row),
        "nonintegral high carry",
    )
    return representative, carry


def scale_integer(stream, size, multiplier, inverse=False):
    """Permute one complete sequence. A record can carry any opaque suffix."""
    require(multiplier > 0 and gcd(multiplier, size) == 1, "unit scaling")
    if size == 1 or multiplier == 1:
        return list(stream)
    # Each run is increasing in the output address. The selector has fixed period.
    runs = [deque() for _ in range(multiplier)]
    selector = -pow(size, -1, multiplier) % multiplier
    if inverse:
        for y, record in enumerate(stream):
            runs[(selector * y) % multiplier].append(record)
        return [record for run in runs for record in run]
    for x, record in enumerate(stream):
        runs[multiplier * x // size].append(record)
    return [runs[(selector * y) % multiplier].popleft() for y in range(size)]


def scale_records(records, value):
    unit = Fraction(value)
    data = scale_integer(records, len(records), abs(unit.numerator))
    if unit < 0:
        data = data[:1] + data[:0:-1]
    return scale_integer(data, len(data), unit.denominator, inverse=True)


def digit_swap(stream, prefix, radix, gap, suffix):
    """Permute [prefix][radix][gap][radix][suffix] by stable digit buckets."""
    data = iter(stream)
    result = []
    for _ in range(prefix):
        buckets = [[[] for _ in range(radix)] for _ in range(radix)]
        for a in range(radix):
            for _ in range(gap):
                for b in range(radix):
                    piece = list(islice(data, suffix))
                    require(len(piece) == suffix, "incomplete suffix")
                    buckets[b][a].append(piece)
        for by_input in buckets:
            for pieces in zip(*by_input, strict=True):
                for piece in pieces:
                    result.extend(piece)
    return result


def cold_swap(data, q, width, prefix, gap, suffix):
    """Exchange two q^width fields across any complete gap."""
    for j in range(width):
        data = digit_swap(
            data,
            prefix * q**j,
            q,
            gap * q ** (width - 1),
            suffix * q ** (width - 1 - j),
        )
    return data


def elementary_swap(stream, q, width, fields, left, right):
    left, right = sorted((left, right))
    side = q**width
    return cold_swap(
        stream,
        q,
        width,
        side**left,
        side ** (right - left - 1),
        side ** (fields - 1 - right),
    )


def target_pass(stream, size, fields, target, operation):
    """Read the prefix in order. Move each suffix as one complete record."""
    length = size ** (fields - target - 1)
    source = iter(stream)
    result = []
    for prefix in product(range(size), repeat=target):
        slots = [list(islice(source, length)) for _ in range(size)]
        require(all(len(slot) == length for slot in slots), "truncated target range")
        for slot in operation(prefix, slots):
            result.extend(slot)
    return result


def rotate(slots, offset):
    offset %= len(slots)
    return slots[-offset:] + slots[:-offset] if offset else slots


def high_stream(stream, matcher, prime, width, carry, swap=elementary_swap):
    """Run the high part in physical row order. An old swap accepts the full gap."""
    n = len(matcher)
    fields = n * n
    size = prime ** (width - 1)
    data = list(stream)
    require(len(data) == size**fields, "incomplete high fibre")
    program = row_program(matcher, prime)
    if size == 1:
        return data
    for row in range(n):
        for op, *args in program:
            target = row * n + args[0]
            if op == "scale":
                data = target_pass(
                    data,
                    size,
                    fields,
                    target,
                    lambda _prefix, slots: scale_records(slots, args[1]),
                )
            elif op == "swap":
                data = swap(data, prime, width - 1, fields, target, row * n + args[1])
            else:
                source = row * n + args[1]
                swapped = source > target
                if swapped:
                    data = swap(data, prime, width - 1, fields, target, source)
                    target, source = source, target
                coeff = residue(args[2], size)
                data = target_pass(
                    data,
                    size,
                    fields,
                    target,
                    lambda prefix, slots: rotate(slots, prefix[source] * coeff),
                )
                if swapped:
                    data = swap(data, prime, width - 1, fields, target, source)
        for j, c in enumerate(carry[row]):
            if c:
                offset = residue(c, size)
                data = target_pass(
                    data,
                    size,
                    fields,
                    row * n + j,
                    lambda _, slots: rotate(slots, offset),
                )
    return data
