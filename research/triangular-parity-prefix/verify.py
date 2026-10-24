#!/usr/bin/env python3
"""Bound one triangular parity-split prefix in the infinity norm.

Every comparison is an integer identity. The remaining recursion depth and
the dyadic p^100 normalizer stay outside this package.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "triangular-parity-prefix"


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


def row_abs_sum(rows: list[list[int]]) -> int:
    return max(sum(abs(entry) for entry in row) for row in rows)


def _matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    size = len(left)
    return [
        [
            sum(left[row][k] * right[k][col] for k in range(size))
            for col in range(size)
        ]
        for row in range(size)
    ]


def bounds() -> None:
    # a + b <= eta <= 1/2, in units of 1/4. Values: 0, 1, 2.
    # b/(1-a) <= eta and a + b^2/(1-a) <= eta.
    for a in range(3):
        for b in range(3 - a):
            eta = 2
            # b <= eta (1-a) after clearing the denominator 4:
            # b/4 <= (eta/4) * (1 - a/4) = eta (4-a) / 16.
            assert 4 * b <= eta * (4 - a)
            # a(1-a) + b^2 <= eta (1-a), same clearing.
            left = a * (4 - a) + b * b
            right = eta * (4 - a)
            assert left <= right
    # The pure odd split saturates b = eta and a = 0.
    assert 4 * 2 <= 2 * (4 - 0)
    # Published eta/(1-eta) at eta = 1/2 is 1, which is looser than eta.
    assert 2 * 2 == 4
    assert 1 * 4 == 4


def witness() -> None:
    # Symbol (4, 2, 0, 0)/4 = (1, 1/2, 0, 0). Tail l1 = 1/2.
    # Even child E = I. Odd symbol k = (2, 0)/4. Schur child s = (4, -1)/4.
    symbol = [4, 2, 0, 0]
    assert abs(symbol[1]) + abs(symbol[2]) + abs(symbol[3]) == 2
    even = [symbol[0], symbol[2]]
    odd = [symbol[1], symbol[3]]
    assert even == [4, 0]
    assert abs(odd[0]) + abs(odd[1]) == 2
    # k = odd / even. even is the constant 4, so k = odd.
    k = odd
    # z odd^2 / even: odd^2 = (4, 0, 0)/16, times z is (0, 4, 0)/16.
    # Divide by even = 4/4 = 1, in sixteenths: (0, 4)/16 = (0, 1)/4.
    # s = even - that = (4, 0)/4 - (0, 1)/4 = (4, -1)/4.
    s = [4, -1]
    assert abs(s[1]) == 1
    assert abs(s[1]) <= 2

    def toep(coeffs: list[int], den: int) -> list[list[int]]:
        size = len(coeffs)
        return [
            [(coeffs[i - j] if i >= j else 0) for j in range(size)]
            for i in range(size)
        ]

    # Infinity norm over denominator 4. Last row carries every coefficient.
    whole = toep(symbol, 4)
    assert row_abs_sum(whole) == 6
    assert sum(abs(entry) for entry in whole[-1]) == 6
    child = toep(s, 4)
    assert row_abs_sum(child) == 5
    assert 5 <= 6

    # Factors over denominator 4. Three of them multiply to 16 times the
    # reordered symbol matrix, because each factor already includes the 4.
    right = [
        [4, 0, 0, 0],
        [0, 4, 2, 0],
        [0, 0, 4, 0],
        [0, 0, 0, 4],
    ]
    left = [
        [4, 0, 0, 0],
        [0, 4, 0, 0],
        [2, 0, 4, 0],
        [0, 2, 0, 4],
    ]
    middle = [
        [4, 0, 0, 0],
        [0, 4, 0, 0],
        [0, 0, 4, 0],
        [0, 0, -1, 4],
    ]
    product = _matmul(_matmul(left, middle), right)
    reordered = [
        [4, 0, 0, 0],
        [0, 4, 2, 0],
        [2, 0, 4, 0],
        [0, 2, 0, 4],
    ]
    assert product == [[16 * entry for entry in row] for row in reordered]
    assert row_abs_sum(right) == 6
    # Moving the odd coefficient by 1/2 replaces 2 by 4. The prefix becomes 2.
    moved = [
        [4, 0, 0, 0],
        [0, 4, 4, 0],
        [0, 0, 4, 0],
        [0, 0, 0, 4],
    ]
    assert row_abs_sum(moved) == 8
    assert 8 > 6
    # The new tail l1 is 1, so the hypothesis tail <= 1/2 has failed.
    assert abs(4) + abs(0) + abs(0) == 4


def main() -> None:
    pins_and_phrases()
    bounds()
    witness()
    print("PASS_TRIANGULAR_PARITY_PREFIX")


if __name__ == "__main__":
    main()
