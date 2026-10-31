"""Exact 52-bit worst-case abstract codec for the explicit rank-four frame.

For @CubeJerry, substantial OpenAI Codex assistance. Apache-2.0.
The changed output contract and unpriced physical costs are explicit in PROOF.md.
"""
from itertools import product
from math import prod

import construction as c
import recovery as r


def max_states():
    return ((13 ** 8 + 14 * 13 ** 4 + 1) // 16) ** 2


def parity_pairs(matrix, output):
    """The exact affine coset of C x C from the binary dual witnesses."""
    syndrome = [sum(output[i] for i in pair) & 1 for pair in c.DUAL_ROWS]
    adjusted = list(output)
    for value, column in zip(syndrome, c.COLUMNS):
        for i, coefficient in column:
            adjusted[i] += value * coefficient
    totals = r.parity_options(matrix, adjusted)
    target = [(value + output[i]) & 1
              for value, i in zip(syndrome, c.SELECTORS)]
    masks = [sum((value & 1) << j for j, value in enumerate(matrix[i]))
             for i in c.SELECTORS]
    last = [q for q in range(256)
            if all((q & row).bit_count() % 2 == bit
                   for row, bit in zip(masks, target))]
    return product(totals, last)


def joint_cells(s):
    low, high = r.total_interval(s, 2)
    cells = {(p, q): [] for p, q in product(range(2), repeat=2)}
    for total in range(low, high + 1):
        cells[total & 1, r.scalar_step(s, total) & 1].append(total)
    return cells


def blocks(matrix, output):
    r.require(len(output) == 112 and all(map(r.exact_int, output)),
              "output must be an exact owner vector")
    tables = [joint_cells(s) for s in r.project(matrix, output)]
    result = []
    for p, q in parity_pairs(matrix, output):
        cells = [table[(p >> j) & 1, (q >> j) & 1]
                 for j, table in enumerate(tables)]
        count = prod(map(len, cells))
        if count:
            result.append(((p, q), cells, count))
    return result


def fiber_count(matrix, output):
    return sum(count for _, _, count in blocks(matrix, output))


def unrank_total(matrix, output, tag):
    r.require(r.exact_int(tag) and tag >= 0, "invalid optimal recovery tag")
    for _, cells, count in blocks(matrix, output):
        if tag >= count:
            tag -= count
            continue
        total = [0] * 8
        for j in range(7, -1, -1):
            tag, index = divmod(tag, len(cells[j]))
            total[j] = cells[j][index]
        r.require(tag == 0, "unconsumed optimal recovery tag")
        return total
    raise ValueError("tag exceeds the actual optimal-frame output fiber")


def rank_total(matrix, output, total):
    r.require(len(total) == 8 and all(map(r.exact_int, total)),
              "total must be eight exact integers")
    s = r.project(matrix, output)
    p = sum((value & 1) << j for j, value in enumerate(total))
    q = sum((r.scalar_step(a, b) & 1) << j
            for j, (a, b) in enumerate(zip(s, total)))
    offset = 0
    for pair, cells, count in blocks(matrix, output):
        if pair != (p, q):
            offset += count
            continue
        rank = 0
        for value, cell in zip(total, cells):
            r.require(value in cell, "total outside its joint scalar cell")
            rank = rank * len(cell) + cell.index(value)
        return offset + rank
    raise ValueError("total fails the optimal-frame output syndrome")


def decode(matrix, output, tag):
    c.validate(matrix, *c.matrices())
    total = unrank_total(matrix, output, tag)
    return c.inverse_from_total(matrix, list(output), total)


def encode(matrix, vector):
    c.validate(matrix, *c.matrices())
    r.require(len(vector) == 112 and all(map(r.exact_int, vector)),
              "input must be an exact owner vector")
    output = c.forward(matrix, vector)
    total = c.total_for_input(matrix, vector, output)
    return output, rank_total(matrix, output, total)
