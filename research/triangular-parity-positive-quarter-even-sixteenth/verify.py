#!/usr/bin/env python3
"""Record proper-prefix infinity norms for the even sixteenth on the positive quarter.

Every value is an integer numerator over 2^30. The schedule is the same
nested parity order: right shear, even child, Schur child, left shear.
The dyadic p^100 normalizer stays outside this package.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "triangular-parity-positive-quarter-even-sixteenth"
DEN = 1 << 30


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    gaussian = (ROOT / "research/unconditional-batched-crt/GAUSSIAN.md").read_text(
        encoding="utf-8"
    )
    shallow = (
        ROOT / "research/unconditional-batched-crt/vendor/SHALLOW-TOEPLITZ.md"
    ).read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "logarithmic prefix norm O(log B log poly(p))." in gaussian
    assert "sufficient dyadic p^100 bound" in gaussian
    assert "D_tri(N)=O(log^2 N)." in shallow
    assert "eta/(1-eta)" in shallow


def eye(size: int) -> list[list[int]]:
    return [[DEN if row == col else 0 for col in range(size)] for row in range(size)]


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    size = len(left)
    product = []
    for row in range(size):
        out = []
        for col in range(size):
            total = sum(left[row][k] * right[k][col] for k in range(size))
            assert total % DEN == 0
            out.append(total // DEN)
        product.append(out)
    return product


def row_abs_sum(rows: list[list[int]]) -> int:
    return max(sum(abs(entry) for entry in row) for row in rows)


def poly_mul(left: list[int], right: list[int], size: int) -> list[int]:
    raw = [0] * size
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            if i + j < size:
                raw[i + j] += a * b
    out = []
    for value in raw:
        assert value % DEN == 0
        out.append(value // DEN)
    return out


def series_div(num: list[int], den: list[int], size: int) -> list[int]:
    assert den[0] == DEN
    inv = [0] * size
    inv[0] = DEN
    for degree in range(1, size):
        total = 0
        for lag in range(1, degree + 1):
            if lag < len(den):
                total += den[lag] * inv[degree - lag]
        assert total % DEN == 0
        inv[degree] = -(total // DEN)
    return poly_mul(num, inv, size)


def split(symbol: list[int]) -> tuple[list[int], list[int], list[int]]:
    even = symbol[0::2]
    odd = symbol[1::2]
    size = len(even)
    quotient = series_div(odd, even, size)
    # Modulo z^1, multiplication by z is zero, so the Schur child is the even child.
    if size == 1:
        return even, quotient, [even[0]]
    square = poly_mul(odd, odd, size)
    shifted = [0] + series_div(square, even, size)[:-1]
    schur = [even[i] - shifted[i] for i in range(size)]
    return even, quotient, schur


def to_natural(reordered: list[list[int]]) -> list[list[int]]:
    size = len(reordered)
    perm = list(range(0, size, 2)) + list(range(1, size, 2))
    inverse = [0] * size
    for index, source in enumerate(perm):
        inverse[source] = index
    return [
        [reordered[inverse[row]][inverse[col]] for col in range(size)]
        for row in range(size)
    ]


def factors(symbol: list[int]) -> list[list[list[int]]]:
    """Factors in this symbol's even/odd basis. The first factor is applied first."""
    size = len(symbol)
    if size == 1:
        assert symbol == [DEN]
        return [[[DEN]]]
    even, quotient, schur = split(symbol)
    half = size // 2
    shifted = [0] + quotient[:-1]
    right = eye(size)
    left = eye(size)
    for row in range(half):
        for col in range(row + 1):
            right[row][half + col] = shifted[row - col]
            left[half + row][col] = quotient[row - col]
    out = [right]
    for child, offset in ((even, 0), (schur, half)):
        for factor in factors(child):
            natural = to_natural(factor)
            block = eye(size)
            for row in range(len(natural)):
                for col in range(len(natural)):
                    block[offset + row][offset + col] = natural[row][col]
            out.append(block)
    out.append(left)
    return out


