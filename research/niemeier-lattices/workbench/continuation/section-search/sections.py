"""Exact binary decoder ranks for Reed--Muller sections of D16+ spinors.

Local research by DominikScholz with OpenAI GPT-6 Astra in T3 Code.
No complete supplier or kappa claim.
"""
from itertools import combinations
from pathlib import Path
import json
import time


def require(ok, message):
    if not ok:
        raise ValueError(message)


def evaluation(monomial):
    return sum(int(all(x >> j & 1 for j in monomial)) << x for x in range(16))


def section(k):
    monomials = ([(i,) for i in range(4)] + list(combinations(range(4), 2))
                 + list(combinations(range(4), 3))[:k])
    masks = [evaluation(m) for m in monomials]
    words = [0]
    for mask in masks:
        words += [w ^ mask for w in words]
    n = len(words)
    require(len(set(words)) == n, 'Independent function evaluations')
    require(all(w & 1 == 0 and w.bit_count() % 2 == 0 for w in words),
            'Canonical even spinor signs')
    kernel = [int(w == 0 or w.bit_count() == 8) for w in words]
    first = sum(c << i for i, c in enumerate(kernel))
    swaps = []
    for bit in range(len(masks)):
        shift = 1 << bit
        mask = sum(((1 << shift) - 1) << start for start in range(0, n, 2 * shift))
        swaps.append((shift, mask))
    basis = {}
    previous_gray = 0
    row = first
    for index in range(n):
        gray = index ^ (index >> 1)
        if index:
            bit = (gray ^ previous_gray).bit_length() - 1
            shift, mask = swaps[bit]
            row = ((row & mask) << shift) | ((row >> shift) & mask)
        previous_gray = gray
        value = row
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return dict(cubic_dimensions=k, ports=n, dimension=16,
                orthogonality_degree=sum(kernel)-1, rank=len(basis),
                full_center_bill=16*len(basis),
                asymptotic_rank_surplus=n-16*len(basis),
                monomials=[list(m) for m in monomials])


if __name__ == '__main__':
    result = []
    for k in range(5):
        start = time.monotonic()
        row = section(k)
        result.append(row)
        print(row, 'seconds', time.monotonic()-start, flush=True)
    Path(__file__).with_name('SECTIONS.json').write_text(json.dumps(result, indent=2)+'\n')
