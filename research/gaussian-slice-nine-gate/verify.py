#!/usr/bin/env python3
"""Absorb one heavy slice by the factor-9 gate.

Every comparison is an integer identity. The inverse bound stays a hypothesis.
The coefficient-9 monomial gate stays at 16.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-slice-nine-gate"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ceil_log2(value: int) -> int:
    level = 0
    power = 1
    while power < value:
        power *= 2
        level += 1
    return level


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    gate = (ROOT / "research/gaussian-tensor-nine/README.md").read_text(encoding="utf-8")
    nine = (ROOT / "research/gaussian-neumann-nine/README.md").read_text(encoding="utf-8")
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "16 g L ≤ p" in gate
    assert "9 < 16" in gate
    assert "9 > 8" in gate
    assert "8 p^2 < U < 9 p^2." in nine
    assert "||P_i-H_i^-1||_2 <= p^10 exp(-p^2)." in halo


def ninths() -> None:
    # Nine times the eighths is 72 (E + C p). The gate enters as 80 * 9 g L.
    assert 80 * 9 == 720
    assert 9 * 8 == 72
    assert 9 * 4 == 36
    assert 72 * (2 * 3 + 5) == 36 * (4 * 3 + 2 * 5)
    # 36 p^2 - 80 p - 144 is positive at p = 64 and increases by 72 p - 44.
    assert 36 * 64 * 64 - 80 * 64 - 144 == 142192
    assert 142192 > 0
    assert (36 * 65 * 65 - 80 * 65 - 144) - 142192 == 72 * 64 - 44
    # Dropping the 1 in 1 + p^4 leaves p^{10 g}, strictly below the next bit.
    assert 10 * (2 - 1) + 6 + 4 == 10 * 2
    assert 1 + 2**4 < 2 * 2**4


def separates_ten() -> None:
    # p = 65, g = 1 meets factor 9 and misses factor 10.
    assert ceil_log2(65) == 7
    assert 9 * 1 * 7 <= 65
    assert 10 * 1 * 7 > 65
    # The factor-10 eighths line 80 g L <= 8 p fails at this point.
    assert 80 * 1 * 7 > 8 * 65
    one = 10 * 1 * 7 + 1 - 65 * 65
    assert one == -4154
    assert one <= -1
    # A point already legal for 10 remains legal for 9.
    assert ceil_log2(64) == 6
    assert 9 * 1 * 6 <= 64
    assert 10 * 1 * 6 <= 64


def outside() -> None:
    # At p = 2 and g = 1 the factor-9 hypothesis fails, and the slice exceeds 1.
    assert ceil_log2(2) == 1
    assert 9 * 1 * 1 > 2
    total = 5040 + 5040 + 2520 + 840 + 210 + 42 + 7
    assert total == 13699
    assert 3 * 5040 - total == 1421
    assert 8 < 1421 * 7
    assert 3**4 == 81
    assert 2**6 * (1 + 2**4) == 1088
    assert 81 < 1088


def main() -> None:
    pins_and_phrases()
    ninths()
    separates_ten()
    outside()
    print("PASS_GAUSSIAN_SLICE_NINE_GATE")


if __name__ == "__main__":
    main()
