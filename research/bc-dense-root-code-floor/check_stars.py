#!/usr/bin/env python3
"""Independent graph-incidence / inverse-map check; no primary imports or elimination.

ywz65, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import product


def need(ok, message):
    if not ok:
        raise ValueError(message)


def labels(n, anchor, other):
    order = ([other] if other != anchor else [])
    order += [j for j in range(n) if j != anchor and j not in order]
    return [frozenset([anchor])] + [frozenset([anchor, j]) for j in order]


def pairing(a, b):
    # Axis-axis: unit diagonal and all distinct axes orthogonal.
    if len(a) == len(b) == 1:
        return 1
    # Axis-edge: orthogonal precisely when disjoint.
    if len(a) != len(b):
        return int(a.isdisjoint(b))
    # Edge-edge: sign-insensitive same-edge block, or disjoint edges.
    return int(a == b or a.isdisjoint(b))


def multiply(matrix, x):
    return tuple(sum(a*b for a, b in zip(row, x)) % 2 for row in matrix)


def recover(y, same):
    if same:
        return y
    tail = tuple(y[0] ^ value for value in y[2:])
    return ((y[0] + sum(tail)) % 2, y[1], *tail)


def main():
    checked = 0
    matrices = 0
    for n in range(1, 11):
        for i in range(n):
            for j in range(n):
                rs, cs = labels(n, i, j), labels(n, j, i)
                matrix = [[pairing(a, b) for b in cs] for a in rs]
                preimages = set()
                for y in product((0, 1), repeat=n):
                    x = recover(y, i == j)
                    need(multiply(matrix, x) == y, 'explicit inverse failed')
                    preimages.add(x)
                    checked += 1
                need(len(preimages) == 2**n, 'inverse is not bijective')
                matrices += 1
    # A single erased same-edge entry breaks the distinct-anchor star inverse.
    matrix = [[1, 0], [0, 0]]
    need(multiply(matrix, recover((0, 1), False)) != (0, 1), 'erased-edge control ineffective')
    print(f'PASS_BC_GRAPH_STAR_INVERSES dimensions=10 matrices={matrices} right_hand_sides={checked} controls=1')


if __name__ == '__main__':
    main()