def witness() -> None:
    # (2^30, 2^28, -2^26, -2^26, -2^26, 2^26, 2^26, 2^26)/2^30
    # = (1, 1/4, -1/16, -1/16, -1/16, 1/16, 1/16, 1/16).
    quarter = DEN // 4
    sixteenth = DEN // 16
    symbol = [DEN, quarter, -sixteenth, -sixteenth, -sixteenth, sixteenth, sixteenth, sixteenth]
    assert sum(abs(entry) for entry in symbol[1:]) == 5 * DEN // 8
    even, quotient, schur = split(symbol)
    assert even == [DEN, -sixteenth, -sixteenth, sixteenth]
    assert quotient == [quarter, -3 * DEN // 64, 77 * DEN // 1024, 797 * DEN // 16384]
    assert schur == [DEN, -DEN // 8, -9 * DEN // 256, 103 * DEN // 4096]
    even_child, even_quotient, even_schur = split(even)
    assert even_child == [DEN, -sixteenth]
    assert even_quotient == [-sixteenth, 15 * DEN // 256]
    assert even_schur == [DEN, -17 * DEN // 256]
    schur_even, schur_quotient, schur_child = split(schur)
    assert schur_even == [DEN, -9 * DEN // 256]
    assert schur_quotient == [-DEN // 8, 85 * DEN // 4096]
    assert schur_child == [DEN, -13 * DEN // 256]

    produced = factors(symbol)
    assert len(produced) == 22
    nontrivial = [factor for factor in produced if factor != eye(8)]
    assert len(nontrivial) == 10
    cap_1405 = 1405 * (DEN // 1024)
    cap_11_8 = 11 * (DEN // 8)
    cap_23_16 = 23 * (DEN // 16)
    cap_3_2 = 3 * (DEN // 2)
    cap_25_16 = 25 * (DEN // 16)
    cap_13_8 = 13 * (DEN // 8)
    assert row_abs_sum(produced[0]) == cap_1405
    assert produced[0][1][4] == quarter
    assert produced[0][2][4] == -3 * DEN // 64
    assert produced[0][2][5] == quarter
    assert produced[0][3][4] == 77 * DEN // 1024
    assert produced[0][3][5] == -3 * DEN // 64
    assert produced[0][3][6] == quarter
    # Even child's right shear, entry -1/16, lifts this opening to 11/8.
    assert produced[1][2][1] == -sixteenth
    assert row_abs_sum(produced[1]) == 17 * (DEN // 16)
    # Even grandchild's left shear, entry -1/16, lifts 11/8 to 23/16.
    assert produced[5][2][0] == -sixteenth
    assert row_abs_sum(produced[5]) == 17 * (DEN // 16)
    # Even child's Schur left shear does not lift the running norm past 23/16.
    assert produced[9][3][1] == -17 * DEN // 256
    assert row_abs_sum(produced[9]) == 273 * (DEN // 256)
    # Even child's left shear lifts 23/16 to 25/16, above 3/2.
    assert produced[10][1][0] == -sixteenth
    assert produced[10][3][0] == 15 * DEN // 256
    assert produced[10][3][2] == -sixteenth
    assert row_abs_sum(produced[10]) == 287 * (DEN // 256)
    # The Schur quotient starts at -1/8, so that child's right shear is not I.
    assert produced[11][6][5] == -DEN // 8
    assert row_abs_sum(produced[11]) == 9 * (DEN // 8)
    assert produced[15][6][4] == -9 * DEN // 256
    assert row_abs_sum(produced[15]) == 265 * (DEN // 256)
    assert produced[19][7][5] == -13 * DEN // 256
    assert row_abs_sum(produced[19]) == 269 * (DEN // 256)
    assert produced[20][5][4] == -DEN // 8
    assert produced[20][7][4] == 85 * DEN // 4096
    assert produced[20][7][6] == -DEN // 8
    assert row_abs_sum(produced[20]) == 4693 * (DEN // 4096)
    last = 797 * DEN // 16384
    assert produced[-1][7][0] == last
    assert row_abs_sum(produced[-1]) == 23277 * (DEN // 16384)
    assert all(last not in row for factor in produced[:-1] for row in factor)

    running = eye(8)
    proper = []
    for factor in produced[:-1]:
        running = matmul(factor, running)
        proper.append(row_abs_sum(running))
    assert proper == [cap_1405] + [cap_11_8] * 4 + [cap_23_16] * 5 + [cap_25_16] * 11
    assert max(proper) == cap_25_16
    assert cap_1405 < cap_11_8 < cap_23_16 < cap_3_2 < cap_25_16 < cap_13_8
    assert proper[0] == cap_1405
    assert proper[1] == cap_11_8
    assert proper[4] == cap_11_8
    assert proper[5] == cap_23_16
    assert proper[9] == cap_23_16
    assert proper[10] == cap_25_16
    assert sum(1 for value in proper if value > cap_3_2) == 11
    assert sum(1 for value in proper if value > cap_25_16) == 0
    full = matmul(produced[-1], running)
    toeplitz = [
        [(symbol[row - col] if row >= col else 0) for col in range(8)]
        for row in range(8)
    ]
    perm = list(range(0, 8, 2)) + list(range(1, 8, 2))
    reordered = [[toeplitz[perm[row]][perm[col]] for col in range(8)] for row in range(8)]
    assert full == reordered
    assert row_abs_sum(full) == cap_13_8
    # Above #4886's 1373/1024 and #4838's 1403/1024, and still below 11/8.
    assert 1373 < 1403 < 1405 < 11 * 128 < 1411 < 1413 < 23 * 64
    assert 23 * 4 < 93
    assert 93 * 2 < 3 * 64
    assert 25 * 2 > 3 * 16
    assert 25 < 26
    assert 13 * 2 < 9 * 4


def main() -> None:
    pins_and_phrases()
    witness()
    print("PASS_TRIANGULAR_PARITY_POSITIVE_QUARTER_EVEN_SIXTEENTH")


if __name__ == "__main__":
    main()
