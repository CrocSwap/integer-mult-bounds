#!/usr/bin/env python3
"""Record proper-prefix infinity norms for one degree-6 sign on n=8.

Every value is an integer numerator over 2^30. The schedule is the same
nested parity order: right shear, even child, Schur child, left shear.
The dyadic p^100 normalizer stays outside this package.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "triangular-parity-degree-six-sign"
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
    # (2^30, 2^27, 2^26, 2^26, 2^26, 2^26, -2^26, 2^26)/2^30
    # = (1, 1/8, 1/16, 1/16, 1/16, 1/16, -1/16, 1/16).
    eighth = DEN // 8
    sixteenth = DEN // 16
    symbol = [DEN, eighth, sixteenth, sixteenth, sixteenth, sixteenth, -sixteenth, sixteenth]
    assert sum(abs(entry) for entry in symbol[1:]) == DEN // 2
    even, quotient, schur = split(symbol)
    assert even == [DEN, sixteenth, sixteenth, -sixteenth]
    assert quotient == [eighth, 7 * DEN // 128, 105 * DEN // 2048, 2087 * DEN // 32768]
    assert schur == [DEN, 3 * DEN // 64, 49 * DEN // 1024, -1313 * DEN // 16384]
    even_child, even_quotient, even_schur = split(even)
    assert even_child == [DEN, sixteenth]
    assert even_quotient == [sixteenth, -17 * DEN // 256]
    assert even_schur == [DEN, 15 * DEN // 256]
    schur_even, schur_quotient, schur_child = split(schur)
    assert schur_even == [DEN, 49 * DEN // 1024]
    assert schur_quotient == [3 * DEN // 64, -5399 * DEN // 65536]
    assert schur_child == [DEN, 187 * DEN // 4096]

    produced = factors(symbol)
    assert len(produced) == 22
    nontrivial = [factor for factor in produced if factor != eye(8)]
    assert len(nontrivial) == 10
    cap_2521 = 2521 * (DEN // 2048)
    cap_5_4 = 5 * (DEN // 4)
    cap_21_16 = 21 * (DEN // 16)
    cap_23_16 = 23 * (DEN // 16)
    cap_3_2 = 3 * (DEN // 2)
    assert row_abs_sum(produced[0]) == cap_2521
    assert produced[0][3][4] == 105 * DEN // 2048
    assert produced[0][3][5] == 7 * DEN // 128
    assert produced[0][3][6] == eighth
    # Even child's right shear, entry 1/16, lifts the opening to 5/4.
    assert row_abs_sum(nontrivial[1]) == 17 * (DEN // 16)
    assert nontrivial[1][2][1] == sixteenth
    # Even grandchild's left shear, entry 1/16, lifts 5/4 to 21/16.
    assert row_abs_sum(nontrivial[2]) == 17 * (DEN // 16)
    assert nontrivial[2][2][0] == sixteenth
    # Even child's left shear carries -17/256 and lifts 21/16 to 23/16.
    assert nontrivial[4][1][0] == sixteenth
    assert nontrivial[4][3][0] == -17 * DEN // 256
    assert nontrivial[4][3][2] == sixteenth
    assert row_abs_sum(nontrivial[4]) == 289 * (DEN // 256)
    # Schur child's left shear carries -5399/65536 and stays at 23/16.
    assert nontrivial[8][5][4] == 3 * DEN // 64
    assert nontrivial[8][7][4] == -5399 * DEN // 65536
    assert nontrivial[8][7][6] == 3 * DEN // 64
    assert row_abs_sum(nontrivial[8]) == 74007 * (DEN // 65536)
    assert produced[-1][7][0] == 2087 * DEN // 32768

    running = eye(8)
    proper = []
    for factor in produced[:-1]:
        running = matmul(factor, running)
        proper.append(row_abs_sum(running))
    assert proper == [cap_2521] + [cap_5_4] * 4 + [cap_21_16] * 5 + [cap_23_16] * 11
    assert max(proper) == cap_23_16
    assert cap_2521 < cap_5_4 < cap_21_16 < cap_23_16 < cap_3_2
    assert proper[9] == cap_21_16
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
    assert 2521 < 5 * 512
    assert 5 * 4 < 21
    assert 21 < 23
    assert 23 * 2 < 3 * 16
    assert 3 * 4 < 9 * 2
    assert 15 != 17
    assert 735 != 1313
    assert 1575 != 2087
    assert 2521 != 2087
    assert 2793 != 5399


def main() -> None:
    pins_and_phrases()
    witness()
    print("PASS_TRIANGULAR_PARITY_DEGREE_SIX_SIGN")


if __name__ == "__main__":
    main()
