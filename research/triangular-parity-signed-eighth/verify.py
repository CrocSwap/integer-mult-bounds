#!/usr/bin/env python3
"""Record proper-prefix infinity norms for one signed n=8 symbol.

Every value is an integer numerator over 2^30. The schedule is the same
nested parity order: right shear, even child, Schur child, left shear.
The dyadic p^100 normalizer stays outside this package.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "triangular-parity-signed-eighth"
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
    # (2^30, 3*2^27, -2^27, 0, ...)/2^30 = (1, 3/8, -1/8, 0, 0, 0, 0, 0).
    three = 3 * DEN // 8
    one = DEN // 8
    symbol = [DEN, three, -one, 0, 0, 0, 0, 0]
    assert abs(symbol[1]) + abs(symbol[2]) == DEN // 2
    even, quotient, schur = split(symbol)
    assert even == [DEN, -one, 0, 0]
    assert quotient == [three, 3 * DEN // 64, 3 * DEN // 512, 3 * DEN // 4096]
    assert schur == [DEN, -17 * DEN // 64, -9 * DEN // 512, -9 * DEN // 4096]
    even_child, even_quotient, even_schur = split(even)
    assert even_child == [DEN, 0]
    assert even_quotient == [-one, 0]
    assert even_schur == [DEN, -(DEN // 64)]
    schur_even, schur_quotient, schur_child = split(schur)
    assert schur_even == [DEN, -9 * DEN // 512]
    assert schur_quotient == [-17 * DEN // 64, -225 * DEN // 32768]
    assert schur_child == [DEN, -361 * DEN // 4096]

    produced = factors(symbol)
    assert len(produced) == 22
    nontrivial = [factor for factor in produced if factor != eye(8)]
    assert len(nontrivial) == 9
    # The absolute row sum of z k is unchanged by the even-coefficient sign,
    # so the first prefix is again 1 + 3/8 + 3/64 + 3/512 = 731/512.
    cap_731 = 731 * (DEN // 512)
    cap_3_2 = 3 * (DEN // 2)
    assert row_abs_sum(produced[0]) == cap_731
    assert produced[0][3][4] == 3 * DEN // 512
    assert produced[0][3][5] == 3 * DEN // 64
    assert produced[0][3][6] == three
    assert row_abs_sum(nontrivial[1]) == 9 * (DEN // 8)
    assert nontrivial[1][2][1] == -one

    running = eye(8)
    proper = []
    for factor in produced[:-1]:
        running = matmul(factor, running)
        proper.append(row_abs_sum(running))
    assert proper == [cap_731] + [cap_3_2] * 20
    assert max(proper) == cap_3_2
    assert cap_731 < cap_3_2
    full = matmul(produced[-1], running)
    toeplitz = [
        [(symbol[row - col] if row >= col else 0) for col in range(8)]
        for row in range(8)
    ]
    perm = list(range(0, 8, 2)) + list(range(1, 8, 2))
    reordered = [[toeplitz[perm[row]][perm[col]] for col in range(8)] for row in range(8)]
    assert full == reordered
    assert row_abs_sum(full) == cap_3_2
    assert 731 * 2 < 3 * 512
    assert 3 * 4 < 9 * 2


def main() -> None:
    pins_and_phrases()
    witness()
    print("PASS_TRIANGULAR_PARITY_SIGNED_EIGHTH")


if __name__ == "__main__":
    main()
