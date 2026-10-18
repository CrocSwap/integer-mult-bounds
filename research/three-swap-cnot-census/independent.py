"""Separate faithful-regular census from actual binary address matrices.

Enumerates all 512 scalar matrices to select rank-one idempotents, uses LEFT
multiplication of complete 18x18 binary matrices, and checks optimized steps
against dense row multiplication through radius three. Imports no producer code.
Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import itertools


def rank(rows):
    basis = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in basis:
                row ^= basis[bit]
            else:
                basis[bit] = row
                break
    return len(basis)


def small_product(left, right):
    result = []
    for row in left:
        new = 0
        for j, source in enumerate(right):
            if (row >> j) & 1:
                new ^= source
        result.append(new)
    return tuple(result)


def address_permutation(matrix):
    return tuple(sum(((row & vector).bit_count() % 2) << i
                     for i, row in enumerate(matrix)) - 1 for vector in (1, 2, 3))


def address_group():
    return tuple(sorted((m for m in itertools.product(range(4), repeat=2)
                         if rank(m) == 2), key=address_permutation))


def scalar_idempotents():
    result = []
    for rows in itertools.product(range(8), repeat=3):
        if rank(rows) == 1 and small_product(rows, rows) == rows:
            u = sum((row != 0) << i for i, row in enumerate(rows))
            v = next(row for row in rows if row)
            result.append((rows, u, v))
    return tuple(result)


def multiply(left, right, size=18):
    """Generic dense binary matrix multiplication; no group-algebra shortcut."""
    row_mask = (1 << size) - 1
    right_rows = [(right >> (size * i)) & row_mask for i in range(size)]
    result = 0
    for i in range(size):
        row = (left >> (size * i)) & row_mask
        output = 0
        while row:
            bit = row & -row
            output ^= right_rows[bit.bit_length() - 1]
            row ^= bit
        result |= output << (size * i)
    return result


def identity():
    return sum(1 << (19 * i) for i in range(18))


def target():
    group = address_group()
    index = {m: i for i, m in enumerate(group)}
    swap = (2, 1)
    result = 0
    for register in range(3):
        for h, matrix in enumerate(group):
            row = index[small_product(swap, matrix)]
            result |= 1 << (18 * (6 * register + row) + 6 * register + h)
    return result


def census(radius=4):
    group = address_group()
    index = {m: i for i, m in enumerate(group)}
    idempotents = scalar_idempotents()
    if len(group) != 6 or len(idempotents) != 28:
        raise ValueError("independent generator inventory")
    row_mask = (1 << 18) - 1
    chunk_mask = (1 << 108) - 1
    labels = ((3, 2), (1, 3))
    permutations = [tuple(index[small_product(g, h)] for h in group) for g in labels]
    dense_generators = []
    grouped = []
    for permutation in permutations:
        row_moves = tuple((18 * source, 18 * destination)
                          for destination, source in enumerate(permutation))
        by_v = []
        for v in range(1, 8):
            us = []
            for rows, u, actual_v in idempotents:
                if actual_v != v:
                    continue
                gen = identity()
                for i in range(3):
                    for j in range(3):
                        if (rows[i] >> j) & 1:
                            for h in range(6):
                                gen ^= 1 << (18 * (6 * i + h) + 6 * j + h)
                                gen ^= 1 << (18 * (6 * i + h) + 6 * j + permutation[h])
                us.append((u, gen))
                dense_generators.append(gen)
            by_v.append((v, us))
        grouped.append((row_moves, by_v))
    if len(set(dense_generators)) != 56:
        raise ValueError("duplicate independent generators")
    seen = {identity()}
    levels = [seen.copy()]
    attempts = []
    dense_checks = 0
    for depth in range(1, radius + 1):
        new = set()
        attempts.append(len(levels[-1]) * 56)
        for word in levels[-1]:
            r0 = word & chunk_mask
            r1 = (word >> 108) & chunk_mask
            r2 = word >> 216
            combos = (0, r0, r1, r0 ^ r1, r2, r0 ^ r2, r1 ^ r2, r0 ^ r1 ^ r2)
            for row_moves, by_v in grouped:
                for v, us in by_v:
                    chunk = combos[v]
                    transformed = 0
                    for source, destination in row_moves:
                        transformed |= ((chunk >> source) & row_mask) << destination
                    delta = chunk ^ transformed
                    for u, gen in us:
                        changed = word
                        if u & 1:
                            changed ^= delta
                        if u & 2:
                            changed ^= delta << 108
                        if u & 4:
                            changed ^= delta << 216
                        if depth <= 3:
                            if changed != multiply(gen, word):
                                raise ValueError("optimized/dense regular transition mismatch")
                            dense_checks += 1
                        if changed not in seen:
                            new.add(changed)
        seen.update(new)
        levels.append(new)
    return levels, attempts, dense_checks
