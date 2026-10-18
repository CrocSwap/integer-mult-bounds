#!/usr/bin/env python3
"""Packed exact census for the three-call D8 inverse-pair target."""

from __future__ import annotations

import itertools

N = 3
GROUP_ORDER = 8
S = 4                       # r^0 s
T = 7                       # r^3 s = r^-1 s
R = 1                       # r
R_INV = 3                   # r^-1
IDENTITY_GA = 1              # bit 0 represents the group identity


def group_product(a: int, b: int) -> int:
    """D8 multiplication for indices i + 4e representing r^i s^e."""
    i, e = a & 3, a >> 2
    j, f = b & 3, b >> 2
    return ((i + (-j if e else j)) & 3) + (4 * (e ^ f))


def make_ring_table() -> tuple[tuple[int, ...], ...]:
    basis = tuple(
        tuple(1 << group_product(i, j) for j in range(GROUP_ORDER))
        for i in range(GROUP_ORDER)
    )
    table: list[tuple[int, ...]] = []
    for a in range(256):
        row: list[int] = []
        for b in range(256):
            out = 0
            aa = a
            while aa:
                bit_a = aa & -aa
                i = bit_a.bit_length() - 1
                aa ^= bit_a
                bb = b
                while bb:
                    bit_b = bb & -bb
                    j = bit_b.bit_length() - 1
                    bb ^= bit_b
                    out ^= basis[i][j]
            row.append(out)
        table.append(tuple(row))
    return tuple(table)


RING_MUL = make_ring_table()
IDENTITY = tuple(IDENTITY_GA if i == j else 0 for i in range(N) for j in range(N))
TARGET = tuple(
    (1 << R) if (i, j) == (0, 0)
    else (1 << R_INV) if (i, j) == (1, 1)
    else IDENTITY_GA if (i, j) == (2, 2)
    else 0
    for i in range(N) for j in range(N)
)


def scalar_product(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * 9
    for i in range(N):
        for j in range(N):
            value = 0
            for k in range(N):
                value ^= RING_MUL[a[3 * i + k]][b[3 * k + j]]
            out[3 * i + j] = value
    return tuple(out)


def rank_one_idempotents() -> tuple[tuple[int, ...], ...]:
    result = []
    for u in range(1, 1 << N):
        for v in range(1, 1 << N):
            if (u & v).bit_count() % 2 != 1:
                continue
            result.append(tuple(
                ((u >> i) & 1) & ((v >> j) & 1)
                for i in range(N) for j in range(N)
            ))
    assert len(result) == 28
    return tuple(result)


def factor(g: int, projector: tuple[int, ...]) -> tuple[int, ...]:
    delta = (1 << g) ^ IDENTITY_GA
    return tuple(
        (IDENTITY_GA if i == j else 0) ^ (delta if projector[3 * i + j] else 0)
        for i in range(N) for j in range(N)
    )


def gates() -> tuple[tuple[str, tuple[int, ...]], ...]:
    projectors = rank_one_idempotents()
    return tuple(
        (label, factor(group_element, projector))
        for label, group_element in (("s", S), ("t", T))
        for projector in projectors
    )


def direct_word() -> tuple[tuple[str, tuple[int, ...]], ...]:
    e11 = (1, 0, 0, 0, 0, 0, 0, 0, 0)
    e22 = (0, 0, 0, 0, 1, 0, 0, 0, 0)
    return (
        ("s", factor(S, e11)),
        ("t", factor(T, e11)),
        ("t", factor(T, e22)),
        ("s", factor(S, e22)),
    )


def census(target: tuple[int, ...], ops: tuple[tuple[str, tuple[int, ...]], ...]):
    prefixes = [
        (a, b, scalar_product(a[1], b[1]))
        for a, b in itertools.product(ops, repeat=2)
    ]
    matches = []
    checked = 0
    for a, b, prefix in prefixes:
        for c in ops:
            checked += 1
            if scalar_product(prefix, c[1]) == target:
                matches.append((a[0], b[0], c[0]))
    return checked, matches


def main() -> None:
    ops = gates()
    checked, matches = census(TARGET, ops)
    direct = IDENTITY
    for _, gate in direct_word():
        direct = scalar_product(direct, gate)
    assert direct == TARGET
    print(
        "D8 inverse-pair W3 exact search: "
        f"generators={len(ops)} triples={checked} matches={len(matches)} "
        f"direct_calls={len(direct_word())}"
    )
    if matches:
        print("first match:", matches[0])
    else:
        print("complete length-three census: no word reaches diag([r],[r^-1],1)")


if __name__ == "__main__":
    main()
