#!/usr/bin/env python3
"""Ideal one-at-a-time lever budgets for the selected complex word (planning numbers, not constructions).

Each row changes one premise of the ceiling model and reports the packing ceiling (ideal idle
packing, halving guard R = 51) relative to the selected word's ceiling. These are favorable
relaxations: every row omits whatever cost realizing the lever would add elsewhere.

usage: levers.py
Douglas Colkitt, with Claude (Anthropic) assistance. Apache-2.0.
"""
import sys
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ceiling as C  # noqa: E402

M, FAM, ST = 73, 896, 9
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}


def cap(local, centre=64, unpaid=1, families=FAM):
    return C.ceiling(local, M, families, ST, centre, grid=Q(1, 10 ** 12), unpaid=unpaid)[1]


def main():
    base = cap(WORD)
    mass = sum(r * n for r, n in WORD.items())
    rows = [
        ('selected word (baseline)', base),
        ('centre path free: no 8 rank-8 copies, centre charge 0', cap({r: n for r, n in WORD.items() if r != 8}, centre=0)),
        ('centre path shared by 2 calls (copies and charge halved)', cap({**WORD, 8: 4}, centre=32)),
        ('local mass delivered as rank-16 children', cap({16: Q(mass, 16)})),
        ('local mass delivered as rank-8 children', cap({8: Q(mass, 8)})),
        ('two unpaid coordinates per live family', cap(WORD, unpaid=2)),
        ('centre free and rank-16 children combined', cap({16: Q(mass - 64, 16)}, centre=0)),
    ]
    for name, a in rows:
        print(f'{name:58s} a_cap={float(a):.6f}  x{float(a / base):.2f}  kappa_cap={float(a / (1 + a)):.6f}')


if __name__ == '__main__':
    main()
