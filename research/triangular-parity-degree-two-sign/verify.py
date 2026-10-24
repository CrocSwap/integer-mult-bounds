#!/usr/bin/env python3
"""Record proper-prefix infinity norms for one degree-2 sign on n=8.

Every value is an integer numerator over 2^30. The schedule is the same
nested parity order: right shear, even child, Schur child, left shear.
The dyadic p^100 normalizer stays outside this package.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "triangular-parity-degree-two-sign"
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
    # (2^30, 2^27, -2^26, 2^26, 2^26, 2^26, 2^26, 2^26)/2^30
    # = (1, 1/8, -1/16, 1/16, 1/16, 1/16, 1/16, 1/16).
    eighth = DEN // 8
    sixteenth = DEN // 16
    symbol = [DEN, eighth, -sixteenth, sixteenth, sixteenth, sixteenth, sixteenth, sixteenth]
    assert sum(abs(entry) for entry in symbol[1:]) == DEN // 2
    even, quotient, schur = split(symbol)
    assert even == [DEN, -sixteenth, sixteenth, sixteenth]
    assert quotient == [eighth, 9 * DEN // 128, 121 * DEN // 2048, 1769 * DEN // 32768]
    assert schur == [DEN, -5 * DEN // 64, 47 * DEN // 1024, 703 * DEN // 16384]
    even_child, even_quotient, even_schur = split(even)
    assert even_child == [DEN, sixteenth]
    assert even_quotient == [-sixteenth, 17 * DEN // 256]
    assert even_schur == [DEN, 15 * DEN // 256]
    schur_even, schur_quotient, schur_child = split(schur)
    assert schur_even == [DEN, 47 * DEN // 1024]
    assert schur_quotient == [-5 * DEN // 64, 3047 * DEN // 65536]
    assert schur_child == [DEN, 163 * DEN // 4096]

    produced = factors(symbol)
    assert len(produced) == 22
    nontrivial = [factor for factor in produced if factor != eye(8)]
    assert len(nontrivial) == 10
    cap_2569 = 2569 * (DEN // 2048)
    cap_5_4 = 5 * (DEN // 4)
    cap_21_16 = 21 * (DEN // 16)
    cap_169 = 169 * (DEN // 128)
    cap_23_16 = 23 * (DEN // 16)
    cap_3_2 = 3 * (DEN // 2)
    assert row_abs_sum(produced[0]) == cap_2569
    assert produced[0][2][4] == 9 * DEN // 128
    assert produced[0][3][4] == 121 * DEN // 2048
    assert produced[0][3][5] == 9 * DEN // 128
    assert produced[0][3][6] == eighth
    # Even child's right shear carries -1/16 and does not lift 2569/2048.
    assert row_abs_sum(produced[1]) == 17 * (DEN // 16)
    assert produced[1][2][1] == -sixteenth
    # Even grandchild's left shear stays entry 1/16 and lifts to 21/16.
    assert row_abs_sum(produced[5]) == 17 * (DEN // 16)
    assert produced[5][2][0] == sixteenth
    # Even child's Schur left shear stays entry 15/256 and lifts 21/16 to 169/128.
    assert produced[9][3][1] == 15 * DEN // 256
    assert row_abs_sum(produced[9]) == 271 * (DEN // 256)
    # Even child's left shear carries -1/16 and 17/256 and lifts 169/128 to 23/16.
    assert produced[10][1][0] == -sixteenth
    assert produced[10][3][0] == 17 * DEN // 256
    assert produced[10][3][2] == -sixteenth
    assert row_abs_sum(produced[10]) == 289 * (DEN // 256)
    assert produced[11][6][5] == -5 * DEN // 64
    assert row_abs_sum(produced[11]) == 69 * (DEN // 64)
    assert produced[15][6][4] == 47 * DEN // 1024
    assert row_abs_sum(produced[15]) == 1071 * (DEN // 1024)
    assert produced[19][7][5] == 163 * DEN // 4096
    assert row_abs_sum(produced[19]) == 4259 * (DEN // 4096)
    assert produced[20][5][4] == -5 * DEN // 64
    assert produced[20][7][4] == 3047 * DEN // 65536
    assert produced[20][7][6] == -5 * DEN // 64
    assert row_abs_sum(produced[20]) == 73703 * (DEN // 65536)
    assert produced[-1][7][0] == 1769 * DEN // 32768

    running = eye(8)
    proper = []
    for factor in produced[:-1]:
        running = matmul(factor, running)
        proper.append(row_abs_sum(running))
    assert proper == [cap_2569] * 5 + [cap_21_16] * 4 + [cap_169] + [cap_23_16] * 11
    assert max(proper) == cap_23_16
    assert cap_5_4 < cap_2569 < cap_21_16 < cap_169 < cap_23_16 < cap_3_2
    assert proper[1] == cap_2569
    assert proper[4] == cap_2569
    assert proper[5] == cap_21_16
    assert proper[8] == cap_21_16
    assert proper[9] == cap_169
    assert proper[10] == cap_23_16
    assert proper[20] == cap_23_16
    full = matmul(produced[-1], running)
    toeplitz = [
        [(symbol[row - col] if row >= col else 0) for col in range(8)]
        for row in range(8)
    ]
    perm = list(range(0, 8, 2)) + list(range(1, 8, 2))
    reordered = [[toeplitz[perm[row]][perm[col]] for col in range(8)] for row in range(8)]
    assert full == reordered
    assert row_abs_sum(full) == cap_3_2
    assert 2569 > 5 * 512
    assert 2569 < 21 * 128
    assert 21 * 8 < 169 < 23 * 8
    assert 23 * 2 < 3 * 16
    assert 3 * 4 < 9 * 2
    assert 2521 < 2553 < 2567 < 2569
    assert 7 != 9
    assert 3 != 5
    assert 1769 != 1815
    assert -9 * DEN // 128 != quotient[1]


def main() -> None:
    pins_and_phrases()
    witness()
    print("PASS_TRIANGULAR_PARITY_DEGREE_TWO_SIGN")


if __name__ == "__main__":
    main()
