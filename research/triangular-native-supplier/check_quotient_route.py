"""Compare full quotient tape motion with independent row-minor formulas."""

from argparse import ArgumentParser
from fractions import Fraction
from io import BytesIO
from pathlib import Path
from struct import Struct
import sys


def determinant(a):
    if not a:
        return 1
    n = len(a)
    if n == 1:
        return a[0][0]
    if n == 2:
        return a[0][0] * a[1][1] - a[0][1] * a[1][0]
    # Fraction-free elimination gives the integer determinant.
    b = [list(row) for row in a]
    sign, prev = 1, 1
    for i in range(n - 1):
        k = next((k for k in range(i, n) if b[k][i]), None)
        if k is None:
            return 0
        if k != i:
            b[k], b[i] = b[i], b[k]
            sign = -sign
        p = b[i][i]
        for j in range(i + 1, n):
            for k in range(i + 1, n):
                b[j][k] = (b[j][k] * p - b[j][i] * b[i][k]) // prev
        prev = p
    return sign * b[-1][-1]


def oracle_right(g, word, modulus):
    rows = [list(row) for row in g]
    for op, i, *args in word:
        for row in rows:
            if op == "swap":
                j = args[0]
                row[i], row[j] = row[j], row[i]
            elif op == "scale":
                k = Fraction(args[0])
                row[i] = row[i] * k.numerator * pow(k.denominator, -1, modulus) % modulus
            else:
                j, k = args
                k = Fraction(k)
                row[i] = (row[i] + row[j] * k.numerator * pow(k.denominator, -1, modulus)) % modulus
    pivots, normal, lower = [], [], []
    n = len(g)
    for i, row in enumerate(rows):
        minor = [[src[j] for j in pivots] for src in rows[:i]]
        den = pow(determinant(minor), -1, modulus)
        numer = []
        for j in range(i):
            m = list(minor)
            m[j] = [row[c] for c in pivots]
            numer.append(determinant(m) * den % modulus)
        y = [
            (x - sum(a * r[j] for a, r in zip(numer, rows[:i], strict=True))) % modulus
            for j, x in enumerate(row)
        ]
        ell = [
            (int(k == i) + sum(a * r[k] for a, r in zip(numer, lower, strict=True))) % modulus
            for k in range(n)
        ]
        pivots.append(next(j for j, x in enumerate(y) if x % 3))
        normal.append(y)
        lower.append(ell)
    return normal, lower


def shape(row):
    used = set()
    free = []
    for i, r in enumerate(row):
        free.extend((i, j) for j in range(len(r)) if j not in used)
        used.add(next(j for j, v in enumerate(r) if v % 3))
    return free


def output_index(g, word, side, lows):
    modulus = side * 3
    y, ell = oracle_right(g, word, modulus)
    dst = [(i, j) for i, j in shape(y)]
    low = tuple(z % 3 for r in y for z in r)
    index = 0 if lows is None else lows[low]
    for i, j in dst:
        index = index * side + y[i][j] // 3
    return index, ell


def update_vector(v, lower, modulus):
    result = []
    for x, row in zip(v, lower, strict=True):
        result.append(
            (x - sum(c * y for c, y in zip(row[: len(result)], result, strict=True))) % modulus
        )
    return bytes(result)


def check(n, digits, one_low, word):
    from quotient_route import (
        canonical_lows,
        free_count,
        high_packet,
        low_count,
        quotient_right_route,
    )
    from quotient_route import right_matrix, representative
    from streaming_routes import cold_swap_tape, read_exact

    side = 3 ** (digits - 1)
    stride = side ** free_count(n)
    all_lows = list(canonical_lows(n))
    assert len(set(all_lows)) == low_count(n) == len(all_lows)
    assert all_lows == sorted(all_lows)
    chosen = all_lows if one_low is None else [all_lows[one_low]]
    low_indices = None if one_low is not None else {low: i for i, low in enumerate(all_lows)}
    pack = Struct(">I")
    records = []
    for i in range(len(chosen) * stride):
        records.append(pack.pack(i) + bytes((i * 11 + k * 7) % (3 * side) for k in range(n)))
    size = len(records[0])
    target = [None] * len(records)
    moved = corrected = 0
    for w, low in enumerate(chosen):
        for h in range(stride):
            g = representative(low, h, n, digits)
            # Recover both public indices without the emitter's pivot or digit helpers.
            assert tuple(z % 3 for row in g for z in row) == low
            index = 0
            for i, j in shape(g):
                index = index * side + g[i][j] // 3
            assert index == h
            dest, lower = output_index(g, word, side, low_indices)
            which = w * stride + h
            assert target[dest] is None
            original = records[which]
            target[dest] = original[:4] + update_vector(original[4:], lower, 3 * side)
            moved += dest != which
            corrected += original != target[dest]
    assert all(row is not None for row in target)
    count = [0, 0]

    def swap(src, dst, width, prefix, gap, suffix):
        count[0] += 1
        count[1] += prefix * 3 ** (2 * width) * gap * suffix
        cold_swap_tape(src, dst, width, prefix, gap, suffix)

    def transform(src, dst, lower, length):
        data = read_exact(src, length)
        dst.write(data[:4] + update_vector(data[4:], lower, 3 * side))

    src, dst = BytesIO(b"".join(records)), BytesIO()
    if one_low is None:
        quotient_right_route(
            src, dst, n, digits, 1, size, word, previous_swap=swap, transform=transform
        )
    else:
        lo = tuple(tuple(chosen[0][i : i + n]) for i in range(0, n * n, n))
        image, _ = oracle_right(lo, word, 3)
        high_packet(
            src, dst, lo, image, right_matrix(n, word, 3 * side), digits, size, swap, transform
        )
    expected = b"".join(target)
    assert expected == dst.getvalue(), (
        n,
        digits,
        one_low,
        next((k // size for k, (a, b) in enumerate(zip(expected, dst.getvalue())) if a != b), None),
    )
    if one_low is None:
        from factored_frames import inverse_word

        undo = BytesIO()
        dst.seek(0)
        quotient_right_route(
            dst,
            undo,
            n,
            digits,
            1,
            size,
            tuple(inverse_word(word)),
            previous_swap=cold_swap_tape,
            transform=transform,
        )
        assert undo.getvalue() == b"".join(records)
    print(
        f"n={n} u={digits} low={one_low} records={len(target)} moved={moved} corrected={corrected} earlier_swaps={count[0]} swapped_bytes={count[1]}"
    )
    return dst.getvalue()


def main():
    ap = ArgumentParser()
    ap.add_argument("predecessor", type=Path)
    ap.add_argument("--large", action="store_true")
    args = ap.parse_args()
    sys.path.append(str(args.predecessor))
    w2 = (("add", 0, 1, Fraction(1, 2)), ("swap", 0, 1), ("scale", 1, -2), ("add", 1, 0, 2))
    w3 = w2 + (("add", 2, 1, 4), ("swap", 0, 2), ("add", 1, 2, -1))
    check(2, 1, None, w2)
    check(3, 1, None, w3)
    check(2, 2, None, w2)
    check(3, 2, 51, w3)
    if args.large:
        check(2, 3, None, w2)


if __name__ == "__main__":
    main()
