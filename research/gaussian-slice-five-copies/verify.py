#!/usr/bin/env python3
"""Absorb g copies of the heavy slice by the factor-5 gate.

Every comparison is an integer identity. The inverse bound stays a hypothesis.
The coefficient-9 monomial gate stays at 16.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-slice-five-copies"


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
    # Fifths spend 80 p. Copies replace 40 L by 5 p once 8 L <= p.
    assert 80 * 5 == 400
    assert 5 * 8 == 40
    assert 40 == 5 * 8
    assert 80 + 5 == 85
    assert 40 * (2 * 3 + 5) == 20 * (4 * 3 + 2 * 5)
    # 5 L > 1, so the gate forces g < 2^L.
    assert 5 > 1
    # 8 (m + 1) <= 2^m for m >= 6, and the step preserves a doubling.
    assert 8 * 7 <= 2**6
    assert 8 <= 2**6
    assert 2**6 + 8 <= 2**7
    assert ceil_log2(64) == 6
    assert ceil_log2(65) == 7
    assert 8 * 6 <= 64
    assert 8 * 7 <= 65
    # 20 p^2 - 85 p - 80 is positive at p = 64 and increases by 40 p - 65.
    assert 20 * 64 * 64 - 85 * 64 - 80 == 76400
    assert 76400 > 0
    assert (20 * 65 * 65 - 85 * 65 - 80) - 76400 == 40 * 64 - 65


def witness() -> None:
    # Two axes at p = 70 meet factor 5 and miss factor 6.
    level = ceil_log2(70)
    assert level == 7
    assert 5 * 2 * level <= 70
    assert 6 * 2 * level > 70
    assert 2 < 2**level
    one = 10 * 2 * level + 1 - 70 * 70
    copies = one + level
    assert one == -4759
    assert copies == -4752
    assert copies <= -1


def outside() -> None:
    # At p = 2 and g = 2 the factor-5 hypothesis fails.
    assert ceil_log2(2) == 1
    assert 5 * 2 * 1 > 2
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
    print("PASS_GAUSSIAN_SLICE_FIVE_COPIES")


if __name__ == "__main__":
    main()
