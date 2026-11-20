#!/usr/bin/env python3
"""Check the two rank formulas against the literal product-bit matrices."""


def rank(m: int, operands: range) -> int:
    pivots: dict[int, int] = {}
    for x in operands:
        # One byte per Boolean entry keeps the matrix construction simple.
        row = int.from_bytes(
            bytes(((x * y) >> (m - 1)) & 1 for y in operands), "little"
        )
        while row:
            leading_bit = row.bit_length() - 1
            if leading_bit not in pivots:
                pivots[leading_bit] = row
                break
            row ^= pivots[leading_bit]
    return len(pivots)


def main() -> None:
    print("m  full  expected  odd-by-odd  expected")
    odd_bases = {1: 1, 2: 2}
    for m in range(1, 13):
        size = 1 << m
        full_rank = rank(m, range(size))
        odd_rank = rank(m, range(1, size, 2))
        expected_full = 1 if m == 1 else (size // 2) // 3 + (3 * m) // 2 - 1
        expected_odd = odd_bases[m] if m < 3 else size // 8 + 1
        print(f"{m:2}  {full_rank:4}  {expected_full:8}  {odd_rank:10}  {expected_odd:8}")
        if (full_rank, odd_rank) != (expected_full, expected_odd):
            raise AssertionError(f"rank mismatch at {m=}")


if __name__ == "__main__":
    main()
