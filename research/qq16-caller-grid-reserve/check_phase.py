#!/usr/bin/env python3
"""Direct small Fourier checks independent of elimination; ywz65 + OpenAI Codex."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import phase


def direct(a, edges, character):
    out = [0, 0]
    units = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    for x in range(1 << len(a)):
        q = sum(v*((x >> j) & 1) for j, v in enumerate(a))
        q += 2*sum(((x >> i) & 1)*((x >> j) & 1)
                   for i in range(len(a)) for j in range(i+1, len(a)) if edges[i] >> j & 1)
        u = units[(q+2*(x & character).bit_count()) % 4]
        out[0] += u[0]
        out[1] += u[1]
    return tuple(Q(v, 1 << len(a)) for v in out)


def main():
    coefficients = 0
    forms = 0
    for n in range(1, 4):
        pairs = [(i, j) for i in range(n) for j in range(i+1, n)]
        for a in product(range(4), repeat=n):
            for mask in range(1 << len(pairs)):
                edges = [0]*n
                for bit, (i, j) in enumerate(pairs):
                    if mask >> bit & 1:
                        edges[i] |= 1 << j
                        edges[j] |= 1 << i
                r = phase.rank(a, edges)
                values = []
                for chi in range(1 << n):
                    value = direct(a, edges, chi)
                    phase.need(value == phase.gaussian(a, edges, chi), 'direct Fourier disagreement')
                    if any(value):
                        phase.need(sum(z*z for z in value) == Q(1, 1 << r), 'direct amplitude disagreement')
                    values.append(value)
                    coefficients += 1
                phase.need(sum(any(v) for v in values) == 1 << r, 'Fourier support cardinality')
                # Real-to-real induced infinity norm includes both input components.
                phase.need(sum(abs(x)+abs(y) for x, y in values) == 1 << ((r+1)//2), 'direct real infinity gain')
                phase.witness(a, edges)
                forms += 1
    # Both the odd diagonal and the even quadratic cross term affect the rank.
    phase.need(phase.rank((1,), (0,)) == 1, 'odd diagonal control')
    phase.need(phase.rank((0, 0), (2, 1)) == 2, 'even cross term control')
    phase.need(phase.gaussian((0, 0), (2, 1), 0) == (Q(1, 2), Q(0)), 'rank-zero false surrogate')
    # Full C8 boundary kernel: no reliance on the elimination for this comparison.
    c8 = tuple(direct((1,)*8, (0,)*8, chi) for chi in range(256))
    phase.need(all(sum(v*v for v in z) == Q(1, 256) for z in c8), 'C8 direct amplitude')
    phase.need(max(v.denominator for z in c8 for v in z) == 16, 'C8 direct denominator')
    phase.need(sum(abs(x)+abs(y) for x, y in c8) == 16, 'C8 direct box gain')
    # A C1 tensor square is real up to phase and has denominator two, not four.
    c2 = tuple(direct((1, 1), (0, 0), chi) for chi in range(4))
    phase.need(max(v.denominator for z in c2 for v in z) == 2, 'tensor cancellation control')
    for layers in range(1, 101):
        x, y = 1 << ((layers+1)//2), 1 << (4*layers)
        phase.need(y-16 >= 8*(x-2) and x <= y//8, 'tensor envelope sanity check')
    print(f'PASS_QQ16_PHASE_KERNEL forms={forms} coefficients={coefficients} '
          'c8_coefficients=256 controls=4')


if __name__ == '__main__':
    main()
