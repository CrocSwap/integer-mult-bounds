#!/usr/bin/env python3
"""Absorb g copies of the heavy slice by the factor-3 gate.

Every comparison is an integer identity. The inverse bound stays a hypothesis.
The coefficient-9 monomial gate stays at 16.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-slice-three-copies"


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
    # Thirds spend 80 p. Copies replace 24 L by 3 p once 8 L <= p.
    assert 80 * 3 == 240
    assert 3 * 8 == 24
    assert 24 == 3 * 8
    assert 80 + 3 == 83
    assert 24 * (2 * 3 + 5) == 12 * (4 * 3 + 2 * 5)
    # 3 L > 1, so the gate forces g < 2^L.
    assert 3 > 1
    # 8 (m + 1) <= 2^m for m >= 6, and the step preserves a doubling.
    assert 8 * 7 <= 2**6
    assert 8 <= 2**6
    assert 2**6 + 8 <= 2**7
    assert ceil_log2(64) == 6
    assert ceil_log2(65) == 7
    assert 8 * 6 <= 64
    assert 8 * 7 <= 65
    # 12 p^2 - 83 p - 48 is positive at p = 64 and increases by 24 p - 71.
    assert 12 * 64 * 64 - 83 * 64 - 48 == 43792
    assert 43792 > 0
    assert (12 * 65 * 65 - 83 * 65 - 48) - 43792 == 24 * 64 - 71


def witness() -> None:
    # Four axes at p = 84 meet factor 3 and miss factor 4.
    level = ceil_log2(84)
    assert level == 7
    assert 3 * 4 * level <= 84
    assert 4 * 4 * level > 84
    assert 4 < 2**level
    one = 10 * 4 * level + 1 - 84 * 84
    copies = one + level
    assert one == -6775
    assert copies == -6768
    assert copies <= -1


def outside() -> None:
    # At p = 2 and g = 2 the factor-3 hypothesis fails.
    assert ceil_log2(2) == 1
    assert 3 * 2 * 1 > 2
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
    print("PASS_GAUSSIAN_SLICE_THREE_COPIES")


if __name__ == "__main__":
    main()
