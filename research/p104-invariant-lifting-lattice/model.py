"""Exact common lattice for the fixed P104 integer lifting word.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
The fixed word and prefix-parity premise are credited in README.md.
"""


def need(value, reason):
    if not value:
        raise ValueError(reason)


def size(rank):
    need(type(rank) is int and 1 <= rank <= 7, "rank must be 1..7")
    return 2 << rank


def identity(rank):
    d = size(rank)
    return [[int(i == j) for j in range(d)] for i in range(d)]


def pairs(rank, bit):
    for a in range(1 << rank):
        if not (a >> bit) & 1:
            yield 2 * a, 2 * (a ^ (1 << bit))


def stage(rows, rank, bit):
    """Ideal positive Gaussian stage on columns; division must be exact."""
    result = [None] * size(rank)
    for a, b in pairs(rank, bit):
        ar, ai, br, bi = rows[a], rows[a + 1], rows[b], rows[b + 1]
        for target, signs in zip((a, a + 1, b, b + 1),
                                ((1, -1, 1, 1), (1, 1, -1, 1),
                                 (1, 1, 1, -1), (-1, 1, 1, 1)), strict=True):
            numerators = [sum(c * x for c, x in zip(signs, values, strict=True))
                          for values in zip(ar, ai, br, bi, strict=True)]
            need(all(x % 2 == 0 for x in numerators), "nonintegral ideal stage")
            result[target] = [x // 2 for x in numerators]
    return result


def apply(rows, rank, order):
    result = [row[:] for row in rows]
    for bit in order:
        result = stage(result, rank, bit)
    return result


def member(rows, rank, order):
    """All columns must meet the literal parity constraints at every prefix."""
    current = [row[:] for row in rows]
    for bit in order:
        for a, b in pairs(rank, bit):
            for c in range(2):
                if any((x - y) % 2 for x, y in
                       zip(current[a + c], current[b + c], strict=True)):
                    return False
        current = stage(current, rank, bit)
    return True


def restrict(original, current, first, second):
    """Exact parity-kernel intersection by a determinant-two basis change."""
    odd = [j for j, (x, y) in enumerate(zip(current[first], current[second], strict=True))
           if (x - y) % 2]
    if not odd:
        return 0
    pivot = odd[0]
    for rows in (original, current):
        for row in rows:
            old = row[pivot]
            for j in odd[1:]:
                row[j] -= old
            row[pivot] = 2 * old
    return 1


def intersect_order(basis, rank, order):
    original = [row[:] for row in basis]
    current = [row[:] for row in basis]
    counts = []
    for bit in order:
        count = 0
        for a, b in pairs(rank, bit):
            for c in range(2):
                count += restrict(original, current, a + c, b + c)
        current = stage(current, rank, bit)
        counts.append(count)
    return original, counts


def construct(rank):
    size(rank)
    forward = tuple(range(rank))
    reverse = tuple(reversed(forward))
    gamma, first = intersect_order(identity(rank), rank, forward)
    common, second = intersect_order(gamma, rank, reverse)
    return gamma, common, first, second


def lift(values, rank, inverse=False):
    """Literal signed floor shears, with no ideal arithmetic in this routine."""
    need(len(values) == size(rank) and all(type(x) is int for x in values),
         "integer vector shape")
    out = list(values)
    for bit in reversed(range(rank)) if inverse else range(rank):
        for a, b in pairs(rank, bit):
            dr, di = out[a] - out[b], out[a + 1] - out[b + 1]
            sr, si = out[b] + dr // 2, out[b + 1] + di // 2
            dr, di = (di, -dr) if inverse else (-di, dr)
            br, bi = sr - dr // 2, si - di // 2
            out[a], out[a + 1], out[b], out[b + 1] = br + dr, bi + di, br, bi
    return out


def columns(rows):
    return [list(col) for col in zip(*rows, strict=True)]


def as_column(values):
    return [[x] for x in values]


def address_xor(rows, rank, mask):
    return [rows[2 * (a ^ mask) + c][:]
            for a in range(1 << rank) for c in range(2)]


def multiply_i(rows, rank):
    return [[-x for x in rows[i + 1]] if i % 2 == 0 else rows[i - 1][:]
            for i in range(size(rank))]


def report(rank):
    gamma, common, first, second = construct(rank)
    forward, reverse = tuple(range(rank)), tuple(reversed(range(rank)))
    need(member(common, rank, forward) and member(common, rank, reverse),
         "intersection membership")
    image = apply(common, rank, forward)
    need(member(image, rank, forward) and member(image, rank, reverse),
         "common lattice U invariance")
    twice = apply(image, rank, forward)
    need(twice == address_xor(common, rank, (1 << rank) - 1), "U squared is complement")
    need(member(multiply_i(common, rank), rank, forward) and
         member(multiply_i(common, rank), rank, reverse), "Gaussian unit closure")
    for value, exact in zip(columns(common), columns(image), strict=True):
        need(lift(value, rank) == exact, "lift is exact U on common basis")
        need(lift(exact, rank, inverse=True) == value, "literal inverse restores basis")
    nonpreserving = None
    gamma_image = apply(gamma, rank, forward)
    for j, col in enumerate(columns(gamma_image)):
        if not member(as_column(col), rank, forward):
            nonpreserving = j
            break
    return {
        "rank": rank, "real_dimension": size(rank),
        "gamma_stage_index_bits": first, "extra_reverse_stage_index_bits": second,
        "gamma_index_bits": sum(first), "common_index_bits": sum(first + second),
        "extra_common_bits": sum(second),
        "gamma_image_outside_gamma_basis_column": nonpreserving,
        "uniform_period_grid_bits": size(rank) * (rank // 2 + 1),
        "verified_basis_columns": size(rank),
    }
