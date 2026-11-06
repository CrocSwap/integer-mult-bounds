#!/usr/bin/env python3
"""Independent finite controls for the mixed-prefix rank lemma (over F2).
The universal lemma is the written rank-complement argument in PROOF.md.
"""
from itertools import product


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rank(vectors):
    pivots = {}
    for v in vectors:
        while v:
            p = v.bit_length()-1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p] = v
                break
    return len(pivots)


def dot(a, b):
    return (a & b).bit_count() % 2


def main():
    checked = 0
    for dimension in (1, 2, 3, 4):
        for m0, m1, n0, n1 in product(range(1 << dimension), repeat=4):
            if dot(m0, n0) != 1 or dot(m1, n1) != 0:
                continue
            lhs = 1+bool(m1)+bool(n1)
            rhs = rank([m0, m1])+rank([n0, n1])
            need(lhs <= rhs, 'Mixed-prefix complement inequality')
            checked += 1
    # Both hypotheses matter, rather than merely rank-count arithmetic.
    need(1+1+1 > rank([1, 1])+rank([1, 1]), 'Dropping zero cross-product must fail')
    need(1 > rank([0, 0])+rank([0, 0]), 'Dropping identity block must fail')
    print('F2_SCALAR_BLOCK_FIXTURES', checked)
    print('REJECTED_MISSING_PREMISE_CONTROLS', 2)
    print('PASS_MIXED_PREFIX_RANK_CONTROLS')


if __name__ == '__main__':
    main()
