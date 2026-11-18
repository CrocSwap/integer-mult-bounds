#!/usr/bin/env python3
"""Multiply the six shared-hub factors over F2[z,z^-1] on fixed finite domains."""

from itertools import permutations, product


PROJECTORS = ((6, 5), (5, 6), (7, 7), (12, 20), (20, 12), (28, 28))
WIDTH = 5
TRIPLE_SIZE = 3


def coordinate_sets() -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    return tuple(
        (
            tuple(row for row in range(WIDTH) if image & (1 << row)),
            tuple(column for column in range(WIDTH) if covector & (1 << column)),
        )
        for image, covector in PROJECTORS
    )


def check_labels(
    labels: tuple[int, ...],
    orders: tuple[tuple[tuple[int, ...], bool], ...],
    supports: tuple[tuple[tuple[int, ...], tuple[int, ...]], ...],
) -> int:
    offset = sum(-label for label in labels if label < 0)
    one = 1 << offset
    diagonal_target = (labels[0], labels[0], labels[0] + labels[3], labels[3], labels[3])
    equal_within_triples = labels[0] == labels[1] == labels[2] and labels[3] == labels[4] == labels[5]
    diagonal_cases = 0
    for order, two_blocks in orders:
        rows = [[one if i == j else 0 for j in range(WIDTH)] for i in range(WIDTH)]
        for index in order:
            image, covector = supports[index]
            exponent = labels[index]
            for column in range(WIDTH):
                donor = 0
                for row in covector:
                    donor ^= rows[row][column]
                shifted = donor << exponent if exponent > 0 else donor >> -exponent
                if exponent < 0 and (shifted << -exponent) != donor:
                    raise ValueError('Laurent shift lost a coefficient')
                delta = shifted ^ donor
                for row in image:
                    rows[row][column] ^= delta
        diagonal = all(rows[i][j] == 0 for i in range(WIDTH) for j in range(WIDTH) if i != j)
        if diagonal != (two_blocks and equal_within_triples):
            raise ValueError(f'unexpected diagonal status at labels={labels}, order={order}')
        if diagonal:
            actual = tuple(rows[i][i] for i in range(WIDTH))
            expected = tuple(1 << (offset + label) for label in diagonal_target)
            if actual != expected:
                raise ValueError(f'incorrect diagonal at labels={labels}, order={order}')
            diagonal_cases += 1
    return diagonal_cases


def main() -> None:
    supports = coordinate_sets()
    orders = tuple(
        (order, all(label < TRIPLE_SIZE for label in order[:TRIPLE_SIZE])
         or all(label >= TRIPLE_SIZE for label in order[:TRIPLE_SIZE]))
        for order in permutations(range(len(PROJECTORS)))
    )
    labels_to_check = tuple(product((-2, 1, 2), repeat=len(PROJECTORS))) + (
        (-8, -8, -8, 16, 16, 16),
        (8, 8, 8, -8, -8, -8),
        (4, 4, -4, 1, 1, 1),
    )
    diagonal_cases = sum(check_labels(labels, orders, supports) for labels in labels_to_check)
    cases = len(labels_to_check) * len(orders)
    print(f'PASS_SHARED_HUB_SINGLE_PASS cases={cases} diagonal={diagonal_cases}')


if __name__ == '__main__':
    main()
