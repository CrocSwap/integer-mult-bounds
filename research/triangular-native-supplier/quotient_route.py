"""Move full arbitrary records on lower-unitriangular chart classes."""

from math import prod

from limb_scale import unit_scale
from streaming_routes import copy_bytes, erase, read_exact, shift_field, work_tapes
from ternary_frames import residue


def digits_in_order(radix, width):
    """Emit each tuple once. Keep a single counter with the stated width."""
    row = [0] * width
    while True:
        yield tuple(row)
        pos = width - 1
        while pos >= 0 and row[pos] == radix - 1:
            row[pos] = 0
            pos -= 1
        if pos < 0:
            return
        row[pos] += 1


def low_count(n):
    return prod(3**d - 1 for d in range(1, n + 1))


def free_count(n):
    return n * (n + 1) // 2


def low_rows(n):
    """Emit the canonical representatives in row-major lexicographic order."""
    limits = tuple(3**width for width in range(n, 0, -1))
    ordinals = [1] * n
    while True:
        free = list(range(n))
        rows = []
        for ordinal in ordinals:
            row = [0] * n
            for column in reversed(free):
                ordinal, row[column] = divmod(ordinal, 3)
            pivot = next(column for column in free if row[column])
            free.remove(pivot)
            rows.append(tuple(row))
        yield tuple(rows)
        for index in reversed(range(n)):
            ordinals[index] += 1
            if ordinals[index] < limits[index]:
                break
            ordinals[index] = 1
        else:
            return


def positions(low):
    free = tuple(range(len(low)))
    result = []
    for row in low:
        result.append(free)
        pivot = next(c for c in free if row[c] % 3)
        free = tuple(c for c in free if c != pivot)
    return tuple(result)


def canonical_lows(n):
    for rows in low_rows(n):
        yield tuple(x for row in rows for x in row)


def representative(low, high_index, n, digits):
    """Decode a true flat low and the lexicographic index of its free high digits."""
    side = 3 ** (digits - 1)
    number = high_index
    free = [0] * free_count(n)
    for j in reversed(range(len(free))):
        number, free[j] = divmod(number, side)
    if number or high_index < 0:
        raise ValueError("The high coordinate lies outside the complete chart")
    rows = tuple(tuple(low[i : i + n]) for i in range(0, n * n, n))
    return lift_rows(rows, positions(rows), free)


def lift_rows(low, free, digits):
    """Read the high digits of a canonical row prefix."""
    values = iter(digits)
    result = []
    for row, columns in zip(low, free, strict=True):
        lifted = list(row)
        for c in columns:
            lifted[c] += 3 * next(values)
        result.append(tuple(lifted))
    return tuple(result)


def right_matrix(n, word, modulus):
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    for op, i, *args in word:
        if op == "swap":
            j = args[0]
            for row in rows:
                row[i], row[j] = row[j], row[i]
        elif op == "scale":
            k = residue(args[0], modulus)
            for row in rows:
                row[i] = row[i] * k % modulus
        elif op == "add":
            j, k = args
            k = residue(k, modulus)
            for row in rows:
                row[i] = (row[i] + k * row[j]) % modulus
        else:
            raise ValueError("Unknown matrix factor")
    return tuple(tuple(row) for row in rows)


def multiply_row(row, matrix, modulus):
    return [
        sum(a * x for a, x in zip(row, col, strict=True)) % modulus
        for col in zip(*matrix, strict=True)
    ]


def reduce_row(row, previous, pivots, modulus):
    out, multipliers = list(row), []
    for basis, p in zip(previous, pivots, strict=True):
        scalar = out[p] * pow(basis[p], -1, modulus) % modulus
        multipliers.append(scalar)
        out = [(x - scalar * a) % modulus for x, a in zip(out, basis, strict=True)]
    return out, tuple(multipliers)


def canonical_right(rows, matrix, modulus):
    """Return y,L with rows*matrix=L*y and L lower unitriangular."""
    canon, lower, pivots = [], [], []
    for i, row in enumerate(rows):
        out, coeffs = reduce_row(multiply_row(row, matrix, modulus), canon, pivots, modulus)
        pivots.append(next(j for j, x in enumerate(out) if x % 3))
        canon.append(tuple(out))
        lower.append(coeffs + (1,) + (0,) * (len(rows) - i - 1))
    return tuple(canon), tuple(lower)


