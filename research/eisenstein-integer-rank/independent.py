#!/usr/bin/env python3
"""Independent restriction-of-scalars rank check; no retained rank import."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from random import Random
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from integer_rank import need, rank


def rational_rank(matrix):
    a = [list(row) for row in matrix]
    if not a:
        return 0
    pivot = 0
    for col in range(len(a[0])):
        row = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if row is None:
            continue
        a[pivot], a[row] = a[row], a[pivot]
        divisor = a[pivot][col]
        a[pivot] = [x/divisor for x in a[pivot]]
        for i in range(pivot+1, len(a)):
            factor = a[i][col]
            a[i] = [x-factor*y for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def expanded(matrix):
    out = []
    for row in matrix:
        out.append([z for a, b in row for z in (F(a), -F(b))])
        out.append([z for a, b in row for z in (F(b), F(a)-F(b))])
    return out


def check(matrix):
    exact = rational_rank(expanded(matrix))
    need(exact == 2*rank(matrix), 'restriction-of-scalars rank disagreement')


def main():
    alphabet = [(0, 0), (1, 0), (0, 1), (1, 1)]
    count = 0
    for flat in product(alphabet, repeat=6):
        matrix = [list(flat[:3]), list(flat[3:])]
        check(matrix)
        check([list(row) for row in zip(*matrix)])
        count += 2
    rational = alphabet+[(F(-2, 3), F(5, 6))]
    for flat in product(rational, repeat=4):
        check([list(flat[:2]), list(flat[2:])])
        count += 1
    rng = Random(20261015)
    for rows in range(8):
        for cols in range(8):
            for sample in range(3):
                matrix = [[(F(rng.randrange(-9, 10), rng.randrange(1, 10)),
                            F(rng.randrange(-9, 10), rng.randrange(1, 10)))
                           for _ in range(cols)] for _ in range(rows)]
                if sample == 1 and rows > 1:
                    matrix[-1] = list(matrix[0])
                if sample == 2 and rows:
                    scale = (1 << 170)+1
                    matrix[0] = [(a*scale, b*scale) for a, b in matrix[0]]
                check(matrix)
                count += 1
    print(f'PASS_INDEPENDENT_EISENSTEIN_RANK matrices={count} rational_restriction=2K')


if __name__ == '__main__':
    main()
