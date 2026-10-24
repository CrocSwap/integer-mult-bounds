#!/usr/bin/env python3
"""Absorb g copies of the heavy slice by the factor-8 gate.

Every comparison is an integer identity. The inverse bound stays a hypothesis.
The coefficient-9 monomial gate stays at 16.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-slice-eight-copies"


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


def budget() -> None:
    # 80 g L <= 10 p, and the extra level becomes one more p.
    assert 8 * 10 == 80
    assert 10 + 1 == 11
    assert 8 * 1 == 8
    assert 8 * (2 * 3 + 5) == 4 * (4 * 3 + 2 * 5)
    # 8 L > 1, so the gate forces g < 2^L.
    assert 8 > 1
    # 8 (m + 1) <= 2^m for m >= 6, and the step preserves a doubling.
    assert 8 * 7 <= 2**6
    assert 8 <= 2**6
    assert 2**6 + 8 <= 2**7
    assert ceil_log2(64) == 6
    assert ceil_log2(65) == 7
    assert 8 * 6 <= 64
    assert 8 * 7 <= 65
    # 4 p^2 - 11 p - 16 is positive at p = 64 and increases by 8 p - 7.
    assert 4 * 64 * 64 - 11 * 64 - 16 == 15664
    assert 15664 > 0
    assert (4 * 65 * 65 - 11 * 65 - 16) - 15664 == 8 * 64 - 7


def witness() -> None:
    # Two axes at p = 112 meet factor 8 and miss factor 9.
    level = ceil_log2(112)
    assert level == 7
    assert 8 * 2 * level <= 112
    assert 9 * 2 * level > 112
    assert 2 < 2**level
    one = 10 * 2 * level + 1 - 112 * 112
    copies = one + level
    assert one == -12403
    assert copies == -12396
    assert copies <= -1


def outside() -> None:
    # At p = 2 and g = 2 the factor-8 hypothesis fails.
    assert ceil_log2(2) == 1
    assert 8 * 2 * 1 > 2
    assert 10 * 2 * 1 + 1 + 1 - 2 * 2 == 18
    # e < 3, so two copies of the p = 2 slice exceed 1.
    total = 5040 + 5040 + 2520 + 840 + 210 + 42 + 7
    assert total == 13699
    assert 3 * 5040 - total == 1421
    assert 8 < 1421 * 7
    assert 3**4 == 81
    assert 2**6 * (1 + 2**4) == 1088
    assert 2 * (2**10) * 1088 > 81


def main() -> None:
    pins_and_phrases()
    budget()
    witness()
    outside()
    print("PASS_GAUSSIAN_SLICE_EIGHT_COPIES")


if __name__ == "__main__":
    main()
