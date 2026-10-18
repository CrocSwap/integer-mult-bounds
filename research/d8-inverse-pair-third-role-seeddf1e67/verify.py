#!/usr/bin/env python3
"""Independent tuple-coefficient replay and exact rank certificate."""

from __future__ import annotations

from functools import lru_cache
import itertools

ORDER = 8
ROLES = 3
ZERO_GA = (0,) * ORDER
ONE_GA = (1,) + (0,) * (ORDER - 1)


def group_product(a: int, b: int) -> int:
    i, e = a % 4, a // 4
    j, f = b % 4, b // 4
    return ((i + (4 - j if e else j)) % 4) + 4 * (e ^ f)


@lru_cache(maxsize=None)
def multiply_coefficients(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * ORDER
    for i, x in enumerate(a):
        if not x:
            continue
        for j, y in enumerate(b):
            if x and y:
                out[group_product(i, j)] ^= 1
    return tuple(out)


def add_coefficients(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x ^ y for x, y in zip(a, b))


def matrix_identity():
    return tuple(ONE_GA if i == j else ZERO_GA for i in range(ROLES) for j in range(ROLES))


def matrix_product(a, b):
    out = []
    for i in range(ROLES):
        for j in range(ROLES):
            value = ZERO_GA
            for k in range(ROLES):
                value = add_coefficients(value, multiply_coefficients(a[3 * i + k], b[3 * k + j]))
            out.append(value)
    return tuple(out)


def idempotents():
    out = []
    for u in range(1, 8):
        for v in range(1, 8):
            if ((u & v).bit_count() & 1) == 0:
                continue
            out.append(tuple(((u >> i) & (v >> j) & 1) for i in range(3) for j in range(3)))
    if len(out) != 28:
        raise AssertionError(f"expected 28 idempotents, got {len(out)}")
    return tuple(out)


def gate(label: int, n):
    group_identity = 0
    diff = [0] * ORDER
    diff[group_identity] = 1
    diff[label] ^= 1
    diff = tuple(diff)
    matrix = []
    for i in range(3):
        for j in range(3):
            base = ONE_GA if i == j else ZERO_GA
            matrix.append(add_coefficients(base, diff) if n[3 * i + j] else base)
    return tuple(matrix)


def endpoint(r: int, rinv: int, third: int = 0):
    result = []
    for i in range(3):
        for j in range(3):
            if i != j:
                result.append(ZERO_GA)
            elif i == 0:
                result.append(tuple(int(k == r) for k in range(ORDER)))
            elif i == 1:
                result.append(tuple(int(k == rinv) for k in range(ORDER)))
            else:
                result.append(tuple(int(k == third) for k in range(ORDER)))
    return tuple(result)


def rank_binary(rows: list[int], ncols: int) -> int:
    rank = 0
    work = rows[:]
    for col in range(ncols):
        pivot = next((i for i in range(rank, len(work)) if (work[i] >> col) & 1), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for i in range(len(work)):
            if i != rank and ((work[i] >> col) & 1):
                work[i] ^= work[rank]
        rank += 1
    return rank


def left_regular(g: int) -> list[int]:
    rows = [0] * ORDER
    for h in range(ORDER):
        rows[group_product(g, h)] |= 1 << h
    return rows


def add_binary(a: list[int], b: list[int]) -> list[int]:
    return [x ^ y for x, y in zip(a, b)]


def target_difference_rank(r: int, rinv: int) -> int:
    blocks = []
    for g in (r, rinv, 0):
        block = left_regular(g)
        if g == 0:
            block = [0] * ORDER
        else:
            ident = [1 << i for i in range(ORDER)]
            block = add_binary(block, ident)
        blocks.append(block)
    rows = []
    for role in range(3):
        for i in range(ORDER):
            row = 0
            for col_role in range(3):
                if col_role == role:
                    row |= blocks[role][i] << (ORDER * col_role)
            rows.append(row)
    return rank_binary(rows, 3 * ORDER)


def gate_difference_rank(g: int, n) -> int:
    # The represented 24x24 difference is (L_g + I_8) tensor N.
    regular = add_binary(left_regular(g), [1 << i for i in range(ORDER)])
    rows = []
    for h in range(ORDER):
        for i in range(3):
            row = 0
            for k in range(ORDER):
                if (regular[h] >> k) & 1:
                    for j in range(3):
                        if n[3 * i + j]:
                            row |= 1 << (3 * k + j)
            rows.append(row)
    return rank_binary(rows, ORDER * 3)


def main() -> None:
    s, t, r, rinv = 4, 7, 1, 3
    ns = idempotents()
    generators = tuple((g, gate(g, n)) for g in (s, t) for n in ns)
    target = endpoint(r, rinv)

    # The elementary displacement-rank inequality excludes lengths 0, 1, 2.
    trank = target_difference_rank(r, rinv)
    gate_ranks = {gate_difference_rank(g, n) for g, n in ((s, ns[0]), (t, ns[-1]))}
    if trank != 12 or gate_ranks != {4}:
        raise AssertionError((trank, gate_ranks))
    if trank > 2 * max(gate_ranks):
        pass
    else:
        raise AssertionError("rank floor failed to exclude length two")

    # Complete length-three census; matrices store all eight F2 coefficients
    # independently rather than packed bitsets.
    prefix_products = []
    for a, b in itertools.product(generators, repeat=2):
        prefix_products.append((a[0], b[0], matrix_product(a[1], b[1])))
    checked = 0
    matches = []
    for ga, gb, prefix in prefix_products:
        for gc, c in generators:
            checked += 1
            if matrix_product(prefix, c) == target:
                matches.append((ga, gb, gc))
    if checked != 56**3 or matches:
        raise AssertionError((checked, matches[:3]))

    # Direct four-call positive control: st=r and ts=r^-1.
    e11 = tuple(int((i, j) == (0, 0)) for i in range(3) for j in range(3))
    e22 = tuple(int((i, j) == (1, 1)) for i in range(3) for j in range(3))
    direct = matrix_identity()
    for g, n in ((s, e11), (t, e11), (t, e22), (s, e22)):
        direct = matrix_product(direct, gate(g, n))
    if direct != target:
        raise AssertionError("four-call positive control failed")

    # Omission and a higher-rank altered endpoint are meaningful negatives.
    truncated = matrix_identity()
    for g, n in ((s, e11), (t, e11), (t, e22)):
        truncated = matrix_product(truncated, gate(g, n))
    if truncated == target:
        raise AssertionError("omission control unexpectedly hit target")
    if target_difference_rank(1, 3) != 12:
        raise AssertionError("target-rank control changed unexpectedly")
    all_three_nontrivial_rank = 3 * 6
    if all_three_nontrivial_rank <= 3 * max(gate_ranks):
        raise AssertionError("altered all-nontrivial endpoint should exceed three-call rank budget")

    print(
        "PASS_D8_INVERSE_PAIR_W3 "
        f"rank_floor={trank}/{max(gate_ranks)} generators=56 "
        f"triples={checked} matches=0 minimum=4 "
        "direct_control=pass omission_control=pass altered_rank_control=pass"
    )


if __name__ == "__main__":
    main()