def row_action(low, before, after, output, pivots, previous, matrix, modulus):
    """Return the affine map on this row's free high digits."""
    columns = []
    for c in before:
        v, _ = reduce_row(matrix[c], previous, pivots, modulus)
        columns.append(tuple(v[k] for k in after))
    a = tuple(zip(*columns, strict=True))
    base = multiply_row([low[k] for k in before], columns, modulus)
    shift = tuple(((x - output[c]) % modulus) // 3 for x, c in zip(base, after, strict=True))
    return a, shift


def elementary_factors(matrix, side):
    """Use row reduction to factor the invertible matrix over the local ring."""
    a = [[x % side for x in row] for row in matrix]
    inverses = []
    for j in range(len(a)):
        p = next(i for i in range(j, len(a)) if a[i][j] % 3)
        if p != j:
            a[p], a[j] = a[j], a[p]
            inverses.append(("swap", p, j))
        unit = a[j][j]
        if unit != 1:
            inv = pow(unit, -1, side)
            a[j] = [x * inv % side for x in a[j]]
            inverses.append(("scale", j, unit))
        for i in range(len(a)):
            if i == j or not a[i][j]:
                continue
            k = a[i][j]
            a[i] = [(x - k * y) % side for x, y in zip(a[i], a[j], strict=True)]
            inverses.append(("add", i, j, k))
    return reversed(inverses)


def affine_packet(source, target, digits, fields, piece, matrix, shift, previous_swap):
    """Move each free high digit in one exposed-prefix packet."""
    side = 3**digits
    with work_tapes(3) as (a, b, temporary):
        copy_bytes(source, a, side**fields * piece)

        def step(action, *args):
            nonlocal a, b
            a.seek(0)
            action(a, b, *args)
            erase(a)
            a, b = b, a

        def exchange(i, j):
            left, right = sorted((i, j))
            step(
                previous_swap,
                digits,
                side**left,
                side ** (right - left - 1),
                side ** (fields - right - 1) * piece,
            )

        def add(dst, src, k):
            k %= side
            if not k:
                return
            if src > dst:
                exchange(src, dst)
            left, right = sorted((src, dst))
            step(
                shift_field,
                temporary,
                side**left,
                side,
                side ** (right - left - 1),
                side ** (fields - right - 1) * piece,
                k,
                0,
            )
            if src > dst:
                exchange(src, dst)

        for kind, i, *args in elementary_factors(matrix, side):
            if kind == "add":
                add(i, *args)
            elif kind == "swap":
                exchange(i, args[0])
            else:
                step(
                    unit_scale,
                    digits,
                    side**i,
                    side ** (fields - i - 1) * piece,
                    args[0],
                    previous_swap,
                )
        for i, k in enumerate(shift):
            if k:
                step(
                    shift_field,
                    temporary,
                    side**i,
                    side,
                    1,
                    side ** (fields - i - 1) * piece,
                    None,
                    k,
                )
        a.seek(0)
        copy_bytes(a, target, side**fields * piece)


def high_packet(source, target, low, result_low, matrix, digits, piece, previous_swap, transform):
    n = len(low)
    q, side, modulus = free_count(n), 3 ** (digits - 1), 3**digits
    before, after = positions(low), positions(result_low)
    pivots = [next(j for j in free if row[j]) for free, row in zip(after, result_low, strict=True)]
    volume = side**q * piece
    with work_tapes(2) as (a, b):
        if transform is None:
            copy_bytes(source, a, volume)
        else:
            for high in digits_in_order(side, q):
                g = lift_rows(low, before, high)
                _, lower = canonical_right(g, matrix, modulus)
                transform(source, a, lower, piece)
        used = 0
        if side > 1:
            for i in range(n):
                a.seek(0)
                for prefix in digits_in_order(side, used):
                    previous = lift_rows(result_low[:i], after[:i], prefix)
                    linear, shift = row_action(
                        low[i],
                        before[i],
                        after[i],
                        result_low[i],
                        pivots[:i],
                        previous,
                        matrix,
                        modulus,
                    )
                    affine_packet(a, b, digits - 1, q - used, piece, linear, shift, previous_swap)
                erase(a)
                a, b = b, a
                used += len(before[i])
        a.seek(0)
        copy_bytes(a, target, volume)


def sort_packets(data, tags, target, slots, block, tag_width, tapes):
    """Use stable ternary passes. Each tag describes one complete high packet."""
    other, other_tags, *buckets = tapes
    for j in reversed(range(tag_width)):
        data.seek(0)
        tags.seek(0)
        for _ in range(slots):
            tag = read_exact(tags, tag_width)
            bucket = tag[j]
            buckets[2 * bucket].write(tag)
            copy_bytes(data, buckets[2 * bucket + 1], block)
        erase(data)
        erase(tags)
        for k in range(3):
            for tape, dest in ((buckets[2 * k], other_tags), (buckets[2 * k + 1], other)):
                length = tape.tell()
                tape.seek(0)
                copy_bytes(tape, dest, length)
                erase(tape)
        data, other = other, data
        tags, other_tags = other_tags, tags
    data.seek(0)
    copy_bytes(data, target, slots * block)
    erase(data)
    erase(tags)


def quotient_right_route(
    source, target, n, digits, groups, suffix_bytes, word, *, previous_swap=None, transform=None
):
    """Move each complete [low][high][body] bank in its own group."""
    if n < 1 or digits < 1 or groups < 0 or suffix_bytes <= 0:
        raise ValueError("The full chart and each suffix must have positive size")
    if digits > 1 and previous_swap is None:
        raise ValueError("The high router requires the preceding ordinary interchange")
    word = tuple(word)
    slots, q = low_count(n), free_count(n)
    block = 3 ** ((digits - 1) * q) * suffix_bytes
    if not word:
        copy_bytes(source, target, groups * slots * block)
        return
    matrix = right_matrix(n, word, 3**digits)
    with work_tapes(10) as (data, tags, *others):
        for _ in range(groups):
            for low in low_rows(n):
                image, _ = canonical_right(low, matrix, 3)
                tags.write(bytes(x for row in image for x in row))
                high_packet(
                    source, data, low, image, matrix, digits, suffix_bytes, previous_swap, transform
                )
            sort_packets(data, tags, target, slots, block, n * n, others)
